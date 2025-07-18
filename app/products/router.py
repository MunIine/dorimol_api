from fastapi import APIRouter, Depends 
from app.products.dao import ProductDAO
from app.products.rb import RBProducts
from app.schema import SProduct, SProductAll

router = APIRouter(prefix='/products', tags=['Товары'])

@router.get("/", summary="Получить товары по фильтру", response_model=list[SProduct])
async def get_products_by_category(request_body: RBProducts = Depends(RBProducts)):
    return await ProductDAO.search(**request_body.to_dict())

@router.get("/{id}", summary="Получить всю информацию о товаре по id", response_model=SProductAll)
async def get_product_by_id(id: str):
    return await ProductDAO.search_full(id)