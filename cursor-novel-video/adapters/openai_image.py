#!/usr/bin/env python3
"""Optional OpenAI image generation for scene visuals."""

from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path

_MAX_BYTES = 20 * 1024 * 1024
_TIMEOUT = 30.0
_ALLOWED_SUFFIXES = (
    "oaidalleapiprodscus.blob.core.windows.net",
    "oaidalleapiprod.blob.core.windows.net",
    "cdn.openai.com",
)


def _legacy_download(url: str, httpx_mod) -> bytes:
    """Fallback when novel_suite is not on PYTHONPATH (video-only checkout)."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Only https URLs allowed")
    host = parsed.hostname.lower()
    if not any(host == s or host.endswith(f".{s}") for s in _ALLOWED_SUFFIXES):
        raise ValueError(f"Host not allowlisted: {host}")
    total = 0
    chunks: list[bytes] = []
    with httpx_mod.Client(timeout=_TIMEOUT, follow_redirects=True, max_redirects=3) as client:
        with client.stream("GET", url) as resp:
            resp.raise_for_status()
            for chunk in resp.iter_bytes():
                total += len(chunk)
                if total > _MAX_BYTES:
                    raise ValueError(f"Download exceeds {_MAX_BYTES} bytes")
                chunks.append(chunk)
    return b"".join(chunks)


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
        if not url:
            print("ERROR: image response missing URL and b64_json", file=sys.stderr)
            return 1
        try:
            from novel_suite.core.path_safety import download_https_bytes

            data = download_https_bytes(url)
        except ImportError:
            if httpx is None:
                print("ERROR: need httpx or novel-suite for URL download", file=sys.stderr)
                return 1
            data = _legacy_download(url, httpx)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        args.output.write_bytes(data)
    print(f"OK: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
