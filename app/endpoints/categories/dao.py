from app.dao import BaseDAO
from app.models import Category

class CategoryDAO(BaseDAO):
    model = Category