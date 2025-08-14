#!/usr/bin/env python3
"""
image_resizer.py

Usage:
    python image_resizer.py input.jpg output.webp
Optional flags:
    --mode {fill,fit}        fill = crop to exactly target aspect (default)
                             fit  = fit inside target and pad with background
    --width WIDTH
    --height HEIGHT
    --maxkb MAX_KB
    --bg R,G,B               background color for 'fit' mode (default 255,255,255)
    --keep-orientation       change width and height by places
"""

import sys
import io
from PIL import Image
import os
import argparse

def open_image(path):
    img = Image.open(path)
    icc_profile = img.info.get('icc_profile')
    img = img.convert("RGBA")
    return img, icc_profile

def resize_fill(img, target_w, target_h):
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        # source is wider -> crop sides
        new_w = int(target_ratio * src_h)
        left = (src_w - new_w) // 2
        box = (left, 0, left + new_w, src_h)
    else:
        # source is taller -> crop top/bottom
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        box = (0, top, src_w, top + new_h)

    cropped = img.crop(box)
    resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

    return resized

def resize_fit_and_pad(img, target_w, target_h, bg=(255,255,255,255)):
    img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    bg_img = Image.new("RGBA", (target_w, target_h), bg)
    offset = ((target_w - img.width) // 2, (target_h - img.height) // 2)
    bg_img.paste(img, offset, img if img.mode == "RGBA" else None)

    return bg_img

def strip_metadata_save_webp(img, out_buffer, quality, method=6, icc_profile=None):
    save_kwargs = {
        "format": "WEBP",
        "quality": quality,
        "method": method,
        "lossless": False,
    }
    if icc_profile:
        save_kwargs["icc_profile"] = icc_profile
    img.save(out_buffer, **save_kwargs)
    return out_buffer.getbuffer().nbytes


def compress_image(input_path, output_path,
                   width, height, max_kb,
                   mode, bg, min_quality,
                   keep_orientation, no_resize):

    img, icc_profile = open_image(input_path)

    src_w, src_h = img.size

    if not no_resize:
        if keep_orientation:
            # Если ширина исходника >= высоты — размер не меняем,
            # иначе меняем местами width и height
            if src_w >= src_h:
                target_w, target_h = width, height
            else:
                target_w, target_h = height, width
        else:
            # Строго по заданным размерам
            target_w, target_h = width, height

    else:
        # Не меняем размеры, используем исходные
        target_w, target_h = src_w, src_h

    if mode == "fill":
        prepared = resize_fill(img, target_w, target_h)
    else:
        bg_with_alpha = (bg[0], bg[1], bg[2], 255)
        prepared = resize_fit_and_pad(img, target_w, target_h, bg_with_alpha)

    prepared_rgb = prepared.convert("RGB")

    quality = 95
    step = 5
    current_img = prepared_rgb
    attempt = 0
    max_attempts = 30
    target_bytes = max_kb * 1024

    best_bytes = None
    best_buf = None

    while attempt < max_attempts:
        attempt += 1
        buf = io.BytesIO()
        size_bytes = strip_metadata_save_webp(current_img, buf, quality, icc_profile=icc_profile)

        if size_bytes <= target_bytes:
            best_bytes = size_bytes
            best_buf = buf
            if quality + step <= 100:
                quality = min(100, quality + step)
                if quality == 100:
                    break
                continue
            else:
                break

        if quality - step >= min_quality:
            quality -= step
            continue

        new_w = max(100, int(current_img.width * 0.9))
        new_h = max(100, int(current_img.height * 0.9))
        if new_w == current_img.width and new_h == current_img.height:
            break
        current_img = current_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        quality = 90

    if best_buf is not None:
        with open(output_path, "wb") as f:
            f.write(best_buf.getvalue())
        if best_bytes is None:
            best_bytes = len(best_buf.getvalue())
        print(f"Wrote {output_path} — {best_bytes/1024:.1f} KB (mode={mode})")
        return True
    else:
        final_buf = io.BytesIO()
        strip_metadata_save_webp(current_img, final_buf, quality, icc_profile=icc_profile)
        with open(output_path, "wb") as f:
            f.write(final_buf.getvalue())
        final_size = os.path.getsize(output_path)
        print(f"Wrote {output_path} — {final_size/1024:.1f} KB (may exceed {max_kb} KB).")
        return False


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("input", help="input image path or folder")
    p.add_argument("output", nargs="?", default=None, help="output folder (optional)")
    p.add_argument("--mode", choices=["fill","fit"], default="fill")
    p.add_argument("--width", type=int, default=600)
    p.add_argument("--height", type=int, default=800)
    p.add_argument("--maxkb", type=int, default=100)
    p.add_argument("--bg", type=str, default="255,255,255",
                   help="background RGB for fit mode, e.g. 255,255,255")
    p.add_argument("--keep-orientation", action="store_true",
                   help="Keep orientation: change width and height by places")
    p.add_argument("--no-resize", action="store_true",
               help="Save old sizes.")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    bg = tuple(int(x) for x in args.bg.split(","))

    def process_one(input_path, output_dir):
        fname = os.path.splitext(os.path.basename(input_path))[0] + ".webp"
        if output_dir:
            out_path = os.path.join(output_dir, fname)
        else:
            out_path = os.path.join(os.getcwd(), fname)
        ok = compress_image(input_path, out_path,
                            width=args.width, height=args.height,
                            max_kb=args.maxkb, mode=args.mode, bg=bg,
                            keep_orientation=args.keep_orientation,
                            min_quality=20, no_resize=args.no_resize)
        if not ok:
            sys.exit(2)

    if os.path.isdir(args.input):
        # Папка: обработать все изображения
        input_files = [os.path.join(args.input, f) for f in os.listdir(args.input)
                      if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp"))]
        for f in input_files:
            process_one(f, args.output)
    else:
        # Файл: обработать один
        process_one(args.input, args.output)