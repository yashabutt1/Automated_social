"""
Central configuration for The Love Lens content pipeline.
Edit this file to change branding, models, sizes, or how many posts per run.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Brand identity
# ---------------------------------------------------------------------------
PAGE_NAME = "The Love Lens"
HANDLE = "@thelovelens"          # shown small on cards; set to "" to hide

# ---------------------------------------------------------------------------
# Models  (verify current names at ai.google.dev/gemini-api/docs/models)
# ---------------------------------------------------------------------------
# One GEMINI_API_KEY powers the text side. Backgrounds are generated locally
# with Pillow, so the image model config is retained only as metadata.
TEXT_MODEL = "gemini-2.5-flash"          # fast + cheap for copy
IMAGE_MODEL = "gemini-2.5-flash-image"   # retained for compatibility; not used

# ---------------------------------------------------------------------------
# How much to make each run
# ---------------------------------------------------------------------------
CARDS_PER_RUN = 2      # short quote cards (text on generated background)
PARAGRAPH_CARDS_PER_RUN = 2  # longer micro-essay cards
REELS_PER_RUN = 1      # reel scripts (text output only, you film/animate)

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
