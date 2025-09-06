from datetime import timedelta
import requests
from sqlalchemy import select
from app.config import get_email_api_key, get_email_from, get_email_to
from app.database import async_session_maker
from app.models import Order, Product

async def send_order_email(order: Order):
    text =f"""Заказ #{order.id}\nДата и время: {(order.created_at+timedelta(hours=3)).strftime("%d.%m.%Y %H:%M")}\n
Клиент: {order.full_name}
Телефон: {order.phone_number}
"""
    if order.delivery_address is not None:
        text += f'Адрес: {order.delivery_address}\n'

    if order.comment is not None:
        text += f'Комментарий: {order.comment}\n'

    async with async_session_maker() as session:
        product_ids = [item.product_id for item in order.items]

        query = select(Product.id, Product.name).where(Product.id.in_(product_ids))
        result = await session.execute(query)
        product_names = {row["id"]: row["name"] for row in result.mappings().all()}

        query = select(Product.id, Product.unit).where(Product.id.in_(product_ids))
        result = await session.execute(query)
        product_units = {row["id"]: row["unit"] for row in result.mappings().all()}


    text += "\nТовары:"
    for index, product in enumerate(order.items):
        text += f'\n{index+1}) [{product.product_id}] {product_names[product.product_id]} - {product.quantity} {product_units[product.product_id]}  x {product.item_price} Р = {product.quantity * product.item_price} Р'

    return requests.post(
          "https://api.mailgun.net/v3/sandbox29a24eb4cf7c4c0bbbc712cb2722265f.mailgun.org/messages",
          auth=("api", get_email_api_key()),
          data={
            "from": f"Orders email <{get_email_from()}>",
            "to": f"EcoBaza <{get_email_to()}>",
              "subject": f"Заказ #{order.id}",
              "text": text.strip()
            }
        )