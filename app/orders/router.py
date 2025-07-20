from fastapi import APIRouter
from app.orders.dao import OrdersDAO
from app.schema import SOrderAdd

router = APIRouter(prefix='/orders', tags=['Заказы'])

@router.post(path="/add/")
async def add_order(order: SOrderAdd):
    check = await OrdersDAO.add_order(order)
    if check:
        return {"message": "Заказ успешно добавлен", "order": order}
    else:
        return {"message": "Ошибка при добавлении заказа"}