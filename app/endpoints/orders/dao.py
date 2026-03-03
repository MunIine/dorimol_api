from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.dao import BaseDAO
from app.database import async_session_maker
from app.models import Order, OrderItem, Product
from app.schema import SOrder, SOrderAdd, SOrderPreview
from sqlalchemy.exc import SQLAlchemyError


class OrdersDAO(BaseDAO):
    model = Order

    @classmethod
    async def add_order(cls, order_in: SOrderAdd):
        async with async_session_maker() as session:
            async with session.begin():
                total_price = 0
                order = Order(
                    full_name=order_in.full_name,
                    phone_number=order_in.phone_number,
                    delivery_address=order_in.delivery_address,
                    comment=order_in.comment,
                )
                for item_in in order_in.items:
                    product = await session.execute(select(Product).filter(Product.id == item_in.product_id))
                    product = product.scalar_one()

                    isWholesalePrice = item_in.quantity >= product.wholesale_start_quantity

                    if (product.price != item_in.item_price and not isWholesalePrice) or (
                        product.wholesale_price != item_in.item_price and isWholesalePrice
                    ):
                        await session.rollback()
                        raise HTTPException(
                            status_code=409,
                            detail="Цена изменилась. Пожалуйста, обновите страницу и повторите заказ."
                        )

                    order_items = OrderItem(
                        product_id=item_in.product_id,
                        quantity=item_in.quantity,
                        item_price=product.price if not isWholesalePrice else product.wholesale_price
                    )

                    total_price += order_items.item_price * item_in.quantity
                    order.items.append(order_items)

                order.total_price = total_price

                session.add(order)
                try:
                    await session.flush()
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e

                return order

    @classmethod
    async def get_orders_by_user(cls, user_uid: str) -> list[SOrderPreview]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(Order)
                .where(Order.user_id == user_uid)
                .order_by(Order.id.desc())
                .limit(5) # TODO: remove limit
            )
            orders = list(map(lambda order: SOrderPreview.model_validate(order), result.scalars().unique().all()))
            return orders

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