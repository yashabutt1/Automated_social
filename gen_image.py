"""Local background generation for The Love Lens.

Backgrounds are drawn with Pillow so the pipeline can run without any image API
calls. The mood argument is accepted for compatibility with the existing pipeline
and is used to rotate palette choices.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import config


def _palette_for_mood(mood: str):
    palettes = [
        ("plum", "#1a1424", "#0f0a16"),
        ("ember", "#1f1518", "#120c0e"),
        ("indigo", "#141830", "#0d0f1c"),
        ("teal", "#12201c", "#0b1512"),
    ]
    if not mood:
        return palettes[0]
    key = sum(ord(ch) for ch in mood.lower()) % len(palettes)
    return palettes[key]


def _to_rgb(color: str):
    return tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))


def _add_grain(img: Image.Image) -> Image.Image:
    width, height = img.size
    noise = Image.effect_noise((width, height), 12)
    noise = noise.filter(ImageFilter.GaussianBlur(radius=0.4))
    return Image.blend(img, noise.convert("RGB"), 0.02)


def make_background(mood: str, out_path, w=None, h=None) -> str:
    """Generate a soft branded background locally and save it as a PNG."""
    w = w or config.CARD_W
    h = h or config.CARD_H
    out_path = Path(out_path)

    _, start_hex, end_hex = _palette_for_mood(mood)
    start = _to_rgb(start_hex)
    end = _to_rgb(end_hex)

    img = Image.new("RGB", (w, h), start)
    draw = ImageDraw.Draw(img)

    for y in range(h):
        t = y / max(1, h - 1)
        r = tuple(int(start[i] + (end[i] - start[i]) * t) for i in range(3))
        draw.line((0, y, w, y), fill=r)

    img = _add_grain(img)
    img = img.resize((w, h), Image.Resampling.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return str(out_path)
