from fastapi import APIRouter
from app.schema import STokens, SAuthFirebaseIdToken
from app.service.user_service import UserService 

router = APIRouter(prefix='/auth', tags=['Авторизация'])

@router.post("/firebase", summary="Авторизация firebase", response_model=STokens)
async def create_jwt(body: SAuthFirebaseIdToken):
    user_service = UserService()
    user = await user_service.get_user(body.id_token)

    access_token, refresh_token = user_service.token_service.generate_tokens(user)
    
    return STokens(
        access_token=access_token,
        refresh_token=refresh_token,
    )