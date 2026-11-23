"""Topic taxonomy + rotation for The Love Lens.

The old pipeline hard-coded a single lane (anxious texting / mixed signals /
situationships) into every prompt, so every post came out on the same subject.
This module defines a wide spectrum of love & relationship topics and hands the
run a *different* set each time, remembering recent picks so the feed keeps
moving through new ground.

Each topic carries:
  - id / category      : identity + grouping
  - angle              : what the writer should focus on (injected into prompts)
  - tone               : the emotional register for this piece
  - pexels_queries     : image search terms that match the feeling
  - mood               : palette hint for the local gradient fallback
"""
from __future__ import annotations

import json
import random
from pathlib import Path

_HISTORY_FILE = ".topic_history.json"


TOPICS: list[dict] = [
    # ---- warm / what love feels like -------------------------------------
    {
        "id": "warm_presence",
        "category": "warm",
        "angle": "the quiet comfort of being with someone whose presence makes you feel calm and safe",
        "tone": "warm, tender, reassuring",
        "pexels_queries": ["couple holding hands sunset", "couple hugging warm light", "cozy couple home"],
        "mood": "soft-focus sunset light, warm golden bokeh, dreamy and romantic",
    },
    {
        "id": "small_gestures",
        "category": "warm",
        "angle": "how real love shows up in tiny everyday gestures, not grand declarations",
        "tone": "warm, observant, a little poetic",
        "pexels_queries": ["couple morning coffee", "two coffee cups window", "breakfast in bed couple"],
        "mood": "cozy morning light through a window, shallow depth of field, tender",
    },
    {
        "id": "safe_love",
        "category": "warm",
        "angle": "what it feels like to finally be with someone who is steady and easy to trust",
        "tone": "warm, grounded, relieved",
        "pexels_queries": ["couple embrace cozy", "couple laughing together", "couple candlelight dinner"],
        "mood": "candlelight and soft shadows, warm intimate glow",
    },

    # ---- self-love / worth ----------------------------------------------
    {
        "id": "self_worth",
        "category": "selflove",
        "angle": "affirming the reader is worthy of love exactly as they are, without earning it",
        "tone": "uplifting, affirming, gentle",
        "pexels_queries": ["woman smiling sunlight", "self care flowers", "person peaceful nature"],
        "mood": "wildflowers backlit by low evening sun, hazy and tender",
    },
    {
        "id": "self_partnership",
        "category": "selflove",
        "angle": "learning to enjoy your own company and treat yourself with the care you give others",
        "tone": "encouraging, calm, warm",
        "pexels_queries": ["woman reading tea cozy", "person walking beach calm", "self care morning light"],
        "mood": "a quiet beach at dusk, muted pastel sky, calm water",
    },
    {
        "id": "confidence_bloom",
        "category": "selflove",
        "angle": "the quiet confidence that grows when you stop shrinking yourself for anyone",
        "tone": "empowering, warm, hopeful",
        "pexels_queries": ["woman confident golden hour", "person sunrise field", "flowers blooming spring"],
        "mood": "sunrise over an open field, golden hopeful light",
    },

    # ---- hope / new love -------------------------------------------------
    {
        "id": "new_love_flutter",
        "category": "hope",
        "angle": "the sweet nervous excitement of the very beginning, when someone feels different",
        "tone": "hopeful, light, giddy",
        "pexels_queries": ["couple first date laughing", "couple walking city night", "couple ice cream summer"],
        "mood": "string lights glowing over a blurred night, warm romantic bokeh",
    },
    {
        "id": "love_is_coming",
        "category": "hope",
        "angle": "reassurance that good, gentle love is still on its way even after a hard chapter",
        "tone": "hopeful, soft, believing",
        "pexels_queries": ["sunrise horizon hopeful", "flowers spring pastel", "open road morning light"],
        "mood": "soft sunrise sky, pastel clouds, wide and hopeful",
    },
    {
        "id": "open_heart",
        "category": "hope",
        "angle": "choosing to stay open to love even though it means being a little brave",
        "tone": "tender, hopeful, honest",
        "pexels_queries": ["hands reaching sunlight", "person open arms nature", "heart shape light bokeh"],
        "mood": "warm bokeh hearts of light, dreamy and gentle",
    },

    # ---- healing / moving on --------------------------------------------
    {
        "id": "healing_gentle",
        "category": "healing",
        "angle": "being gentle with yourself while a heart slowly mends, at its own pace",
        "tone": "comforting, soft, patient",
        "pexels_queries": ["rain window calm", "candle quiet cozy", "person tea blanket window"],
        "mood": "rain on a window at night, blurred warm lights, moody and intimate",
    },
    {
        "id": "letting_go",
        "category": "healing",
        "angle": "releasing what no longer fits so there is room for something that does",
        "tone": "honest, freeing, kind",
        "pexels_queries": ["autumn leaves falling", "person walking away path", "empty bench autumn"],
        "mood": "an empty park bench under autumn trees at golden hour",
    },
    {
        "id": "closure_within",
        "category": "healing",
        "angle": "finding your own closure instead of waiting for an apology that may never come",
        "tone": "grounded, gentle, strong",
        "pexels_queries": ["misty forest morning", "calm lake reflection", "person journaling window"],
        "mood": "misty forest at dawn, soft light through trees, calm",
    },

    # ---- communication / understanding ----------------------------------
    {
        "id": "honest_words",
        "category": "communication",
        "angle": "how naming what you feel plainly is a form of care, not conflict",
        "tone": "warm, direct, reassuring",
        "pexels_queries": ["couple talking cafe", "two people conversation window", "couple deep talk"],
        "mood": "two people by a sunlit cafe window, soft focus, warm",
    },
    {
        "id": "being_heard",
        "category": "communication",
        "angle": "the relief of being truly listened to, and how to offer that to someone you love",
        "tone": "gentle, warm, thoughtful",
        "pexels_queries": ["couple listening close", "friends talking warm", "couple forehead touch"],
        "mood": "soft intimate light, two silhouettes close together",
    },
    {
        "id": "repair_after_fight",
        "category": "communication",
        "angle": "how coming back to each other softly after a hard moment builds trust",
        "tone": "hopeful, tender, honest",
        "pexels_queries": ["couple making up hug", "couple reconciliation sunset", "hands holding close"],
        "mood": "warm reconciled light, hands entwined, golden hour",
    },

    # ---- gratitude / appreciation ---------------------------------------
    {
        "id": "gratitude_love",
        "category": "gratitude",
        "angle": "noticing and naming the good in the person you already have",
        "tone": "warm, grateful, tender",
        "pexels_queries": ["couple gratitude sunset", "couple dancing kitchen", "couple laughing home"],
        "mood": "warm kitchen light, cozy and grateful, soft focus",
    },
    {
        "id": "everyday_magic",
        "category": "gratitude",
        "angle": "the ordinary moments that turn out to be the ones you treasure most",
        "tone": "nostalgic, warm, sweet",
        "pexels_queries": ["couple walking dog park", "couple cooking together", "couple road trip window"],
        "mood": "golden everyday light, gentle nostalgia, film-like",
    },

    # ---- committed / long-term love -------------------------------------
    {
        "id": "long_love",
        "category": "committed",
        "angle": "the deep, unshowy love that grows over years of choosing each other",
        "tone": "warm, steady, moving",
        "pexels_queries": ["older couple holding hands", "couple growing old together", "couple silhouette beach"],
        "mood": "soft beach silhouette at dusk, calm and enduring",
    },
    {
        "id": "chosen_daily",
        "category": "committed",
        "angle": "how love is a choice you make again on ordinary, unremarkable days",
        "tone": "grounded, warm, reassuring",
        "pexels_queries": ["couple home cozy evening", "couple reading together", "couple tea porch"],
        "mood": "warm lamp-lit evening at home, cozy and safe",
    },

    # ---- playful / flirty -----------------------------------------------
    {
        "id": "playful_love",
        "category": "playful",
        "angle": "the goofy, teasing, laugh-until-it-hurts side of loving someone",
        "tone": "light, playful, warm",
        "pexels_queries": ["couple laughing piggyback", "couple playful beach", "couple silly fun"],
        "mood": "bright playful daylight, sun flare, joyful",
    },
    {
        "id": "flirty_spark",
        "category": "playful",
        "angle": "the electric little moments of attraction and being wanted",
        "tone": "flirty, warm, light",
        "pexels_queries": ["couple close smiling flirty", "couple dancing close", "couple summer evening"],
        "mood": "warm evening glow, close and electric, soft bokeh",
    },

    # ---- longing / missing someone --------------------------------------
    {
        "id": "longing",
        "category": "longing",
        "angle": "the tender ache of missing someone and what that longing is really telling you",
        "tone": "wistful, warm, honest",
        "pexels_queries": ["person window rain longing", "empty coffee cup window", "silhouette window evening"],
        "mood": "rain on glass, warm lights beyond, wistful and intimate",
    },
    {
        "id": "distance_love",
        "category": "longing",
        "angle": "keeping love warm across distance and the small ways closeness survives miles",
        "tone": "tender, hopeful, warm",
        "pexels_queries": ["person phone smiling window", "airport reunion hug", "sunset horizon two"],
        "mood": "warm sunset horizon, distant and tender",
    },

    # ---- boundaries / self-respect (kept, but one of many) --------------
    {
        "id": "boundaries_kind",
        "category": "boundaries",
        "angle": "how a clear, kind boundary protects your peace without closing your heart",
        "tone": "warm, firm, caring",
        "pexels_queries": ["woman calm confident window", "person peaceful sunlight", "quiet morning coffee"],
        "mood": "calm morning light, steady and self-assured",
    },
    {
        "id": "asking_for_needs",
        "category": "boundaries",
        "angle": "the strength in naming what you need out loud instead of hoping to be guessed",
        "tone": "encouraging, warm, honest",
        "pexels_queries": ["person thoughtful window light", "woman writing journal", "person calm nature"],
        "mood": "soft window light, thoughtful and grounded",
    },

    # ---- more warmth / connection ---------------------------------------
    {
        "id": "comfort_bad_day",
        "category": "warm",
        "angle": "being someone's soft place to land at the end of a hard day",
        "tone": "comforting, warm, tender",
        "pexels_queries": ["couple hugging blanket home", "couple comforting each other", "couple cozy sofa evening"],
        "mood": "warm lamp-lit living room, soft and safe",
    },
    {
        "id": "feeling_safe_yourself",
        "category": "warm",
        "angle": "the freedom of being fully, unguardedly yourself with someone",
        "tone": "warm, relieved, tender",
        "pexels_queries": ["couple laughing relaxed home", "couple candid natural", "couple silly comfortable"],
        "mood": "natural warm daylight, easy and unguarded",
    },
    {
        "id": "home_person",
        "category": "warm",
        "angle": "the moment a person stops being a place you visit and becomes home",
        "tone": "warm, moving, gentle",
        "pexels_queries": ["couple forehead touch sunset", "couple embrace window", "couple silhouette warm"],
        "mood": "golden hour glow, intimate and safe",
    },
    {
        "id": "affection_touch",
        "category": "warm",
        "angle": "the quiet language of hugs, held hands, and being close",
        "tone": "tender, warm, sweet",
        "pexels_queries": ["couple holding hands close", "couple hugging warm", "hands intertwined sunlight"],
        "mood": "soft warm light on entwined hands, gentle",
    },

    # ---- more communication / depth -------------------------------------
    {
        "id": "deep_talks",
        "category": "communication",
        "angle": "the late-night conversations that quietly stitch two people together",
        "tone": "warm, thoughtful, intimate",
        "pexels_queries": ["couple talking night lights", "couple deep conversation cafe", "two people talking cozy"],
        "mood": "warm string lights at night, close and open",
    },
    {
        "id": "reassurance",
        "category": "communication",
        "angle": "how a little reassurance, freely given, settles an anxious heart",
        "tone": "gentle, warm, steadying",
        "pexels_queries": ["couple reassuring hug", "couple comforting hands", "couple tender moment"],
        "mood": "soft warm light, calm and steadying",
    },

    # ---- more committed / growth ----------------------------------------
    {
        "id": "grow_together",
        "category": "committed",
        "angle": "two people growing side by side without growing apart",
        "tone": "warm, hopeful, steady",
        "pexels_queries": ["couple walking nature together", "couple hiking sunset", "couple planting garden"],
        "mood": "open golden landscape, growing and hopeful",
    },
    {
        "id": "slow_mornings",
        "category": "committed",
        "angle": "the unhurried weekend mornings that are their own kind of love letter",
        "tone": "cozy, warm, content",
        "pexels_queries": ["couple lazy morning bed", "couple coffee sunlight kitchen", "couple pancakes morning"],
        "mood": "soft morning sun through curtains, cozy and slow",
    },
    {
        "id": "patient_love",
        "category": "committed",
        "angle": "love that doesn't rush, that lets things unfold in their own time",
        "tone": "calm, warm, reassuring",
        "pexels_queries": ["couple peaceful sunset bench", "couple relaxed park", "couple calm nature"],
        "mood": "calm dusk light, unhurried and warm",
    },

    # ---- more gratitude / hope / healing --------------------------------
    {
        "id": "celebrate_them",
        "category": "gratitude",
        "angle": "being someone's loudest, proudest cheerleader",
        "tone": "warm, uplifting, joyful",
        "pexels_queries": ["couple celebrating happy", "couple cheering joy", "couple laughing proud"],
        "mood": "bright joyful light, celebratory and warm",
    },
    {
        "id": "first_ily",
        "category": "hope",
        "angle": "the brave, fluttery courage of saying 'I love you' first",
        "tone": "hopeful, tender, brave",
        "pexels_queries": ["couple tender first love", "couple close whisper", "couple romantic evening"],
        "mood": "soft romantic dusk, brave and tender",
    },
    {
        "id": "forgiveness",
        "category": "healing",
        "angle": "choosing repair over being right, and softening back toward each other",
        "tone": "gentle, honest, hopeful",
        "pexels_queries": ["couple making up embrace", "couple reconcile hands", "couple tender apology"],
        "mood": "warm forgiving light, hands reaching, gentle",
    },

    # ---- value / knowledge / solution (positive, highly shareable) --------
    {
        "id": "lasting_love_habits",
        "category": "committed",
        "angle": "the small daily habits that quietly keep love alive for decades — name one or two you can start today",
        "tone": "warm, encouraging, practical",
        "pexels_queries": ["older couple cooking together", "mature couple morning coffee", "senior couple gardening"],
        "mood": "warm homey light, everyday devotion",
    },
    {
        "id": "daily_appreciation",
        "category": "gratitude",
        "angle": "the simple practice of noticing and thanking your partner out loud, and how it changes a marriage",
        "tone": "warm, uplifting, grateful",
        "pexels_queries": ["older couple grateful smiling", "mature couple holding hands table", "couple thank you hug"],
        "mood": "soft grateful light, tender",
    },
    {
        "id": "good_apology",
        "category": "communication",
        "angle": "how a sincere, humble 'I'm sorry' repairs and actually strengthens a long relationship — the little lesson",
        "tone": "gentle, wise, hopeful",
        "pexels_queries": ["older couple reconciling hands", "mature couple serious talk", "couple forgiveness embrace"],
        "mood": "warm reconciled light, gentle",
    },
    {
        "id": "reconnect_after_kids",
        "category": "committed",
        "angle": "finding each other again after years of raising a family — small ways to come back together",
        "tone": "warm, hopeful, reassuring",
        "pexels_queries": ["mature couple date night", "empty nest couple home", "older couple walking park"],
        "mood": "warm golden light, rediscovered closeness",
    },
    {
        "id": "romance_after_60",
        "category": "playful",
        "angle": "keeping romance, laughter, and flirting alive in a long marriage — proof the spark doesn't retire",
        "tone": "warm, playful, joyful",
        "pexels_queries": ["senior couple dancing home", "older couple laughing beach", "mature couple playful kitchen"],
        "mood": "bright joyful warm light",
    },
    {
        "id": "best_is_ahead",
        "category": "hope",
        "angle": "the reminder that your happiest chapter and deepest love may still be ahead — it is never too late",
        "tone": "hopeful, uplifting, warm",
        "pexels_queries": ["mature woman hopeful sunrise", "older couple sunset horizon", "woman smiling golden light"],
        "mood": "golden sunrise, hopeful and open",
    },
    {
        "id": "words_that_heal",
        "category": "communication",
        "angle": "the simple phrases that instantly make a partner feel loved, safe, and seen — try one tonight",
        "tone": "warm, practical, tender",
        "pexels_queries": ["older couple close talking", "mature couple forehead touch", "couple whispering tender"],
        "mood": "soft intimate warm light",
    },
    {
        "id": "grandmother_wisdom",
        "category": "warm",
        "angle": "the timeless love advice passed down from mothers and grandmothers that still holds true",
        "tone": "nostalgic, warm, wise",
        "pexels_queries": ["grandmother hands tea", "multigenerational family warm", "older woman smiling window"],
        "mood": "soft nostalgic light, timeless and warm",
    },
    {
        "id": "choose_joy",
        "category": "selflove",
        "angle": "choosing small daily joys and gratitude together — happiness as a habit you build, not a thing you wait for",
        "tone": "uplifting, warm, positive",
        "pexels_queries": ["older woman laughing joyful", "mature couple sunshine happy", "woman gratitude flowers"],
        "mood": "bright cheerful light, joyful",
    },
    # ---- funny / relatable (broad, all-ages, highly shareable) ------------
    {
        "id": "funny_stealing_food",
        "category": "funny",
        "angle": "the one who says 'I'm not hungry' then eats half your plate — the little domestic crimes of love",
        "tone": "funny, playful, 'this is literally us'",
        "pexels_queries": ["couple laughing eating", "friends sharing food fun", "couple cooking laughing"],
        "mood": "bright candid warm kitchen light, playful",
    },
    {
        "id": "modern_overthinking",
        "category": "funny",
        "angle": "the overthinking spiral — rereading the text, watching the typing dots appear and disappear",
        "tone": "funny, self-aware, relatable",
        "pexels_queries": ["person looking at phone cozy", "texting phone bed", "coffee phone morning"],
        "mood": "soft modern light, cozy, a little dramatic",
    },
    {
        "id": "real_green_flags",
        "category": "real",
        "angle": "the unglamorous green flags — they text you they got home safe, they remember the small thing",
        "tone": "honest, validating, a little warm",
        "pexels_queries": ["couple candid city", "holding hands walking street", "couple phone smiling"],
        "mood": "natural candid daylight, real",
    },
    {
        "id": "funny_blanket_war",
        "category": "funny",
        "angle": "the nightly blanket war and fighting over the thermostat — intimacy as low-grade warfare",
        "tone": "funny, cozy, playful",
        "pexels_queries": ["couple cozy bed laughing", "messy bed morning", "couple blanket home"],
        "mood": "soft bedroom morning light, cozy funny",
    },
    {
        "id": "shared_brain",
        "category": "funny",
        "angle": "developing a shared brain — finishing each other's weird sentences, one look saying everything",
        "tone": "funny, warm, 'us'",
        "pexels_queries": ["couple laughing together", "two people inside joke", "friends laughing cafe"],
        "mood": "warm candid, joyful",
    },
    {
        "id": "real_healing_nonlinear",
        "category": "real",
        "angle": "healing isn't linear — some days you're completely fine, then a song or a smell undoes you",
        "tone": "honest, raw, gently hopeful",
        "pexels_queries": ["person window rain thoughtful", "walking alone autumn", "coffee window quiet"],
        "mood": "muted moody soft light, honest",
    },
    {
        "id": "friendship_soulmate",
        "category": "real",
        "angle": "the friend who's basically a soulmate — platonic love that holds you together",
        "tone": "warm, funny, tag-a-friend",
        "pexels_queries": ["best friends laughing", "friends hugging happy", "two friends coffee talking"],
        "mood": "bright warm candid, joyful",
    },
    {
        "id": "real_knowing_worth",
        "category": "real",
        "angle": "quietly knowing your worth — choosing peace over almost-love, no bitterness, just standards",
        "tone": "honest, empowering, grounded (not preachy)",
        "pexels_queries": ["confident woman city", "person walking sunlight calm", "portrait window light"],
        "mood": "clean confident daylight, calm",
    },
    {
        "id": "little_rituals",
        "category": "warm",
        "angle": "the tiny private rituals — the specific way you say goodnight, the inside nickname nobody else gets",
        "tone": "warm, specific, tender",
        "pexels_queries": ["couple forehead kiss", "couple home evening warm", "hands coffee two"],
        "mood": "soft golden intimate light, tender",
    },
    {
        "id": "family_chaos_love",
        "category": "real",
        "angle": "the beautiful chaos of family — nobody's normal, everybody's loud, and you'd pick them every time",
        "tone": "funny, warm, heartfelt",
        "pexels_queries": ["big family dinner laughing", "family candid home", "family holiday table"],
        "mood": "warm busy home light, joyful",
    },
]


def by_id(topic_id: str) -> dict | None:
    for t in TOPICS:
        if t["id"] == topic_id:
            return t
    return None


def _state_path(output_root: Path | str) -> Path:
    return Path(output_root) / _HISTORY_FILE


def _load_state(output_root: Path | str) -> dict:
    """State schema: {"bag": [ids not yet used this cycle], "recent": [last ids]}.

    Tolerates the old list-only format by treating it as ``recent``.
    """
    try:
        data = json.loads(_state_path(output_root).read_text(encoding="utf-8"))
        if isinstance(data, list):
            return {"bag": [], "recent": [str(x) for x in data]}
        if isinstance(data, dict):
            return {"bag": list(data.get("bag", [])), "recent": list(data.get("recent", []))}
    except Exception:
        pass
    return {"bag": [], "recent": []}


def _save_state(output_root: Path | str, state: dict) -> None:
    path = _state_path(output_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        all_ids = {t["id"] for t in TOPICS}
        clean = {
            "bag": [x for x in state.get("bag", []) if x in all_ids],
            "recent": [x for x in state.get("recent", []) if x in all_ids][-len(all_ids):],
        }
        path.write_text(json.dumps(clean, indent=2), encoding="utf-8")
    except Exception:
        pass


def _refilled_bag(recent: list[str], avoid_head: int) -> list[str]:
    """A freshly shuffled bag of every topic id, arranged so it does not start
    with a topic used at the very end of the previous cycle (avoids a topic
    repeating across the day boundary)."""
    all_ids = [t["id"] for t in TOPICS]
    avoid = set(recent[-avoid_head:]) if avoid_head else set()
    for _ in range(20):
        bag = all_ids[:]
        random.shuffle(bag)
        if not any(tid in avoid for tid in bag[:avoid_head]):
            return bag
    return bag  # good enough after several tries


def pick_topics(n: int, output_root: Path | str) -> list[dict]:
    """Return ``n`` topics for one day's batch.

    Uses a persistent shuffle-bag: every topic is served exactly once before any
    topic repeats, so the feed cycles through the whole catalogue before coming
    back around. Within a single day categories are kept distinct where possible,
    and a topic never repeats across consecutive days. (Even when a topic does
    eventually come back around, the copy and the photo are always new — the text
    is deduped forever and photos are deduped by id.)
    """
    state = _load_state(output_root)
    bag = [x for x in state["bag"] if by_id(x)]
    recent = state["recent"]

    chosen: list[dict] = []
    used_categories: set[str] = set()
    guard = 0
    while len(chosen) < n and guard < 500:
        guard += 1
        if not bag:
            bag = _refilled_bag(recent, avoid_head=n)

        # Prefer the first bag item whose category is new for today.
        idx = next((i for i, tid in enumerate(bag)
                    if (t := by_id(tid)) and t["category"] not in used_categories), None)
        if idx is None:
            idx = 0
        topic = by_id(bag.pop(idx))
        if not topic:
            continue
        chosen.append(topic)
        used_categories.add(topic["category"])

    recent = recent + [t["id"] for t in chosen]
    _save_state(output_root, {"bag": bag, "recent": recent})
    return chosen
