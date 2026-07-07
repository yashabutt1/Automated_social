import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

import config

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")


def _env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not set. Add it to .env first.")
    return value


def _resolve_page_access_token(page_id: str) -> str:
    configured_token = os.getenv("FB_PAGE_TOKEN", "").strip()
    if not configured_token:
        raise RuntimeError("Set FB_PAGE_TOKEN to either a Page access token or a user token that can access /me/accounts")

    debug_url = "https://graph.facebook.com/v21.0/debug_token"
    debug_params = {"input_token": configured_token, "access_token": configured_token}
    debug_resp = requests.get(debug_url, params=debug_params, timeout=30)
    debug_payload = debug_resp.json()
    if not debug_resp.ok:
        raise RuntimeError(json.dumps(debug_payload, indent=2))

    token_type = debug_payload.get("data", {}).get("type", "").upper()
    if token_type == "PAGE":
        print(f"Using configured Page access token for page {page_id}")
        return configured_token

    if token_type != "USER":
        raise RuntimeError("FB_PAGE_TOKEN must be a valid User or Page access token")

    print("FB_PAGE_TOKEN is a user token; resolving a Page access token from /me/accounts")
    url = "https://graph.facebook.com/v21.0/me/accounts"
    params = {"access_token": configured_token, "fields": "id,name,access_token"}
    resp = requests.get(url, params=params, timeout=30)
    payload = resp.json()
    if not resp.ok:
        raise RuntimeError(json.dumps(payload, indent=2))

    for page in payload.get("data", []):
        if page.get("id") == page_id:
            page_token = page.get("access_token", "").strip()
            if page_token:
                print(f"Resolved Page access token from /me/accounts for page {page_id}")
                return page_token

    raise RuntimeError("Could not resolve a Page access token from /me/accounts. Grant the app the required Page permissions and use a Page access token in FB_PAGE_TOKEN.")


def check_token():
    page_id = _env("FB_PAGE_ID")
    token = _resolve_page_access_token(page_id)
    url = "https://graph.facebook.com/v21.0/debug_token"
    params = {"input_token": token, "access_token": token}
    try:
        resp = requests.get(url, params=params, timeout=30)
        payload = resp.json()
        if not resp.ok:
            print(payload)
            raise RuntimeError("Facebook token validation failed")
        data = payload.get("data", {})
        expires_at = data.get("expires_at")
        if expires_at:
            from datetime import datetime, timezone
            expiry = datetime.fromtimestamp(expires_at, tz=timezone.utc)
            days_left = (expiry - datetime.now(timezone.utc)).days
            print(f"Token expires at {expiry.isoformat()} ({days_left} days left)")
            if days_left < 7:
                print("Warning: fewer than 7 days remain. Re-generate and extend the token in the Access Token Debugger.")
        else:
            print("Token does not expire")
        return payload
    except Exception as exc:
        print(f"Facebook token check failed: {exc}")
        print("If the token is expired or invalid, re-generate it in the Access Token Debugger and extend it before posting.")
        raise


def build_caption(caption: str) -> str:
    return caption.strip()


def post_card(image_path, caption):
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(image_path)

    page_id = _env("FB_PAGE_ID")
    page_token = _resolve_page_access_token(page_id)
    url = f"https://graph.facebook.com/v21.0/{page_id}/photos"
    with image_path.open("rb") as fh:
        files = {"source": (image_path.name, fh, "image/png")}
        data = {"caption": build_caption(caption), "access_token": page_token}
        try:
            resp = requests.post(url, files=files, data=data, timeout=120)
            payload = resp.json()
            if not resp.ok:
                if payload.get("error", {}).get("code") in {190, 102}:
                    print("Facebook rejected the request. If the token is expired or invalid, re-generate and extend the Page access token in the Access Token Debugger.")
                raise RuntimeError(json.dumps(payload, indent=2))
            print(json.dumps(payload, indent=2))
            return payload
        except requests.RequestException as exc:
            raise RuntimeError(f"Network error while posting to Facebook: {exc}") from exc


def _latest_output_dir() -> Path:
    output_root = config.OUTPUT_DIR
    dirs = sorted(p for p in output_root.iterdir() if p.is_dir())
    if not dirs:
        raise FileNotFoundError("No output directories found")
    return dirs[-1]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Post a card to the Facebook Page")
    parser.add_argument("--test", action="store_true", help="Post one existing card from the latest output folder")
    parser.add_argument("--image", help="Path to the image file to post")
    parser.add_argument("--caption", default="New from The Love Lens", help="Caption to post")
    args = parser.parse_args(argv)

    if args.test:
        output_dir = _latest_output_dir()
        image_path = output_dir / "cards" / "card_1.png"
        if not image_path.exists():
            image_path = next((p for p in (output_dir / "cards").glob("*.png") if p.is_file()), None)
        if image_path is None or not image_path.exists():
            raise FileNotFoundError("No card images found in the latest output folder")
        print(f"Posting {image_path}...")
        post_card(image_path, args.caption)
        return

    if args.image:
        post_card(args.image, args.caption)
        return

    parser.error("Specify --test or --image")


if __name__ == "__main__":
    if "--test" in sys.argv:
        check_token()
    main(sys.argv[1:])
