from sqlalchemy.exc import SQLAlchemyError

from app.constants import DiscountConst
from app.dao import BaseDAO
from app.models import Order, User
from app.database import async_session_maker
from sqlalchemy import func, select

from app.schema import SUserFull

class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def get_user(cls, uid: str):
        async with async_session_maker() as session:
            result = await session.execute(select(cls.model).where(cls.model.uid == uid))
            user = result.scalars().one_or_none()
            return user

    @classmethod
    async def get_user_full(cls, uid: str):
        async with async_session_maker() as session:
            orders_count_subq = select(func.count(Order.id)).where(Order.user_id == cls.model.uid).scalar_subquery()
            requst = select(cls.model, orders_count_subq.label("orders_count")).where(cls.model.uid == uid)
            result = await session.execute(requst)

            row = result.one_or_none()
            if row is None:
                return None
            
            user, orders_amount = row

            user_data = user.__dict__.copy()
            user_data["orders_amount"] = orders_amount
            user_data["discount_tiers"] = DiscountConst.discount_tiers
            user_data["current_discount"] = max(
                (tier["percent"] for tier in DiscountConst.discount_tiers if orders_amount >= tier["orders_required"]),
                default=0
            )

            return SUserFull.model_validate(user_data)
        
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

                setattr(user, "updated_at", func.now())
                
                try:
                    await session.flush()
                    await session.commit()
                except SQLAlchemyError as e:
                    raise e
                
                return user