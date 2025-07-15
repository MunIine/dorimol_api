from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class SProduct(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str = Field(..., description="Уникальный идентификатор продукта", min_length=8, max_length=8)
    category_id: int = Field(..., description="ID категории")
    name: str = Field(..., description="Название")
    description: Optional[str] = Field(None, description="Описание")
    image_url: str = Field(..., description="URL изображения продукта на сервере")
    price: float = Field(..., description="Цена")
    unit: str = Field(..., description="Единица измерения: кг, шт...")
    stock: float = Field(..., description="Количество на складе")
    status: str = Field(..., description="Статус: default, new, sale...")
    order_count: int = Field(..., description="Количество заказов")