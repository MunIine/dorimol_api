from fastapi import APIRouter 
from app.categories.dao import CategoryDAO
from app.schema import SCategory

router = APIRouter(prefix='/categories', tags=['Категории'])

@router.get("/", summary="Получить все категории", response_model=list[SCategory])
async def get_all_categories():
    return await CategoryDAO.find_all(enabled=True)