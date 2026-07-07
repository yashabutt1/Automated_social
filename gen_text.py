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
            "line": "Silence can say more than a fight.",
            "caption": "A calm pause can protect a relationship better than a rushed reaction.",
            "hashtags": ["relationshipwisdom", "emotionalintelligence", "healthyboundaries"],
        },
        {
            "line": "The right love feels steady, not intense.",
            "caption": "Real connection grows through calm consistency, not constant chaos.",
            "hashtags": ["datingadvice", "healthyrelationships", "selfworth"],
        },
        {
            "line": "Trust is built in the small moments.",
            "caption": "Small acts of reliability create the safety that lasting love needs.",
            "hashtags": ["trust", "relationshiptips", "emotionalsecurity"],
        },
        {
            "line": "You do not need to chase what stays.",
            "caption": "Some love feels easy because it is grounded in peace, not pressure.",
            "hashtags": ["loveadvice", "healing", "selfrespect"],
        },
        {
            "line": "A soft answer can end a hard day.",
            "caption": "Gentle words often do more healing than sharp ones ever could.",
            "hashtags": ["communication", "relationshiphealth", "softlife"],
        },
        {
            "line": "Not every late reply deserves a second chance.",
            "caption": "A little clarity can save a lot of emotional energy.",
            "hashtags": ["datingtruth", "boundaries", "selfrespect"],
        },
        {
            "line": "Mixed signals are still a signal.",
            "caption": "When someone keeps you guessing, your nervous system will notice before your heart does.",
            "hashtags": ["mixedsignals", "attachment", "datingadvice"],
        },
        {
            "line": "If you are waiting for plans that never arrive, stop making excuses for someone else's availability.",
            "caption": "You deserve someone who makes time for you without a second reminder.",
            "hashtags": ["situationships", "selfworth", "datingadvice"],
        },
        {
            "line": "Anxious texting won’t make their feelings clearer; it only makes you feel smaller.",
            "caption": "Send one message, then do something that makes you feel good regardless of their reply.",
            "hashtags": ["anxiety", "selfcare", "texting"],
        },
        {
            "line": "If every conversation is up to you, it's not a partnership — it's a job.",
            "caption": "You can ask for balance without apologizing for wanting it.",
            "hashtags": ["boundaries", "communication", "relationshiphealth"],
        },
        {
            "line": "You can be kind and still say no to being the fallback option.",
            "caption": "Healthy love is not your second choice dressed in good intentions.",
            "hashtags": ["selfrespect", "redflags", "datingtruth"],
        },
        {
            "line": "A slow reply isn't always a sign of disinterest — but if it makes you feel terrible, that's also valid.",
            "caption": "Take back your power by doing one thing that makes you feel steady tonight.",
            "hashtags": ["anxioustexting", "selfworth", "datingadvice"],
        },
        {
            "line": "People who ghost you don't owe you an explanation — they owe you less of your time.",
            "caption": "The sooner you stop rewinding the story, the sooner you can start the next chapter.",
            "hashtags": ["ghosting", "movingon", "selfcare"],
        },
        {
            "line": "It is okay to want clarity instead of a constant game of maybe.",
            "caption": "Ask for what you need and treat their answer as useful information, not a personal failure.",
            "hashtags": ["clarity", "communication", "relationships"],
        },
        {
            "line": "A real connection doesn't leave you guessing about whether you matter.",
            "caption": "If someone is inconsistent, your response can be consistency with yourself.",
            "hashtags": ["consistency", "selfworth", "dating"],
        },
        {
            "line": "You are allowed to stop using your energy to solve someone else's relationship habits.",
            "caption": "Healthy boundaries are the kindest thing you can give yourself and the people around you.",
            "hashtags": ["boundaries", "healing", "selfcare"],
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
            "hashtags": ["relationshiptips", "datingadvice", "greenflags"],
            "visual": "Text on a soft gradient with calm b-roll",
            "runtime": "18s",
        }
        for _ in range(n)
    ]

def _fallback_paragraphs(n: int):
    templates = [
        {
            "body": "I keep telling myself I'm over it.\nThen I see the same old pattern and feel that old ache again.\nIt's not dramatic.\nIt's just exhausting.\nSome people leave you with a habit of checking your phone.",
            "caption": "A little honesty can be easier to share than a perfect caption.",
            "hashtags": ["relationshiptruth", "healing", "datingreality"],
        },
        {
            "body": "I used to think I was overthinking it.\nThen I realized I was just reading the room and not liking what I saw.\nThe problem wasn't my imagination.\nIt was the fact that the effort was one-sided.\nSome people make you feel crazy for noticing the pattern.",
            "caption": "Sometimes the most honest thing is noticing the pattern before it gets louder.",
            "hashtags": ["overthinking", "selfrespect", "datingreality"],
        },
        {
            "body": "It's funny how someone can be absent for weeks\nand still make your whole day feel weird.\nYou keep telling yourself it's not a big deal.\nThen you notice you are waiting for a text that never comes.\nThat is not romance. That is a habit.",
            "caption": "A little humor can make a hard truth land better.",
            "hashtags": ["ghosting", "datinghumor", "attachment"],
        },
        {
            "body": "If every plan you make is tentative, that's not flexibility — that's inconsistency asking for your patience.\nYou can still be kind while asking for a little more effort.\nHealthy communication isn't demanding; it's saying what you need and giving them space to respond.\nThat is the kind of conversation that makes relationships feel safer.\nYou deserve to know if you're a priority or an option.",
            "caption": "Being honest about your needs is not dramatic — it's the first step to feeling less anxious.",
            "hashtags": ["communication", "boundaries", "situationships"],
        },
        {
            "body": "Anxious texting happens when you put too much power in the reply.\nTry one clear message, then do one activity that makes you feel grounded.\nYour worth doesn't change while you wait.\nSomeone else's timing is not a grade on your character.\nThat is how you keep your energy from getting stuck in their inbox.",
            "caption": "A calm response to anxious texting is choosing your own well-being first.",
            "hashtags": ["anxiety", "selfcare", "texting"],
        },
        {
            "body": "You can care about someone and still walk away from the parts that hurt you.\nKindness doesn't mean staying in confusion.\nIf they keep avoiding plans and explanations, they're asking you to guess your own future.\nThat is not love.\nIt's okay to choose someone who gives you space, clarity, and respect.",
            "caption": "You don't have to explain your boundaries to people who already don't respect them.",
            "hashtags": ["selfworth", "boundaries", "movingon"],
        },
        {
            "body": "When a relationship feels more like chasing than receiving, it is time to stop making the next move for them.\nA healthy connection is about both people showing up.\nIf you're always the one starting the conversation, you're not building trust — you're building exhaustion.\nLet your next message be to yourself instead of to someone who isn't matching you.\nThat is how you make room for something more real.",
            "caption": "You can choose the person who makes you feel secure, not the one who keeps you guessing.",
            "hashtags": ["authenticity", "datingadvice", "relationships"],
        },
        {
            "body": "A healthy relationship doesn't ask you to shrink your dreams.\nIf you keep editing who you are to fit someone else's mood, you're slowly losing sight of what feels right.\nLoving yourself enough to stay true is the best way to tell someone else how to treat you.\nThat is not selfish.\nThat is self-respect.",
            "caption": "Your dreams are not negotiable just because someone else is inconsistent.",
            "hashtags": ["selfrespect", "growth", "healthyrelationships"],
        },
        {
            "body": "A good connection should make you feel safer, not more unsure of yourself.\nIf you are constantly wondering when they will show up, you are in a relationship with uncertainty.\nYou can still be kind while choosing people who make you feel steady.\nThat is how you build trust with someone, rather than with your own hope.",
            "caption": "Steady love makes you feel safe, not second-guessed.",
            "hashtags": ["trust", "security", "boundaries"],
        },
        {
            "body": "Sometimes the most loving thing you can do is stop trying to fix how someone else behaves.\nTheir habits are not your responsibility.\nYou can create distance with care, and let your own life become the safer space you deserve.\nThat is still a kind choice, even if it feels hard.",
            "caption": "You are allowed to protect your heart without being cold.",
            "hashtags": ["boundaries", "healing", "selfcare"],
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
