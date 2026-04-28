from enum import Enum
from sqlalchemy import asc, case, desc

class ProductConst:
    statuses = ["default", "new", "sale"]
    default_status = "default"

class SortingProductConst(str, Enum):
    default = "popularity"
    price_asc = "price_asc"
    price_desc = "price_desc"
    popularity = "popularity"
    new = "new"
    sale = "sale"

    def sort_expression(self, Product):
        match self:
            case SortingProductConst.price_asc:
                return asc(Product.price)
            case SortingProductConst.price_desc:
                return desc(Product.price)
            case SortingProductConst.popularity:
                return desc(Product.order_count)
            case SortingProductConst.new:
                return case((Product.status == "new", 0), else_=1)
            case SortingProductConst.sale:
                return case((Product.status == "sale", 0), else_=1)

class OrderConst:
    statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
    default_status = "pending"
    orders_by_user_limit_default = 25

class DeliveryTypes(str, Enum):
    PICKUP = "pickup"
    COURIER = "courier"
class AvatarUploadConst:
    max_size = 5 * 1024 * 1024 # 5MB
    MAGIC_BYTES = {
        b"\xff\xd8\xff": "jpeg",
        b"\x89PNG": "png",
        b"RIFF": "webp",
    }

    @staticmethod
    def get_image_type(data: bytes) -> str | None:
        for magic, fmt in AvatarUploadConst.MAGIC_BYTES.items():
            if data.startswith(magic):
                # webp дополнительная проверка из-за контейнера riff
                if fmt == "webp" and data[8:12] != b"WEBP":
                    continue
                return fmt
        return None
    
class DiscountConst:
    discount_tiers = [
        {"percent": 3, "orders_required": 3},
        {"percent": 5, "orders_required": 6},
        {"percent": 7, "orders_required": 10},
    ]