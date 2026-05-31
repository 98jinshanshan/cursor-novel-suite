#!/usr/bin/env python3
"""Burn SRT subtitles onto video with FFmpeg."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="Burn SRT subtitles into MP4")
    ap.add_argument("--video", type=Path, required=True)
    ap.add_argument("--srt", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if not args.video.is_file() or not args.srt.is_file():
        print("ERROR: missing video or srt", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    srt = str(args.srt.resolve()).replace("\\", "/").replace(":", "\\:")
    vf = f"subtitles='{srt}'"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(args.video),
        "-vf",
        vf,
        "-c:a",
        "copy",
        str(args.output),
    ]
    subprocess.run(cmd, check=True)
    print(f"OK: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
