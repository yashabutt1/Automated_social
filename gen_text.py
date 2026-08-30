"""Text generation for The Love Lens.

The pipeline prefers Gemini for copy, but it can fall back to local templates
when the API is unavailable or quota-limited so the review workflow still runs.

Both the live prompts and the local fallbacks are now organised by *topic
category* (see topics.py) so the feed keeps moving through different subjects
instead of repeating the same anxious-texting lane every run.
"""
import json
import os
import random
import re

from google import genai

import config
import prompts

_client = None
if os.getenv("GEMINI_API_KEY"):
    try:
        _client = genai.Client()  # reads GEMINI_API_KEY from the environment
    except Exception:
        _client = None


def _parse_json(raw: str):
    """Strip any code fences and parse a JSON array from the model output."""
    cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
    # Grab the outermost [...] in case the model added stray text.
    start, end = cleaned.find("["), cleaned.rfind("]")
    if start != -1 and end != -1:
        cleaned = cleaned[start : end + 1]
    return json.loads(cleaned)


# ---------------------------------------------------------------------------
# Local fallback pools, tagged by topic category. These only run when Gemini is
# unreachable or out of quota. They deliberately span the whole spectrum so a
# fallback day still looks varied.
# ---------------------------------------------------------------------------
_FALLBACK_LINES: list[dict] = [
    {"category": "warm", "title": "Soft Landing",
     "line": "The right person feels less like a spark and more like finally being able to exhale.",
     "caption": "Calm can be its own kind of romance. Who makes your shoulders drop the moment they walk in?",
     "hashtags": ["love", "relationships", "calm", "safelove", "connection", "warmth"]},
    {"category": "warm", "title": "Little Things",
     "line": "Real love is the saved last bite, the warmed-up car, the text that just says 'get home safe.'",
     "caption": "The small stuff is the whole thing. What tiny gesture made you feel loved this week?",
     "hashtags": ["love", "smallgestures", "relationships", "romance", "everydaylove", "care"]},
    {"category": "selflove", "title": "As You Are",
     "line": "You don't have to become impressive to be loved. You already qualify, exactly as you are.",
     "caption": "You were never too much or not enough. What would change if you believed that today?",
     "hashtags": ["selflove", "selfworth", "worthy", "healing", "confidence", "love"]},
    {"category": "selflove", "title": "Own Company",
     "line": "Learn to be the kind of company you'd cross a room for. The rest gets easier from there.",
     "caption": "Falling for your own company changes what you'll settle for. How do you enjoy your own time?",
     "hashtags": ["selflove", "growth", "confidence", "selfcare", "healing", "peace"]},
    {"category": "hope", "title": "On Its Way",
     "line": "Just because it hasn't happened yet doesn't mean it isn't coming. Gentle love takes the scenic route sometimes.",
     "caption": "Your story isn't over; it's mid-sentence. What are you still hopeful for?",
     "hashtags": ["hope", "love", "newbeginnings", "faith", "romance", "healing"]},
    {"category": "hope", "title": "Stay Open",
     "line": "Staying soft after being hurt isn't naive. It's the bravest thing a heart can do.",
     "caption": "Keeping your heart open is quiet courage. What helps you stay hopeful?",
     "hashtags": ["hope", "vulnerability", "healing", "openheart", "love", "courage"]},
    {"category": "healing", "title": "Slow Mend",
     "line": "Healing isn't linear and it isn't late. Your heart is allowed to take the time it needs.",
     "caption": "Be as patient with yourself as you'd be with a friend. What are you healing from right now?",
     "hashtags": ["healing", "selfcare", "growth", "movingon", "peace", "gentle"]},
    {"category": "healing", "title": "Make Room",
     "line": "Letting go isn't losing. It's clearing the space something better was always meant to fill.",
     "caption": "You're not giving up; you're making room. What have you finally set down?",
     "hashtags": ["lettinggo", "healing", "movingon", "growth", "selfrespect", "peace"]},
    {"category": "communication", "title": "Say It Plain",
     "line": "Saying 'this matters to me' out loud isn't drama. It's how two people find each other in the dark.",
     "caption": "Naming what you feel is a gift, not a fight. What do you wish you said sooner?",
     "hashtags": ["communication", "relationships", "honesty", "connection", "love", "healthylove"]},
    {"category": "communication", "title": "Truly Heard",
     "line": "Being fully listened to feels a lot like being loved. Sometimes it's the same thing.",
     "caption": "We all want to feel heard. When did someone last really listen to you?",
     "hashtags": ["communication", "listening", "connection", "love", "relationships", "empathy"]},
    {"category": "gratitude", "title": "Right Here",
     "line": "Don't wait for the anniversary to notice them. The ordinary Tuesday version of your person is the real gift.",
     "caption": "Appreciation out loud is underrated. What are you grateful for in someone today?",
     "hashtags": ["gratitude", "love", "appreciation", "relationships", "romance", "everydaylove"]},
    {"category": "committed", "title": "Chosen Again",
     "line": "Lasting love isn't one big yes. It's a thousand small ones, on the days it would be easier not to.",
     "caption": "Love is a daily choice. What makes it easy to keep choosing yours?",
     "hashtags": ["love", "commitment", "marriage", "longterm", "relationships", "devotion"]},
    {"category": "playful", "title": "My Favorite",
     "line": "The best kind of love laughs at its own inside jokes and never fully explains them to anyone.",
     "caption": "Silly together is a love language. What's your dumbest shared joke?",
     "hashtags": ["love", "playful", "couplegoals", "laughter", "relationships", "joy"]},
    {"category": "longing", "title": "Miss You",
     "line": "Missing someone is just love with nowhere to go for a little while. Let it mean what it means.",
     "caption": "Longing has its own tenderness. Who are you missing tonight?",
     "hashtags": ["longing", "love", "missingyou", "longdistance", "romance", "heart"]},
    {"category": "boundaries", "title": "Kind & Clear",
     "line": "A boundary said kindly still counts. You can protect your peace without hardening your heart.",
     "caption": "Kind and clear can live in the same sentence. What boundary are you proud of?",
     "hashtags": ["boundaries", "selfrespect", "selfcare", "peace", "relationships", "love"]},
]

_FALLBACK_PARAGRAPHS: list[dict] = [
    {"category": "warm", "title": "Come Home",
     "body": "Some people feel like a held breath.\nAnd then you meet the one who feels like letting it out.\nNo performing, no bracing, no keeping score.\nJust the quiet relief of being known.\nThat ease is not boring. That ease is the whole point.",
     "caption": "Peace is deeply romantic. Who feels like home to you?",
     "hashtags": ["love", "safelove", "calm", "relationships", "connection", "warmth"]},
    {"category": "selflove", "title": "Enough",
     "body": "You keep waiting to feel finished before you let yourself be loved.\nBut you were never a project.\nYou are allowed to be a work in progress and still be adored today.\nStop auditioning for a life that is already yours.\nYou qualify as you are.",
     "caption": "You don't have to earn love. What would you do differently if you believed that?",
     "hashtags": ["selflove", "selfworth", "healing", "confidence", "worthy", "love"]},
    {"category": "hope", "title": "Still Coming",
     "body": "It hasn't happened yet.\nThat is not the same as it never will.\nSome love takes the long way to reach you.\nKeep your heart a little open, a little soft.\nThe good kind is quieter than you expect, and it is not lost.",
     "caption": "Gentle love is still out there. What are you hopeful for?",
     "hashtags": ["hope", "love", "newbeginnings", "faith", "healing", "romance"]},
    {"category": "healing", "title": "At Your Pace",
     "body": "Nobody handed you a timeline for this.\nYou are allowed to heal in seasons, not deadlines.\nSome days you'll feel almost whole.\nSome days the ache returns without warning.\nBoth are the process. Be as kind to yourself as you'd be to a friend.",
     "caption": "Healing isn't a race. What helps on the hard days?",
     "hashtags": ["healing", "selfcare", "movingon", "growth", "peace", "gentle"]},
    {"category": "communication", "title": "Just Ask",
     "body": "You don't have to hint and hope they guess.\nName the thing you need, plainly and kindly.\nA clear ask is not a demand.\nIt's an invitation to be met.\nThen you get to see who can meet you there.",
     "caption": "Clarity is a kind of love. What do you need to say out loud?",
     "hashtags": ["communication", "relationships", "honesty", "needs", "connection", "healthylove"]},
    {"category": "gratitude", "title": "Notice Them",
     "body": "Don't save your kind words for a toast.\nTell them now, on the ordinary day.\nThank them for the small, invisible things.\nThe love that gets spoken tends to grow.\nThe love that gets assumed tends to fade.",
     "caption": "Appreciation is a habit worth keeping. What will you thank someone for today?",
     "hashtags": ["gratitude", "love", "appreciation", "relationships", "romance", "kindness"]},
    {"category": "committed", "title": "The Long Yes",
     "body": "Real love is rarely the fireworks.\nIt's the small yes you say on a tired Tuesday.\nIt's staying curious about someone you already know.\nIt's choosing them again, softly, without applause.\nThat quiet loyalty is the most romantic thing there is.",
     "caption": "Love is a daily choice. What keeps yours steady?",
     "hashtags": ["love", "commitment", "longterm", "marriage", "devotion", "relationships"]},
    {"category": "playful", "title": "Us Being Us",
     "body": "The best love has a language no one else speaks.\nInside jokes that make no sense out loud.\nDumb nicknames you'd never admit to.\nLaughing until you can't breathe over nothing.\nDon't underestimate the person who makes you giggle.",
     "caption": "Playfulness keeps love young. What's your silliest shared moment?",
     "hashtags": ["love", "playful", "laughter", "couplegoals", "joy", "relationships"]},
    {"category": "boundaries", "title": "Soft & Sure",
     "body": "You can love someone and still say not like this.\nA boundary isn't a wall you build against them.\nIt's a door you keep on your own house.\nSay it kindly. Say it clearly.\nPeace and warmth are allowed to coexist.",
     "caption": "Boundaries protect the good stuff. What boundary are you learning to hold?",
     "hashtags": ["boundaries", "selfrespect", "selfcare", "love", "peace", "relationships"]},
]


def _strip(item: dict) -> dict:
    return {k: v for k, v in item.items() if k != "category"}


def _fallback_for_topics(pool: list[dict], topics: list[dict]) -> list[dict]:
    """Return one distinct fallback per topic, matching category where possible."""
    remaining = pool[:]
    random.shuffle(remaining)
    out: list[dict] = []
    for topic in topics:
        cat = (topic or {}).get("category")
        pick = next((x for x in remaining if x.get("category") == cat), None)
        if pick is None:
            pick = remaining[0] if remaining else random.choice(pool)
        if pick in remaining:
            remaining.remove(pick)
        out.append(_strip(pick))
    return out


def _fallback_lines(topics: list[dict]):
    return _fallback_for_topics(_FALLBACK_LINES, topics)


def _fallback_paragraphs(topics: list[dict]):
    return _fallback_for_topics(_FALLBACK_PARAGRAPHS, topics)


def _align(items, topics, pool):
    """Make ``items`` line up 1:1 with ``topics``; fill any gaps from fallback."""
    if not isinstance(items, list):
        items = []
    items = [x for x in items if isinstance(x, dict)]
    if len(items) >= len(topics):
        return items[: len(topics)]
    # backfill the missing tail with topic-matched fallbacks
    missing = topics[len(items):]
    return items + _fallback_for_topics(pool, missing)


def _fallback_reels(n: int):
    return [
        {
            "format": "Green flag / Red flag — two quick contrasts on one behavior",
            "hook": "A calm response is a green flag.",
            "beats": ["When they listen without interrupting", "When they rush to defend instead", "The difference is honesty"],
            "caption": "Healthy relationships are built from small moments of emotional maturity.",
            "hashtags": ["relationshiptips", "datingadvice", "greenflags", "communication", "healthyrelationships", "boundaries"],
            "visual": "Text on a soft gradient with calm b-roll",
            "runtime": "18s",
        }
        for _ in range(n)
    ]


def make_lines(topics: list[dict]):
    """One batched Gemini call -> one {title, line, caption, hashtags} per topic."""
    if not topics:
        return []
    if _client is None:
        return _fallback_lines(topics)
    try:
        resp = _client.models.generate_content(
            model=config.TEXT_MODEL, contents=prompts.lines_prompt(topics))
        return _align(_parse_json(resp.text), topics, _FALLBACK_LINES)
    except Exception as exc:
        print(f"  Gemini line generation failed ({exc}); using local fallback content")
        return _fallback_lines(topics)


def make_paragraphs(topics: list[dict]):
    """One batched Gemini call -> one {title, body, caption, hashtags} per topic."""
    if not topics:
        return []
    if _client is None:
        return _fallback_paragraphs(topics)
    try:
        resp = _client.models.generate_content(
            model=config.TEXT_MODEL, contents=prompts.paragraph_prompt(topics))
        return _align(_parse_json(resp.text), topics, _FALLBACK_PARAGRAPHS)
    except Exception as exc:
        print(f"  Gemini paragraph generation failed ({exc}); using local fallback content")
        return _fallback_paragraphs(topics)


def _fallback_product_caption(name: str) -> str:
    return (f"Someone just came to mind, didn't they? 💛 {name} — the kind of "
            f"little 'I'm thinking of you' gift that makes their whole day softer. "
            f"Send it here 👉")


def make_product_captions(products: list[dict]):
    """One batched Gemini call -> a persuasive caption per product (by name)."""
    if not products:
        return []
    names = [p.get("name", "") for p in products]
    if _client is None:
        return [{"caption": _fallback_product_caption(n)} for n in names]
    try:
        resp = _client.models.generate_content(
            model=config.TEXT_MODEL, contents=prompts.product_prompt(names))
        items = _parse_json(resp.text)
        if not isinstance(items, list) or len(items) < len(names):
            raise ValueError("short/invalid product caption response")
        return items[: len(names)]
    except Exception as exc:
        print(f"  Gemini product caption failed ({exc}); using local fallback")
        return [{"caption": _fallback_product_caption(n)} for n in names]


def make_reels(n: int):
    """Return a list of reel-script dicts."""
    if _client is None:
        return _fallback_reels(n)
    try:
        resp = _client.models.generate_content(
            model=config.TEXT_MODEL, contents=prompts.reels_prompt(n, config.REEL_FORMATS))
        return _parse_json(resp.text)
    except Exception as exc:
        print(f"  Gemini reel generation failed ({exc}); using local fallback content")
        return _fallback_reels(n)
