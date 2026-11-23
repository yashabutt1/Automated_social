"""Pull REAL, meaningful relationship articles from trusted blogs, so posts are
grounded in genuine advice/insight instead of generic quote-card lines.

Needs feedparser + requests. Fails soft (skips a dead feed). Browser User-Agent,
since default feedparser UA is often blocked.
"""
from __future__ import annotations

import re

import requests

try:
    import feedparser
except Exception:  # pragma: no cover
    feedparser = None

_UA = {"User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")}

# (name, rss_url) — curated, genuinely useful relationship writers.
FEEDS = [
    ("Nicole Talks Love", "https://nicoletalkslove.com/blog/feed/"),
    ("Nicole Talks Love", "https://nicoletalkslove.com/feed/"),
    ("Modern Love Counseling", "https://modernlovecounseling.com/feed/"),
    ("Modern Love Counseling", "https://modernlovecounseling.com/modern-relationship-advice/feed/"),
    ("Eva VP", "https://www.evavp.com/relationship-blog?format=rss"),
]

# Skip meta/SEO/location-landing posts that aren't real relationship insight.
_SKIP = ("couples therapy denver", "near me", "cost of", "how much does",
         "privacy policy", "terms of", "newsletter", "podcast episode")


def _clean(html: str) -> str:
    s = re.sub(r"<[^>]+>", " ", html or "")
    s = s.replace("&amp;", "&").replace("&nbsp;", " ").replace("&#8217;", "'").replace("&rsquo;", "'")
    return re.sub(r"\s+", " ", s).strip()


def _usable(title: str) -> bool:
    t = (title or "").lower()
    return bool(title) and not any(s in t for s in _SKIP)


def fetch_articles(max_per_feed: int = 6) -> list[dict]:
    """Recent {title, link, summary, source} relationship articles across feeds."""
    if feedparser is None:
        return []
    items, seen = [], set()
    for name, url in FEEDS:
        try:
            r = requests.get(url, headers=_UA, timeout=20)
            parsed = feedparser.parse(r.content)
        except Exception as exc:
            print(f"  feed {name} failed ({exc})")
            continue
        kept = 0
        for e in parsed.entries:
            title = (e.get("title") or "").strip()
            link = (e.get("link") or "").strip()
            summary = _clean(e.get("summary") or e.get("description") or "")[:500]
            key = title.lower()
            if not title or not link or key in seen or not _usable(title):
                continue
            seen.add(key)
            items.append({"title": title, "link": link, "summary": summary, "source": name})
            kept += 1
            if kept >= max_per_feed:
                break
    return items


def domain(url: str) -> str:
    m = re.search(r"https?://(?:www\.)?([^/]+)", url or "")
    return m.group(1) if m else ""
