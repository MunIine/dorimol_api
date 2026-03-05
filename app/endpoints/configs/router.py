from typing import Any
from fastapi import APIRouter
from app.endpoints.configs.dao import ConfigDAO

router = APIRouter(prefix='/config', tags=['Конфигурация'])

@router.get("/", summary="Получить файл конфигурации", response_model=dict[str, Any])
async def get_config():
    return await ConfigDAO.get_config()