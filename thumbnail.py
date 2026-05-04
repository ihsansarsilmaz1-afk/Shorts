"""
thumbnail.py — Pillow ile YouTube thumbnail (1280×720 PNG) üretir.
"""

import os
from PIL import Image, ImageDraw, ImageFont

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

THUMB_W = 1280
THUMB_H = 720
FONT_PATH = "assets/fonts/Montserrat-Bold.ttf"


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    if os.path.exists(FONT_PATH):
        return ImageFont.truetype(FONT_PATH, size)
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


def generate_thumbnail(
    title: str,
    thumbnail_text: str,
    output_path: str = "output/thumbnail.png",
    hz: float = None,
) -> str:
    """
    1280×720 PNG thumbnail üretir.
    hz verilirse Hz modu (mavi degrade + Hz badge), yoksa war modu (kırmızı degrade + WHAT IF? badge).
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    img = Image.new("RGB", (THUMB_W, THUMB_H), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    if hz:
        # Mavi-mor degrade — Hz/frekans modu
        for x in range(THUMB_W // 2):
            alpha = int(180 * (1 - x / (THUMB_W // 2)))
            for y in range(THUMB_H):
                dist = ((x ** 2 + y ** 2) ** 0.5) / ((THUMB_W ** 2 + THUMB_H ** 2) ** 0.5)
                if dist < 0.5:
                    blend = int(alpha * (1 - dist * 2))
                    cr, cg, cb = img.getpixel((x, y))
                    img.putpixel((x, y), (
                        min(255, cr + blend // 6),
                        min(255, cg + blend // 4),
                        min(255, cb + blend),
                    ))
    else:
        # Kırmızı degrade — war modu
        for x in range(THUMB_W // 2):
            alpha = int(180 * (1 - x / (THUMB_W // 2)))
            r = min(255, 180 + alpha // 3)
            g = 0
            b = 0
            for y in range(THUMB_H):
                dist = ((x ** 2 + y ** 2) ** 0.5) / ((THUMB_W ** 2 + THUMB_H ** 2) ** 0.5)
                if dist < 0.5:
                    blend = int(alpha * (1 - dist * 2))
                    cr, cg, cb = img.getpixel((x, y))
                    img.putpixel((x, y), (
                        min(255, cr + blend),
                        cg,
                        cb,
                    ))

    # Büyük ana metin (thumbnail_text — 4 kelimeye kadar, ALL CAPS)
    main_font_size = 140
    main_font = _load_font(main_font_size)

    # Metin kutusunu hesapla ve ortala
    words = thumbnail_text.upper().split()
    lines = []
    if len(words) <= 2:
        lines = [thumbnail_text.upper()]
    else:
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    line_h = main_font_size + 20
    total_h = line_h * len(lines)
    y_start = (THUMB_H - total_h) // 2 - 30

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=main_font)
        text_w = bbox[2] - bbox[0]
        x = (THUMB_W - text_w) // 2
        y = y_start + i * line_h

        # Gölge
        for dx, dy in [(-4, -4), (4, 4), (-4, 4), (4, -4)]:
            draw.text((x + dx, y + dy), line, font=main_font, fill=(0, 0, 0))

        # Ana metin
        draw.text((x, y), line, font=main_font, fill=(255, 255, 255))

    # Alt başlık (title)
    sub_font_size = 42
    sub_font = _load_font(sub_font_size)
    sub_text = title if len(title) <= 50 else title[:47] + "..."
    bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    sub_w = bbox[2] - bbox[0]
    x = (THUMB_W - sub_w) // 2
    y = y_start + total_h + 20

    # Alt başlık gölgesi
    draw.text((x + 2, y + 2), sub_text, font=sub_font, fill=(0, 0, 0))
    draw.text((x, y), sub_text, font=sub_font, fill=(255, 215, 0))  # Altın sarısı

    # Sol üst köşe badge — Hz modunda frekans etiketi, war modunda "WHAT IF?"
    tag_font = _load_font(36)
    if hz:
        badge_label = f"{hz:.0f} Hz"
        badge_color = (10, 30, 120)   # koyu mavi — frekans kimliği
        badge_w = 180
    else:
        badge_label = "WHAT IF?"
        badge_color = (180, 0, 0)     # kırmızı — war kimliği
        badge_w = 200
    draw.rectangle([(20, 20), (20 + badge_w, 72)], fill=badge_color)
    draw.text((30, 28), badge_label, font=tag_font, fill=(255, 255, 255))

    img.save(output_path, "PNG", optimize=True)
    print(f"[thumbnail] Thumbnail kaydedildi: {output_path}")
    return output_path


if __name__ == "__main__":
    import json, sys

    script_path = sys.argv[1] if len(sys.argv) > 1 else "output/script.json"
    with open(script_path, encoding="utf-8") as f:
        script = json.load(f)

    generate_thumbnail(script["title"], script["thumbnail_text"])
    print("[thumbnail] Tamamlandı.")
