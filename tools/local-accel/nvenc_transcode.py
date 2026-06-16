#!/usr/bin/env python3
"""NVENC transcode helper — explicit opt-in only."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="Transcode video with NVENC fallback to libx264")
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if not args.input.is_file():
        print(f"ERROR: missing input {args.input}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)

    nvenc = [
        "ffmpeg", "-y", "-i", str(args.input),
        "-c:v", "h264_nvenc", "-preset", "p4", "-cq", "23",
        "-c:a", "copy", str(args.output),
    ]
    proc = subprocess.run(nvenc, capture_output=True, text=True, timeout=600, check=False)
    if proc.returncode == 0 and args.output.is_file():
        print(f"OK nvenc: {args.output}")
        return 0

    x264 = [
        "ffmpeg", "-y", "-i", str(args.input),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "copy", str(args.output),
    ]
    proc2 = subprocess.run(x264, capture_output=True, text=True, timeout=600, check=False)
    if proc2.returncode == 0 and args.output.is_file():
        print(f"OK libx264 fallback: {args.output}")
        return 0
    print(proc.stderr or proc2.stderr, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
