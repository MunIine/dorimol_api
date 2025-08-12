from app.dao import BaseDAO
from app.models import Config

class ConfigDAO(BaseDAO):
    model = Config