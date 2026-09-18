import io
import pytest
from PIL import Image


@pytest.fixture
def test_user():
    """Базовый словарь с тестовыми данными пользователя (без привязки к БД)."""
    return {
        "uid": "test_user_uid",
        "role": "user",
        "onboarding_completed": True,
        "phone_number": "+37378877788",
    }


@pytest.fixture
def test_image_bytes():
    """Возвращает валидные байты PNG изображения для тестов."""
    buf = io.BytesIO()
    img = Image.new("RGB", (100, 100), color="blue")
    img.save(buf, format="PNG")
    return buf.getvalue()