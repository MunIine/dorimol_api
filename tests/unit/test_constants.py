from app.constants import (
    ProductConst,
    SortingProductConst,
    OrderConst,
    DeliveryTypes,
    DiscountConst,
)


def test_product_constants():
    assert ProductConst.default_status == "default"
    assert "new" in ProductConst.statuses
    assert "sale" in ProductConst.statuses


def test_sorting_product_constants():
    assert SortingProductConst.price_asc.value == "price_asc"
    assert SortingProductConst.price_desc.value == "price_desc"
    assert SortingProductConst.popularity.value == "popularity"
    assert SortingProductConst.new.value == "new"
    assert SortingProductConst.sale.value == "sale"


def test_order_constants():
    assert OrderConst.default_status == "pending"
    assert "confirmed" in OrderConst.statuses
    assert "delivered" in OrderConst.statuses
    assert OrderConst.orders_by_user_limit_default == 25


def test_delivery_types_enum():
    assert DeliveryTypes.PICKUP.value == "pickup"
    assert DeliveryTypes.COURIER.value == "courier"


def test_discount_constants():
    assert len(DiscountConst.discount_tiers) == 3
    assert DiscountConst.discount_tiers[0] == {"percent": 3, "orders_required": 3}
    assert DiscountConst.discount_tiers[1] == {"percent": 5, "orders_required": 6}
    assert DiscountConst.discount_tiers[2] == {"percent": 7, "orders_required": 10}
