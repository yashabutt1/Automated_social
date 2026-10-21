"""Curated bank of REAL, correctly-attributed quotes for long-form reflection
posts (the "Thoughts That Linger" style — a warm essay woven around a famous
quote). These are hand-curated so the AI never invents or misattributes a quote;
it only writes the reflection *around* the given one. Edit freely — add your own
favorites or remove any you're unsure about.

A shuffle-bag picker serves each quote once before any repeats.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import config

_HISTORY_FILE = ".quote_history.json"

QUOTES: list[dict] = [
    {"text": "Happiness always looks small while you hold it in your hands, but let it go, and you learn at once how big and precious it is.", "author": "Maxim Gorky"},
    {"text": "The best thing to hold onto in life is each other.", "author": "Audrey Hepburn"},
    {"text": "Love does not consist of gazing at each other, but in looking outward together in the same direction.", "author": "Antoine de Saint-Exupéry"},
    {"text": "The best and most beautiful things in the world cannot be seen or even touched — they must be felt with the heart.", "author": "Helen Keller"},
    {"text": "What we once enjoyed and deeply loved we can never lose, for all that we love deeply becomes a part of us.", "author": "Helen Keller"},
    {"text": "A successful marriage requires falling in love many times, always with the same person.", "author": "Mignon McLaughlin"},
    {"text": "Grow old along with me! The best is yet to be.", "author": "Robert Browning"},
    {"text": "Where there is love there is life.", "author": "Mahatma Gandhi"},
    {"text": "To get the full value of joy you must have someone to divide it with.", "author": "Mark Twain"},
    {"text": "A happy marriage is a long conversation which always seems too short.", "author": "André Maurois"},
    {"text": "Age does not protect you from love. But love, to some extent, protects you from age.", "author": "Jeanne Moreau"},
    {"text": "The giving of love is an education in itself.", "author": "Eleanor Roosevelt"},
    {"text": "Life is the flower for which love is the honey.", "author": "Victor Hugo"},
    {"text": "We are most alive when we're in love.", "author": "John Updike"},
    {"text": "To love and be loved is to feel the sun from both sides.", "author": "David Viscott"},
    {"text": "The heart that loves is always young.", "author": "Greek Proverb"},
    {"text": "They say a person needs just three things to be truly happy in this world: someone to love, something to do, and something to hope for.", "author": "Tom Bodett"},
    {"text": "The best portion of a good person's life: the little, nameless, unremembered acts of kindness and of love.", "author": "William Wordsworth"},
    {"text": "Love is composed of a single soul inhabiting two bodies.", "author": "Aristotle"},
    {"text": "In all the world, there is no heart for me like yours. In all the world, there is no love for you like mine.", "author": "Maya Angelou"},
    {"text": "You don't love someone for their looks, or their clothes, but because they sing a song only you can hear.", "author": "Oscar Wilde"},
    {"text": "Gratitude is not only the greatest of virtues, but the parent of all the others.", "author": "Cicero"},
    {"text": "Count your age by friends, not years. Count your life by smiles, not tears.", "author": "John Lennon"},
    {"text": "The simplest things are often the truest.", "author": "Richard Bach"},
]


def _history_path() -> Path:
    return config.OUTPUT_DIR / _HISTORY_FILE


def _load_bag() -> list[int]:
    try:
        data = json.loads(_history_path().read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [int(x) for x in data]
    except Exception:
        pass
    return []


def _save_bag(bag: list[int]) -> None:
    try:
        _history_path().parent.mkdir(parents=True, exist_ok=True)
        _history_path().write_text(json.dumps(bag), encoding="utf-8")
    except Exception:
        pass


def pick_quotes(n: int) -> list[dict]:
    """Return n quotes, each used once before any repeats (shuffle-bag)."""
    if n < 1 or not QUOTES:
        return []
    bag = [i for i in _load_bag() if 0 <= i < len(QUOTES)]
    chosen = []
    while len(chosen) < n:
        if not bag:
            bag = list(range(len(QUOTES)))
            random.shuffle(bag)
        chosen.append(QUOTES[bag.pop()])
    _save_bag(bag)
    return chosen
