#!/usr/bin/env python3
"""Generate SRT subtitles from script text and audio (optional Whisper beat-lock)."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from result_contract import emit_result


def probe_duration(path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    return float(subprocess.check_output(cmd, text=True).strip())


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？!?])\s*", text.strip())
    return [p.strip() for p in parts if p.strip()]


def whisper_segments(audio: Path) -> list[tuple[float, float, str]] | None:
    try:
        import whisper  # type: ignore
    except ImportError:
        return None
    model = whisper.load_model("base")
    result = model.transcribe(str(audio), language="zh")
    segs = []
    for seg in result.get("segments", []):
        segs.append((float(seg["start"]), float(seg["end"]), str(seg["text"]).strip()))
    return segs or None


def format_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(entries: list[tuple[float, float, str]], out: Path) -> None:
    lines: list[str] = []
    for i, (start, end, text) in enumerate(entries, 1):
        lines.append(str(i))
        lines.append(f"{format_ts(start)} --> {format_ts(end)}")
        lines.append(text)
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")


def proportional_entries(sentences: list[str], duration: float) -> list[tuple[float, float, str]]:
    if not sentences:
        return []
    weights = [max(len(s), 1) for s in sentences]
    total = sum(weights)
    entries: list[tuple[float, float, str]] = []
    t = 0.0
    for sent, w in zip(sentences, weights):
        seg = duration * (w / total)
        entries.append((t, min(t + seg, duration), sent))
        t += seg
    return entries


def main() -> int:
    ap = argparse.ArgumentParser(description="Beat-lock: script.md + audio.mp3 → subtitles.srt")
    ap.add_argument("--script", type=Path, required=True)
    ap.add_argument("--audio", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--whisper", action="store_true", help="Use openai-whisper if installed")
    args = ap.parse_args()

    if not args.audio.is_file():
        print(f"ERROR: missing audio {args.audio}", file=sys.stderr)
        return 1
    text = args.script.read_text(encoding="utf-8")
    duration = probe_duration(args.audio)

    entries: list[tuple[float, float, str]] | None = None
    if args.whisper:
        entries_data = whisper_segments(args.audio)
        if entries_data:
            entries = entries_data

    if entries is None:
        entries = proportional_entries(split_sentences(text), duration)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_srt(entries, args.output)
    print(f"OK: {args.output} ({len(entries)} cues, {duration:.1f}s)")
    emit_result("ok", path=str(args.output), cues=len(entries), duration_sec=round(duration, 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
