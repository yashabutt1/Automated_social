# The Love Lens — content pipeline

The Love Lens generates a daily batch of quote cards and paragraph cards, writes a review folder, notifies you in Telegram for approval, and can auto-post approved cards to Facebook. The workflow is designed to stay useful even when Gemini quota runs out: the pipeline falls back to a local content pool and still produces a complete review batch.

## What each file does

- [run.py](run.py): orchestrates a full batch. It creates a dated output folder, runs content generation, writes the review page and [output](output)/captions.json, and renders the cards.
- [notify.py](notify.py): sends the generated cards to Telegram with approve/reject buttons so you can review them on your phone.
- [approve_bot.py](approve_bot.py): listens for Telegram callback taps, looks up the matching caption from the batch's captions.json entry, posts approved cards to Facebook, and avoids reposting cards after a restart by tracking already-posted files.
- [post_fb.py](post_fb.py): handles the Facebook Page photo post request using the Page access token and the card caption.
- [dedupe.py](dedupe.py): checks new lines and paragraph bodies against previously generated captions so the pipeline avoids repeating content.
- [topics.py](topics.py): a wide taxonomy of love/relationship topics (warm, self-love, hope, healing, communication, gratitude, committed, playful, longing, boundaries). Each run picks distinct, recently-unused topics so the feed keeps covering new ground instead of repeating one lane. Recent picks are remembered in `output/.topic_history.json`.
- [fetch_image.py](fetch_image.py): fetches an attractive, topic-matched portrait photo from Pexels, crops it to the card size, and remembers recently-used photo IDs (`output/.pexels_history.json`) so images don't repeat. Needs `PEXELS_API_KEY`; fails soft to the gradient when absent.
- [gen_image.py](gen_image.py): returns the background for each card — a Pexels photo when available, otherwise the original locally-drawn Pillow gradient.
- [compose.py](compose.py): renders the final decorated cards with Pillow — background photo, a readability scrim, soft floral corner accents, an elegant script title (Snell Roundhand), and the serif body text.
- [reel_visuals.py](reel_visuals.py): visual-variety catalogue for reels (nature / love / aesthetic categories) with rotation so the two daily reels differ and don't repeat day to day.
- [fetch_video.py](fetch_video.py): downloads a free HD vertical stock clip from Pexels for a reel, deduped by clip ID.
- [fetch_music.py](fetch_music.py): picks a royalty-free track from the `music/` folder, avoiding recently-used ones.
- [compose_video.py](compose_video.py): builds the finished reel with ffmpeg — cover-cropped 9:16 clip + branded text overlay + music with fades (H.264/AAC).

## Amazon affiliate product posts

Each run also picks `PRODUCT_POSTS_PER_RUN` (default 2) products from your curated
pool, writes a persuasive gift-angle caption + the required Associates disclosure,
and sends them to Telegram for approval. Approved ones post to the page as link
posts (Facebook renders the product card).

- **No PA-API required.** Curate best-seller links yourself in `products.txt`
  (one `Name | URL` per line — see `products.example.txt`). No Amazon scraping.
- Your Associate tag is read from `AMAZON_ASSOC_TAG` in `.env` and forced onto
  every link (even if the pasted link carried someone else's tag).
- Products are deduped by ASIN so the same item isn't reposted until the others
  have been used. Add more links anytime; refill when the pool runs low.
- [fetch_products.py](fetch_products.py) parses the pool and builds links;
  [post_fb.py](post_fb.py) `post_link()` publishes the feed post.

## Video reels

Each run also builds `VIDEO_REELS_PER_RUN` (default 2) finished reels: a free
Pexels clip + branded overlay + royalty-free music, sent to Telegram with the
same Approve/Reject buttons. Approved reels post to the page via the Facebook
Reels API (falling back to a normal video post if the token can't use Reels).

Requirements:
- **ffmpeg / ffprobe** — static binaries live in `bin/` (Homebrew's build was
  broken on this machine). Replace or point `config.FFMPEG` elsewhere as needed.
- **Music** — drop royalty-free tracks into `music/` (see `music/README.txt`).
  Pixabay Music is recommended: free, no attribution, safe for a monetized page.
  Empty folder → reels ship without music.
- [run_daily_guard.sh](run_daily_guard.sh): the cron-friendly wrapper that runs the daily generation and notification flow safely. It checks output/.last_run_date, skips if the job already ran today, and only writes the marker after both generation and notification succeed.
- [prompts.py](prompts.py): stores the text-generation prompts for lines, paragraphs, and reels.
- [config.py](config.py): central settings for branding, model names, output size, background moods, and batch size.

## Local setup

1. Install Python 3.10+ and the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy the sample environment file and add your own values:
   ```bash
   cp .env.example .env
   ```
   For attractive photo backgrounds, add a free `PEXELS_API_KEY` (get one at
   https://www.pexels.com/api/). Without it, cards fall back to gradient backgrounds.
   To turn photos off entirely, set `IMAGE_SOURCE = "gradient"` in [config.py](config.py).
3. Add the brand font if you want the cards to look more polished. See [fonts/README.txt](fonts/README.txt).

Do not commit your actual .env file. Keep secrets in environment variables only.

## Local run

```bash
python run.py
```

This creates a dated review folder under [output](output) and writes [output](output)/review.html plus the batch captions file.

## Daily automation workflow

The automation flow is:

1. Cron (or another scheduler) triggers [run_daily_guard.sh](run_daily_guard.sh).
2. The wrapper runs [run.py](run.py) and then [notify.py](notify.py).
3. Telegram sends the cards with approval buttons.
4. You approve or reject on your phone.
5. [approve_bot.py](approve_bot.py) posts approved cards to Facebook using the real caption from the matching entry in captions.json.
6. Already-posted files are tracked so a crash or restart does not re-post them.

## Cron line

Use this in crontab (hourly; the guard decides when to actually run):

```cron
0 * * * * /Users/yashabutt/love-lens-pipeline/run_daily_guard.sh
```

[run_daily_guard.sh](run_daily_guard.sh) runs **two batches a day in local time** —
a **morning** slot (first tick in 07:00–11:59) and an **evening** slot (18:00–22:59) —
so content lands in both peak windows instead of once at UTC midnight. Each slot
generates into its own `output/<date>-<slot>` folder (via `LOVELENS_SLOT`) so the
evening batch never overwrites the morning one that's still awaiting approval.
On a laptop, cron only fires while the Mac is awake, so a slot runs at the first
hourly tick inside its window that the machine is on; if the Mac is closed for a
whole window that slot is skipped for the day.

## Launchd service for macOS

A LaunchAgent is included as [com.lovelens.approvebot.plist](com.lovelens.approvebot.plist). It starts the approval bot automatically at login and restarts it if it exits unexpectedly.

Install it with:

```bash
mkdir -p ~/Library/LaunchAgents
cp /Users/yashabutt/love-lens-pipeline/com.lovelens.approvebot.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.lovelens.approvebot.plist
```

Logs go to [approvebot.out](approvebot.out) and [approvebot.err](approvebot.err).

## Moving to a cloud server later

When you are ready to run this on a server instead of your Mac:

1. Clone the repository on the server.
2. Add the same .env values there (do not commit secrets).
3. Install Python dependencies with `pip install -r requirements.txt`.
4. Install cron and launchd-compatible scheduling tools as needed for the host OS.
5. Copy the same automation scripts and set up the scheduler there.

## Compliance gate

Before anything goes live:

- Keep the wording original.
- Keep it warm, human, and helpful.
- Avoid manipulation tactics and clinical claims.
- Make sure the hook lands quickly and the text still sounds like a real person wrote it.

The human approval step remains part of the workflow, even when the rest is automated.
