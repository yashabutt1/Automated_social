"""Visual variety for reels.

The reel's *words* come from the love/relationship topic system, but its *video*
is chosen from a wider visual palette so the feed isn't all couples — some people
prefer scenery, some prefer intimate. Categories rotate so the two daily reels
differ from each other and from the day before.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

_HISTORY_FILE = ".reel_visual_history.json"

CATEGORIES: dict[str, list[str]] = {
    "nature": [
        "blooming flowers macro", "ocean waves golden sunset", "autumn leaves falling slow",
        "forest sunlight rays morning", "misty mountains dawn", "wildflowers breeze field",
        "cherry blossom petals falling", "starry night sky timelapse", "calm lake reflection sunrise",
        "snow falling pine forest", "lavender field sunset", "waterfall lush green",
    ],
    "love": [
        "older couple holding hands walking", "mature couple laughing together",
        "senior couple dancing at home", "grandparents couple sunset", "couple hugging warm",
        "older couple forehead touch tender", "couple silhouette sunset",
        "family hug multigenerational", "couple grey hair smiling", "couple coffee morning cozy",
    ],
    "aesthetic": [
        "coffee steam morning light", "candle flame cozy dark", "book pages turning sunlight",
        "sun through sheer curtains", "hand writing letter", "city lights bokeh night rain",
        "rain on window warm light", "fairy lights warm bokeh", "tea cup window rainy day",
    ],
}


def _history_path(output_root: Path | str) -> Path:
    return Path(output_root) / _HISTORY_FILE


def _load_last(output_root: Path | str) -> list[str]:
    try:
        data = json.loads(_history_path(output_root).read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [str(x) for x in data]
    except Exception:
        pass
    return []


def _save_last(output_root: Path | str, cats: list[str]) -> None:
    try:
        p = _history_path(output_root)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(cats), encoding="utf-8")
    except Exception:
        pass


def pick_visuals(n: int, output_root: Path | str) -> list[dict]:
    """Return ``n`` visual specs (distinct categories where possible), avoiding
    the categories used on the previous run, each with shuffled search queries."""
    last = set(_load_last(output_root))
    names = list(CATEGORIES.keys())
    fresh = [c for c in names if c not in last]
    random.shuffle(fresh)
    random.shuffle(names)
    ordered = fresh + [c for c in names if c not in fresh]

    chosen_cats: list[str] = []
    i = 0
    while len(chosen_cats) < n:
        chosen_cats.append(ordered[i % len(ordered)])
        i += 1
        # after one pass, allow repeats if n > number of categories
        if i >= len(ordered) and len(chosen_cats) < n:
            random.shuffle(ordered)

    specs = []
    for idx, cat in enumerate(chosen_cats):
        queries = CATEGORIES[cat][:]
        random.shuffle(queries)
        specs.append({"id": f"{cat}_{idx}", "category": cat, "pexels_queries": queries})

    _save_last(output_root, chosen_cats)
    return specs
