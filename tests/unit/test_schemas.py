import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.constants import DeliveryTypes
from app.schema import (
    SProduct,
    SOrderItemAdd,
    SOrderAdd,
)


def test_product_schema_valid():
    data = {
        "id": "12345678",
        "category_id": 1,
        "name": "Яблоко",
        "image_url": "/media/products/apple.webp",
        "price": 100.0,
        "wholesale_price": 80.0,
        "wholesale_start_quantity": 10.0,
        "unit": "кг",
        "stock": 50.0,
        "status": "default",
        "order_count": 5,
        "rating": 4.8,
    }
    product = SProduct.model_validate(data)
    assert product.id == "12345678"
    assert product.price == 100.0
    assert product.rating == 4.8


def test_product_schema_invalid_id_length():
    data = {
        "id": "short",  # < 8 символов
        "category_id": 1,
        "name": "Яблоко",
        "image_url": "/media/products/apple.webp",
        "price": 100.0,
        "wholesale_price": 80.0,
        "wholesale_start_quantity": 10.0,
        "unit": "кг",
        "stock": 50.0,
        "status": "default",
        "order_count": 5,
        "rating": 4.8,
    }
    with pytest.raises(ValidationError):
        SProduct.model_validate(data)


def test_order_item_add_schema_valid():
    item = SOrderItemAdd(product_id="12345678", quantity=3.5)
    assert item.product_id == "12345678"
    assert item.quantity == 3.5


def test_order_item_add_schema_negative_quantity():
    with pytest.raises(ValidationError):
        SOrderItemAdd(product_id="12345678", quantity=0)

    with pytest.raises(ValidationError):
        SOrderItemAdd(product_id="12345678", quantity=-2.0)


def test_order_add_schema_valid():
    data = {
        "delivery_type": DeliveryTypes.COURIER,
        "expected_total_price": Decimal("500.00"),
        "city": "Test city",
        "address": "Test address",
        "comment": "Test comment",
        "items": [
            {"product_id": "12345678", "quantity": 2.0}
        ],
    }
    order = SOrderAdd.model_validate(data)
    assert order.delivery_type == DeliveryTypes.COURIER
    assert order.expected_total_price == Decimal("500.00")
    assert len(order.items) == 1


def test_order_add_schema_invalid_delivery_type():
    data = {
        "delivery_type": "invalid_type",
        "expected_total_price": Decimal("500.00"),
        "items": [{"product_id": "12345678", "quantity": 1.0}],
    }
    with pytest.raises(ValidationError):
        SOrderAdd.model_validate(data)
