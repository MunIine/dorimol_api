import pytest
from app.database import async_session_maker
from app.models import Feedback

@pytest.mark.api
@pytest.mark.asyncio
async def test_get_feedbacks_by_product_id_success(product_factory, async_client):
    """Получение отзывов конкретного товара с изоляцией от других товаров."""
    prod1 = await product_factory(name="Товар 1")
    prod2 = await product_factory(name="Товар 2")

    async with async_session_maker() as session:
        async with session.begin():
            fb1 = Feedback(product_id=prod1.id, rating=5, comment="Отлично")
            fb2 = Feedback(product_id=prod1.id, rating=4, comment="Хорошо")
            fb3 = Feedback(product_id=prod2.id, rating=1, comment="Плохо")
            session.add_all([fb1, fb2, fb3])
            await session.commit()

    response = await async_client.get(f"/feedbacks/{prod1.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    comments = {f["comment"] for f in data}
    assert comments == {"Отлично", "Хорошо"}

    # Проверка схемы SFeedback
    assert data[0]["rating"] in (4, 5)
    assert "created_at" in data[0]
    assert "updated_at" in data[0]


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_feedbacks_empty(product_factory, async_client):
    """Возврат пустого списка для товара без отзывов."""
    prod = await product_factory(name="Товар без отзывов")
    response = await async_client.get(f"/feedbacks/{prod.id}")
    assert response.status_code == 200
    assert response.json() == []