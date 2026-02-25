from fastapi import APIRouter
from app.schema import SAuthFirebaseAnwer, SAuthFirebaseIdToken
from app.service.user_service import UserService 

router = APIRouter(prefix='/auth', tags=['Авторизация'])

@router.post("/firebase", summary="Авторизация firebase", response_model=SAuthFirebaseAnwer)
async def create_jwt(body: SAuthFirebaseIdToken):
    user_service = UserService()
    user = user_service.get_user(body.id_token)
    access_token = user_service.generate_access_token(user)
    refresh_token = user_service.generate_refresh_token(user)
    return SAuthFirebaseAnwer(
        access_token=access_token,
        refresh_token=refresh_token,
    )