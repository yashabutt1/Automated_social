"""Amazon Associates product picker (manual-link mode, no PA-API).

You curate a pool of best-seller links in products.txt (one "name | url" per
line). This module parses that pool, ensures YOUR Associate tag is on every
link, and picks a few products per day that haven't been posted recently.

No Amazon scraping happens here — product discovery is your curation; we only
build the affiliate URL from a link you already chose, which is allowed under
the Associates Operating Agreement (it's your own tag).
"""
from __future__ import annotations

import json
import os
import random
import re
from pathlib import Path
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

import config

_HISTORY_FILE = ".product_history.json"
_RECENT = 60

_ASIN_RE = re.compile(r"(?:/dp/|/gp/product/|/gp/aw/d/|/product/|/d/|asin=)([A-Z0-9]{10})", re.I)
_BARE_ASIN_RE = re.compile(r"/([A-Z0-9]{10})(?:[/?]|$)")


def _tag() -> str:
    return os.getenv("AMAZON_ASSOC_TAG", "").strip() or config.AMAZON_ASSOC_TAG


def _marketplace() -> str:
    return os.getenv("AMAZON_MARKETPLACE", "").strip() or config.AMAZON_MARKETPLACE or "www.amazon.com"


def extract_asin(url: str) -> str | None:
    m = _ASIN_RE.search(url) or _BARE_ASIN_RE.search(url)
    return m.group(1).upper() if m else None


def build_affiliate_url(url: str) -> str:
    """Return a clean product URL carrying our Associate tag."""
    tag = _tag()
    asin = extract_asin(url)
    if asin:
        base = f"https://{_marketplace()}/dp/{asin}/"
        return f"{base}?tag={tag}" if tag else base
    # Fallback: keep the given URL but set/replace the tag query param.
    parts = urlparse(url if "//" in url else "https://" + url)
    query = dict(parse_qsl(parts.query))
    if tag:
        query["tag"] = tag
    return urlunparse(parts._replace(query=urlencode(query)))


def load_products() -> list[dict]:
    """Parse products.txt into [{name, url, asin}] entries."""
    path = config.PRODUCTS_FILE
    if not path.exists():
        return []
    items = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "|" not in line:
            continue
        name, url = (p.strip() for p in line.split("|", 1))
        if not name or not url or "EXAMPLE" in url:
            continue
        items.append({"name": name, "url": url, "asin": extract_asin(url)})
    return items


def _history_path() -> Path:
    return config.OUTPUT_DIR / _HISTORY_FILE


def _load_recent() -> list[str]:
    try:
        data = json.loads(_history_path().read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [str(x) for x in data]
    except Exception:
        pass
    return []


def _save_recent(keys: list[str]) -> None:
    try:
        _history_path().parent.mkdir(parents=True, exist_ok=True)
        _history_path().write_text(json.dumps(keys[-_RECENT:]), encoding="utf-8")
    except Exception:
        pass


def _key(item: dict) -> str:
    return item.get("asin") or item.get("url")


def pick_products(n: int) -> list[dict]:
    """Pick up to n products not posted recently; each gets an affiliate_url."""
    products = load_products()
    if not products:
        return []
    recent = set(_load_recent())
    fresh = [p for p in products if _key(p) not in recent]
    random.shuffle(fresh)
    if len(fresh) < n:
        stale = [p for p in products if _key(p) in recent]
        random.shuffle(stale)
        fresh += stale
    chosen = fresh[:n]
    for p in chosen:
        p["affiliate_url"] = build_affiliate_url(p["url"])
    _save_recent(_load_recent() + [_key(p) for p in chosen])
    return chosen
