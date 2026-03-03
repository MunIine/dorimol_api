from sqlalchemy.exc import SQLAlchemyError

from app.dao import BaseDAO
from app.models import Order, User
from app.database import async_session_maker
from sqlalchemy import func, select

class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def get_user(cls, uid: str):
        async with async_session_maker() as session:
            result = await session.execute(select(cls.model).where(cls.model.uid == uid))
            user = result.scalars().one_or_none()
            return user

    @classmethod
    async def get_user_with_orders_count(cls, uid: str):
        async with async_session_maker() as session:
            orders_count_subq = select(func.count(Order.id)).where(Order.user_id == cls.model.uid).scalar_subquery()
            requst = select(cls.model, orders_count_subq.label("orders_count")).where(cls.model.uid == uid)
            result = await session.execute(requst)

            row = result.one_or_none()
            if row is None:
                return None, None
            
            user, orders_amount = row
            return user, orders_amount
        
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