import os
from dotenv import load_dotenv
import requests
from app.config import get_email_api_key
from app.models import Order

def send_order_email(order: Order):
    text =f"""Оформлен заказ #{order.id} на сумму {order.total_price}Р в {order.created_at.strftime("%d.%m.%Y")}\n
ФИО: {order.full_name}
Номер телефона: {order.phone_number}
"""
    if order.delivery_address is not None:
        text += f'Адрес доставки: {order.delivery_address}\n'

    text += "\nТовары:"
    for product in order.items:
        text += f'\nID: {product.product_id}, Количество: {product.quantity}, Цена: {product.item_price}'

    return requests.post(
          "https://api.mailgun.net/v3/sandbox29a24eb4cf7c4c0bbbc712cb2722265f.mailgun.org/messages",
          auth=("api", get_email_api_key()),
          data={
            "from": "Orders email <postmaster@sandbox29a24eb4cf7c4c0bbbc712cb2722265f.mailgun.org>",
            "to": "EcoBaza <ecobaza.b@gmail.com>",
              "subject": f"Заказ #{order.id}",
              "text": text
            }
        )