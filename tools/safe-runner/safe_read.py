#!/usr/bin/env python3
"""Restricted file read — line window only, rejects large binaries."""

from __future__ import annotations

import argparse
import mimetypes
import sys
from datetime import datetime
from pathlib import Path

MAX_DEFAULT = 120
MAX_HARD = 300
MAX_BYTES = 2_000_000
BINARY_SUFFIXES = {".mp4", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".zip", ".epub"}


def _log_dir() -> Path:
    d = Path.cwd() / ".tmp" / "safe-runner"
    d.mkdir(parents=True, exist_ok=True)
    return d


def main() -> int:
    ap = argparse.ArgumentParser(description="Safe partial file read")
    ap.add_argument("path", type=Path)
    ap.add_argument("--from", dest="from_line", type=int, default=1)
    ap.add_argument("--lines", type=int, default=MAX_DEFAULT)
    args = ap.parse_args()
    n = min(max(args.lines, 1), MAX_HARD)
    path = args.path.resolve()

    if not path.is_file():
        print(f"ERROR: not a file: {path}", file=sys.stderr)
        return 1
    if path.suffix.lower() in BINARY_SUFFIXES:
        print(f"ERROR: refused binary/media: {path}", file=sys.stderr)
        return 1
    if path.stat().st_size > MAX_BYTES:
        print(f"ERROR: file too large ({path.stat().st_size} bytes)", file=sys.stderr)
        return 1
    mime, _ = mimetypes.guess_type(str(path))
    if mime and not mime.startswith("text"):
        print(f"ERROR: refused non-text mime {mime}", file=sys.stderr)
        return 1

    all_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(args.from_line - 1, 0)
    chunk = all_lines[start : start + n]
    text = "\n".join(chunk)
    if len(all_lines) > start + n:
        log = _log_dir() / f"safe_read_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log.write_text("\n".join(all_lines), encoding="utf-8")
        print(text)
        print(f"\n[safe_read] showing {len(chunk)}/{len(all_lines)} lines; full: {log}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
