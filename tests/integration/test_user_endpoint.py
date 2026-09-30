import asyncio
import os
import pytest
from app.constants import AvatarUploadConst
from app.schema import SUser
from app.service.token_service import TokenService
from app.service.userDAO import UserDAO


@pytest.mark.api
@pytest.mark.asyncio
async def test_user_me(test_tokens, test_user, async_client):
    response = await async_client.get(
        "/user/me",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["uid"] == test_user["uid"]
    assert data["phone_number"] == test_user["phone_number"]


@pytest.mark.api
@pytest.mark.asyncio
async def test_user_me_without_authorization(async_client):
    response = await async_client.get("/user/me")
    assert response.status_code == 401


# ==================== User Update Tests ====================


@pytest.mark.api
@pytest.mark.asyncio
async def test_user_update(test_tokens, async_client):
    response = await async_client.patch(
        "/user/update",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"},
        json={"name": "test", "onboarding_completed": True}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test"
    assert data["onboarding_completed"] is True


@pytest.mark.api
@pytest.mark.asyncio
async def test_update_non_created_user(async_client):
    tokens = TokenService().generate_tokens(SUser(
        uid="noname",
        role="user",
        onboarding_completed=False
    ))
    response = await async_client.patch(
        "/user/update",
        headers={"Authorization": f"Bearer {tokens.access_token}"},
        json={"name": "test", "onboarding_completed": True}
    )
    assert response.status_code == 401


@pytest.mark.api
@pytest.mark.asyncio
async def test_user_update_without_authorization(async_client):
    response = await async_client.patch(
        "/user/update",
        json={"name": "test", "onboarding_completed": True}
    )
    assert response.status_code == 401


# ==================== User Orders Tests ====================


@pytest.mark.api
@pytest.mark.asyncio
async def test_orders_non_created_user(async_client):
    tokens = TokenService().generate_tokens(SUser(
        uid="noname",
        role="user",
        onboarding_completed=False
    ))
    response = await async_client.get(
        "/user/me/orders",
        headers={"Authorization": f"Bearer {tokens.access_token}"}
    )

    assert response.status_code == 200
    assert response.json()["orders"] == []


@pytest.mark.api
@pytest.mark.asyncio
async def test_user_orders_empty(test_tokens, async_client):
    response = await async_client.get(
        "/user/me/orders",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"}
    )

    assert response.status_code == 200
    assert response.json()["orders"] == []


@pytest.mark.api
@pytest.mark.asyncio
async def test_user_orders_without_authorization(async_client):
    response = await async_client.get("/user/me/orders")
    assert response.status_code == 401


@pytest.mark.api
@pytest.mark.asyncio
async def test_orders_pagination(test_tokens, order_factory, async_client):
    orders = [await order_factory() for _ in range(5)]
    response = await async_client.get(
        "/user/me/orders?limit=2&offset=0",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["orders"]) == 2
    assert data["next_offset"] == 2


@pytest.mark.api
@pytest.mark.asyncio
async def test_orders_pagination_with_offset(test_tokens, order_factory, async_client):
    orders = [await order_factory() for _ in range(5)]
    response = await async_client.get(
        "/user/me/orders?limit=2&offset=4",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["orders"]) == 1
    assert data["next_offset"] is None


@pytest.mark.api
@pytest.mark.asyncio
async def test_orders_isolation(test_tokens, order_factory, async_client):
    await UserDAO.create_user(
        uid="another_user_uid",
        phone_number="number"
    )
    await order_factory(user_id="another_user_uid")
    my_order = await order_factory()
    response = await async_client.get(
        "/user/me/orders",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["orders"]) == 1
    assert data["orders"][0]["id"] == str(my_order.id)


# ==================== Avatar Upload Tests ====================


@pytest.mark.api
@pytest.mark.asyncio
async def test_update_avatar_success(test_tokens, test_user, test_image_bytes, async_client):
    files = {"avatar": ("avatar.png", test_image_bytes, "image/png")}
    response = await async_client.post(
        "/user/update/avatar",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"},
        files=files,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["image_url"] is not None
    assert data["image_url"].startswith("media/avatars/")
    assert os.path.exists(data["image_url"])

    user_in_db = await UserDAO.get_user(test_user["uid"])
    assert user_in_db is not None
    assert user_in_db.image_url == data["image_url"]


@pytest.mark.api
@pytest.mark.asyncio
async def test_update_avatar_replace(test_tokens, test_image_bytes, async_client):
    first_resp = await async_client.post(
        "/user/update/avatar",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"},
        files={"avatar": ("avatar1.png", test_image_bytes, "image/png")},
    )
    assert first_resp.status_code == 200
    first_path = first_resp.json()["image_url"]
    assert os.path.exists(first_path)

    await asyncio.sleep(1.05)

    second_resp = await async_client.post(
        "/user/update/avatar",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"},
        files={"avatar": ("avatar2.png", test_image_bytes, "image/png")},
    )
    assert second_resp.status_code == 200
    second_path = second_resp.json()["image_url"]
    assert first_path != second_path

    assert not os.path.exists(first_path)
    assert os.path.exists(second_path)


@pytest.mark.api
@pytest.mark.asyncio
async def test_update_avatar_invalid_format(test_tokens, async_client):
    files = {"avatar": ("document.txt", b"plain text is not an image", "text/plain")}
    response = await async_client.post(
        "/user/update/avatar",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"},
        files=files,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect file format"


@pytest.mark.api
@pytest.mark.asyncio
async def test_update_avatar_too_large(test_tokens, async_client):
    large_file = b"\x89PNG\r\n\x1a\n" + b"0" * (AvatarUploadConst.max_size + 1)
    files = {"avatar": ("large.png", large_file, "image/png")}
    response = await async_client.post(
        "/user/update/avatar",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"},
        files=files,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "File is too large"


@pytest.mark.api
@pytest.mark.asyncio
async def test_update_avatar_without_authorization(test_image_bytes, async_client):
    files = {"avatar": ("avatar.png", test_image_bytes, "image/png")}
    response = await async_client.post(
        "/user/update/avatar",
        files=files,
    )

    assert response.status_code == 401
