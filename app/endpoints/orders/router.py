from uuid import UUID

from fastapi import APIRouter, Depends, Response
from app.dependencies import get_authorization, get_user_service
from app.email import send_order_email
from app.endpoints.orders.dao import OrdersDAO
from app.schema import SOrder, SOrderAdd
from app.service.user_service import UserService

router = APIRouter(prefix='/orders', tags=['Заказы'])

@router.post(path="/add", status_code=201)
async def add_order(
    order: SOrderAdd, 
    authorization: str = Depends(get_authorization),
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_current_user_full(authorization)
    new_order = await OrdersDAO.add_order(order, user)
    return {"id": new_order.id}

@router.get(path="/{order_id}", summary="Получение заказа по ID", response_model=SOrder)
async def get_order_by_id(
    order_id: UUID, 
    authorization: str = Depends(get_authorization),
    user_service: UserService = Depends(get_user_service)
):
    uid = user_service.token_service.check_authorization(authorization)["uid"]

    order = await OrdersDAO.get_order_by_id(order_id, uid)
    return order