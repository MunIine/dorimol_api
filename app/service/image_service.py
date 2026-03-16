from PIL import Image
import io

def crop_to_square(image: Image.Image) -> Image.Image:
    w, h = image.size
    min_side = min(w, h)
    left = (w - min_side) // 2
    top = (h - min_side) // 2
    return image.crop((left, top, left + min_side, top + min_side))

def process_avatar(contents: bytes, target_size: int = 512) -> bytes:
    image = Image.open(io.BytesIO(contents))
    
    # Конвертируем в RGB (если PNG с прозрачностью — RGBA)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGBA")
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background.convert("RGB")
    else:
        image = image.convert("RGB")

    # Обрезаем по центру в квадрат, затем ресайзим
    image = crop_to_square(image)
    w, h = image.size
    final_size = min(w, target_size)
    image = image.resize((final_size, final_size), Image.LANCZOS) # type: ignore

    # Сохраняем в WebP
    output = io.BytesIO()
    image.save(output, format="WEBP", quality=85, method=6)
    return output.getvalue()