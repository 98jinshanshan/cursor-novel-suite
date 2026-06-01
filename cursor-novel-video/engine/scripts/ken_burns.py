#!/usr/bin/env python3
"""Ken Burns effect on still image via FFmpeg."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from result_contract import emit_result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", type=Path, required=True)
    ap.add_argument("--duration", type=float, default=5.0)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    args = ap.parse_args()
    if not shutil.which("ffmpeg"):
        print("ERROR: ffmpeg not in PATH", file=sys.stderr)
        return 1
    if not args.image.exists():
        print(f"ERROR: missing {args.image}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    w, h, d = args.width, args.height, args.duration
    vf = (
        f"scale={w*2}:{h*2}:force_original_aspect_ratio=increase,crop={w*2}:{h*2},"
        f"zoompan=z='min(zoom+0.001,1.08)':d={int(d*25)}:s={w}x{h}:fps=25"
    )
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(args.image),
        "-vf", vf, "-t", str(d), "-pix_fmt", "yuv420p", str(args.output),
    ]
    subprocess.run(cmd, check=True)
    print(f"OK: {args.output}")
    emit_result("ok", path=str(args.output), kind="video")
    return 0


if __name__ == "__main__":
    sys.exit(main())
