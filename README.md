# The Love Lens — content pipeline

The Love Lens generates a daily batch of quote cards and paragraph cards, writes a review folder, notifies you in Telegram for approval, and can auto-post approved cards to Facebook. The workflow is designed to stay useful even when Gemini quota runs out: the pipeline falls back to a local content pool and still produces a complete review batch.

## What each file does

- [run.py](run.py): orchestrates a full batch. It creates a dated output folder, runs content generation, writes the review page and [output](output)/captions.json, and renders the cards.
- [notify.py](notify.py): sends the generated cards to Telegram with approve/reject buttons so you can review them on your phone.
- [approve_bot.py](approve_bot.py): listens for Telegram callback taps, looks up the matching caption from the batch's captions.json entry, posts approved cards to Facebook, and avoids reposting cards after a restart by tracking already-posted files.
- [post_fb.py](post_fb.py): handles the Facebook Page photo post request using the Page access token and the card caption.
- [dedupe.py](dedupe.py): checks new lines and paragraph bodies against previously generated captions so the pipeline avoids repeating content.
- [gen_image.py](gen_image.py): generates the local background image for each card.
- [compose.py](compose.py): renders the final quote-card and paragraph-card images with Pillow.
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

Use this in crontab:

```cron
0 * * * * /Users/yashabutt/love-lens-pipeline/run_daily_guard.sh
```

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
