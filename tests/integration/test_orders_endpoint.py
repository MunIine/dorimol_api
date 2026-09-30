from decimal import Decimal
import uuid
import pytest
from app.constants import DeliveryTypes
from app.database import async_session_maker
from app.models import Order
from app.schema import SUser
from app.service.token_service import TokenService
from app.service.userDAO import UserDAO
from sqlalchemy import select
from sqlalchemy.orm import joinedload


# ==================== POST /orders/add Tests ====================


@pytest.mark.api
@pytest.mark.asyncio
async def test_add_order_pickup_success(test_tokens, registered_user, db_product, async_client):
    """Успешное создание заказа с самовывозом (розничная цена, без скидки)."""
    # 2 шт * 100.0 = 200.00 (< wholesale_start_quantity = 5.0)
    order_data = {
        "delivery_type": DeliveryTypes.PICKUP.value,
        "expected_total_price": "200.00",
        "comment": "Заберу сам в 18:00",
        "items": [
            {"product_id": db_product.id, "quantity": 2.0}
        ]
    }

    response = await async_client.post(
        "/orders/add",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"},
        json=order_data
    )

    assert response.status_code == 201
    result = response.json()
    assert "id" in result
    order_id = uuid.UUID(result["id"])

    # Проверяем сохраненные данные в БД
    async with async_session_maker() as session:
        db_order = (await session.execute(
            select(Order).options(joinedload(Order.items)).where(Order.id == order_id)
        )).unique().scalar_one_or_none()

        assert db_order is not None
        assert db_order.user_id == registered_user.uid
        assert db_order.delivery_type == DeliveryTypes.PICKUP
        assert db_order.full_name == registered_user.name
        assert db_order.phone_number == registered_user.phone_number
        assert db_order.comment == "Заберу сам в 18:00"
        assert db_order.city is None
        assert db_order.address is None
        assert db_order.total_price == Decimal("200.00")
        assert len(db_order.items) == 1
        assert db_order.items[0].product_id == db_product.id
        assert db_order.items[0].quantity == 2.0
        assert db_order.items[0].item_price == Decimal("200.00")


@pytest.mark.api
@pytest.mark.asyncio
async def test_add_order_courier_success(test_tokens, registered_user, db_product, async_client):
    """Успешное создание курьерского заказа с указанием города и адреса."""
    order_data = {
        "delivery_type": DeliveryTypes.COURIER.value,
        "expected_total_price": "100.00",
        "city": "Тирасполь",
        "address": "ул. 25 Октября, д. 1",
        "comment": "Код от домофона 42",
        "items": [
            {"product_id": db_product.id, "quantity": 1.0}
        ]
    }

    response = await async_client.post(
        "/orders/add",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"},
        json=order_data
    )

    assert response.status_code == 201
    order_id = uuid.UUID(response.json()["id"])

    async with async_session_maker() as session:
        db_order = (await session.execute(
            select(Order).where(Order.id == order_id)
        )).unique().scalar_one_or_none()

        assert db_order is not None
        assert db_order.delivery_type == DeliveryTypes.COURIER
        assert db_order.city == "Тирасполь"
        assert db_order.address == "ул. 25 Октября, д. 1"
        assert db_order.comment == "Код от домофона 42"


@pytest.mark.api
@pytest.mark.asyncio
async def test_add_order_wholesale_price(test_tokens, registered_user, product_factory, async_client):
    """Проверка применения оптовой цены при количестве >= wholesale_start_quantity."""
    product = await product_factory(
        price=100.0,
        wholesale_price=75.0,
        wholesale_start_quantity=5.0
    )
    # 6 шт >= 5.0 -> оптовая цена 75.0 * 6 = 450.00
    order_data = {
        "delivery_type": DeliveryTypes.PICKUP.value,
        "expected_total_price": "450.00",
        "items": [
            {"product_id": product.id, "quantity": 6.0}
        ]
    }

    response = await async_client.post(
        "/orders/add",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"},
        json=order_data
    )

    assert response.status_code == 201
    order_id = uuid.UUID(response.json()["id"])

    async with async_session_maker() as session:
        db_order = (await session.execute(
            select(Order).options(joinedload(Order.items)).where(Order.id == order_id)
        )).unique().scalar_one_or_none()

        assert db_order is not None
        assert db_order.total_price == Decimal("450.00")
        assert db_order.items[0].item_price == Decimal("450.00")


@pytest.mark.api
@pytest.mark.asyncio
async def test_add_order_with_user_discount(test_tokens, registered_user, order_factory, db_product, async_client):
    """Проверка применения накопительной скидки пользователя (3 заказа = 3% скидки)."""
    # Создаем пользователю 3 предыдущих заказа, чтобы получить скидку 3%
    for _ in range(3):
        await order_factory()

    # Товар стоит 100.0. 2 шт = 200.00. Скидка 3%: 200.00 * (100 - 3) / 100 = 194.00
    order_data = {
        "delivery_type": DeliveryTypes.PICKUP.value,
        "expected_total_price": "194.00",
        "items": [
            {"product_id": db_product.id, "quantity": 2.0}
        ]
    }

    response = await async_client.post(
        "/orders/add",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"},
        json=order_data
    )

    assert response.status_code == 201
    order_id = uuid.UUID(response.json()["id"])

    async with async_session_maker() as session:
        db_order = (await session.execute(
            select(Order).where(Order.id == order_id)
        )).unique().scalar_one_or_none()

        assert db_order is not None
        assert db_order.total_price == Decimal("194.00")


@pytest.mark.api
@pytest.mark.asyncio
async def test_add_order_multiple_products(test_tokens, registered_user, product_factory, async_client):
    """Создание заказа с несколькими позициями (одна в розницу, вторая по оптовой цене)."""
    prod_retail = await product_factory(price=50.0, wholesale_price=40.0, wholesale_start_quantity=10.0)
    prod_wholesale = await product_factory(price=80.0, wholesale_price=60.0, wholesale_start_quantity=3.0)

    # prod_retail: 2 * 50.0 = 100.00
    # prod_wholesale: 4 * 60.0 = 240.00 (т.к. 4 >= 3)
    # Total: 340.00
    order_data = {
        "delivery_type": DeliveryTypes.PICKUP.value,
        "expected_total_price": "340.00",
        "items": [
            {"product_id": prod_retail.id, "quantity": 2.0},
            {"product_id": prod_wholesale.id, "quantity": 4.0},
        ]
    }

    response = await async_client.post(
        "/orders/add",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"},
        json=order_data
    )

    assert response.status_code == 201
    order_id = uuid.UUID(response.json()["id"])

    async with async_session_maker() as session:
        db_order = (await session.execute(
            select(Order).options(joinedload(Order.items)).where(Order.id == order_id)
        )).unique().scalar_one_or_none()

        assert db_order is not None
        assert db_order.total_price == Decimal("340.00")
        assert len(db_order.items) == 2
        assert db_order.items[0].item_price == Decimal("100.00")
        assert db_order.items[1].item_price == Decimal("240.00")


@pytest.mark.api
@pytest.mark.asyncio
async def test_add_order_price_mismatch_conflict(test_tokens, registered_user, db_product, async_client):
    """Ошибка 409 при расхождении ожидаемой и расчетной стоимости заказа."""
    order_data = {
        "delivery_type": DeliveryTypes.PICKUP.value,
        "expected_total_price": "999.99",  # Реальная стоимость: 100.00
        "items": [
            {"product_id": db_product.id, "quantity": 1.0}
        ]
    }

    response = await async_client.post(
        "/orders/add",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"},
        json=order_data
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Price changed. Please refresh page and try again"


@pytest.mark.api
@pytest.mark.asyncio
async def test_add_order_product_not_found(test_tokens, registered_user, async_client):
    """Ошибка 404 при попытке заказать несуществующий товар."""
    order_data = {
        "delivery_type": DeliveryTypes.PICKUP.value,
        "expected_total_price": "100.00",
        "items": [
            {"product_id": "nonexist", "quantity": 1.0}
        ]
    }

    response = await async_client.post(
        "/orders/add",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"},
        json=order_data
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


@pytest.mark.api
@pytest.mark.asyncio
async def test_add_order_without_authorization(db_product, async_client):
    """Ошибка 401 при создании заказа без токена авторизации."""
    order_data = {
        "delivery_type": DeliveryTypes.PICKUP.value,
        "expected_total_price": "100.00",
        "items": [
            {"product_id": db_product.id, "quantity": 1.0}
        ]
    }

    response = await async_client.post("/orders/add", json=order_data)
    assert response.status_code == 401


# ==================== GET /orders/{order_id} Tests ====================


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_order_by_id_success(test_tokens, registered_user, order_factory, async_client):
    """Успешное получение информации о заказе по его ID."""
    order = await order_factory(
        city="Бендеры",
        address="ул. Суворова 5",
        comment="Позвонить перед доставкой"
    )

    response = await async_client.get(
        f"/orders/{order.id}",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(order.id)
    assert data["status"] == order.status
    assert data["full_name"] == order.full_name
    assert data["phone_number"] == order.phone_number
    assert data["city"] == "Бендеры"
    assert data["address"] == "ул. Суворова 5"
    assert data["comment"] == "Позвонить перед доставкой"
    assert len(data["items"]) == len(order.items)
    assert "created_at" in data


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_order_by_id_isolation_another_user(order_factory, async_client):
    """Попытка пользователя запросить чужой заказ возвращает 404."""
    # Заказ принадлежит пользователю 1
    order = await order_factory()

    # Пользователь 2
    user2 = await UserDAO.create_user(uid="user_intruder_uid", phone_number="+37377777777")
    tokens_user2 = TokenService().generate_tokens(SUser(
        uid=user2.uid,
        role=user2.role,
        onboarding_completed=user2.onboarding_completed
    ))

    response = await async_client.get(
        f"/orders/{order.id}",
        headers={"Authorization": f"Bearer {tokens_user2.access_token}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_order_by_id_not_found(test_tokens, async_client):
    """Запрос несуществующего заказа возвращает 404."""
    random_id = uuid.uuid4()
    response = await async_client.get(
        f"/orders/{random_id}",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_order_by_id_invalid_uuid(test_tokens, async_client):
    """Передача некорректного UUID возвращает 422."""
    response = await async_client.get(
        "/orders/invalid-uuid-12345",
        headers={"Authorization": f"Bearer {test_tokens.access_token}"}
    )

    assert response.status_code == 422


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_order_by_id_without_authorization(order_factory, async_client):
    """Запрос заказа без авторизации возвращает 401."""
    order = await order_factory()

    response = await async_client.get(f"/orders/{order.id}")
    assert response.status_code == 401
