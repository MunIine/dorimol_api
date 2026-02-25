from app.dao import BaseDAO
from app.models import Feedback

class FeedbackDAO(BaseDAO):
    model = Feedback