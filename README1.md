# The Love Lens — content pipeline

Generates a daily batch of **quote cards** (original line over an AI-generated
background) and **reel scripts**, drops them in a dated review folder, and waits
for you to approve before anything is posted.

One `GEMINI_API_KEY` powers everything: Gemini writes the copy, Nano Banana draws
the backgrounds.

```
run.py         orchestrates a full batch  ->  output/<date>/review.html
config.py      branding, models, sizes, how many per run, background moods
prompts.py     the copy prompts (voice + compliance rules)
gen_text.py    Gemini: lines + reel scripts
gen_image.py   Nano Banana: backgrounds
compose.py     Pillow: text-on-photo card
```

## Setup (once)

1. Install Python 3.10+ and the deps:
   ```
   pip install -r requirements.txt
   ```
2. Get a key at https://aistudio.google.com, then:
   ```
   cp .env.example .env      # then paste your key into .env
   ```
3. Add the brand font (optional but recommended) — see `fonts/README.txt`.

## Run it

```
python run.py
```

You'll get `output/<today>/review.html`. Open it, run the checklist, approve the
good ones, then load the approved cards + captions into your scheduler.

Tune volume, sizes, and moods in `config.py` (`CARDS_PER_RUN`, `REELS_PER_RUN`,
`CARD_W/H`, `BACKGROUND_MOODS`).

## Posting — the simplest reliable path

This pipeline **does not post for you**, on purpose. Unattended auto-posting is
exactly the pattern Meta's originality rules penalize, and direct Facebook API
posting needs a Meta developer app + review.

Instead:
1. Connect The Love Lens Page (+ Instagram + TikTok) to a scheduler —
   **Metricool** has a free tier and posts to all three.
2. Each run, open `review.html`, approve, and upload the approved cards.
   Paste the caption from `captions.json`.
3. The scheduler drips them out daily. That's your "hands-off" — with a 5-minute
   human gate in the middle.

Upgrade to direct Facebook API posting only once the manual loop feels slow.

## The compliance gate (do not skip)

For every post, before it goes live:
- Original wording — not a reworded version of someone's post.
- True and safe — no manipulation advice, no clinical claims.
- Sounds human — read it aloud; if it sounds like a bot, regenerate.
- Hook lands in ~1.5s.
- **Label AI images** where Meta asks — the backgrounds are AI-generated and
  carry Google's SynthID watermark. Use Meta's "AI info" toggle when posting
  photorealistic ones.

## Ideas for your Claude Code agent

Open this folder in VS Code and ask the agent to:
- "Add a `--count` flag to `run.py` so I can make a whole week at once."
- "Add a second card size (1080x1080 square) alongside the 4:5."
- "Write a `dedupe.py` that checks new lines against past `captions.json` files
  so I never repeat a line."
- "Add a Metricool CSV export so I can bulk-upload the approved captions."
- "Add simple logging + a cost counter for image generations."

Keep the human approval step no matter what you automate.
