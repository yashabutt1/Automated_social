"""
All text-generation prompts live here so you can tune voice in one place.
The rules block is the compliance guardrail — keep it strict.

Every prompt is now built around a single *topic* (see topics.py) so each card
covers different ground instead of circling the same subject every run.
"""

import config

RULES = f"""You write for a warm, faceless love & relationships page.

AUDIENCE: {config.AUDIENCE}

Non-negotiable rules:
- Original wording only. Never copy known quotes, lyrics, or any specific creator's phrasing.
- Grounded in healthy relationship psychology: connection, communication, care, self-respect.
- No manipulation tactics, no "get your ex back" tricks, no clinical mental-health diagnoses or claims.
- Voice: warm, human, a little poetic, never preachy, never abstract poster-speak.

MAKE IT SHAREABLE (very important — this is how the page grows):
- Lead with POSITIVITY, hope, warmth, and happiness. This audience shares what
  uplifts them, not what stings.
- Give real VALUE in every post: a gentle insight, a small practical solution or
  habit to try, or an uplifting reframe — not just a pretty sentence.
- Be SOLUTION-ORIENTED: name the good feeling or the small thing that helps, more
  than the problem.
- End on a warm, hopeful, or empowering note that makes the reader want to SHARE
  it to her own timeline or send it to someone she loves.
- Aim for the "yes, exactly — I'm sharing this" reaction.
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


def engagement_prompt(n: int, formats: list[str]) -> str:
    """Interactive posts designed to pull comments."""
    fmt_list = "\n".join(f"- {f}" for f in formats)
    return f"""{RULES}
Write {n} highly engaging, comment-baiting posts for a love & relationships page.
The whole point is to make people STOP and reply. Rotate across these formats
(use a different one for each of the {n} items):
{fmt_list}

For each post:
- "prompt": the short, punchy text that goes ON the card (max ~14 words for
  questions; for a fun-fact use 1-2 short sentences with the surprising fact).
  Make it irresistible to answer or react to. No hashtags on the card.
- "title": a 1-3 word script-font header, e.g. "Your Turn", "Tell Me",
  "Real Talk", "Did You Know", "This or That", "Finish This".
- "caption": the Facebook caption — restate/expand the hook and EXPLICITLY invite
  a comment (e.g. "👇 Drop your answer below — I read every one."). Warm, human.
- "hashtags": 6-9, broad + niche.

Fun-fact items must be TRUE and about love/attraction/relationships psychology or
history — no made-up statistics. If unsure, choose a safe, well-known fact.

Respond with ONLY a JSON array of exactly {n} objects, no markdown:
[{{"title":"...","prompt":"...","caption":"...","hashtags":["...","..."]}}]"""


def product_prompt(names: list[str]) -> str:
    """Persuasive gift-angle captions for a list of Amazon products."""
    n = len(names)
    listing = "\n".join(f"{i}. {name}" for i, name in enumerate(names, 1))
    return f"""You write short, warm, irresistible product captions for a love &
relationships page whose audience buys thoughtful gifts for the people they love.

AUDIENCE: {config.AUDIENCE}
Frame gifts for how THIS audience gives: to a spouse of many years, an adult
child, a grandchild, a dear friend, or to treat herself.

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
