import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

import post_fb

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

ROOT = Path(__file__).resolve().parent
LOG_FILE = ROOT / "approval_log.txt"
REJECTED_DIR = ROOT / "rejected"
POSTED_DIR = ROOT / "posted"
OFFSET_FILE = ROOT / "last_update_offset.txt"
REJECTED_DIR.mkdir(exist_ok=True)
POSTED_DIR.mkdir(exist_ok=True)


def _env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not set. Add it to .env first.")
    return value


def _log(message: str):
    line = f"[{datetime.now(timezone.utc).isoformat()}] {message}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def _latest_output_dir() -> Path:
    output_root = ROOT / "output"
    dirs = sorted(p for p in output_root.iterdir() if p.is_dir())
    if not dirs:
        raise FileNotFoundError("No output directories found")
    return dirs[-1]


def _get_updates(offset: int = 0):
    token = _env("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"timeout": 50, "offset": offset}
    resp = requests.get(url, params=params, timeout=60)
    payload = resp.json()
    if not payload.get("ok"):
        raise RuntimeError(json.dumps(payload, indent=2))
    return payload.get("result", [])


def _load_offset() -> int:
    if not OFFSET_FILE.exists():
        return 0
    try:
        return int(OFFSET_FILE.read_text(encoding="utf-8").strip())
    except Exception:
        return 0


def _save_offset(offset: int):
    OFFSET_FILE.write_text(str(offset), encoding="utf-8")


def _answer_callback(query_id, text):
    token = _env("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
    requests.post(url, data={"callback_query_id": query_id, "text": text}, timeout=30)


def _edit_message(chat_id, message_id, text):
    token = _env("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/editMessageText"
    requests.post(url, data={"chat_id": chat_id, "message_id": message_id, "text": text}, timeout=30)


def _move_to_rejected(filename: str):
    src = _latest_output_dir() / "cards" / filename
    if src.exists():
        target = REJECTED_DIR / filename
        src.rename(target)
        return str(target)
    return None


def _posted_marker(latest: Path, filename: str) -> Path:
    marker_name = f"{latest.name}_{filename}"
    return POSTED_DIR / marker_name


def process_update(update):
    callback = update.get("callback_query")
    if not callback:
        return
    data = callback.get("data", "")
    query_id = callback.get("id")
    chat_id = callback.get("message", {}).get("chat", {}).get("id")
    message_id = callback.get("message", {}).get("message_id")
    if not data.startswith(("approve:", "reject:")):
        return
    action, filename = data.split(":", 1)
    latest = _latest_output_dir()
    image_path = latest / "cards" / filename
    posted_marker = _posted_marker(latest, filename)

    if action == "approve":
        if posted_marker.exists():
            _answer_callback(query_id, "Already posted")
            _edit_message(chat_id, message_id, f"Already posted {filename}")
            _log(f"Already posted {filename}, skipped")
            return
        if not image_path.exists():
            _answer_callback(query_id, "Image not found")
            _log(f"Approve failed: {filename} missing")
            return
        try:
            caption = ""
            captions_path = latest / "captions.json"
            if captions_path.exists():
                payload = json.loads(captions_path.read_text(encoding="utf-8"))
                for item in payload.get("cards", []):
                    if item.get("file") == filename:
                        caption = item.get("caption", "").strip()
                        break
            result = post_fb.post_card(str(image_path), caption)
            try:
                posted_marker.write_text("posted", encoding="utf-8")
            except Exception as write_exc:
                _log(f"Warning: could not write posted marker for {filename}: {write_exc}")
            post_id = result.get("id")
            page_id = os.getenv("FB_PAGE_ID", "").strip()
            link = f"https://www.facebook.com/{page_id}/posts/{post_id}" if page_id and post_id else str(post_id or "")
            _answer_callback(query_id, "Posted ✅")
            _edit_message(chat_id, message_id, f"Posted ✅ {link}")
            _log(f"Approved and posted {filename} -> {link}")
        except Exception as exc:
            _answer_callback(query_id, f"Failed: {exc}")
            _log(f"Approve failed for {filename}: {exc}")
    else:
        moved = _move_to_rejected(filename)
        _answer_callback(query_id, "Skipped")
        _edit_message(chat_id, message_id, f"Skipped {filename}")
        _log(f"Rejected {filename} -> {moved}")


def main():
    offset = _load_offset()
    while True:
        try:
            updates = _get_updates(offset)
            for update in updates:
                process_update(update)
                offset = max(offset, update.get("update_id", 0) + 1)
                _save_offset(offset)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError, requests.exceptions.RequestException) as exc:
            _log(f"network hiccup, retrying: {exc}")
            time.sleep(3)
            continue
        except Exception as exc:
            _log(f"unexpected loop error, retrying: {exc}")
            time.sleep(3)
            continue
        time.sleep(2)


if __name__ == "__main__":
    main()
