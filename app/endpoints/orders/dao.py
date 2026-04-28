from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.constants import DeliveryTypes
from app.dao import BaseDAO
from app.database import async_session_maker
from app.models import Order, OrderItem, Product
from app.schema import SOrder, SOrderAdd, SOrderPreview, SUserFull
from sqlalchemy.exc import SQLAlchemyError


class OrdersDAO(BaseDAO):
    model = Order

    @classmethod
    async def add_order(cls, order_in: SOrderAdd, user: SUserFull):
        async with async_session_maker() as session:
            async with session.begin():
                delivery_type = DeliveryTypes(order_in.delivery_type)
                total_price = Decimal("0")
                order = Order(
                    user_id = user.uid,
                    delivery_type = delivery_type,
                    full_name = user.name,
                    phone_number = user.phone_number,
                    comment = order_in.comment
                )
                if delivery_type == DeliveryTypes.COURIER:
                    order.city = order_in.city
                    order.address = order_in.address

                product_ids = [item.product_id for item in order_in.items]
                products_result = await session.execute(
                    select(Product).where(Product.id.in_(product_ids))
                )
                products = {p.id: p for p in products_result.scalars().all()}

                for item_in in order_in.items:
                    product = products.get(item_in.product_id)
                    if product is None:
                        raise HTTPException(
                            status_code=404,
                            detail="Product not found"
                        )

                    item_price = Decimal("0")
                    if item_in.quantity >= product.wholesale_start_quantity: # wholesale price
                        item_price = Decimal(str(product.wholesale_price)) * Decimal(str(item_in.quantity))
                    else:
                        item_price = Decimal(str(product.price)) * Decimal(str(item_in.quantity))
                    
                    total_price += item_price

                    order.items.append(OrderItem(
                        product_id = item_in.product_id,
                        quantity = item_in.quantity,
                        item_price = item_price
                    ))
                    
                discount_factor = (Decimal("100") - Decimal(str(user.current_discount))) / Decimal("100")
                order.total_price = total_price * discount_factor
                
                if order.total_price != order_in.expected_total_price:
                    raise HTTPException(
                        status_code=409,
                        detail="Price changed. Please refresh page and try again"
                    )
                
                session.add(order)

                try:
                    await session.flush()
                    await session.commit()
                except SQLAlchemyError as e:
                    raise e

                return order

    @classmethod
    async def get_orders_by_user(cls, user_uid: str, limit: int, offset: int) -> tuple[list[SOrderPreview], int | None]:
        async with async_session_maker() as session:
            next_offset = None

            result = await session.execute(
                select(Order)
                .where(Order.user_id == user_uid)
                .order_by(Order.created_at.desc())
                .limit(limit+1)
                .offset(offset)
            )
            orders = result.scalars().unique().all()
            orders_paginated = list(map(lambda order: SOrderPreview.model_validate(order), orders[:limit]))
            if len(orders) > limit:
                next_offset = offset + limit

            return orders_paginated, next_offset

    @classmethod
    async def get_order_by_id(cls, order_id: UUID, user_id: str):
        async with async_session_maker() as session:
            result = await session.execute(
                select(Order)
                .options(joinedload(Order.items))
                .where(Order.id == order_id, Order.user_id == user_id)
            )
            order = result.unique().scalar_one_or_none()
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            return SOrder.model_validate(order)