#!/usr/bin/env python3
"""Generate title card PNG for video scenes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def make_title_card(text: str, out: Path, width: int, height: int) -> None:
    img = Image.new("RGB", (width, height), color=(15, 20, 35))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("msyh.ttc", 48)
    except OSError:
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except OSError:
            font = ImageFont.load_default()
    draw.multiline_text((80, height // 3), text[:200], fill=(240, 240, 245), font=font, spacing=12)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    args = ap.parse_args()
    make_title_card(args.text, args.output, args.width, args.height)
    print(f"OK: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
