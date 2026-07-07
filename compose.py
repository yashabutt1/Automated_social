"""
Composite an original line onto a generated background -> finished PNG card.
"""
from PIL import Image, ImageDraw, ImageFont

import config


def _load_font(path, size):
    try:
        return ImageFont.truetype(str(path), size)
    except Exception:
        print(f"Warning: font not found at {path}; falling back to a bold system serif font")
        return ImageFont.load_default()


def _wrap(draw, text, font, max_w):
    words, lines, line = text.split(), [], ""
    for word in words:
        test = f"{line} {word}".strip()
        if draw.textlength(test, font=font) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def _overlay(base, strength):
    """Lightly darken the image so the headline stays readable."""
    w, h = base.size
    grad = Image.new("L", (1, h))
    for y in range(h):
        t = y / h
        a = int(255 * strength * (0.7 + 0.3 * (1 - abs(t - 0.5) * 2)))
        grad.putpixel((0, y), a)
    alpha = grad.resize((w, h))
    dark = Image.new("RGB", (w, h), (10, 8, 14))
    base.paste(dark, (0, 0), alpha)
    return base


def make_card(background_path, line, out_path, handle=None):
    handle = config.HANDLE if handle is None else handle
    w, h = config.CARD_W, config.CARD_H

    img = Image.open(background_path).convert("RGB").resize((w, h))
    img = _overlay(img, 0.2)
    draw = ImageDraw.Draw(img)

    print("FONT OK:", config.FONT_DISPLAY)
    max_w = int(w * 0.84)
    min_size = int(w * 0.06)
    size = int(w * 0.11)
    padding_x = int(w * 0.08)

    font = _load_font(config.FONT_DISPLAY, size)
    while True:
        lines = _wrap(draw, line, font, max_w)
        line_h = int(size * 1.15)
        total_h = line_h * len(lines)
        if total_h <= h * 0.7 or size <= min_size:
            break
        size -= 6
        font = _load_font(config.FONT_DISPLAY, size)

    print(f"FINAL font size = {size}")

    y = (h - total_h) // 2
    for ln in lines:
        tw = draw.textlength(ln, font=font)
        x = padding_x
        draw.text((x + 2, y + 2), ln, font=font, fill=(0, 0, 0))
        draw.text((x, y), ln, font=font, fill=(245, 240, 236))
        y += line_h

    if handle:
        sf = _load_font(config.FONT_SMALL, int(h * 0.022))
        tw = draw.textlength(handle, font=sf)
        draw.text(((w - tw) // 2, int(h * 0.94)), handle, font=sf,
                  fill=(230, 224, 220))

    img.save(out_path)
    return str(out_path)


def make_paragraph_card(body, out_path, handle=None):
    handle = config.HANDLE if handle is None else handle
    w, h = config.CARD_W, config.CARD_H

    img = Image.new("RGB", (w, h), (12, 10, 16))
    img = _overlay(img, 0.2)
    draw = ImageDraw.Draw(img)

    max_w = int(w * 0.88)
    max_h = int(h * 0.82)
    start_size = int(w * 0.058)
    min_size = int(w * 0.042)
    line_spacing = 1.35

    raw_lines = [line.strip() for line in body.splitlines() if line.strip()]
    if not raw_lines:
        raw_lines = [body]

    size = start_size
    wrapped_lines = []
    while size >= min_size:
        font = _load_font(config.FONT_DISPLAY, size)
        wrapped_lines = []
        for ln in raw_lines:
            wrapped_lines.extend(_wrap(draw, ln, font, max_w))
        line_h = int(size * line_spacing)
        total_h = line_h * len(wrapped_lines)
        if total_h <= max_h:
            break
        size -= 2
    else:
        font = _load_font(config.FONT_DISPLAY, min_size)
        wrapped_lines = []
        for ln in raw_lines:
            wrapped_lines.extend(_wrap(draw, ln, font, max_w))

    n = len(wrapped_lines) or 1
    line_h = int(size * line_spacing)
    total_h = line_h * n
    top_margin = int(h * 0.07)
    bottom_margin = int(h * 0.09)
    available_h = h - top_margin - bottom_margin - int(h * 0.04)
    y = top_margin + int((available_h - total_h) / 2)

    for ln in wrapped_lines:
        tw = draw.textlength(ln, font=font)
        x = int((w - tw) / 2)
        draw.text((x + 2, y + 2), ln, font=font, fill=(0, 0, 0))
        draw.text((x, y), ln, font=font, fill=(245, 240, 236))
        y += line_h

    if handle:
        sf = _load_font(config.FONT_SMALL, int(h * 0.022))
        tw = draw.textlength(handle, font=sf)
        draw.text(((w - tw) // 2, int(h * 0.94)), handle, font=sf,
                  fill=(230, 224, 220))

    print(f"PARAGRAPH font size = {size}, lines = {n}")
    img.save(out_path)
    return str(out_path)
