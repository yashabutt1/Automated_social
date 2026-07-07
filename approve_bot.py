import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

import post_fb

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

ROOT = Path(__file__).resolve().parent
LOG_FILE = ROOT / "approval_log.txt"
REJECTED_DIR = ROOT / "rejected"
REJECTED_DIR.mkdir(exist_ok=True)


def _env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not set. Add it to .env first.")
    return value


def _log(message: str):
    line = f"[{datetime.utcnow().isoformat()}] {message}"
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
    params = {"timeout": 10, "offset": offset}
    resp = requests.get(url, params=params, timeout=30)
    payload = resp.json()
    if not payload.get("ok"):
        raise RuntimeError(json.dumps(payload, indent=2))
    return payload.get("result", [])


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
    if action == "approve":
        image_path = _latest_output_dir() / "cards" / filename
        if not image_path.exists():
            _answer_callback(query_id, "Image not found")
            _log(f"Approve failed: {filename} missing")
            return
        try:
            caption = ""
            latest = _latest_output_dir()
            captions_path = latest / "captions.json"
            if captions_path.exists():
                payload = json.loads(captions_path.read_text(encoding="utf-8"))
                for item in payload.get("cards", []):
                    if item.get("file") == filename:
                        caption = item.get("caption", "")
                        break
            result = post_fb.post_card(str(image_path), caption)
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
    offset = 0
    while True:
        updates = _get_updates(offset)
        for update in updates:
            process_update(update)
            offset = max(offset, update.get("update_id", 0) + 1)
        time.sleep(2)


if __name__ == "__main__":
    main()
