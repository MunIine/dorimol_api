import os
import time
import asyncio
import aiofiles
from fastapi import HTTPException, UploadFile
from firebase_admin import auth
from app.constants import AvatarUploadConst
from app.schema import SUser, SUserFull, SUserUpdate
from app.service.image_service import process_avatar
from app.service.userDAO import UserDAO
from app.service.token_service import TokenService

class UserService:
    def __init__(self):
        self.token_service = TokenService()

    async def get_or_create_user(self, id_token: str) -> SUser:
        response = auth.verify_id_token(id_token=id_token, clock_skew_seconds=3)
        uid = response["uid"]

        user = await UserDAO.get_user(uid)
        if user is not None:
            return SUser.model_validate(user)
        
        user = await UserDAO.create_user(uid, phone_number=response.get("phone_number"))
        return SUser.model_validate(user)
    
    async def get_current_user(self, authorization: str | None) -> SUserFull:
        payloads = self.token_service.check_authorization(authorization)
        uid = payloads["uid"]

        user, orders_amount = await UserDAO.get_user_with_orders_count(uid)
        
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user.__dict__.copy()
        user_data["orders_amount"] = orders_amount
        return SUserFull.model_validate(user_data)
    
    async def update_user(self, update_body: SUserUpdate, authorization: str | None) -> SUser:
        data = update_body.model_dump(exclude_unset=True)

        uid = self.token_service.check_authorization(authorization)["uid"]
        user = await UserDAO.update_user(uid, data)

        return SUser.model_validate(user)
    
    async def update_user_avatar(self, avatar: UploadFile, authorization: str | None):
        uid = self.token_service.check_authorization(authorization)["uid"]
        user = await UserDAO.get_user(uid)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        file = await avatar.read()

        if AvatarUploadConst.get_image_type(file) is None:
            raise HTTPException(status_code=400, detail="Incorrect file format")

        if len(file) > AvatarUploadConst.max_size:
            raise HTTPException(status_code=400, detail="File is too large")

        new_avatar = await asyncio.to_thread(process_avatar, file)

        file_path = f"media/avatars/{uid}_{int(time.time())}.webp"
        old_file_path = user.image_url

        await UserDAO.update_user(uid, {"image_url": file_path})

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(new_avatar)

        if old_file_path and await asyncio.to_thread(os.path.exists, old_file_path):
            await asyncio.to_thread(os.remove, old_file_path)
    
    async def refresh_tokens(self, authorization: str | None):
        payload = self.token_service.check_authorization(authorization)
        if payload.get("exp", 0) < int(time.time()):
            raise HTTPException(status_code=401, detail="Refresh token expired")
        
        try:
            user = await UserDAO.get_user(payload['uid'])
            return self.token_service.generate_tokens(SUser.model_validate(user))
        except KeyError:
            raise HTTPException(status_code=401, detail="Invalid token payload")