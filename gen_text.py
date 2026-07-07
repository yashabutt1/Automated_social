"""Text generation for The Love Lens.

The pipeline prefers Gemini for copy, but it can fall back to local templates
when the API is unavailable or quota-limited so the review workflow still runs.
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


def _fallback_lines(n: int):
    templates = [
        {
            "line": "If you're waiting on a plan, remember busy is not the same as choosing you.",
            "caption": "Not every late response deserves a second guess. Sometimes it just means they are not ready to show up.",
            "hashtags": ["datingadvice", "boundaries", "mixedsignals", "situationships", "selfrespect", "communication"],
        },
        {
            "line": "When your inbox feels like homework, it is okay to close it and do something that feels good.",
            "caption": "A calm step away from the phone can be the easiest way to stop making someone else's attention your mood.",
            "hashtags": ["anxiety", "selfcare", "texting", "mentalhealth", "selflove", "boundarysetting"],
        },
        {
            "line": "You can care about someone and still say no to being their fallback plan.",
            "caption": "Being kind does not mean accepting a seat at the back of their priorities.",
            "hashtags": ["selfworth", "boundaries", "datingtruth", "relationships", "movingon", "healthyrelationships"],
        },
        {
            "line": "Mixed signals are still a signal — they just happen to be the wrong one.",
            "caption": "Pay attention to patterns, not excuses. That is the easiest way to protect yourself from the same ache again.",
            "hashtags": ["mixedsignals", "datingadvice", "selfrespect", "redflags", "communication", "love"],
        },
        {
            "line": "If every message feels like a test, stop studying and start living your own life.",
            "caption": "A little distance can show you whether someone is actually missing you or just missing a moment of boredom.",
            "hashtags": ["texting", "selfcare", "confidence", "datingadvice", "healthyrelationships", "space"],
        },
        {
            "line": "Someone who checks in only when they are lonely is not asking for you — they are asking for company.",
            "caption": "You deserve someone who wants to share their day with you, not someone who only remembers you in a pinch.",
            "hashtags": ["situationships", "ghosting", "selfworth", "datingtruth", "boundaries", "relationships"],
        },
        {
            "line": "A gentle answer can end a hard day better than a dramatic fight.",
            "caption": "Choose words that make you feel steady, not words that keep you second-guessing yourself.",
            "hashtags": ["communication", "relationshiphealth", "kindness", "softlife", "datingadvice", "relatable"],
        },
        {
            "line": "It is okay to want clarity instead of staying in a loop of maybe.",
            "caption": "Ask for one clear next step and let their answer tell you if you should stay or go.",
            "hashtags": ["clarity", "boundaries", "datingadvice", "communication", "selfrespect", "movingon"],
        },
        {
            "line": "When you feel like the only one trying, that feeling is a very good signal.",
            "caption": "Recognize the imbalance and give yourself permission to stop being the only person carrying the conversation.",
            "hashtags": ["relationshipadvice", "selfcare", "boundaries", "communication", "datingtruth", "confidence"],
        },
        {
            "line": "You can still be hopeful about love while being honest about how it's treating you today.",
            "caption": "The best choice is not perfect love. It's the one that feels safe enough to show up for.",
            "hashtags": ["hope", "healthyrelationships", "datingadvice", "selfrespect", "love", "boundaries"],
        },
        {
            "line": "A text that makes you anxious is not a sign of passion. It's a sign to protect your time.",
            "caption": "You are allowed to stop chasing the feeling and start choosing someone who makes you feel calmer.",
            "hashtags": ["anxiety", "texting", "selfcare", "boundaries", "datingtruth", "communication"],
        },
        {
            "line": "You do not need to explain your needs to someone who does not make space for them.",
            "caption": "Sometimes the kindest thing you can do is ask for what you need and then notice if they can meet you there.",
            "hashtags": ["needs", "boundaries", "communication", "selfworth", "relationshipadvice", "dating"],
        },
        {
            "line": "Moving on isn't giving up, it's making room for the person who actually wants to be in your life.",
            "caption": "A small step away from the wrong person can feel a lot better than staying in the same uncomfortable place.",
            "hashtags": ["movingon", "selfcare", "datingtruth", "growth", "healthyrelationships", "confidence"],
        },
    ]
    shuffled = templates[:]
    random.shuffle(shuffled)
    return shuffled[:n]


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

def _fallback_paragraphs(n: int):
    templates = [
        {
            "body": "If every message feels like a test, you're allowed to stop answering and start doing something that feels good.",
            "caption": "A little space from the phone can help you see whether they are actually missing you or just missing a moment of boredom.",
            "hashtags": ["anxiety", "texting", "selfcare", "communication", "datingadvice", "boundaries"],
        },
        {
            "body": "You're not wrong for wanting a plan. If someone only reaches out when they are lonely, they are choosing company, not you.",
            "caption": "You deserve someone who checks in because they want you, not because they have no other plans.",
            "hashtags": ["situationships", "ghosting", "selfworth", "datingtruth", "boundaries", "movingon"],
        },
        {
            "body": "It is okay to ask for one clear next step instead of staying in a loop of maybe.",
            "caption": "Asking for clarity is not pressure. It's the only way to know if this is something worth your time.",
            "hashtags": ["clarity", "communication", "boundaries", "relationshipadvice", "dating", "selfrespect"],
        },
        {
            "body": "A kind answer can be stronger than a dramatic argument. It shows you can stay calm even when the situation is messy.",
            "caption": "You can still be gentle while also protecting your own peace.",
            "hashtags": ["communication", "kindness", "relationshiphealth", "maturity", "selfcare", "datingadvice"],
        },
        {
            "body": "If you feel like the only one trying, that feeling is a very good signal. It's okay to stop making all the plans and let them meet you halfway.",
            "caption": "Balanced effort is the most honest way to tell whether someone is actually in this with you.",
            "hashtags": ["balance", "boundaries", "relationships", "datingadvice", "selfcare", "confidence"],
        },
        {
            "body": "Moving on from someone who only texts when it's convenient isn't a loss. It's a choice to keep the people who actually want to be there.",
            "caption": "Sometimes the kindest thing you can do for yourself is clear a little space.",
            "hashtags": ["movingon", "selfworth", "growth", "datingtruth", "boundaries", "selfcare"],
        },
        {
            "body": "Anxious texting doesn't make their feelings clearer. It just makes you feel smaller and keeps you waiting for a message you can't control.",
            "caption": "Try one clear message, then do one thing that makes you feel grounded.",
            "hashtags": ["anxiety", "texting", "selfcare", "boundaries", "datingadvice", "mentalwellness"],
        },
        {
            "body": "You can care about someone and still stop playing games with your own time.",
            "caption": "The healthiest thing you can do is treat your schedule like something you deserve to protect.",
            "hashtags": ["selfrespect", "boundaries", "dating", "communication", "relationships", "selfcare"],
        },
        {
            "body": "Not every late reply is a sign of drama. But if it makes you feel anxious every time, that's a signal you need to take back.",
            "caption": "Your peace is worth more than a message that only shows up on someone else's terms.",
            "hashtags": ["anxioustexting", "peace", "selfcare", "boundaries", "datingadvice", "confidence"],
        },
    ]
    shuffled = templates[:]
    random.shuffle(shuffled)
    return shuffled[:n]

def _generate(prompt: str, fallback_factory):
    if _client is None:
        if fallback_factory.__name__ == "_fallback_lines":
            return _fallback_lines(config.CARDS_PER_RUN)
        return _fallback_reels(config.REELS_PER_RUN)
    try:
        resp = _client.models.generate_content(model=config.TEXT_MODEL, contents=prompt)
        return _parse_json(resp.text)
    except Exception as exc:
        print(f"  Gemini text generation failed ({exc}); using local fallback content")
        return fallback_factory(config.CARDS_PER_RUN if fallback_factory.__name__ == "_fallback_lines" else config.REELS_PER_RUN)


def make_lines(n: int):
    """Return a list of {line, caption, hashtags} dicts."""
    return _generate(prompts.lines_prompt(n), _fallback_lines)


def make_paragraphs(n: int):
    """Return a list of {body, caption, hashtags} dicts."""
    if _client is None:
        return _fallback_paragraphs(n)

    try:
        resp = _client.models.generate_content(model=config.TEXT_MODEL, contents=prompts.paragraph_prompt(n))
        return _parse_json(resp.text)
    except Exception as exc:
        print(f"  Gemini paragraph generation failed ({exc}); using local fallback content")
        return _fallback_paragraphs(n)


def make_reels(n: int):
    """Return a list of reel-script dicts."""
    return _generate(prompts.reels_prompt(n, config.REEL_FORMATS), _fallback_reels)
