"""
All text-generation prompts live here so you can tune voice in one place.
The rules block is the compliance guardrail — keep it strict.

Every prompt is now built around a single *topic* (see topics.py) so each card
covers different ground instead of circling the same subject every run.
"""

RULES = """You write for a warm, faceless love & relationships page.
Non-negotiable rules:
- Original wording only. Never copy known quotes, lyrics, or any specific creator's phrasing.
- Grounded in healthy relationship psychology: connection, communication, care, self-respect.
- No manipulation tactics, no "get your ex back" tricks, no clinical mental-health diagnoses or claims.
- Voice: warm, human, a little poetic, never preachy, never abstract poster-speak.
"""


def _topics_block(topics: list[dict]) -> str:
    lines = ["THE TOPICS FOR THIS BATCH — write exactly one item for EACH, in this",
             "same order, and keep each item strictly about its own topic:"]
    for i, t in enumerate(topics, 1):
        lines.append(f"{i}. Focus: {t['angle']}  |  Tone: {t['tone']}")
    lines.append('Do NOT default to "anxious texting", "mixed signals", or '
                 '"situationships" unless a focus above literally says so.')
    return "\n".join(lines)


def _title_rule() -> str:
    return ('Each item also needs a "title": a 1-3 word evocative phrase (Title Case) '
            'that will be set in an elegant script font at the top of the card, like '
            '"Soft Love" or "Come Home" or "Chosen". No punctuation in the title.')


def lines_prompt(topics: list[dict]) -> str:
    """Prompt for one short quote-card line per topic (single batched call)."""
    n = len(topics)
    return f"""{RULES}
{_topics_block(topics)}

Write exactly {n} original one-line quote-card lines — one for each topic above, in order.
Each line should sound like something a real person would genuinely say, text, or
think in that exact feeling — warm and conversational, not abstract advice.
Vary the rhythm so the lines don't sound formulaic. Where it fits, name a small
action, image, or mindset shift instead of only describing the feeling.

{_title_rule()}

Respond with ONLY a JSON array of exactly {n} objects, in the same order as the topics,
no markdown, no backticks:
[{{"title": "...", "line": "...", "caption": "one warm sentence + a soft question for the comments", "hashtags": ["...", "..."]}}]
Give 6 to 9 hashtags each, mixing broad and niche, relevant to that item's topic."""


def paragraph_prompt(topics: list[dict]) -> str:
    """Prompt for one micro-essay card per topic (single batched call)."""
    n = len(topics)
    return f"""{RULES}
{_topics_block(topics)}

Write exactly {n} original micro-essay cards — one for each topic above, in order.
Each should be 5 to 8 short lines. Each line feels like a real person noticing
something true about that specific feeling and, where natural, offering one small,
gentle thing to try or hold onto.
Keep the voice warm, human, and specific to each topic. Do not use abstract words
like journey, worth, authentic self, profound, or unwavering. Match each item's tone
rather than turning every card into a hard truth.

{_title_rule()}

Respond with ONLY a JSON array of exactly {n} objects, in the same order as the topics,
no markdown, no backticks:
[{{"title": "...", "body": "line one\\nline two\\nline three", "caption": "one warm sentence + a soft question for the comments", "hashtags": ["...", "..."]}}]
Give 6 to 9 hashtags each, mixing broad and niche, relevant to that item's topic."""


def product_prompt(names: list[str]) -> str:
    """Persuasive gift-angle captions for a list of Amazon products."""
    n = len(names)
    listing = "\n".join(f"{i}. {name}" for i, name in enumerate(names, 1))
    return f"""You write short, warm, irresistible product captions for a love &
relationships page whose audience buys thoughtful gifts for the people they love.

Products (write exactly one caption for EACH, in this order):
{listing}

For each caption:
- Open with a warm, relatable hook, then make the reader picture gifting it to
  someone they care about (partner, friend, mom, someone going through a hard time).
- Make it tempting and emotional so they want to buy it right now — but do NOT
  invent specific specs, prices, claims, or reviews you weren't given. Stay true
  to the product name/angle provided.
- 2-4 short sentences. Warm, human, a little playful. Use 1-3 tasteful emojis.
- End with a soft nudge to tap the link (e.g. "Send it here 👉" / "Grab it here 👉").
- Do NOT include the URL or hashtags in the caption text.

Respond with ONLY a JSON array of exactly {n} objects, in order, no markdown:
[{{"caption": "..."}}]"""


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
