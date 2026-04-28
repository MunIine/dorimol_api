from fastapi import APIRouter, Depends, File, Header, UploadFile
from app.dependencies import get_authorization, get_user_service
from app.endpoints.orders.rb import RBOrdersByUser
from app.schema import SCurrentUserOrders, SOrderPreview, SUserFull, SUserUpdate
from app.service.user_service import UserService
from app.endpoints.orders.dao import OrdersDAO

router = APIRouter(prefix='/user', tags=['Пользователь'])

@router.patch("/update", summary="Обновление данных пользователя", response_model=SUserFull)
async def update_user(
    body: SUserUpdate,
    authorization: str = Depends(get_authorization),
    user_service: UserService = Depends(get_user_service)
):
    await user_service.update_user(body, authorization)
    
    user = await user_service.get_current_user_full(authorization)
    return user

@router.post("/update/avatar", summary="Обновление аватара пользователя", response_model=SUserFull)
async def update_user_avatar(
    avatar: UploadFile = File(...),
    authorization: str = Depends(get_authorization),
    user_service: UserService = Depends(get_user_service)
):
    await user_service.update_user_avatar(avatar, authorization)
    
    user = await user_service.get_current_user_full(authorization)
    return user

@router.get("/me", summary="Получение данных текущего пользователя", response_model=SUserFull)
async def get_current_user(
    authorization: str = Depends(get_authorization),
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_current_user_full(authorization)
    return user

@router.get("/me/orders", summary="Получение заказов текущего пользователя", response_model=SCurrentUserOrders)
async def get_current_user_orders(
    authorization: str = Depends(get_authorization),
    user_service: UserService = Depends(get_user_service),
    request_body: RBOrdersByUser = Depends(RBOrdersByUser)
):
    uid = user_service.token_service.check_authorization(authorization)["uid"]
    parameters = request_body.to_dict()

    orders, next_offset = await OrdersDAO.get_orders_by_user(uid, **parameters)
    return SCurrentUserOrders(
        orders=orders,
        offset=parameters["offset"],
        limit=parameters["limit"],
        next_offset=next_offset,
    )