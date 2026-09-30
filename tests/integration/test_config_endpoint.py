import pytest
from app.database import async_session_maker
from app.models import Config

@pytest.mark.api
@pytest.mark.asyncio
async def test_get_config_success(async_client):
    """Получение конфигурации приложения в виде словаря."""
    async with async_session_maker() as session:
        async with session.begin():
            session.add_all([
                Config(key="app_info", value={"version": "1.0.0", "name": "Dorimol"}),
            ])
            await session.commit()

    response = await async_client.get("/config/")
    assert response.status_code == 200
    data = response.json()
    assert data["app_info"] == {"version": "1.0.0", "name": "Dorimol"}


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_config_empty(async_client):
    """Возврат пустого словаря при отсутствии записей конфигурации."""
    response = await async_client.get("/config/")
    assert response.status_code == 200
    assert response.json() == {}
