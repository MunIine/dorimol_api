from fastapi import APIRouter, Depends 
from app.products.dao import ProductDAO
from app.products.rb import RBProductsByCategory, RBProductsByIdOrName
from app.schema import SProduct, SProductAll

router = APIRouter(prefix='/products', tags=['Товары'])

@router.get("/", summary="Получить товары по категории", response_model=list[SProduct])
async def get_products_by_category(request_body: RBProductsByCategory = Depends(RBProductsByCategory)):
    return await ProductDAO.search(None, **request_body.to_dict())

@router.get("/{id_or_name}", summary="Получить товары по id или имени", response_model=list[SProduct])
async def get_products_by_id_or_name(request_body: RBProductsByIdOrName = Depends(RBProductsByIdOrName)):
    return await ProductDAO.search(**request_body.to_dict())

@router.get("/product/{id}", summary="Получить всю информацию о товаре по id", response_model=SProductAll)
async def get_product_by_id(id: str):
    return await ProductDAO.search_full(id)