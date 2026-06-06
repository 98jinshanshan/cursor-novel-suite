#!/usr/bin/env python3
"""FFmpeg compose for summary and drama modes."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from result_contract import emit_result
from subprocess_safe import check_output, run_command

def make_title_card(text: str, out: Path, w: int, h: int) -> None:
    run_command(
        [sys.executable, str(Path(__file__).parent / "make_title_card.py"),
         "--text", text, "--output", str(out), "--width", str(w), "--height", str(h)],
        check=True,
        timeout=120,
    )


def probe_duration(path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ]
    out = check_output(cmd, timeout=60).strip()
    return float(out)


def compose_summary(job_dir: Path, aspect: str) -> Path:
    if aspect == "9:16":
        w, h = 1080, 1920
    elif aspect == "16:9":
        w, h = 1920, 1080
    else:
        w, h = 1080, 1080

    sb_path = job_dir / "storyboard.json"
    sb = json.loads(sb_path.read_text(encoding="utf-8"))
    assets = job_dir / "assets"
    assets.mkdir(exist_ok=True)
    visual = assets / "comfyui_slide.png"
    if not visual.is_file():
        visual = assets / "slide.png"
    if not visual.is_file():
        card = assets / "title.png"
        title = sb.get("source_chapter", "章节摘要")
        make_title_card(title, card, w, h)
        visual = card

    clip = job_dir / "clip.mp4"
    run_command(
        [sys.executable, str(Path(__file__).parent / "ken_burns.py"),
         "--image", str(visual), "--duration", "3", "--output", str(clip),
         "--width", str(w), "--height", str(h)],
        check=True,
        timeout=300,
    )

    audio = job_dir / "audio.mp3"
    if not audio.exists():
        raise FileNotFoundError(f"Missing {audio}; run tts_edge.py first")

    out = job_dir / "output" / f"{sb.get('job_id', 'video')}_summary.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    dur = max(probe_duration(audio), probe_duration(clip))
    cmd = [
        "ffmpeg", "-y",
        "-i", str(clip), "-i", str(audio),
        "-filter_complex", f"[0:v]tpad=stop_mode=clone:stop_duration={dur}[v]",
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-c:a", "aac", "-shortest", str(out),
    ]
    run_command(cmd, check=True, timeout=600)
    return out


def compose_segment_video(video: Path, audio: Path, output: Path) -> Path:
    """Mux I2V clip with scene TTS; pad/trim video to audio length."""
    if not video.is_file():
        raise FileNotFoundError(f"Missing scene video: {video}")
    if not audio.is_file():
        raise FileNotFoundError(f"Missing scene audio: {audio}")
    dur = max(probe_duration(audio), 1.0)
    output.parent.mkdir(parents=True, exist_ok=True)
    run_command(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-i",
            str(audio),
            "-filter_complex",
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,"
            f"tpad=stop_mode=clone:stop_duration={dur}[v]",
            "-map",
            "[v]",
            "-map",
            "1:a",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-shortest",
            str(output),
        ],
        check=True,
        timeout=600,
    )
    return output


def compose_scene_segment(image: Path, audio: Path, output: Path, w: int, h: int) -> Path:
    """Per-segment compose: Ken Burns visual synced to scene TTS (knowledge-video style)."""
    if not audio.is_file():
        raise FileNotFoundError(f"Missing scene audio: {audio}")
    dur = max(probe_duration(audio), 1.0)
    vis = output.with_name(output.stem + "_vis.mp4")
    run_command(
        [
            sys.executable,
            str(Path(__file__).parent / "ken_burns.py"),
            "--image",
            str(image),
            "--duration",
            str(dur),
            "--output",
            str(vis),
            "--width",
            str(w),
            "--height",
            str(h),
        ],
        check=True,
        timeout=300,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    run_command(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(vis),
            "-i",
            str(audio),
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-shortest",
            str(output),
        ],
        check=True,
        timeout=600,
    )
    vis.unlink(missing_ok=True)
    return output


def concat_scene_clips(clips: list[Path], output: Path) -> Path:
    if not clips:
        raise FileNotFoundError("No scene clips to concat")
    list_file = output.parent / "concat_scenes.txt"
    list_file.write_text("\n".join(f"file '{p.resolve()}'" for p in clips), encoding="utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    run_command(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(output)],
        check=True,
        timeout=600,
    )
    return output


def compose_drama(job_dir: Path) -> Path:
    sb = json.loads((job_dir / "storyboard.json").read_text(encoding="utf-8"))
    scenes_dir = job_dir / "scenes"
    parts = sorted(scenes_dir.glob("scene_s*.mp4"), key=lambda p: p.name)
    if not parts:
        parts = sorted(scenes_dir.glob("scene_*.mp4"), key=lambda p: p.name)
    if not parts:
        raise FileNotFoundError("No per-scene clips in scenes/ (run segment pipeline first)")
    merged = job_dir / "merged.mp4"
    concat_scene_clips(parts, merged)
    mode = sb.get("mode", "drama")
    suffix = {"motion-comic": "motion_comic", "motion-drama": "motion_drama"}.get(mode, "drama")
    out = job_dir / "output" / f"{sb['job_id']}_{suffix}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(merged, out)
    return out


def main() -> int:
    if not shutil.which("ffmpeg"):
        print("ERROR: ffmpeg required", file=sys.stderr)
        return 1
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["summary", "drama", "resize", "segment", "segment_video"])
    ap.add_argument("--job", type=Path)
    ap.add_argument("--aspect", default="9:16")
    ap.add_argument("--input", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--image", type=Path)
    ap.add_argument("--audio", type=Path)
    args = ap.parse_args()
    if args.mode == "summary":
        if not args.job:
            print("summary needs --job", file=sys.stderr)
            return 1
        out = compose_summary(args.job.resolve(), args.aspect)
    elif args.mode == "drama":
        if not args.job:
            print("drama needs --job", file=sys.stderr)
            return 1
        out = compose_drama(args.job.resolve())
    elif args.mode == "segment_video":
        if not args.input or not args.audio or not args.output:
            print("segment_video needs --input --audio --output", file=sys.stderr)
            return 1
        out = compose_segment_video(args.input.resolve(), args.audio.resolve(), args.output.resolve())
    elif args.mode == "segment":
        if not args.image or not args.audio or not args.output:
            print("segment needs --image --audio --output", file=sys.stderr)
            return 1
        if args.aspect == "9:16":
            w, h = 1080, 1920
        elif args.aspect == "16:9":
            w, h = 1920, 1080
        else:
            w, h = 1080, 1080
        out = compose_scene_segment(args.image.resolve(), args.audio.resolve(), args.output.resolve(), w, h)
    else:
        if not args.input or not args.output:
            print("resize needs --input --output", file=sys.stderr)
            return 1
        run_command(
            ["ffmpeg", "-y", "-i", str(args.input), "-vf", "scale=1080:1920", str(args.output)],
            check=True,
            timeout=600,
        )
        out = args.output
    print(f"OK: {out}")
    emit_result("ok", path=str(out), mode=args.mode)
    return 0


if __name__ == "__main__":
    sys.exit(main())
