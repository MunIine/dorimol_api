from firebase_admin import auth
from app.schema import SUser, SUserUpdate
from app.service.userDAO import UserDAO
from app.service.token_service import TokenService

class UserService:
    def __init__(self):
        self.token_service = TokenService()

    async def get_user(self, id_token: str) -> SUser:
        response = auth.verify_id_token(id_token=id_token, clock_skew_seconds=3)
        uid = response["uid"]

        user = await UserDAO.get_user(uid)
        if user is not None:
            return SUser.from_user(user)
        
        user = await UserDAO.create_user(uid)
        return SUser.from_user(user)
    
    async def update_user(self, update_body: SUserUpdate, access_token: str):
        data = update_body.to_dict()
        data = {k: v for k, v in data.items() if v is not None}

        uid = TokenService().decode_token(access_token)["uid"]
        user = await UserDAO.update_user(uid, data)

        return SUser.from_user(user)