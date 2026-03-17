from fastapi import APIRouter, Depends, Header, Response
from app.dependencies import get_authorization, get_user_service
from app.schema import STokens, SAuthFirebaseIdToken
from app.service.user_service import UserService 

router = APIRouter(prefix='/auth', tags=['Авторизация'])

@router.post("/firebase", summary="Авторизация firebase", response_model=STokens)
async def create_jwt(body: SAuthFirebaseIdToken, user_service: UserService = Depends(get_user_service)):
    user = await user_service.get_or_create_user(body.id_token)
    tokens = user_service.token_service.generate_tokens(user)
    return tokens

@router.post("/refresh", summary="Обновление токенов", response_model=STokens)
async def refresh_tokens(
    authorization: str = Depends(get_authorization),
    user_service: UserService = Depends(get_user_service)
):
    tokens = await user_service.refresh_tokens(authorization)
    return tokens

@router.get("/validate", summary="Проверка валидности токена")
async def validate_token(
    authorization: str = Depends(get_authorization),
    user_service: UserService = Depends(get_user_service)
):
    user_service.token_service.check_authorization(authorization)
    return Response(status_code=200)