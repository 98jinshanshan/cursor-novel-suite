#!/usr/bin/env python3
"""Basic video QC."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def ffprobe_json(path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", str(path),
    ]
    return json.loads(subprocess.check_output(cmd, text=True))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("--min-duration", type=float, default=1.0)
    ap.add_argument("--require-audio", action="store_true")
    args = ap.parse_args()
    if not args.video.exists():
        print(f"FAIL: not found {args.video}", file=sys.stderr)
        return 1
    data = ffprobe_json(args.video)
    streams = data.get("streams", [])
    fmt = data.get("format", {})
    dur = float(fmt.get("duration", 0))
    has_v = any(s.get("codec_type") == "video" for s in streams)
    has_a = any(s.get("codec_type") == "audio" for s in streams)
    ok = has_v and dur >= args.min_duration
    if args.require_audio:
        ok = ok and has_a
    result = {"ok": ok, "duration": dur, "has_video": has_v, "has_audio": has_a}
    print(json.dumps(result, indent=2))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
