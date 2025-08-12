from sqlalchemy import Enum as sqlEnum
from sqlalchemy import Text, Table, Column, ForeignKey, String,  text
from sqlalchemy.orm import relationship, Mapped, mapped_column, declared_attr
from app.constants import ProductConst
from app.database import Base, str_uniq, int_pk

product_vendors = Table(
    "product_vendors",
    Base.metadata,
    Column("product_id", ForeignKey("products.id"), primary_key=True),
    Column("vendor_id", ForeignKey("vendors.id"), primary_key=True)
)
class Product(Base):
    id: Mapped[str] = mapped_column(String(8), primary_key=True, autoincrement=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    name: Mapped[str_uniq]
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    wholesale_price: Mapped[float] = mapped_column(nullable=False)
    wholesale_start_quantity: Mapped[float] = mapped_column(nullable=False)
    unit: Mapped[str] = mapped_column(sqlEnum(*ProductConst.units, name="unit"), nullable=False)
    stock: Mapped[float] = mapped_column(nullable=False, server_default=text("0"))
    status: Mapped[str] = mapped_column(sqlEnum(*ProductConst.statuses, name="status"), nullable=False, server_default=text(f"\'{ProductConst.default_status}\'"))
    order_count: Mapped[int] = mapped_column(nullable=False, server_default=text("0"))
    rating: Mapped[float] = mapped_column(nullable=True)

    vendors: Mapped[list["Vendor"]] = relationship("Vendor", secondary=product_vendors, back_populates="products")
    category: Mapped["Category"] = relationship("Category", back_populates="products")

    def __str__(self):
        return f"Product(id={self.id}, name={self.name}, price={self.price}, unit={self.unit})"

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name})>"

    def toDict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "image_url": self.image_url,
            "price": self.price,
            "wholesale_price": self.wholesale_price,
            "wholesale_start_quantity": self.wholesale_start_quantity,
            "unit": self.unit,
            "stock": self.stock,
            "status": self.status,
            "order_count": self.order_count,
            "rating": self.rating,
        }

class Feedback(Base):
    id: Mapped[int_pk]
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)

    def __str__(self):
        return f"Feedback(id={self.id}, product_id={self.product_id}, rating={self.rating})"

    def __repr__(self):
        return f"<Feedback(id={self.id}, product_id={self.product_id})>"

class Vendor(Base):
    id: Mapped[int_pk]
    name: Mapped[str_uniq]

    products: Mapped[list[Product]] = relationship("Product", secondary=product_vendors, back_populates="vendors")

    def __str__(self):
        return f"Vendor(id={self.id}, name={self.name})"

    def __repr__(self):
        return f"<Vendor(id={self.id}, name={self.name})>"

class Category(Base):
    id: Mapped[int_pk]
    name: Mapped[str_uniq]
    image_url: Mapped[str] = mapped_column(nullable=False)

    products: Mapped[list[Product]] = relationship("Product", back_populates="category")

    def __str__(self):
        return f"Category(id={self.id}, name={self.name})"

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"

class Order(Base):
    id: Mapped[int_pk]
    full_name: Mapped[str] = mapped_column(nullable=False)
    phone_number: Mapped[str] = mapped_column(nullable=False)
    delivery_address: Mapped[str] = mapped_column(Text, nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    total_price: Mapped[float] = mapped_column(nullable=False)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "order_items"

    id: Mapped[int_pk]
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(nullable=False)
    item_price: Mapped[float] = mapped_column(nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")

class Config(Base):
    id: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(String, nullable=False)