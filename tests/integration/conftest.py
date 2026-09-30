from decimal import Decimal
import glob
import os
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.community.postgres import PostgresContainer
import app.models  # Регистрация всех моделей в Base.metadata
from app.constants import DeliveryTypes, OrderConst
from app.database import Base, async_session_maker
from app.main import app
from app.models import Category, Feedback, Order, OrderItem, Product, Vendor
from app.schema import SUser
from app.service.token_service import TokenService
from app.service.userDAO import UserDAO


# ==================== Database Infrastructure ====================


@pytest.fixture(scope="session")
def postgres_container():
    """Запускает временный контейнер PostgreSQL на время тестовой сессии."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
async def test_engine(postgres_container):
    """Создает async engine для тестовой БД и применяет схему (таблицы)."""
    try:
        test_db_url = postgres_container.get_connection_url(driver="asyncpg")
    except TypeError:
        test_db_url = postgres_container.get_connection_url()

    if "postgresql+psycopg2://" in test_db_url:
        test_db_url = test_db_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    elif "postgresql://" in test_db_url and "postgresql+asyncpg://" not in test_db_url:
        test_db_url = test_db_url.replace("postgresql://", "postgresql+asyncpg://")

    engine = create_async_engine(test_db_url, poolclass=NullPool, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Перенаправляем глобальный sessionmaker на тестовую БД
    async_session_maker.configure(bind=engine)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# ==================== Autouse Cleanup Fixtures ====================


@pytest.fixture(autouse=True)
async def clean_tables(test_engine):
    """Очищает данные из всех таблиц после каждого API-теста для обеспечения изоляции."""
    yield
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture(autouse=True)
def clean_test_avatars():
    """Гарантирует удаление созданных в тестах файлов аватарок после каждого теста."""
    yield
    for f in glob.glob("media/avatars/test_user_uid*"):
        if os.path.exists(f):
            try:
                os.remove(f)
            except OSError:
                pass


# ==================== HTTP Client Fixture ====================


@pytest.fixture(scope="session")
async def async_client():
    """HTTP-клиент для вызова эндпоинтов приложения с подключенной тестовой БД."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


# ==================== User Fixtures ====================


@pytest.fixture
async def db_test_user(test_user):
    """Создает тестового пользователя в БД перед запуском теста."""
    user = await UserDAO.create_user(
        uid=test_user["uid"],
        phone_number=test_user.get("phone_number")
    )
    return user


@pytest.fixture
def test_tokens(test_user, db_test_user):
    """Генерирует пару JWT-токенов для тестового пользователя из БД."""
    tokens = TokenService().generate_tokens(SUser.model_validate(test_user))
    return tokens


@pytest.fixture
async def registered_user(db_test_user):
    """Тестовый пользователь с заполненным именем для корректного оформления заказов."""
    return await UserDAO.update_user(db_test_user.uid, {"name": "Иван Иванов"})


# ==================== Catalog & Order Fixtures ====================


@pytest.fixture
def category_factory():
    """Фабрика для создания тестовых категорий."""
    counter = 0

    async def _create_category(
        name: str | None = None,
        image_url: str = "http://test/cat.png",
        enabled: bool = True,
    ) -> Category:
        nonlocal counter
        counter += 1
        cat_name = name or f"Тестовая категория {counter}"

        async with async_session_maker() as session:
            async with session.begin():
                category = Category(
                    name=cat_name,
                    image_url=image_url,
                    enabled=enabled,
                )
                session.add(category)
                await session.flush()
                await session.commit()
                return category

    return _create_category


@pytest.fixture
async def db_category(category_factory):
    """Создает тестовую категорию в БД по умолчанию."""
    return await category_factory(name="Тестовая категория")


@pytest.fixture
def product_factory(db_category):
    """Фабрика для создания тестовых товаров."""
    counter = 0

    async def _create_product(
        product_id: str | None = None,
        category_id: int | None = None,
        name: str | None = None,
        description: str | None = None,
        price: float = 100.0,
        wholesale_price: float = 80.0,
        wholesale_start_quantity: float = 5.0,
        stock: float = 100.0,
        image_url: str = "http://test/prod.png",
        status: str = "default",
        order_count: int = 0,
        enabled: bool = True,
        rating: float | None = None,
    ) -> Product:
        nonlocal counter
        counter += 1
        pid = product_id or f"prod{counter:04d}"
        pname = name or f"Тестовый товар {counter}"
        cat_id = category_id or db_category.id

        async with async_session_maker() as session:
            async with session.begin():
                product = Product(
                    id=pid,
                    category_id=cat_id,
                    name=pname,
                    description=description,
                    image_url=image_url,
                    price=price,
                    wholesale_price=wholesale_price,
                    wholesale_start_quantity=wholesale_start_quantity,
                    stock=stock,
                    status=status,
                    order_count=order_count,
                    enabled=enabled,
                    rating=rating,
                )
                session.add(product)
                await session.flush()
                await session.commit()
                return product

    return _create_product


@pytest.fixture
async def db_product(product_factory):
    """Создает одиночный тестовый товар по умолчанию."""
    return await product_factory()


@pytest.fixture
def order_factory(db_test_user, db_product):
    """Фабрика для создания тестовых заказов."""
    async def _create_order(
        user_id: str | None = None,
        delivery_type: DeliveryTypes = DeliveryTypes.PICKUP,
        status: str = OrderConst.default_status,
        full_name: str = "Иван Иванов",
        phone_number: str = "+37378877788",
        total_price: Decimal = Decimal("200.00"),
        city: str | None = None,
        address: str | None = None,
        comment: str | None = None,
        items: list[tuple[Product, float]] | None = None,
    ) -> Order:
        actual_user_id = user_id or db_test_user.uid
        async with async_session_maker() as session:
            async with session.begin():
                order = Order(
                    user_id=actual_user_id,
                    delivery_type=delivery_type,
                    status=status,
                    full_name=full_name,
                    phone_number=phone_number,
                    city=city,
                    address=address,
                    comment=comment,
                    total_price=total_price,
                )
                if items is not None:
                    for prod, qty in items:
                        order.items.append(
                            OrderItem(
                                product_id=prod.id,
                                quantity=qty,
                                item_price=Decimal(str(prod.price)) * Decimal(str(qty)),
                            )
                        )
                else:
                    order.items.append(
                        OrderItem(
                            product_id=db_product.id,
                            quantity=1.0,
                            item_price=total_price,
                        )
                    )
                session.add(order)
                await session.flush()
                await session.commit()
                return order

    return _create_order