#!/usr/bin/env python3
"""Optional OpenAI image generation for scene visuals."""

from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(
            "ERROR: set OPENAI_API_KEY or use make_title_card.py (free)",
            file=sys.stderr,
        )
        return 2
    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: pip install openai", file=sys.stderr)
        return 1
    try:
        import httpx
    except ImportError:
        httpx = None  # type: ignore[assignment]

    client = OpenAI(api_key=api_key)
    resp = client.images.generate(
        model="gpt-image-1", prompt=args.prompt, size="1024x1536"
    )
    b64 = resp.data[0].b64_json
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if b64:
        args.output.write_bytes(base64.b64decode(b64))
    else:
        url = resp.data[0].url
        if not url or httpx is None:
            print("ERROR: need httpx for URL download: pip install httpx", file=sys.stderr)
            return 1
        args.output.write_bytes(httpx.get(url).content)
    print(f"OK: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
