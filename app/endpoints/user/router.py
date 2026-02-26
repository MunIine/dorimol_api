from fastapi import APIRouter, HTTPException, Header
from app.schema import STokens, SUserUpdate
from app.service.user_service import UserService 

router = APIRouter(prefix='/user', tags=['Пользователь'])

@router.post("/update", summary="Обновление данных пользователя", response_model=STokens)
async def update_user(body: SUserUpdate, authorization: str | None = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    user_service = UserService()
    user = await user_service.update_user(body, token)

    access_token, refresh_token = user_service.token_service.generate_tokens(user)

    return STokens(
        access_token=access_token,
        refresh_token=refresh_token,
    )