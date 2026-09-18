import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.community.postgres import PostgresContainer
import app.models  # Регистрация всех моделей в Base.metadata
from app.database import Base, async_session_maker
from app.main import app
from app.service.userDAO import UserDAO


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


@pytest.fixture
def test_user():
    return {
        "uid": "test_user_uid",
        "role": "user",
        "onboarding_completed": True,
        "phone_number": "+37378877788",
    }

@pytest.fixture
async def db_user(test_user):
    """Создает тестового пользователя в БД перед запуском теста."""
    user = await UserDAO.create_user(
        uid=test_user["uid"],
        phone_number=test_user.get("phone_number")
    )
    return user

@pytest.fixture(scope="session")
async def async_client():
    """HTTP-клиент для вызова эндпоинтов приложения с подключенной тестовой БД."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client