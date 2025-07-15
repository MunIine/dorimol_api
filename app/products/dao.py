from fastapi import HTTPException
from sqlalchemy import select
from app.database import async_session_maker
from app.dao import BaseDAO
from app.models import Product


class ProductDAO(BaseDAO):
    model = Product

    @classmethod
    async def find_by_id_or_name(cls, arg: str):
        async with async_session_maker() as session:
            query = select(cls.model)
            query = query.filter_by(id=arg) if arg.isdigit() else query.filter_by(name=arg)
            result = await session.execute(query)
            rez = result.scalar_one_or_none()
            if rez is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with argument '{arg}' not found"
                )
            return rez