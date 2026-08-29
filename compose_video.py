"""Build a finished reel: stock clip + branded text overlay + music.

Two steps:
  1. Render a transparent 1080x1920 PNG overlay with Pillow (a readability scrim,
     an elegant script title, the short line, and the handle) — same visual
     language as the cards.
  2. ffmpeg composites: cover-scale/crop the clip to 9:16, loop/trim to the target
     length, overlay the PNG, mix in music with fades, and encode H.264/AAC.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

import config
import compose  # reuse fonts + text helpers


def _reel_scrim(w, h):
    """A semi-transparent dark layer, heavier top/bottom, for text legibility."""
    grad = Image.new("L", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        edge = abs(t - 0.5) * 2
        a = int(150 * (0.55 + 0.45 * edge))  # ~85 mid, ~150 edges
        grad.putpixel((0, y), a)
    alpha = grad.resize((w, h))
    layer = Image.new("RGBA", (w, h), (10, 8, 14, 0))
    layer.putalpha(alpha)
    return layer


def make_reel_overlay(title, line, out_png, handle=None):
    handle = config.HANDLE if handle is None else handle
    w, h = config.REEL_W, config.REEL_H
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img = Image.alpha_composite(img, _reel_scrim(w, h))
    draw = ImageDraw.Draw(img)
    cx = w / 2

    # vertical block centered a little above middle
    top = int(h * 0.30)
    if title:
        tf = compose._load_script_font(int(w * 0.16))
        compose._draw_center(draw, title, tf, cx, top, fill=(250, 246, 242))
        top += int(w * 0.16 * 1.05) + int(h * 0.02)

    max_w = int(w * 0.84)
    min_size = int(w * 0.058)
    size = int(w * 0.088)
    font = compose._load_font(config.FONT_DISPLAY, size)
    body_bottom = int(h * 0.72)
    avail = body_bottom - top
    while True:
        lines = compose._wrap(draw, line, font, max_w)
        line_h = int(size * 1.2)
        total_h = line_h * len(lines)
        if total_h <= avail or size <= min_size:
            break
        size -= 4
        font = compose._load_font(config.FONT_DISPLAY, size)
    y = top + max(0, (avail - total_h) // 2)
    for ln in lines:
        compose._draw_center(draw, ln, font, cx, y)
        y += line_h

    if handle:
        sf = compose._load_font(config.FONT_SMALL, int(h * 0.018))
        compose._draw_center(draw, handle, sf, cx, int(h * 0.93),
                             fill=(235, 229, 225))

    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_png)
    return str(out_png)


def make_reel(clip_path, title, line, out_path, music_path=None,
              seconds=None, handle=None):
    """Composite clip + overlay + optional music into a finished reel MP4."""
    seconds = seconds or config.REEL_TARGET_SECONDS
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    overlay_png = out_path.with_suffix(".overlay.png")
    make_reel_overlay(title, line, overlay_png, handle=handle)

    fade = 0.6
    vfilter = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,setsar=1,fps=30[bg];"
        "[bg][1:v]overlay=0:0:format=auto,"
        f"fade=t=in:st=0:d={fade},fade=t=out:st={seconds - fade:.2f}:d={fade}[v]"
    )

    cmd = [
        config.FFMPEG, "-y",
        "-stream_loop", "-1", "-i", str(clip_path),   # 0: video (looped)
        "-i", str(overlay_png),                        # 1: overlay
    ]
    if music_path:
        cmd += ["-stream_loop", "-1", "-i", str(music_path)]  # 2: music (looped)
        afilter = (
            f"[2:a]afade=t=in:st=0:d=1,"
            f"afade=t=out:st={seconds - 1.5:.2f}:d=1.5,volume=0.85[a]"
        )
        filter_complex = vfilter + ";" + afilter
        cmd += ["-filter_complex", filter_complex, "-map", "[v]", "-map", "[a]"]
    else:
        cmd += ["-filter_complex", vfilter, "-map", "[v]"]

    cmd += [
        "-t", str(seconds),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-preset", "medium", "-crf", "20", "-r", "30",
    ]
    if music_path:
        cmd += ["-c:a", "aac", "-b:a", "192k"]
    cmd += ["-movflags", "+faststart", str(out_path)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        overlay_png.unlink()
    except Exception:
        pass
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[-1500:]}")
    return str(out_path)
