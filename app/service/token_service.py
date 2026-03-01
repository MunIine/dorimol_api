from fastapi import HTTPException
from app.config import get_jwt_secret_key
import jwt
import time

from app.schema import STokens, SUser

class TokenService:
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
            "role": user.role,
            "onboarding_completed": user.onboarding_completed,
            "iat": now,
            "exp": now + 30 * 24 * 3600,
        }
        token = jwt.encode(payload, get_jwt_secret_key(), algorithm="HS256")
        return token
    
    def generate_tokens(self, user: SUser):
        access_token = self.generate_access_token(user)
        refresh_token = self.generate_refresh_token(user)
        return STokens(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        
    def check_authorization(self, authorization: str | None):
        """Check authorization header and return decoded token payload if valid, otherwise raise HTTPException.

        :param authorization: Authorization header value, expected format "Bearer <token>
        :type authorization: str | None

        :raises HTTPException[401]: Authorization header missing
        :raises HTTPException[401]: Invalid authentication scheme
        :raises HTTPException[401]: Invalid authorization header format
        :raises HTTPException[401]: Token expired
        :raises HTTPException[401]: Token invalid

        :rtype: dict[str, Any]
        :returns: payload
        """
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(status_code=401, detail="Invalid authentication scheme")
            return jwt.decode(token, key=get_jwt_secret_key(), algorithms=["HS256"])
        
        except ValueError:
           raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token invalid")
    
    def refresh_tokens(self, authorization: str | None):
        payload = self.check_authorization(authorization)
        if payload.get("exp", 0) < int(time.time()):
            raise HTTPException(status_code=401, detail="Refresh token expired")
        
        try:
            user = SUser.from_dict(payload)
            return self.generate_tokens(user)
        except KeyError:
            raise HTTPException(status_code=401, detail="Invalid token payload")