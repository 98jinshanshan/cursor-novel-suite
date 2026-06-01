#!/usr/bin/env python3
"""Edge TTS for Chinese narration."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from result_contract import emit_result


async def run_tts(text: str, output: Path, voice: str) -> None:
    try:
        import edge_tts
    except ImportError:
        print("ERROR: pip install edge-tts", file=sys.stderr)
        sys.exit(1)
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", default="")
    ap.add_argument("--text-file", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    args = ap.parse_args()
    text = args.text
    if args.text_file:
        text = args.text_file.read_text(encoding="utf-8")
    if not text.strip():
        print("ERROR: empty text", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(run_tts(text.strip(), args.output, args.voice))
    print(f"OK: {args.output}")
    emit_result("ok", path=str(args.output), kind="audio")
    return 0


if __name__ == "__main__":
    sys.exit(main())
