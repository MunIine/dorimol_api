from fastapi import APIRouter, Header, Response
from app.schema import STokens, SAuthFirebaseIdToken
from app.service.user_service import UserService 

router = APIRouter(prefix='/auth', tags=['Авторизация'])

@router.post("/firebase", summary="Авторизация firebase", response_model=STokens)
async def create_jwt(body: SAuthFirebaseIdToken):
    user_service = UserService()
    user = await user_service.get_user(body.id_token)

    tokens = user_service.token_service.generate_tokens(user)
    
    return tokens

@router.post("/refresh", summary="Обновление токенов", response_model=STokens)
async def refresh_tokens(authorization: str | None = Header(None)):
    user_service = UserService()

    token = user_service.token_service.check_authorization(authorization)
    tokens = user_service.token_service.refresh_tokens(token)
    
    return tokens

@router.get("/validate", summary="Проверка валидности токена")
async def validate_token(authorization: str | None = Header(None)):
    user_service = UserService()
    token = user_service.token_service.check_authorization(authorization)
    user_service.token_service.decode_token(token)
    return Response(status_code=200)