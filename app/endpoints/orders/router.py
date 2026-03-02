from fastapi import APIRouter, Header
from app.email import send_order_email
from app.endpoints.orders.dao import OrdersDAO
from app.schema import SOrder, SOrderAdd
from app.service.user_service import UserService

router = APIRouter(prefix='/orders', tags=['Заказы'])

@router.post(path="/add")
async def add_order(order: SOrderAdd):
    check = await OrdersDAO.add_order(order)
    if check:
        await send_order_email(check)
        return {"message": "Заказ успешно добавлен", "order": order}
    else:
        return {"message": "Ошибка при добавлении заказа"}

@router.get(path="/{order_id}", summary="Получение заказа по ID", response_model=SOrder)
async def get_order_by_id(order_id: int, authorization: str | None = Header(None)):
    user_service = UserService()
    user = await user_service.get_current_user(authorization)

    order = await OrdersDAO.get_order_by_id(order_id, user.uid)
    return order