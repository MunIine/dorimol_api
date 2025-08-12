from fastapi import APIRouter
from app.configs.dao import ConfigDAO

router = APIRouter(prefix='/config', tags=['Конфигурация'])

@router.get("/", summary="Получить файл конфигурации", response_model=dict[str, str])
async def get_config():
    return await ConfigDAO.get_config()