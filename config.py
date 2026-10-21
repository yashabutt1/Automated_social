"""
Central configuration for The Love Lens content pipeline.
Edit this file to change branding, models, sizes, or how many posts per run.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Brand identity
# ---------------------------------------------------------------------------
PAGE_NAME = "The Love Lens"
HANDLE = "@thelovelensforall"    # shown small on cards; set to "" to hide

# Who actually follows the page (from Insights): shapes the voice of every post.
AUDIENCE = (
    "Your audience is mostly WOMEN aged 35-65+ in the United States — wives, moms, "
    "and grandmothers who have loved, lost, and loved again. Write for mature grown "
    "women reflecting on real, lasting love: marriage, long partnership, family, "
    "raising kids, empty nests, healing after heartbreak later in life, faith, "
    "gratitude, and self-worth earned over decades. Warm, heartfelt, a little "
    "nostalgic, the kind of thing a woman proudly shares to her own timeline. AVOID "
    "teen/Gen-Z dating slang, 'situationships', hookup culture, and texting-anxiety "
    "framing unless a topic genuinely calls for it.")

# ---------------------------------------------------------------------------
# Calls-to-action appended to captions to boost reach (follow/share/save/tag).
# These signals (shares, saves, comments) are what the algorithm rewards.
# ---------------------------------------------------------------------------
CTA_FOLLOW = f"❤️ Follow {HANDLE} for a little more love, every day."
CTA_SHARE = "🔁 Share this with someone who needs to see it today."
CTA_SAVE = "🔖 Save this for when you need the reminder."
CTA_TAG = "💝 Tag someone who'd love this."

# ---------------------------------------------------------------------------
# Models  (verify current names at ai.google.dev/gemini-api/docs/models)
# ---------------------------------------------------------------------------
# GEMINI_API_KEY powers the text side. Backgrounds now come from Pexels stock
# photos (free API key -> PEXELS_API_KEY in .env). Get one at pexels.com/api.
TEXT_MODEL = "gemini-2.5-flash"          # fast + cheap for copy
IMAGE_MODEL = "gemini-2.5-flash-image"   # retained for compatibility; not used

# Where card backgrounds come from:
#   "pexels"   -> real stock photos matched to each card's topic (recommended)
#   "gradient" -> the original locally-drawn Pillow gradient (offline, no key)
IMAGE_SOURCE = "pexels"

# Draw soft decorative floral accents in the corners (like the studio example).
DECORATE_FLORALS = True

# ---------------------------------------------------------------------------
# How much to make each run
# ---------------------------------------------------------------------------
# Counts are PER BATCH. The pipeline runs twice a day (morning + evening slots),
# so daily totals are roughly double these.
# REELS-FIRST: reels are the only format Facebook pushes to NON-followers, so
# they're weighted heaviest. Feed cards mostly reach existing followers, so they
# are trimmed. Paragraph cards stay (older-women audiences love & share them).
CARDS_PER_RUN = 1      # short quote cards (-> ~2/day)
PARAGRAPH_CARDS_PER_RUN = 1  # heartfelt micro-essay cards (-> ~2/day, shareable)
REELS_PER_RUN = 1      # reel scripts (text output only; not posted)
VIDEO_REELS_PER_RUN = 2  # finished video reels (-> ~4/day, the growth engine)
PRODUCT_POSTS_PER_RUN = 1  # Amazon affiliate product recommendations (-> ~2/day)
ENGAGEMENT_POSTS_PER_RUN = 1  # interactive "comment below" posts (-> ~2/day)

# ---------------------------------------------------------------------------
# Amazon Associates (manual-link mode — no PA-API)
# ---------------------------------------------------------------------------
import os as _os
AMAZON_ASSOC_TAG = _os.getenv("AMAZON_ASSOC_TAG", "").strip()
AMAZON_MARKETPLACE = _os.getenv("AMAZON_MARKETPLACE", "www.amazon.com").strip()
# You curate products here (name | url per line). See products.example.txt.
PRODUCTS_FILE = Path(__file__).parent / "products.txt"
# Optional: a published-to-web Google Sheet (CSV) so links can be added from any
# device. Columns: Name | Amazon URL. Merged with products.txt.
GOOGLE_SHEET_CSV_URL = _os.getenv("GOOGLE_SHEET_CSV_URL", "").strip()
AFFILIATE_DISCLOSURE = (
    "As an Amazon Associate, The Love Lens earns from qualifying purchases.")

# ---------------------------------------------------------------------------
# Video reels
# ---------------------------------------------------------------------------
REEL_W = 1080
REEL_H = 1920          # 9:16 vertical for Reels
REEL_TARGET_SECONDS = 14   # final reel length (clip is looped/trimmed to fit)

# Static ffmpeg/ffprobe binaries live in ./bin (installed there because the
# Homebrew build was broken on this machine). Falls back to PATH if absent.
_BIN = Path(__file__).parent / "bin"
FFMPEG = str(_BIN / "ffmpeg") if (_BIN / "ffmpeg").exists() else "ffmpeg"
FFPROBE = str(_BIN / "ffprobe") if (_BIN / "ffprobe").exists() else "ffprobe"

# Royalty-free music pool. Drop .mp3/.m4a/.wav files here; reels rotate through
# them and avoid recently-used tracks. Empty folder -> reels ship without music.
MUSIC_DIR = Path(__file__).parent / "music"

# ---------------------------------------------------------------------------
# Card output size  (Instagram / Facebook feed)
# ---------------------------------------------------------------------------
CARD_W = 1080
CARD_H = 1350          # 4:5 portrait takes the most feed space. 1080 for square.

# Overlay darkness over the photo so text stays readable (0.0-1.0)
# Backgrounds are now drawn locally with Pillow, so keep the overlay modest
# enough that the gradient color still shows through.
OVERLAY_STRENGTH = 0.45

# Add an AI-content label to Facebook captions when posting generated images.
AI_CONTENT_LABEL = True

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------
# Drop a .ttf into ./fonts and point to it here. Fraunces (free, OFL) matches
# the studio look: fonts.google.com/specimen/Fraunces
FONT_DISPLAY = Path(__file__).parent / "fonts" / "static" / "Fraunces_72pt-SemiBold.ttf"
FONT_SMALL = Path(__file__).parent / "fonts" / "static" / "Fraunces_72pt-SemiBold.ttf"
# If a font file is missing the code falls back to PIL's default (works, plainer).

# Elegant script font for the short title on each card (the "Love Journey" look).
# Snell Roundhand ships with macOS. On another OS, drop a script .ttf into ./fonts
# and point here; if it's missing the code falls back to Fraunces italic.
FONT_SCRIPT = Path("/System/Library/Fonts/Supplemental/SnellRoundhand.ttc")
FONT_SCRIPT_FALLBACK = Path(__file__).parent / "fonts" / "static" / "Fraunces_72pt-SemiBoldItalic.ttf"

# ---------------------------------------------------------------------------
# Background moods -> local palette choices used by the Pillow renderer.
# Faceless + atmospheric. No identifiable faces, so nothing to clear.
# ---------------------------------------------------------------------------
BACKGROUND_MOODS = [
    "soft-focus sunset light through a rose garden archway, warm golden bokeh, dreamy and romantic, no people",
    "rain on a window at night, blurred warm city lights beyond the glass, moody and intimate, no people",
    "two coffee cups on a wooden table by a sunlit window, cozy morning, shallow depth of field, no people",
    "an empty park bench under autumn trees at golden hour, gentle nostalgia, no people",
    "candlelight and soft shadows on a dark textured wall, warm intimate glow, no people",
    "a quiet beach at dusk, muted pastel sky, calm water, wide and lonely, no people",
    "wildflowers in a field backlit by low evening sun, hazy and tender, no people",
    "string lights glowing over a blurred night background, warm romantic bokeh, no people",
]

# Consistent look for every background so the feed feels like one brand.
# These values are no longer sent to an API; they are kept for reference.
STYLE_SUFFIX = (
    "cinematic photography, muted warm color grade, soft natural light, "
    "high quality, vertical composition, plenty of negative space for text, "
    "no text, no words, no watermark, no people's faces"
)

# ---------------------------------------------------------------------------
# Rotating reel-script formats (matches your starter kit)
# ---------------------------------------------------------------------------
ENGAGEMENT_FORMATS = [
    "A question about relationship truths (e.g. 'What's one relationship truth you wish you knew sooner?')",
    "Fill-in-the-blank (e.g. 'Real love feels like ______.')",
    "This or that (make them pick a side and defend it)",
    "Would you rather (two tempting relationship options)",
    "Finish the sentence (e.g. 'I feel most loved when...')",
    "A surprising TRUE fun fact about love/attraction/history + a question that invites reactions",
    "A gentle hot-take / unpopular opinion that invites agree-or-disagree",
]

REEL_FORMATS = [
    "Green flag / Red flag — two quick contrasts on one behavior",
    "What they say vs. what they mean",
    "One hard truth — a single honest, uncomfortable insight",
    "Attachment style in 15 seconds",
    "The reframe — turn a common fight into a lesson",
]

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path(__file__).parent / "output"


def slot_suffix() -> str:
    """'-morning' / '-evening' when running as a scheduled slot, else ''."""
    s = _os.getenv("LOVELENS_SLOT", "").strip()
    return f"-{s}" if s else ""


def today_dirname(offset_days: int = 0) -> str:
    from datetime import date, timedelta
    return (date.today() + timedelta(days=offset_days)).isoformat() + slot_suffix()


def current_batch_dir(offset_days: int = 0) -> Path:
    """The folder for the batch being generated/sent right now (slot-aware),
    so a morning and evening run on the same day don't overwrite each other."""
    return OUTPUT_DIR / today_dirname(offset_days)
