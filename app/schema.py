from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from app.models import User

class SProduct(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str = Field(..., description="Уникальный идентификатор продукта", min_length=8, max_length=8)
    category_id: int = Field(..., description="ID категории")
    name: str = Field(..., description="Название")
    image_url: str = Field(..., description="URL изображения продукта на сервере")
    price: float = Field(..., description="Цена")
    wholesale_price: float = Field(..., description="Оптовая цена")
    wholesale_start_quantity: float = Field(..., description="Количество товаров для опта")
    unit: str = Field(..., description="Единица измерения: кг, шт...")
    stock: float = Field(..., description="Количество на складе")
    status: str = Field(..., description="Статус: default, new, sale...")
    order_count: int = Field(..., description="Количество заказов")
    rating: float | None = Field(..., description="Средняя оценка продукта")

class SProductAll(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str = Field(..., description="Уникальный идентификатор продукта", min_length=8, max_length=8)
    category_id: int = Field(..., description="ID категории")
    name: str = Field(..., description="Название")
    description: Optional[str] = Field(None, description="Описание")
    image_url: str = Field(..., description="URL изображения продукта на сервере")
    price: float = Field(..., description="Цена")
    wholesale_price: float = Field(..., description="Оптовая цена")
    wholesale_start_quantity: float = Field(..., description="Количество товаров для опта")
    unit: str = Field(..., description="Единица измерения: кг, шт...")
    stock: float = Field(..., description="Количество на складе")
    status: str = Field(..., description="Статус: default, new, sale...")
    order_count: int = Field(..., description="Количество заказов")
    rating: float | None = Field(..., description="Средняя оценка продукта")
    vendors: list[str] = Field(..., description="Список поставщиков")
    feedbacks: list["SFeedback"] = Field(..., description="Список отзывов")
    similars: list["SProduct"] = Field(..., description="Список похожих товаров")

class SCategory(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="ID категории")
    name: str = Field(..., description="Название категории")
    image_url: str = Field(..., description="URL изображения категории на сервере")
class SFeedback(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="ID отзыва")
    rating: int = Field(..., description="Оценка")
    comment: str = Field(..., description="Комментарий")
    updated_at: datetime = Field(..., description="Дата обновления отзыва")
    created_at: datetime = Field(..., description="Дата создания отзыва")

class SOrderAdd(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    full_name: str = Field(..., description="ФИО заказчика")
    phone_number: str = Field(..., description="Телефон заказчика")
    delivery_address: Optional[str] = Field(None, description="Адрес доставки")
    comment: Optional[str] = Field(None, description="Комментарий к заказу")
    items: list["SOrderItemAdd"] = Field(..., description="Список товаров в заказе")

class SOrderItemAdd(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: str = Field(..., description="ID продукта")
    quantity: float = Field(..., description="Количество")
    item_price: float = Field(..., description="Цена за единицу товара")

class SOrderPreview(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(..., description="ID заказа")
    status: str = Field(..., description="Статус заказа")
    total_price: float = Field(..., description="Общая стоимость заказа")
    city: Optional[str] = Field(None, description="Город доставки")
    address: Optional[str] = Field(None, description="Адрес доставки")
    created_at: datetime = Field(..., description="Дата создания заказа")

class SOrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="ID позиции заказа")
    product_id: str = Field(..., description="ID продукта")
    quantity: float = Field(..., description="Количество")
    item_price: float = Field(..., description="Цена за единицу товара")


class SOrder(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(..., description="ID заказа")
    status: str = Field(..., description="Статус заказа")
    full_name: str = Field(..., description="ФИО заказчика")
    phone_number: str = Field(..., description="Телефон заказчика")
    city: Optional[str] = Field(None, description="Город доставки")
    address: Optional[str] = Field(None, description="Адрес доставки")
    comment: Optional[str] = Field(None, description="Комментарий к заказу")
    total_price: float = Field(..., description="Общая стоимость заказа")
    items: list[SOrderItem] = Field(..., description="Список товаров в заказе")
    created_at: datetime = Field(..., description="Дата создания заказа")

class SAuthFirebaseIdToken(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_token: str = Field(..., description="Id токен")

class STokens(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str = Field(..., description="JWT токен")
    refresh_token: str = Field(..., description="Refresh токен")

class SUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: str = Field(..., description="Уникальный идентификатор пользователя")
    role: str = Field(..., description="Роль пользователя: user, admin")
    onboarding_completed: bool = Field(..., description="Завершил ли пользователь онбординг")

class SUserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role: Optional[str] = Field(None, description="Роль пользователя: user, admin")
    onboarding_completed: Optional[bool] = Field(None, description="Завершил ли пользователь онбординг")
    name: Optional[str] = Field(None, description="Имя пользователя")
    phone_number: Optional[str] = Field(None, description="Номер телефона пользователя")
    city: Optional[str] = Field(None, description="Город пользователя")
    address: Optional[str] = Field(None, description="Адрес пользователя")

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "onboarding_completed": self.onboarding_completed,
            "name": self.name,
            "phone_number": self.phone_number,
            "city": self.city,
            "address": self.address
        }
    
class SUserFull(SUser):
    image_url: Optional[str] = Field(None, description="URL изображения пользователя на сервере")
    name: Optional[str] = Field(None, description="Имя пользователя")
    phone_number: str = Field(..., description="Номер телефона пользователя")
    city: Optional[str] = Field(None, description="Город пользователя")
    address: Optional[str] = Field(None, description="Адрес пользователя")
    orders_amount: int = Field(..., description="Количество заказов пользователя")