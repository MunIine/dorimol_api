from unittest.mock import patch
import pytest

from app.schema import SUser
from app.service.token_service import TokenService
from app.service.userDAO import UserDAO

@pytest.mark.asyncio
@pytest.mark.api
async def test_auth_firebase_missing_body(async_client):
    response = await async_client.post("/auth/firebase", json={})
    assert response.status_code == 422

@pytest.mark.asyncio
@pytest.mark.api
async def test_auth_firebase_new_user(async_client, test_user):
    """Регистрация нового пользователя: проверяем, что запись реально сохраняется в PostgreSQL."""
    mock_firebase_response = {
        "uid": test_user["uid"],
        "phone_number": test_user["phone_number"]
    }

    # Мокаем только внешний вызов Firebase Admin SDK
    with patch("app.service.user_service.auth.verify_id_token", return_value=mock_firebase_response):
        response = await async_client.post(
            "/auth/firebase",
            json={"id_token": "valid_firebase_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    # Проверяем, что пользователь реально создан в PostgreSQL через реальный UserDAO
    created_user = await UserDAO.get_user(test_user["uid"])
    assert created_user is not None
    assert created_user.uid == test_user["uid"]
    assert created_user.phone_number == test_user["phone_number"]
    assert created_user.role == "user"


@pytest.mark.asyncio
@pytest.mark.api
async def test_auth_firebase_existing_user(async_client, db_user):
    """Вход уже существующего пользователя: нового пользователя не создает, отдает токены."""
    mock_firebase_response = {
        "uid": db_user.uid,
        "phone_number": db_user.phone_number
    }

    with patch("app.service.user_service.auth.verify_id_token", return_value=mock_firebase_response):
        response = await async_client.post(
            "/auth/firebase",
            json={"id_token": "valid_firebase_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data


@pytest.mark.asyncio
@pytest.mark.api
async def test_auth_refresh_tokens_with_real_db(async_client, db_user):
    """Обновление токенов с проверкой пользователя в реальной тестовой БД."""
    token_service = TokenService()
    tokens = token_service.generate_tokens(SUser.model_validate(db_user))

    response = await async_client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {tokens.refresh_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
@pytest.mark.api
async def test_auth_refresh_tokens_without_user_in_real_db(async_client, test_user):
    """Обновление токенов при отсутствии пользователя в реальной тестовой БД."""
    token_service = TokenService()
    tokens = token_service.generate_tokens(SUser.model_validate(test_user))

    response = await async_client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {tokens.refresh_token}"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.api
async def test_auth_refresh_tokens_missing_header(async_client):
    """Проверка ошибки 401 при отсутствии заголовка Authorization."""
    response = await async_client.post("/auth/refresh")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.api
async def test_auth_validate_token_success(async_client, test_user):
    """Проверка валидности JWT токена."""
    token_service = TokenService()
    user = SUser.model_validate(test_user)
    tokens = token_service.generate_tokens(user)

    response = await async_client.get(
        "/auth/validate",
        headers={"Authorization": f"Bearer {tokens.access_token}"}
    )

    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.api
async def test_auth_validate_token_missing_header(async_client):
    """Проверка ошибки 401 при отсутствии заголовка Authorization."""
    response = await async_client.get("/auth/validate")
    assert response.status_code == 401
