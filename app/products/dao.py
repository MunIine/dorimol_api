from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.constants import SortingProductConst
from app.database import async_session_maker
from app.models import Feedback, Product


class ProductDAO():
    model = Product

    @classmethod
    async def search(cls, **filter_by):
        sorting: str = SortingProductConst.default
        additional_filter = []
        
        for key, value in filter_by.items():
            if value is not None:
                if key == "name":
                    additional_filter.append(cls.model.name.ilike(f"%{value}%"))
                    continue
                if key == "sorting":
                    sorting = value
                    continue

                additional_filter.append(getattr(cls.model, key) == value)

        async with async_session_maker() as session:
            product_query = select(
                cls.model
            ).filter(
                *additional_filter
            ).order_by(
                SortingProductConst[sorting].sort_expression(Product) if sorting in SortingProductConst.__members__ else SortingProductConst.default.value
            )

            product_result = await session.execute(product_query)
            product_info = product_result.unique().scalars().all()
            if not product_info:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with argument '{filter_by}' not found"
                )
            
            return product_info

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
            
            feedback_query = select(Feedback).filter_by(product_id=product_info.id).limit(3)
            feedback_result = await session.execute(feedback_query)

            product_data = product_info.toDict()
            product_data["vendors"] = [vendor.name for vendor in product_info.vendors]
            product_data["feedbacks"] = feedback_result.scalars().all()
            return product_data