import jwt
import time
from firebase_admin import auth
from app.config import get_jwt_secret_key
from app.schema import SUser
from app.service.userDAO import UserDAO


class UserService:
    async def get_user(self, id_token: str) -> SUser:
        response = auth.verify_id_token(id_token=id_token, clock_skew_seconds=3)
        uid = response["uid"]

        user = await UserDAO.get_user(uid)
        if user is not None:
            return SUser(
                uid=user.uid,
                role=user.role,
                onboarding_completed=user.onboarding_completed
            )
        
        user = await UserDAO.create_user(uid)
        return SUser(
            uid=user.uid,
            role=user.role,
            onboarding_completed=user.onboarding_completed
        )
    
    def generate_access_token(self, user: SUser):
        now = int(time.time())
        payload = {
            "uid": user.uid,
            "role": user.role,
            "onboarding_completed": user.onboarding_completed,
            "iat": now,
            "exp": now + 3600,
        }
        token = jwt.encode(payload, get_jwt_secret_key(), algorithm="HS256")
        return token
    
    def generate_refresh_token(self, user: SUser):
        now = int(time.time())
        payload = {
            "uid": user.uid,
            "iat": now,
            "exp": now + 30 * 24 * 3600,
        }
        token = jwt.encode(payload, get_jwt_secret_key(), algorithm="HS256")
        return token