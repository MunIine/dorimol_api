from enum import Enum
from sqlalchemy import Enum as sqlEnum
from sqlalchemy import Text, Table, Column, ForeignKey, String,  text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base, str_uniq, int_pk

unit = sqlEnum("кг", "шт", name="unit")
status = sqlEnum("default", "new", "sale", name="status") #Первое значение идет по умолчанию

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
    unit: Mapped[str] = mapped_column(unit, nullable=False)
    stock: Mapped[float] = mapped_column(nullable=False, server_default=text("0"))
    status: Mapped[str] = mapped_column(status, nullable=False, server_default=text(f"\'{status.enums[0]}\'"))
    order_count: Mapped[int] = mapped_column(nullable=False, server_default=text("0"))

    vendors: Mapped[list["Vendor"]] = relationship("Vendor", secondary=product_vendors, back_populates="products")
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    feedbacks: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="product")

class Feedback(Base):
    id: Mapped[int_pk]
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)

    product: Mapped[Product] = relationship("Product", back_populates="feedbacks")

class Vendor(Base):
    id: Mapped[int_pk]
    name: Mapped[str_uniq]

    products: Mapped[list[Product]] = relationship("Product", secondary=product_vendors, back_populates="vendors")

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name!r})"

    def __repr__(self):
        return str(self)

class Category(Base):
    id: Mapped[int_pk]
    name: Mapped[str_uniq]

    products: Mapped[list[Product]] = relationship("Product", back_populates="category")

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name!r})"

    def __repr__(self):
        return str(self)