from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload
from app.database import async_session_maker
from app.dao import BaseDAO
from app.models import Feedback, Product


class ProductDAO(BaseDAO):
    model = Product

    @classmethod
    async def search(cls, arg: str | None = None, category_id: int | None = None, sorting: str | None = None):
        additional_filter_data = {"category_id": category_id}
        additional_filter = [getattr(cls.model, key) == value for key, value in additional_filter_data.items() if value is not None]

        async with async_session_maker() as session:
            # TODO: Разобраться с аргументами запрос и скоростью
            product_query = select(
                cls.model, func.avg(Feedback.rating).label("rating")
            ).join(
                Feedback, Feedback.product_id == cls.model.id, isouter=True
            ).group_by(
                cls.model.id
            ).filter(
                *additional_filter
            )
            if arg is not None:
                if arg.isdigit():
                    product_query.filter(cls.model.id==arg)
                else:
                    product_query = product_query.filter(cls.model.name.ilike(f"%{arg}%"))

            product_result = await session.execute(product_query)
            product_info = product_result.unique().all()
            if not product_info:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with argument '{arg}' not found"
                )
            
            products = []
            for product in product_info:
                product_data = product[0].toDict()
                product_data["rating"] = None if product[1] is None else round(product[1], 2)
                products.append(product_data)
            
            return products

    @classmethod
    async def search_full(cls, id: str):
        async with async_session_maker() as session:
            product_query = select(cls.model).options(joinedload(cls.model.vendors))
            product_query = product_query.filter_by(id=id)
            product_result = await session.execute(product_query)
            product_info = product_result.unique().scalar_one_or_none()
            if product_info is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with id '{id}' not found"
                )
            product_data = product_info.toDict()
            
            feedback_query = select(Feedback).filter_by(product_id=product_data["id"]).limit(3)
            feedback_result = await session.execute(feedback_query)

            #TODO: Добавить обработку рейтинга
            product_data["rating"] = None
            product_data["vendors"] = [vendor.name for vendor in product_info.vendors]
            product_data["feedbacks"] = feedback_result.scalars().all()
            return product_data