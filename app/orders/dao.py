from fastapi import HTTPException
from sqlalchemy import select
from app.dao import BaseDAO
from app.database import async_session_maker
from app.models import Order, OrderItem, Product
from app.schema import SOrderAdd
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
                    product = await session.execute(select(Product).filter(Product.id==item_in.product_id))
                    product = product.scalar_one()

                    isWholesalePrice = item_in.quantity >= product.wholesale_start_quantity
                    
                    if (product.price != item_in.item_price and not isWholesalePrice) or \
                        (product.wholesale_price != item_in.item_price and isWholesalePrice):
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