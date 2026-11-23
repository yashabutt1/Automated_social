"""
Composite an original line onto a background photo -> finished, decorated card.

The card now layers, bottom to top:
  1. background photo (Pexels) or gradient
  2. a readability scrim so white text always pops
  3. soft decorative floral accents in the corners (optional)
  4. an elegant script title + the serif body text
  5. the handle
"""
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import config


# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
def _load_font(path, size):
    try:
        return ImageFont.truetype(str(path), size)
    except Exception:
        print(f"Warning: font not found at {path}; falling back to a bold system serif font")
        return ImageFont.load_default()


def _load_script_font(size):
    try:
        return ImageFont.truetype(str(config.FONT_SCRIPT), size)
    except Exception:
        return _load_font(config.FONT_SCRIPT_FALLBACK, size)


# ---------------------------------------------------------------------------
# Text layout helpers
# ---------------------------------------------------------------------------
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


def _draw_center(draw, text, font, cx, y, fill=(245, 240, 236), shadow=(0, 0, 0)):
    tw = draw.textlength(text, font=font)
    x = cx - tw / 2
    if shadow is not None:
        draw.text((x + 2, y + 2), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)


# ---------------------------------------------------------------------------
# Readability scrim
# ---------------------------------------------------------------------------
def _scrim(base, strength=0.42):
    """Darken the photo with a soft top+bottom-heavy gradient so text pops."""
    w, h = base.size
    grad = Image.new("L", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        # darker at top and bottom, a touch lighter through the middle
        edge = abs(t - 0.5) * 2  # 0 at center, 1 at edges
        a = int(255 * strength * (0.75 + 0.25 * edge))
        grad.putpixel((0, y), a)
    alpha = grad.resize((w, h))
    dark = Image.new("RGB", (w, h), (12, 9, 15))
    base = base.copy()
    base.paste(dark, (0, 0), alpha)
    return base


# ---------------------------------------------------------------------------
# Decorative florals (drawn, no external assets)
# ---------------------------------------------------------------------------
_FLOWER_COLORS = [
    (246, 166, 193), (245, 146, 126), (201, 168, 224),
    (247, 197, 159), (231, 122, 144), (185, 139, 214),
    (250, 182, 200), (238, 160, 168),
]
_LEAF_COLORS = [(150, 178, 140), (120, 160, 130), (168, 190, 150)]


def _one_flower(r, color, petals=6, alpha=170):
    """Return an RGBA tile with a single soft flower centered in it."""
    tile = int(r * 2.2)
    layer = Image.new("RGBA", (tile, tile), (0, 0, 0, 0))
    c = tile / 2
    petal_len = r
    petal_w = r * 0.62
    for i in range(petals):
        petal = Image.new("RGBA", (tile, tile), (0, 0, 0, 0))
        pd = ImageDraw.Draw(petal)
        pd.ellipse(
            [c - petal_w / 2, c - petal_len, c + petal_w / 2, c + petal_len * 0.08],
            fill=color + (alpha,),
        )
        angle = i * (360 / petals) + random.uniform(-6, 6)
        petal = petal.rotate(angle, resample=Image.BICUBIC, center=(c, c))
        layer = Image.alpha_composite(layer, petal)
    # center
    cd = ImageDraw.Draw(layer)
    cr = r * 0.28
    cd.ellipse([c - cr, c - cr, c + cr, c + cr], fill=(250, 214, 120, min(255, alpha + 40)))
    return layer


def _cluster(canvas, cx, cy, scale):
    """Paint a small cluster of flowers + leaves centered near (cx, cy)."""
    n_flowers = random.randint(2, 3)
    palette = random.sample(_FLOWER_COLORS, k=min(len(_FLOWER_COLORS), n_flowers + 1))
    # leaves first (behind)
    for _ in range(random.randint(2, 4)):
        r = random.uniform(38, 70) * scale
        leaf = _one_flower(r, random.choice(_LEAF_COLORS), petals=2, alpha=120)
        angle = random.uniform(0, 360)
        leaf = leaf.rotate(angle, resample=Image.BICUBIC)
        ox = cx + random.uniform(-90, 90) * scale - leaf.width / 2
        oy = cy + random.uniform(-90, 90) * scale - leaf.height / 2
        canvas.alpha_composite(leaf, (int(ox), int(oy)))
    # flowers on top
    for i in range(n_flowers):
        r = random.uniform(55, 95) * scale
        flower = _one_flower(r, palette[i % len(palette)],
                             petals=random.choice([5, 6, 6]),
                             alpha=random.randint(150, 195))
        ox = cx + random.uniform(-70, 70) * scale - flower.width / 2
        oy = cy + random.uniform(-70, 70) * scale - flower.height / 2
        canvas.alpha_composite(flower, (int(ox), int(oy)))


def _draw_florals(base):
    """Floral corner accents read as dated/'grandma', so they're disabled — the card
    is now clean (photo + gradient + type only). Kept as a no-op for compatibility."""
    return base.convert("RGB") if base.mode != "RGB" else base


# ---------------------------------------------------------------------------
# Background loading
# ---------------------------------------------------------------------------
def _open_bg(background_path, w, h):
    if background_path:
        return Image.open(background_path).convert("RGB").resize((w, h))
    return Image.new("RGB", (w, h), (18, 14, 22))


def _draw_handle(draw, w, h, handle):
    if not handle:
        return
    sf = _load_font(config.FONT_SMALL, int(h * 0.020))
    _draw_center(draw, handle, sf, w / 2, int(h * 0.955),
                 fill=(235, 229, 225), shadow=(0, 0, 0))


# ---------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------
def make_card(background_path, line, out_path, handle=None, title=None):
    handle = config.HANDLE if handle is None else handle
    w, h = config.CARD_W, config.CARD_H

    img = _open_bg(background_path, w, h)
    img = _scrim(img, 0.46)
    if config.DECORATE_FLORALS:
        img = _draw_florals(img)
    draw = ImageDraw.Draw(img)
    cx = w / 2

    top = int(h * 0.13)

    # script title
    if title:
        tf = _load_script_font(int(w * 0.135))
        _draw_center(draw, title, tf, cx, top, fill=(250, 246, 242))
        top += int(w * 0.135 * 1.05)
        top += int(h * 0.04)

    # body line (serif), auto-sized to fit the space *below* the title
    body_bottom = int(h * 0.87)
    avail = body_bottom - top
    max_w = int(w * 0.82)
    min_size = int(w * 0.050)
    size = int(w * 0.090)
    font = _load_font(config.FONT_DISPLAY, size)
    while True:
        lines = _wrap(draw, line, font, max_w)
        line_h = int(size * 1.18)
        total_h = line_h * len(lines)
        if total_h <= avail or size <= min_size:
            break
        size -= 4
        font = _load_font(config.FONT_DISPLAY, size)

    y = top + max(0, (avail - total_h) // 2)
    for ln in lines:
        _draw_center(draw, ln, font, cx, y)
        y += line_h

    _draw_handle(draw, w, h, handle)
    img.save(out_path)
    return str(out_path)


def make_paragraph_card(background_path, body, out_path, handle=None, title=None):
    handle = config.HANDLE if handle is None else handle
    w, h = config.CARD_W, config.CARD_H

    img = _open_bg(background_path, w, h)
    img = _scrim(img, 0.5)
    if config.DECORATE_FLORALS:
        img = _draw_florals(img)
    draw = ImageDraw.Draw(img)
    cx = w / 2

    top = int(h * 0.10)
    if title:
        tf = _load_script_font(int(w * 0.13))
        _draw_center(draw, title, tf, cx, top, fill=(250, 246, 242))
        top += int(w * 0.13 * 1.15)
        top += int(h * 0.03)

    max_w = int(w * 0.84)
    max_h = int(h * 0.78) - top
    start_size = int(w * 0.056)
    min_size = int(w * 0.040)
    line_spacing = 1.32

    raw_lines = [ln.strip() for ln in body.splitlines() if ln.strip()] or [body]

    size = start_size
    wrapped_lines = []
    while size >= min_size:
        font = _load_font(config.FONT_DISPLAY, size)
        wrapped_lines = []
        for ln in raw_lines:
            wrapped_lines.extend(_wrap(draw, ln, font, max_w))
        line_h = int(size * line_spacing)
        if line_h * len(wrapped_lines) <= max_h:
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
    y = top + max(0, int((max_h - total_h) / 2))
    for ln in wrapped_lines:
        _draw_center(draw, ln, font, cx, y)
        y += line_h

    _draw_handle(draw, w, h, handle)
    print(f"PARAGRAPH font size = {size}, lines = {n}")
    img.save(out_path)
    return str(out_path)


# ---------------------------------------------------------------------------
# Interactive / eye-catching cards (quizzes, this-or-that, would-you-rather,
# fun facts, finish-the-sentence). Built to look like a GAME, not a quote:
# a bold label pill, option panels, an "OR" badge, a comment nudge.
# ---------------------------------------------------------------------------
_ACCENT = (232, 94, 118)     # warm rose  (option A, header pill, OR badge)
_ACCENT2 = (108, 132, 224)   # cool indigo (option B)
_INK = (250, 246, 243)


def _fit(draw, text, path, max_w, max_h, start, min_size, spacing=1.15):
    """Largest font (>= min_size) at which `text` wraps within max_w x max_h."""
    size = start
    while size > min_size:
        f = _load_font(path, size)
        lines = _wrap(draw, text, f, max_w)
        if int(size * spacing) * len(lines) <= max_h:
            return f, lines, size
        size -= 2
    f = _load_font(path, min_size)
    return f, _wrap(draw, text, f, max_w), min_size


def _pill(od, text, cx, cy, fill, size, fg=_INK, padx=52, pady=24):
    """Draw a rounded label pill centered at (cx, cy); return its bottom y."""
    f = _load_font(config.FONT_SMALL, size)
    tw = od.textlength(text, font=f)
    w2, h2 = tw / 2 + padx, size / 2 + pady
    od.rounded_rectangle([cx - w2, cy - h2, cx + w2, cy + h2], radius=h2, fill=fill + (255,))
    od.text((cx - tw / 2, cy - size * 0.62), text, font=f, fill=fg + (255,))
    return cy + h2


def make_poll_card(background_path, header, options, out_path, handle=None,
                   footer="COMMENT YOUR PICK BELOW", question=None):
    """A 'pick one' card for this-or-that / would-you-rather / quiz.
    `options` is 2-4 short strings; exactly 2 gets a central OR badge.
    `question` (e.g. a quiz question) is drawn between the header and options."""
    handle = config.HANDLE if handle is None else handle
    w, h = config.CARD_W, config.CARD_H
    base = _scrim(_open_bg(background_path, w, h), 0.58).convert("RGBA")
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    cx = w / 2

    hb = _pill(od, (header or "Pick One").upper(), cx, int(h * 0.11),
               _ACCENT, int(w * 0.045))

    # optional question (quiz) — wrapped, centered, below the header
    q = (question or "").strip()
    if q:
        qf, qlines, qs = _fit(od, q, config.FONT_DISPLAY, int(w * 0.84),
                              int(h * 0.16), int(w * 0.064), int(w * 0.044), spacing=1.14)
        qy = hb + int(h * 0.035)
        lh = int(qs * 1.14)
        for ln in qlines:
            lw = od.textlength(ln, font=qf)
            od.text((cx - lw / 2, qy), ln, font=qf, fill=_INK + (255,))
            qy += lh
        hb = qy

    opts = [o.strip() for o in (options or []) if o and o.strip()][:4] or ["This", "That"]
    two = len(opts) == 2
    top = hb + int(h * 0.045)
    bottom = int(h * 0.865)
    gap = int(h * 0.030)
    panel_h = int((bottom - top - gap * (len(opts) - 1)) / len(opts))
    panel_w = int(w * 0.84)
    x0 = cx - panel_w / 2
    letters = ["A", "B", "C", "D"]

    y = top
    for i, opt in enumerate(opts):
        od.rounded_rectangle([x0, y, x0 + panel_w, y + panel_h], radius=int(panel_h * 0.20),
                             fill=(16, 11, 19, 188), outline=(255, 255, 255, 48), width=3)
        accent = _ACCENT if i % 2 == 0 else _ACCENT2
        br = int(panel_h * 0.19)
        bcx, bcy = x0 + int(panel_w * 0.12), y + panel_h / 2
        od.ellipse([bcx - br, bcy - br, bcx + br, bcy + br], fill=accent + (255,))
        lf = _load_font(config.FONT_SCRIPT, int(br * 1.25))
        lw = od.textlength(letters[i], font=lf)
        od.text((bcx - lw / 2, bcy - br * 0.86), letters[i], font=lf, fill=_INK + (255,))
        tx0 = bcx + br + int(panel_w * 0.05)
        tmax = x0 + panel_w - tx0 - int(panel_w * 0.05)
        tf, tlines, s = _fit(od, opt, config.FONT_DISPLAY, tmax, int(panel_h * 0.74),
                             int(w * 0.055), int(w * 0.030))
        lh = int(s * 1.12)
        ty = bcy - lh * len(tlines) / 2
        for ln in tlines:
            od.text((tx0, ty), ln, font=tf, fill=_INK + (255,))
            ty += lh
        y += panel_h + gap

    if two:
        oy = top + panel_h + gap / 2
        orr = int(w * 0.076)
        od.ellipse([cx - orr, oy - orr, cx + orr, oy + orr], fill=_ACCENT + (255,),
                   outline=(255, 255, 255, 235), width=6)
        of = _load_font(config.FONT_SCRIPT, int(orr * 0.80))
        ow = od.textlength("OR", font=of)
        od.text((cx - ow / 2, oy - orr * 0.55), "OR", font=of, fill=_INK + (255,))

    if footer:
        ff = _load_font(config.FONT_SMALL, int(w * 0.036))
        fw = od.textlength(footer, font=ff)
        fy = int(h * 0.905)
        od.rounded_rectangle([cx - fw / 2 - 34, fy - 16, cx + fw / 2 + 34, fy + int(w * 0.036) + 20],
                             radius=50, fill=(16, 11, 19, 170))
        od.text((cx - fw / 2, fy), footer, font=ff, fill=(255, 255, 255, 240))

    out = Image.alpha_composite(base, overlay).convert("RGB")
    _draw_handle(ImageDraw.Draw(out), w, h, handle)
    out.save(out_path)
    return str(out_path)


def make_prompt_card(background_path, header, text, out_path, handle=None,
                     footer="TELL US IN THE COMMENTS"):
    """A single-statement interactive card for fun facts / finish-the-sentence /
    open questions: a bold label pill, the big line, and a comment nudge."""
    handle = config.HANDLE if handle is None else handle
    w, h = config.CARD_W, config.CARD_H
    base = _scrim(_open_bg(background_path, w, h), 0.55).convert("RGBA")
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    cx = w / 2

    hb = _pill(od, (header or "Your Turn").upper(), cx, int(h * 0.135),
               _ACCENT, int(w * 0.045))
    top = hb + int(h * 0.04)
    bottom = int(h * 0.82)
    tf, tlines, s = _fit(od, text or "", config.FONT_DISPLAY, int(w * 0.82),
                         bottom - top, int(w * 0.090), int(w * 0.048), spacing=1.18)
    lh = int(s * 1.18)
    y = top + max(0, (bottom - top - lh * len(tlines)) // 2)
    for ln in tlines:
        lw = od.textlength(ln, font=tf)
        od.text((cx - lw / 2, y), ln, font=tf, fill=_INK + (255,))
        y += lh

    if footer:
        ff = _load_font(config.FONT_SMALL, int(w * 0.038))
        fw = od.textlength(footer, font=ff)
        fy = int(h * 0.885)
        od.rounded_rectangle([cx - fw / 2 - 36, fy - 16, cx + fw / 2 + 36, fy + int(w * 0.038) + 20],
                             radius=50, fill=_ACCENT + (235,))
        od.text((cx - fw / 2, fy), footer, font=ff, fill=_INK + (255,))

    out = Image.alpha_composite(base, overlay).convert("RGB")
    _draw_handle(ImageDraw.Draw(out), w, h, handle)
    out.save(out_path)
    return str(out_path)
