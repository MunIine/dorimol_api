from fastapi import APIRouter
from app.endpoints.feedbacks.dao import FeedbackDAO
from app.schema import SFeedback

router = APIRouter(prefix='/feedbacks', tags=['Отзывы'])

@router.get("/{product_id}", summary="Получить отзывы по id", response_model=list[SFeedback])
async def get_feedbacks_by_product_id(product_id: str):
    return await FeedbackDAO.find_all(product_id=product_id)