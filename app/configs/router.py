from fastapi import APIRouter
from app.configs.dao import ConfigDAO
from app.schema import SConfig

router = APIRouter(prefix='/config', tags=['Конфигурация'])

@router.get("/", summary="Получить файл конфигурации", response_model=list[SConfig])
async def get_config():
    return await ConfigDAO.find_all()