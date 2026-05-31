#!/usr/bin/env python3
"""Novel-to-video CLI."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
VIDEO_ROOT = ROOT.parent
DEFAULT_JOBS = VIDEO_ROOT / "tmp" / "video_jobs"


def read_chapter(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def summarize_chapter(text: str, max_chars: int = 400) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
    body = " ".join(lines)
    body = re.sub(r"\s+", " ", body)
    if len(body) <= max_chars:
        return body
    return body[: max_chars - 1] + "…"


def split_scenes(text: str) -> list[str]:
    parts = re.split(r"(?m)^##\s+", text)
    scenes = []
    for p in parts:
        p = p.strip()
        if not p or p.startswith("#"):
            continue
        scenes.append(p[:500])
    if not scenes:
        scenes = [summarize_chapter(text, 800)]
    return scenes


def create_job(mode: str, chapter: Path, aspect: str) -> Path:
    job_id = f"{chapter.stem}_{uuid.uuid4().hex[:8]}"
    job_dir = DEFAULT_JOBS / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    text = read_chapter(chapter)
    if mode == "summary":
        narration = summarize_chapter(text, 350)
        scenes = [{"id": "s01", "narration": narration, "visual_job": "mechanism", "duration_target": 60}]
    else:
        scene_texts = split_scenes(text)
        scenes = [
            {"id": f"s{i+1:02d}", "narration": t, "visual_job": "transition", "duration_target": 8}
            for i, t in enumerate(scene_texts[:8])
        ]
        narration = "\n".join(s["narration"] for s in scenes)
    sb = {
        "job_id": job_id,
        "source_chapter": chapter.name,
        "mode": mode,
        "aspect": aspect,
        "target_duration_sec": 90 if mode == "summary" else 240,
        "voice": "zh-CN-XiaoxiaoNeural",
        "scenes": scenes,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    (job_dir / "storyboard.json").write_text(json.dumps(sb, ensure_ascii=False, indent=2), encoding="utf-8")
    (job_dir / "script.md").write_text(narration if mode == "summary" else narration, encoding="utf-8")
    (job_dir / "job_state.json").write_text(
        json.dumps({"status": "running", "stage": "intake", "job_id": job_id}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return job_dir


def run_drama_segments(job_dir: Path, aspect: str) -> None:
    """Per-scene TTS + visual + mux (knowledge-video style)."""
    sb = json.loads((job_dir / "storyboard.json").read_text(encoding="utf-8"))
    scenes_dir = job_dir / "scenes"
    segments_dir = job_dir / "segments"
    scenes_dir.mkdir(exist_ok=True)
    segments_dir.mkdir(exist_ok=True)
    assets = job_dir / "assets"
    assets.mkdir(exist_ok=True)
    w, h = (1080, 1920) if aspect == "9:16" else (1920, 1080)
    voice = sb.get("voice", "zh-CN-XiaoxiaoNeural")

    for sc in sb["scenes"]:
        sid = sc["id"]
        seg_txt = segments_dir / f"{sid}.txt"
        seg_txt.write_text(sc["narration"].strip(), encoding="utf-8")
        seg_audio = scenes_dir / f"{sid}.mp3"
        subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "tts_edge.py"),
                "--text-file",
                str(seg_txt),
                "--output",
                str(seg_audio),
                "--voice",
                voice,
            ],
            check=True,
        )
        card = assets / f"{sid}.png"
        subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "make_title_card.py"),
                "--text",
                sc["narration"][:80],
                "--output",
                str(card),
                "--width",
                str(w),
                "--height",
                str(h),
            ],
            check=False,
        )
        clip = scenes_dir / f"scene_{sid}.mp4"
        subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "compose_ffmpeg.py"),
                "segment",
                "--job",
                str(job_dir),
                "--image",
                str(card),
                "--audio",
                str(seg_audio),
                "--output",
                str(clip),
                "--aspect",
                aspect,
            ],
            check=True,
        )


def merge_scene_audio(job_dir: Path, output: Path) -> None:
    scenes_dir = job_dir / "scenes"
    parts = sorted(scenes_dir.glob("*.mp3"))
    if not parts:
        return
    list_file = job_dir / "audio_concat.txt"
    list_file.write_text("\n".join(f"file '{p.resolve()}'" for p in parts), encoding="utf-8")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(output)],
        check=True,
    )


def run_pipeline(job_dir: Path, mode: str, aspect: str, subtitles: bool = False) -> int:
    script = job_dir / "script.md"

    if mode == "drama":
        run_drama_segments(job_dir, aspect)
        subprocess.run(
            [sys.executable, str(SCRIPTS / "compose_ffmpeg.py"), "drama", "--job", str(job_dir)],
            check=True,
        )
        if subtitles:
            audio_full = job_dir / "audio_full.mp3"
            merge_scene_audio(job_dir, audio_full)
            if audio_full.exists():
                subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPTS / "beat_lock.py"),
                        "--script",
                        str(script),
                        "--audio",
                        str(audio_full),
                        "--output",
                        str(job_dir / "subtitles.srt"),
                    ],
                    check=False,
                )
    else:
        audio = job_dir / "audio.mp3"
        subprocess.run(
            [sys.executable, str(SCRIPTS / "tts_edge.py"), "--text-file", str(script), "--output", str(audio)],
            check=True,
        )
        if subtitles:
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "beat_lock.py"),
                    "--script",
                    str(script),
                    "--audio",
                    str(audio),
                    "--output",
                    str(job_dir / "subtitles.srt"),
                ],
                check=False,
            )
        subprocess.run(
            [sys.executable, str(SCRIPTS / "compose_ffmpeg.py"), "summary", "--job", str(job_dir), "--aspect", aspect],
            check=True,
        )
    outputs = list((job_dir / "output").glob("*.mp4"))
    if outputs:
        final = outputs[0]
        if subtitles and (job_dir / "subtitles.srt").exists():
            burned = job_dir / "output" / f"{final.stem}_subtitled.mp4"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "burn_subtitles.py"),
                    "--video",
                    str(final),
                    "--srt",
                    str(job_dir / "subtitles.srt"),
                    "--output",
                    str(burned),
                ],
                check=False,
            )
            if burned.exists():
                final = burned
        subprocess.run([sys.executable, str(SCRIPTS / "qc_video.py"), str(final), "--require-audio"], check=False)
        (job_dir / "job_state.json").write_text(
            json.dumps(
                {"status": "succeeded", "stage": "export", "artifacts": [{"type": "video", "path": str(final)}]},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"OK: {final}")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    ch = Path(args.chapter)
    if not ch.exists():
        print(f"ERROR: {ch}", file=sys.stderr)
        return 1
    job = create_job("summary", ch, args.aspect)
    return run_pipeline(job, "summary", args.aspect, subtitles=args.subtitles)


def cmd_drama(args: argparse.Namespace) -> int:
    ch = Path(args.chapter)
    if not ch.exists():
        print(f"ERROR: {ch}", file=sys.stderr)
        return 1
    job = create_job("drama", ch, args.aspect)
    return run_pipeline(job, "drama", args.aspect, subtitles=args.subtitles)


def main() -> int:
    p = argparse.ArgumentParser(prog="novel-video")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("summary")
    s.add_argument("--chapter", required=True)
    s.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1"])
    s.add_argument("--subtitles", action="store_true", help="Generate SRT and burn into output")
    s.set_defaults(func=cmd_summary)
    d = sub.add_parser("drama")
    d.add_argument("--chapter", required=True)
    d.add_argument("--aspect", default="9:16")
    d.add_argument("--subtitles", action="store_true")
    d.set_defaults(func=cmd_drama)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
