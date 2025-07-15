from fastapi import APIRouter, Depends 
from app.products.dao import ProductDAO
from app.rb import RBProduct
from app.schema import SProduct

router = APIRouter(prefix='/products', tags=['Товары'])

@router.get("/", summary="Получить все товары", response_model=list[SProduct])
async def get_all_products(request_body: RBProduct = Depends()):
    return await ProductDAO.find_all(**request_body.to_dict())

@router.get("/{id_or_name}", summary="Получить товар по id или имени", response_model=SProduct|None)
async def get_product_by_id_or_name(id_or_name: str):
    return await ProductDAO.find_by_id_or_name(id_or_name)