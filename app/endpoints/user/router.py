from fastapi import APIRouter, Header
from app.schema import SOrderPreview, STokens, SUserFull, SUserUpdate
from app.service.user_service import UserService
from app.endpoints.orders.dao import OrdersDAO

router = APIRouter(prefix='/user', tags=['Пользователь'])

@router.post("/update", summary="Обновление данных пользователя", response_model=STokens)
async def update_user(body: SUserUpdate, authorization: str | None = Header(None)):
    user_service = UserService()
    user = await user_service.update_user(body, authorization)

    tokens = user_service.token_service.generate_tokens(user)

    return tokens

@router.get("/me", summary="Получение данных текущего пользователя", response_model=SUserFull)
async def get_current_user(authorization: str | None = Header(None)):
    user_service = UserService()

    user = await user_service.get_current_user(authorization)
    return user

@router.get("/me/orders", summary="Получение заказов текущего пользователя", response_model=list[SOrderPreview])
async def get_current_user_orders(authorization: str | None = Header(None)):
    user_service = UserService()
    current_user = await user_service.get_current_user(authorization)

    orders = await OrdersDAO.get_orders_by_user(current_user.uid)
    return orders