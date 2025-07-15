from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.database import async_session_maker
from app.dao import BaseDAO
from app.models import Feedback, Product


class ProductDAO(BaseDAO):
    model = Product

    @classmethod
    async def find_by_id_or_name(cls, arg: str):
        async with async_session_maker() as session:
            product_query = select(cls.model).options(joinedload(cls.model.category), joinedload(cls.model.vendors))
            product_query = product_query.filter_by(id=arg) if arg.isdigit() else product_query.filter_by(name=arg)
            product_result = await session.execute(product_query)
            product_info = product_result.unique().scalar_one_or_none()
            if product_info is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with argument '{arg}' not found"
                )
            product_data = product_info.toDict()
            
            feedback_query = select(Feedback).filter_by(product_id=product_data["id"]).limit(3)
            feedback_result = await session.execute(feedback_query)

            product_data["category"] = product_info.category.name
            product_data["vendors"] = [vendor.name for vendor in product_info.vendors]
            product_data["feedbacks"] = feedback_result.scalars().all()
            return product_data