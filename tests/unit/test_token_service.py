import time
import jwt
import pytest
from fastapi import HTTPException

from app.config import get_jwt_secret_key
from app.schema import SUser
from app.service.token_service import TokenService


def test_create_and_validate_jwt(test_user):
    service = TokenService()
    user = SUser.model_validate(test_user)
    tokens = service.generate_tokens(user)

    assert tokens.access_token is not None
    assert tokens.refresh_token is not None

    payload = service.check_authorization(f"Bearer {tokens.access_token}")
    assert payload["uid"] == test_user["uid"]
    assert payload["role"] == test_user["role"]
    assert payload["onboarding_completed"] == test_user["onboarding_completed"]


def test_check_authorization_missing_header():
    service = TokenService()
    with pytest.raises(HTTPException) as exc_info:
        service.check_authorization(None)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authorization header missing"


def test_check_authorization_invalid_format():
    service = TokenService()
    with pytest.raises(HTTPException) as exc_info:
        service.check_authorization("InvalidHeaderFormat")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authorization header format"


def test_check_authorization_invalid_scheme():
    service = TokenService()
    with pytest.raises(HTTPException) as exc_info:
        service.check_authorization("Basic some_base64_token")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication scheme"


def test_check_authorization_expired_token():
    service = TokenService()
    # Создаем заведомо просроченный токен (exp в прошлом)
    now = int(time.time()) - 3600
    expired_payload = {
        "uid": "user_expired",
        "role": "user",
        "onboarding_completed": True,
        "iat": now - 3600,
        "exp": now,
    }
    expired_token = jwt.encode(expired_payload, get_jwt_secret_key(), algorithm="HS256")

    with pytest.raises(HTTPException) as exc_info:
        service.check_authorization(f"Bearer {expired_token}")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token expired"


def test_check_authorization_invalid_signature():
    service = TokenService()
    # Токен, подделанный с другим секретным ключом
    payload = {"uid": "hacker", "role": "admin", "exp": int(time.time()) + 3600}
    fake_token = jwt.encode(payload, "wrong_secret_key_at_least_32_bytes_long_123", algorithm="HS256")

    with pytest.raises(HTTPException) as exc_info:
        service.check_authorization(f"Bearer {fake_token}")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token invalid"


def test_check_authorization_empty_string():
    service = TokenService()
    with pytest.raises(HTTPException) as exc_info:
        service.check_authorization("")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authorization header missing"


def test_check_authorization_too_many_parts():
    service = TokenService()
    with pytest.raises(HTTPException) as exc_info:
        service.check_authorization("Bearer token extra_argument")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authorization header format"


def test_check_authorization_malformed_token():
    service = TokenService()
    with pytest.raises(HTTPException) as exc_info:
        service.check_authorization("Bearer not_a_valid_jwt_string")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token invalid"


def test_check_authorization_case_insensitive_scheme(test_user):
    service = TokenService()
    user = SUser.model_validate(test_user)
    tokens = service.generate_tokens(user)

    # Проверяем lowercase 'bearer'
    payload = service.check_authorization(f"bearer {tokens.access_token}")
    assert payload["uid"] == test_user["uid"]

    # Проверяем uppercase 'BEARER'
    payload = service.check_authorization(f"BEARER {tokens.access_token}")
    assert payload["uid"] == test_user["uid"]


def test_check_authorization_unsupported_algorithm():
    service = TokenService()
    # Токен, закодированный неподдерживаемым алгоритмом (HS384 вместо HS256)
    payload = {"uid": "user1", "exp": int(time.time()) + 3600}
    token = jwt.encode(payload, "a" * 64, algorithm="HS384")

    with pytest.raises(HTTPException) as exc_info:
        service.check_authorization(f"Bearer {token}")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token invalid"

