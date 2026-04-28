from app.constants import OrderConst
class RBOrdersByUser:
    def __init__(self, limit: int = OrderConst.orders_by_user_limit_default, offset: int = 0):
        self.limit = limit
        self.offset = offset

    def to_dict(self) -> dict:
        return {
            'limit': self.limit,
            'offset': self.offset
        }