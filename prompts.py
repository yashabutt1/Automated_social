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
Each line should sound like something a real person would say, text, or think when they are tired of anxious texting, mixed signals, or being stuck in a situationship.
Use warm, conversational language, not abstract poster-speak or preachy advice.
Balance the batch so it includes some validating comfort, some honest truth, some practical next-step energy, and one lighter, slightly hopeful beat.
Ground the writing in real situations: waiting for a plan, feeling like the only one trying, being ghosted, anxious replies, moving on, asking for what you need, and rebuilding confidence.
Keep it helpful by naming a small action or mindset shift, not just the problem.
Avoid manipulation tactics, clinical claims, or the idea that your worth depends on another person's attention.

Examples:
- "If you have to convince someone to stay, you're already doing the work for a person who isn't showing up. Try spending that energy on a plan you actually want."
- "A slow reply doesn't mean you're bad news. It means they are not ready to treat you like someone they want." 
- "When your messages feel like a second job, take one evening off from checking your phone and notice how much lighter you feel."
- "You can be kind and still say no to being the fallback option. That's how you make space for someone who chooses you first."

Respond with ONLY a JSON array of objects, no markdown, no backticks:
[{{"line": "...", "caption": "one warm sentence + a soft question for the comments", "hashtags": ["...", "..."]}}]
Give 6 to 9 hashtags each, mixing broad and niche."""


def paragraph_prompt(n: int) -> str:
    """Prompt for N relationship micro-essay cards."""
    return f"""{RULES}
Write {n} original relationship micro-essay cards.
Each should be 5 to 9 short lines, with each line feeling like a real person noticing a relationship pattern and saying one small thing they can try instead.
Keep the voice warm, conversational, and grounded in everyday dating experiences: anxious texting, mixed signals, feeling unseen, situationships, being the only one trying, moving on, or finally asking for a real answer.
The batch should include a mix of relatable truth, comforting reassurance, a practical next step, and one gentle, slightly lighter beat.
Show a helpful choice instead of only the problem.
Do not use abstract words like journey, worth, authentic self, profound, or unwavering.

Examples:
- "If you're waiting for them to decide, say what you need and then do something that makes you feel steady. That is not cold. That is choosing yourself."
- "When every reply feels like a test, the kindest thing you can do is stop grading their attention and start protecting your peace."
- "A situationship with no plans is not mysterious; it's a pattern. You can ask for one clear next step and see if they can meet you there."
- "There's no shame in moving on from someone who only reaches out when they are bored. You're not giving up; you're making room."

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
