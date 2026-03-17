from uuid import UUID

from fastapi import APIRouter, Depends
from app.dependencies import get_authorization, get_user_service
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
async def get_order_by_id(
    order_id: UUID, 
    authorization: str = Depends(get_authorization),
    user_service: UserService = Depends(get_user_service)
):
    uid = user_service.token_service.check_authorization(authorization)["uid"]

    order = await OrdersDAO.get_order_by_id(order_id, uid)
    return order