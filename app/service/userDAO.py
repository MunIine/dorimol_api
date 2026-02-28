from sqlalchemy.exc import SQLAlchemyError

from app.dao import BaseDAO
from app.models import User
from app.database import async_session_maker
from sqlalchemy import select

class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def get_user(cls, uid: str):
        async with async_session_maker() as session:
            result = await session.execute(select(cls.model).where(cls.model.uid == uid))
            user = result.scalars().one_or_none()
            return user
        
    @classmethod
    async def create_user(cls, uid: str, phone_number: str | None = None):
        async with async_session_maker() as session:
            async with session.begin():
                user = User(uid=uid, phone_number=phone_number)
                session.add(user)
                try:
                    await session.flush()
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                
                return user
            
    @classmethod
    async def update_user(cls, uid: str, data: dict):
        async with async_session_maker() as session:
            async with session.begin():
                result = await session.execute(select(cls.model).where(cls.model.uid == uid))
                user = result.scalars().one_or_none()
                if user is None:
                    raise ValueError(f"User with uid '{uid}' not found")
                
                for key, value in data.items():
                    setattr(user, key, value)
                
                try:
                    await session.flush()
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                
                return user