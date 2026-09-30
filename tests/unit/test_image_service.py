import io
import pytest
from PIL import Image
from app.constants import AvatarUploadConst
from app.service.image_service import crop_to_square, process_avatar


def test_crop_to_square_landscape():
    # Ландшафтное изображение (400x200)
    img = Image.new("RGB", (400, 200), color="red")
    cropped = crop_to_square(img)
    assert cropped.size == (200, 200)


def test_crop_to_square_portrait():
    # Портретное изображение (300x500)
    img = Image.new("RGB", (300, 500), color="blue")
    cropped = crop_to_square(img)
    assert cropped.size == (300, 300)


def test_crop_to_square_already_square():
    # Ужe квадратное изображение (250x250)
    img = Image.new("RGB", (250, 250), color="green")
    cropped = crop_to_square(img)
    assert cropped.size == (250, 250)


def test_process_avatar_valid_image():
    # Создаем изображение в памяти
    img = Image.new("RGBA", (800, 600), color=(255, 0, 0, 128))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    raw_bytes = buffer.getvalue()

    # Обрабатываем аватар
    result_bytes = process_avatar(raw_bytes, target_size=256)

    # Проверяем, что полученные байты — это корректный WebP квадратного размера
    result_img = Image.open(io.BytesIO(result_bytes))
    assert result_img.format == "WEBP"
    assert result_img.size == (256, 256)


def test_avatar_upload_const_magic_bytes():
    jpeg_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    webp_bytes = b"RIFF\x00\x00\x00\x00WEBPVP8 "
    invalid_riff = b"RIFF\x00\x00\x00\x00WAVEfmt "
    random_bytes = b"hello world 123456789"

    assert AvatarUploadConst.get_image_type(jpeg_bytes) == "jpeg"
    assert AvatarUploadConst.get_image_type(png_bytes) == "png"
    assert AvatarUploadConst.get_image_type(webp_bytes) == "webp"
    assert AvatarUploadConst.get_image_type(invalid_riff) is None
    assert AvatarUploadConst.get_image_type(random_bytes) is None
