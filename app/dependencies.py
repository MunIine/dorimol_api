from fastapi import Header, HTTPException
from app.service.user_service import UserService

def get_user_service() -> UserService:
    return UserService()

def get_authorization(authorization: str | None = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authorized")
    return authorization