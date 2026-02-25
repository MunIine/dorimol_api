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
    async def create_user(cls, uid: str):
        async with async_session_maker() as session:
            async with session.begin():
                user = User(uid=uid)
                session.add(user)
                try:
                    await session.flush()
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                
                return user