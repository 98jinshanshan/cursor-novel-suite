#!/usr/bin/env python3
"""Generic Playwright upload — platform URLs passed via CLI args."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse


def _login_in_url(url: str) -> bool:
    return "login" in url.lower()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", type=Path, required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--creator-url", required=True)
    ap.add_argument("--upload-url", required=True)
    ap.add_argument("--aspect", default="9:16")
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--cookies", type=Path)
    ap.add_argument("--save-cookies", type=Path)
    args = ap.parse_args()

    result: dict[str, str | bool] = {"ok": False, "url": "", "error": ""}

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        result["error"] = (
            "playwright not installed — pip install playwright && playwright install chromium"
        )
        print(json.dumps(result, ensure_ascii=False))
        return 1

    creator_base = f"{urlparse(args.creator_url).scheme}://{urlparse(args.creator_url).netloc}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=args.headless)
            context = browser.new_context(viewport={"width": 1280, "height": 800})

            if args.cookies and args.cookies.is_file():
                raw = json.loads(args.cookies.read_text(encoding="utf-8"))
                if isinstance(raw, list):
                    context.add_cookies(raw)

            page = context.new_page()
            page.goto(args.creator_url, wait_until="networkidle", timeout=30000)

            if _login_in_url(page.url):
                if args.headless:
                    result["error"] = "Login required — run auth login or use --no-headless"
                    print(json.dumps(result, ensure_ascii=False))
                    browser.close()
                    return 1
                print("等待扫码登录... 请在浏览器中扫描二维码。", file=sys.stderr)
                page.wait_for_url(f"{creator_base}/**", timeout=120000)

            if args.save_cookies:
                args.save_cookies.parent.mkdir(parents=True, exist_ok=True)
                args.save_cookies.write_text(
                    json.dumps(context.cookies(), ensure_ascii=False),
                    encoding="utf-8",
                )

            page.goto(args.upload_url, wait_until="networkidle", timeout=30000)
            page.locator("input[type=file]").set_input_files(str(args.video.resolve()))
            page.wait_for_timeout(5000)

            title_input = page.locator("[placeholder*='标题'], [contenteditable='true']").first
            title_input.fill(args.title)
            page.wait_for_timeout(2000)

            if args.save_cookies:
                args.save_cookies.write_text(
                    json.dumps(context.cookies(), ensure_ascii=False),
                    encoding="utf-8",
                )

            result["ok"] = True
            result["url"] = page.url
            result["note"] = "Upload prepared. User must click publish manually in browser."
            browser.close()

    except Exception as exc:
        result["error"] = str(exc)

    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
