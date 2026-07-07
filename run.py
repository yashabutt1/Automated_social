"""
The Love Lens — one run makes a batch of cards + reel scripts into a dated
review folder. You open review.html, run the compliance checklist, and load the
approved ones into your scheduler (Metricool/Buffer).

    python run.py

Nothing posts automatically. That human gate is what keeps the page monetizable.
"""
import argparse
import html
import json
import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - fallback for minimal envs
    def load_dotenv() -> bool:
        return False

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

import config
import dedupe


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Generate quote-card batches and reel scripts")
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="How many review batches to generate (default: 1)",
    )
    args = parser.parse_args(argv)
    if args.count < 1:
        parser.error("--count must be at least 1")
    return args


def _day_dir(offset_days: int = 0) -> Path:
    d = config.OUTPUT_DIR / (date.today() + timedelta(days=offset_days)).isoformat()
    (d / "cards").mkdir(parents=True, exist_ok=True)
    (d / "backgrounds").mkdir(parents=True, exist_ok=True)
    return d


def build_review_html(day_dir, cards, reels):
    rows = []
    for i, c in enumerate(cards, 1):
        tags = " ".join(("#" + t.lstrip("#")) for t in c["hashtags"])
        meta = ""
        if c.get("body"):
            meta = f"<p class=\"cap\">{html.escape(c['body'])}</p>"
        else:
            meta = f"<p class=\"cap\">{html.escape(c['caption'])}</p>"
        rows.append(f"""
        <div class="card">
          <img src="cards/{c['file']}" alt="card {i}">
          <div class="meta">
            {meta}
            <p class="tags">{html.escape(tags)}</p>
            <label><input type="checkbox"> approved — original, true, sounds human</label>
          </div>
        </div>""")

    reel_blocks = []
    for i, r in enumerate(reels, 1):
        beats = "".join(f"<li>{html.escape(b)}</li>" for b in r["beats"])
        tags = " ".join(("#" + t.lstrip("#")) for t in r["hashtags"])
        reel_blocks.append(f"""
        <div class="reel">
          <h3>{html.escape(r['format'])} · {html.escape(r.get('runtime',''))}</h3>
          <p class="hook">{html.escape(r['hook'])}</p>
          <ol>{beats}</ol>
          <p class="cap">{html.escape(r['caption'])}</p>
          <p class="tags">{html.escape(tags)}</p>
          <p class="vis"><b>Visual:</b> {html.escape(r['visual'])}</p>
        </div>""")

    doc = f"""<!doctype html><meta charset="utf-8">
<title>The Love Lens — review {date.today().isoformat()}</title>
<style>
  body{{font-family:system-ui,sans-serif;background:#17131f;color:#f2ebe6;margin:0;padding:32px;max-width:1000px;margin:auto}}
  h1{{font-weight:600}} h2{{margin-top:40px;border-bottom:1px solid #3a2f47;padding-bottom:8px}}
  .card{{display:flex;gap:20px;background:#251e30;border:1px solid #3a2f47;border-radius:14px;padding:16px;margin:16px 0}}
  .card img{{width:220px;border-radius:10px}}
  .meta{{flex:1}} .cap{{font-size:15px;line-height:1.5}} .tags{{color:#b0a4dc;font-size:13px}}
  label{{display:block;margin-top:12px;color:#e6b489;font-size:14px}}
  .reel{{background:#251e30;border:1px solid #3a2f47;border-radius:14px;padding:16px;margin:16px 0}}
  .hook{{font-size:18px;font-weight:600;color:#e8a0a8}} ol{{line-height:1.6}}
  .vis{{color:#9a90a8;font-size:13px}}
  .note{{background:#2d2439;border-left:3px solid #e8a0a8;padding:12px 16px;border-radius:0 8px 8px 0;font-size:14px}}
</style>
<h1>The Love Lens — review for {date.today().isoformat()}</h1>
<p class="note">Check each: original wording? true & safe? sounds human? hook lands fast?
Approve the good ones, delete the rest, then load into your scheduler.</p>
<h2>Quote cards ({len(cards)})</h2>
{''.join(rows)}
<h2>Reel scripts ({len(reels)})</h2>
{''.join(reel_blocks)}
"""
    (day_dir / "review.html").write_text(doc, encoding="utf-8")


def generate_batch(offset_days: int = 0):
    import gen_image
    import gen_text
    import compose

    day_dir = _day_dir(offset_days)
    print(f"Generating into {day_dir}")

    used_content = dedupe.load_used_content(config.OUTPUT_DIR)

    print("· writing quote-card lines…")
    lines = gen_text.make_lines(config.CARDS_PER_RUN)
    lines = dedupe.ensure_unique_items(lines, used_content, "line", lambda: gen_text.make_lines(1)[0], attempts=6)

    print("· writing paragraph cards…")
    paragraphs = gen_text.make_paragraphs(config.PARAGRAPH_CARDS_PER_RUN)
    paragraphs = dedupe.ensure_unique_items(paragraphs, used_content, "body", lambda: gen_text.make_paragraphs(1)[0], attempts=6)

    print("· writing reel scripts…")
    reels = gen_text.make_reels(config.REELS_PER_RUN)

    cards = []
    moods = random.sample(config.BACKGROUND_MOODS, min(len(lines) + len(paragraphs), len(config.BACKGROUND_MOODS)))
    for i, item in enumerate(lines, 1):
        mood = moods[(i - 1) % len(moods)]
        print(f"· quote card {i}/{len(lines)} — background…")
        bg = gen_image.make_background(mood, day_dir / "backgrounds" / f"bg_{i}.png")
        card_file = f"card_{i}.png"
        print("  composing text…")
        compose.make_card(bg, item["line"], day_dir / "cards" / card_file)
        cards.append({**item, "file": card_file})

    for i, item in enumerate(paragraphs, 1):
        mood = moods[(len(lines) + i - 1) % len(moods)]
        print(f"· paragraph card {i}/{len(paragraphs)} — background…")
        bg = gen_image.make_background(mood, day_dir / "backgrounds" / f"para_{i}.png")
        card_file = f"paragraph_{i}.png"
        print("  composing paragraph…")
        compose.make_paragraph_card(item["body"], day_dir / "cards" / card_file)
        cards.append({**item, "file": card_file, "body": item["body"]})

    (day_dir / "captions.json").write_text(
        json.dumps({"cards": cards, "reels": reels}, indent=2), encoding="utf-8")
    build_review_html(day_dir, cards, reels)

    return day_dir


def main(argv=None):
    args = parse_args(argv)
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    generated_dirs = []
    for offset in range(args.count):
        generated_dirs.append(generate_batch(offset))

    print("\nCompleted batches:")
    for path in generated_dirs:
        print(f"- {path / 'review.html'}")


if __name__ == "__main__":
    main(sys.argv[1:])
