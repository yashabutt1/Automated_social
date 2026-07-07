# AGENT_TASKS — take The Love Lens pipeline live

Execute these phases **in order**. Run the pipeline between phases; do not batch
multiple changes before testing, because Phase 1 onward spends real Gemini API
credits. After each phase, report what you changed and the command output.

**Hard rule that must survive every change:** nothing posts automatically. The
pipeline's only job is to produce a dated review folder + `review.html`. The
human approval step stays. Do not add any code that publishes to Facebook,
Instagram, or TikTok directly.

---

## Phase 0 — Pre-flight (no API calls yet)

1. Confirm environment loading reads the **real** key file, not the template.
   Search the repo for `load_dotenv` and `.env.example`. It must load `.env`
   (the private file), never `.env.example` (the committed placeholder). Fix if
   wrong. If `load_dotenv()` is missing entirely, add it at the top of `run.py`
   before any Gemini client is created.
2. Confirm `python-dotenv`, `google-genai`, and `pillow` are installed:
   `pip install -r requirements.txt`
3. Print the installed SDK version so we know what we're targeting:
   `python -c "import google.genai, PIL; print(google.genai.__version__, PIL.__version__)"`

**Acceptance:** key loads from `.env`; versions print without error.

---

## Phase 1 — First real smoke test (cheap)

1. In `config.py` temporarily set `CARDS_PER_RUN = 2` and `REELS_PER_RUN = 1`
   so the first live run is inexpensive.
2. Run: `python run.py`
3. Open `output/<today>/review.html` and confirm: 2 cards rendered with the line
   visible and legible, captions present, 1 reel script present.

**Most likely failure points — check these first if it errors:**
- **Text parsing:** `gen_text.py` expects a JSON array back. If the model wraps
  it in prose or markdown, tighten the prompt in `prompts.py` ("Respond with ONLY
  a JSON array, no other text") and keep the fence-stripping in `_parse_json`.
- **Image response shape:** `gen_image.py` reads
  `resp.candidates[0].content.parts[*].inline_data.data`. If the installed SDK
  differs, inspect one raw response (`print(resp)`) and adjust the extraction to
  match. The image bytes may be under `inline_data.data` (base64 or raw bytes) —
  handle both: try raw bytes first, fall back to `base64.b64decode`.
- **Model names:** if a 404/invalid-model error appears, list available models
  (`for m in client.models.list(): print(m.name)`) and update `TEXT_MODEL` /
  `IMAGE_MODEL` in `config.py` to a currently valid name.

**Acceptance:** `review.html` opens with 2 real cards + 1 reel, no traceback.

---

## Phase 2 — Quality pass on the cards

1. **Fonts:** if `fonts/Fraunces-SemiBold.ttf` is absent the card uses PIL's
   default and looks plain. Note this in the run output so the user knows to add
   the font. Do not fail the run over a missing font.
2. **Text wrapping:** test with a deliberately long line (18+ words). Confirm
   `compose.py` shrinks the font and wraps without overflowing the canvas or
   colliding with the handle at the bottom. Fix the fit loop if it overflows.
3. **Overlay:** verify text is readable over a bright background. If not, raise
   `OVERLAY_STRENGTH` in `config.py` or strengthen the gradient in `compose.py`.
4. **AI-image note:** these backgrounds are AI-generated (SynthID watermarked).
   Add one line to the top of `review.html` reminding the user to toggle Meta's
   "AI info" label when posting photorealistic cards.

**Acceptance:** a long line wraps cleanly and stays readable; review page shows
the AI-label reminder.

---

## Phase 3 — Stop repeats (dedupe)

Create `dedupe.py`:
- Before saving new lines, scan every past `output/*/captions.json`.
- Reject any new line that is an exact or near-duplicate (case-insensitive,
  punctuation-stripped) of a past line.
- If a duplicate is found, ask `gen_text` for a replacement rather than shipping
  it.
Wire it into `run.py` so it runs automatically each batch.

**Acceptance:** running `python run.py` twice never produces the same line twice.
Add a unit test in `tests/` for the dedupe matcher.

---

## Phase 4 — Scheduler export (Metricool)

Create `export_metricool.py`:
- Take an approved batch folder and write a `schedule.csv` the user can bulk
  upload to Metricool: columns for the caption text, the image filename, and a
  suggested post date/time (spread one per day starting tomorrow).
- Only include cards the user marked approved. Simplest approach: read a
  `approved.txt` list of filenames the user fills in, or default to all.

**Acceptance:** `schedule.csv` opens in a spreadsheet with one row per approved
card, correct caption + image path + staggered dates.

---

## Phase 5 — Weekly workflow polish

1. Confirm `python run.py --count 7` produces 7 dated folders (or one folder with
   7 days of content — keep whatever the current design does, just make it
   coherent and documented).
2. Update `README.md` "How to use" with the final commands.
3. Restore `config.py` to the real volumes (`CARDS_PER_RUN = 5`,
   `REELS_PER_RUN = 2`) once testing is done.

**Acceptance:** a single command generates a week; README matches reality.

---

## Report back after each phase with:
- Files changed and why (one line each).
- The exact command run and its output (or the error, verbatim).
- Anything you couldn't resolve, so the user can escalate.
