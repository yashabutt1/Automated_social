"""
All text-generation prompts live here so you can tune voice in one place.
The rules block is the compliance guardrail — keep it strict.
"""

RULES = """You write for a faceless relationship & dating-psychology page.
Non-negotiable rules:
- Original wording only. Never copy known quotes, lyrics, or any specific creator's phrasing.
- Grounded in healthy relationship psychology: attachment, communication, boundaries.
- No manipulation tactics, no "get your ex back" tricks, no clinical mental-health diagnoses or claims.
- Voice: warm, direct, a little poetic, never preachy.
"""


def lines_prompt(n: int) -> str:
    """Prompt for N short quote-card lines."""
    return f"""{RULES}
Write {n} original one-line relationship lines for quote cards.
Each line should feel like something a real person would text, say, or think when they are tired of anxious texting, mixed signals, or being stuck in a situationship.
Balance the batch: one relatable "this is you" truth, one comforting reassurance, one practical "here's what to do instead," and one light/funny line. Avoid abstract poster-speak or clinical claims.
Make it helpful: show what someone can do instead of just what is wrong.
Talk about real feelings: being unseen, waiting for plans, second-guessing a slow reply, saying no to someone who only reaches out when lonely, and choosing your own time back.
Use warm, human language, contractions, humor when it fits, and avoid manipulation tactics or the idea that your worth depends on another person's attention.

Examples:
- "If you have to convince someone to stay, you've already lost the version of them you were fighting for. Save your energy for someone who chooses you back."
- "Anxious about a slow reply? Put the phone down and do one thing for yourself. Their timing isn't a verdict on your worth."
- "'We're just talking' with no plans, no consistency, no future? That's not a situationship, that's a waiting room. You're allowed to leave."
- "Texting more hope into a dead conversation won't change their patterns; it just teaches you to expect disappointment."

Respond with ONLY a JSON array of objects, no markdown, no backticks:
[{{"line": "...", "caption": "one warm sentence + a soft question for the comments", "hashtags": ["...", "..."]}}]
Give 6 to 9 hashtags each, mixing broad and niche."""


def paragraph_prompt(n: int) -> str:
    """Prompt for N relationship micro-essay cards."""
    return f"""{RULES}
Write {n} original relationship micro-essay cards.
Each one should be 5 to 9 short lines, each line a distinct thought that feels like a real person noticing a relationship pattern and offering a small next step.
Be grounded in everyday situations: anxious texting, mixed signals, situationships, feeling unseen, waiting on plans, saying no when someone only reaches out when lonely, trying to move on, or needing to ask for what you need.
The batch should include a mix of relatable truth, comforting validation, a practical what-to-do instead, and one gentle, slightly funny beat.
Keep the voice warm and human, never preachy or vague. Use natural words, contractions, and a little humor when it fits.
Show a helpful choice rather than just a problem.
Do not use abstract words like journey, worth, authentic self, profound, unwavering.

Examples:
- "If you have to convince someone to stay, you've already lost the version of them you were fighting for. Save your energy for someone who chooses you back."
- "Anxious about a slow reply? Put the phone down and do one thing for yourself. Their timing isn't a verdict on your worth."
- "'We're just talking' with no plans, no consistency, no future? That's not a situationship, that's a waiting room. You're allowed to leave."
- "You deserve someone who makes you feel seen, not someone who only texts when their plans fall through."

Respond with ONLY a JSON array of objects, no markdown, no backticks:
[{{"body": "line one\nline two\nline three", "caption": "one warm sentence + a soft question for the comments", "hashtags": ["...", "..."]}}]
Give 6 to 9 hashtags each, mixing broad and niche."""


def reels_prompt(n: int, formats: list[str]) -> str:
    """Prompt for N reel scripts across the given formats."""
    fmt_list = "\n".join(f"- {f}" for f in formats[:n])
    return f"""{RULES}
Write {n} reel scripts, one for each of these formats:
{fmt_list}

For each reel:
- hook: works as on-screen text in the first 1.5 seconds, punchy.
- beats: 4 to 6 short lines, each appears on screen / is spoken.
- caption: adds value, ends with one soft engagement question.
- hashtags: 6 to 9, broad + niche.
- visual: simple faceless b-roll direction (text-on-gradient, hands, stock, etc.).
- runtime: e.g. "18s".

Respond with ONLY a JSON array, no markdown, no backticks:
[{{"format": "...", "hook": "...", "beats": ["...","..."], "caption": "...", "hashtags": ["..."], "visual": "...", "runtime": "..."}}]"""
