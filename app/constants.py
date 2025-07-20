from enum import Enum
from sqlalchemy import asc, case, desc

class ProductConst():
    units = ["кг", "шт"]
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
            

class PriceConst:
    delivery_price = 30