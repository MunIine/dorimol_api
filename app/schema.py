from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

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
    full_name: str = Field(..., description="ФИО заказчика")
    phone_number: str = Field(..., description="Телефон заказчика")
    delivery_address: Optional[str] = Field(None, description="Адрес доставки")
    comment: Optional[str] = Field(None, description="Комментарий к заказу")
    items: list["SOrderItemAdd"] = Field(..., description="Список товаров в заказе")

class SOrderItemAdd(BaseModel):
    product_id: str = Field(..., description="ID продукта")
    quantity: float = Field(..., description="Количество")
    item_price: float = Field(..., description="Цена за единицу товара")

class SAuthFirebaseIdToken(BaseModel):
    id_token: str = Field(..., description="Id токен")

class SAuthFirebaseAnwer(BaseModel):
    access_token: str = Field(..., description="JWT токен")
    refresh_token: str = Field(..., description="Refresh токен")

class SUser(BaseModel):
    uid: str = Field(..., description="Уникальный идентификатор пользователя")
    role: str = Field(..., description="Роль пользователя: user, admin")
    onboarding_completed: bool = Field(..., description="Завершил ли пользователь онбординг")