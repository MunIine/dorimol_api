from sqlalchemy import select
from app.dao import BaseDAO
from app.models import Config
from app.database import async_session_maker

class ConfigDAO(BaseDAO):
    model = Config

    @classmethod
    async def get_config(cls):
        async with async_session_maker() as session:
            result = await session.execute(select(cls.model))
            configs = result.scalars().all()
            return {config.id: config.value for config in configs}