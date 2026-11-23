"""
All text-generation prompts live here so you can tune voice in one place.
The rules block is the compliance guardrail — keep it strict.

Every prompt is now built around a single *topic* (see topics.py) so each card
covers different ground instead of circling the same subject every run.
"""

import config

RULES = f"""You write for a relatable, faceless love & relationships page for ALL ages.

AUDIENCE: {config.AUDIENCE}

Non-negotiable rules:
- Original wording only. Never copy known quotes, lyrics, or any specific creator's phrasing.
- Grounded in healthy relationship psychology: connection, communication, care, self-respect.
- No manipulation tactics, no "get your ex back" tricks, no clinical mental-health diagnoses or claims.
- Sound like a real person talking, never a greeting card. No poster-speak, no "may you find…", no preaching.

MAKE IT SHAREABLE — this is the whole game, read carefully:
- BE SPECIFIC AND TRUE-TO-LIFE. Name a concrete moment, habit, text, or feeling people recognize
  instantly ("the way they steal your fries after saying they're not hungry", "falling asleep
  mid-argument and waking up still holding hands", "that 3 a.m. 'you up?' from the one person you
  shouldn't text"). Specific = relatable = SHARED. Generic affirmations ("love is patient", "you
  deserve the world") get scrolled past — never write those.
- VARY THE TONE across posts so the feed feels human: some warm and tender, some genuinely FUNNY
  and real, some honest and a little raw. Do NOT make every post a soft uplift.
- Hit one of three share-triggers in each post: "this is SO us/me" (relatable), "I'm sending this
  to them" (tag-worthy), or "finally, someone said it" (validating a real feeling).
- The reaction you want is "omg this is literally us 😭" — not "aw, that's nice."
"""


def _topics_block(topics: list[dict]) -> str:
    lines = ["THE TOPICS FOR THIS BATCH — write exactly one item for EACH, in this",
             "same order, and keep each item strictly about its own topic:"]
    for i, t in enumerate(topics, 1):
        lines.append(f"{i}. Focus: {t['angle']}  |  Tone: {t['tone']}")
    lines.append("Nail each topic's OWN tone and make it specific and relatable — if the tone "
                 "is funny, actually be funny; if it's raw, be honest. Don't flatten them all into soft warmth.")
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


def grounded_prompt(articles: list[dict]) -> str:
    """Turn REAL relationship articles into original, MEANINGFUL posts (not quotes)."""
    n = len(articles)
    blocks = "\n".join(
        f'{i+1}. ARTICLE: "{a["title"]}" — {(a.get("summary") or "")[:300]} (via {a["source"]})'
        for i, a in enumerate(articles))
    return f"""{RULES}

You are turning REAL relationship articles into original, GENUINELY USEFUL posts — the
kind that actually helps or makes someone feel deeply seen, NOT a vague quote. For each
article, write a post that captures its real insight or advice IN YOUR OWN WORDS: a
specific, true takeaway the reader can use or recognize. Be concrete (name the behaviour,
the feeling, the small shift). Do NOT copy the article's phrasing, do NOT invent studies
or statistics, and stay accurate to the article's actual point. Match a real, grounded
voice — honest and warm, not greeting-card.

ARTICLES (write one post for EACH, in order):
{blocks}

{_title_rule()}

Respond with ONLY a JSON array of exactly {n} objects, same order, no markdown:
[{{"title": "1-3 word phrase", "body": "4-6 short sentences delivering the real insight/advice, specific and honest, ending with a reflective question for the comments", "caption": "one line + a soft question for the comments", "hashtags": ["5 to 8 relevant tags"]}}]"""


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


def reflection_prompt(quote: str, author: str) -> str:
    """A long-form, warm reflection essay woven around a real famous quote —
    the shareable 'Thoughts That Linger' style."""
    return f"""{RULES}

Write ONE long, warm, reflective Facebook post (a mini-essay) built around this
REAL quote. Do NOT change the quote's wording and do NOT invent a different
author — use it exactly and attribute it exactly as given:

QUOTE: "{quote}"
AUTHOR: {author}

Structure (follow it loosely, keep it human):
- Open with a relatable question that draws the reader in ("Have you ever...").
- Lead naturally into the quote and attribute it to {author}.
- Reflect on it in short, easy paragraphs (1-2 sentences each, blank line between)
  — warm, first-person, gently wise, deeply POSITIVE and uplifting.
- Build toward a hopeful, heart-tugging message about love, family, memories,
  gratitude, or being present.
- End with a short run of uplifting takeaways (e.g. "To linger a little longer.
  To laugh a little louder.") and a line that makes the reader want to SHARE it.
- 180-320 words. No hashtags inside the essay.

Also give a short 1-3 word script title for the image card, and 6-9 hashtags.

Respond with ONLY a JSON object, no markdown:
{{"title": "...", "essay": "...", "hashtags": ["...", "..."]}}"""


def engagement_prompt(n: int) -> str:
    """FUN, interactive 'tap / answer / tag' posts — quizzes, games, fun facts."""
    return f"""{RULES}

Write {n} FUN, interactive love & relationship posts for a faceless page — the
kind people can't help but tap, answer, or tag someone in. Playful, modern,
specific, genuinely entertaining — NOT soft affirmations and NOT quotes.

Rotate the FORMAT across the {n} items (use a DIFFERENT one for each):
- "this_or_that": two concrete, relatable options to pick between
  (e.g. "Big spontaneous trip" vs "Cozy weekend in"). Everyday and a little cheeky.
- "would_you_rather": two tempting or funny relationship dilemmas
  (e.g. "Always know what they're thinking" vs "Never argue again").
- "quiz": one playful question + 2-4 short answer options people choose from
  (e.g. "What's your love language, really?").
- "fun_fact": ONE surprising, TRUE, uplifting fact about love, attraction, or the
  science of connection. No made-up statistics — if unsure, use a safe, known fact.
- "finish_sentence": a relatable sentence stem people complete in the comments
  (e.g. "I knew it was real when ______").

For each item return:
- "format": this_or_that | would_you_rather | quiz | fun_fact | finish_sentence
- "header": a 2-3 word card label in Title Case (e.g. "This or That",
  "Would You Rather", "Quick Quiz", "Did You Know?", "Finish This").
- "prompt": the MAIN line that goes on the card — the question, the fact, or the
  sentence stem. Punchy, max ~16 words. For this_or_that / would_you_rather this can
  be a short teaser or empty; the options carry it.
- "options": for this_or_that & would_you_rather EXACTLY 2 short options (max ~6
  words each); for quiz 2-4 short options; for fun_fact & finish_sentence an empty [].
- "caption": a warm, human Facebook caption that restates the hook and EXPLICITLY
  invites a comment or tag (e.g. "👇 Pick one and tell me why"). 1-2 sentences.
- "hashtags": 6-9, broad + niche.

Respond with ONLY a JSON array of exactly {n} objects, no markdown:
[{{"format":"...","header":"...","prompt":"...","options":["...","..."],"caption":"...","hashtags":["...","..."]}}]"""


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
