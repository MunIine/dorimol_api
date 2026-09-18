import pytest
from app.database import Base


@pytest.fixture(autouse=True)
async def clean_tables(test_engine):
    """Очищает данные из всех таблиц после каждого API-теста для обеспечения изоляции."""
    yield
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())