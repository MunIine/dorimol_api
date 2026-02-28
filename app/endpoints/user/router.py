from fastapi import APIRouter, Header
from app.schema import STokens, SUserFull, SUserUpdate
from app.service.user_service import UserService 

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