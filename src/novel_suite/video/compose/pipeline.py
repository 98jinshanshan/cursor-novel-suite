"""Orchestrate TTS → per-scene compose → concat final video."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

from novel_suite.core import errors as E
from novel_suite.core.paths import suite_root, video_root
from novel_suite.core.result import Result, artifact, error_result, ok_result
from novel_suite.video._legacy import load_video_script
from novel_suite.video.storyboard.schema import validate_storyboard


def _run_command(cmd: list[str], *, timeout: float = 300.0) -> None:
    run_command = load_video_script("subprocess_safe").run_command
    proc = run_command(cmd, check=True, timeout=timeout, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "command failed")


def _aspect_size(aspect: str) -> tuple[int, int]:
    if aspect == "16:9":
        return 1920, 1080
    if aspect == "1:1":
        return 1080, 1080
    return 1080, 1920


def _engine_scripts() -> Path:
    return video_root() / "engine" / "scripts"


def _validate_concat_clips(clips: list[Path], workspace: Path) -> str | None:
    """Ensure concat inputs exist and remain under workspace (path traversal guard)."""
    if not clips:
        return "No clips to concat"
    root = workspace.resolve()
    for clip in clips:
        resolved = clip.resolve()
        if not resolved.is_file():
            return f"Clip missing or not a file: {clip}"
        try:
            resolved.relative_to(root)
        except ValueError:
            return f"Clip outside compose workspace: {clip}"
    return None


def _resolve_still(stills_dir: Path, scene_id: str, index: int) -> Path | None:
    candidates = [
        stills_dir / f"scene_{scene_id}.png",
        stills_dir / f"scene_{index}.png",
        stills_dir / f"scene_s{index + 1:02d}.png",
    ]
    for path in candidates:
        if path.is_file():
            return path
    pngs = sorted(stills_dir.glob("scene_*.png"))
    if index < len(pngs):
        return pngs[index]
    return None


def _synthesize_tts(text: str, output: Path, *, voice: str, temp_dir: Path) -> None:
    script = _engine_scripts() / "tts_edge.py"
    if not text.strip():
        duration = 3.0
        _run_command(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=44100:cl=mono",
                "-t",
                str(duration),
                "-q:a",
                "9",
                "-acodec",
                "libmp3lame",
                str(output),
            ],
            timeout=60,
        )
        return
    tts_input = temp_dir / f"{output.stem}_narration.txt"
    tts_input.write_text(text.strip(), encoding="utf-8")
    _run_command(
        [
            sys.executable,
            str(script),
            "--text-file",
            str(tts_input),
            "--output",
            str(output),
            "--voice",
            voice,
        ],
        timeout=180,
    )


def _format_srt_time(seconds: float) -> str:
    ms = int(seconds * 1000)
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _write_srt(scenes: list[dict[str, Any]], path: Path, *, default_duration: float = 5.0) -> None:
    lines: list[str] = []
    offset = 0.0
    for i, scene in enumerate(scenes, start=1):
        narration = str(scene.get("narration", "") or scene.get("description", "")).strip()
        if not narration:
            continue
        duration = float(scene.get("duration_target", default_duration) or default_duration)
        start = offset
        end = offset + max(duration, 1.0)
        lines.append(str(i))
        lines.append(f"{_format_srt_time(start)} --> {_format_srt_time(end)}")
        lines.append(narration)
        lines.append("")
        offset = end
    path.write_text("\n".join(lines), encoding="utf-8")


def _burn_subtitles(video: Path, srt: Path, output: Path) -> None:
    script = _engine_scripts() / "burn_subtitles.py"
    _run_command(
        [
            sys.executable,
            str(script),
            "--video",
            str(video),
            "--srt",
            str(srt),
            "--output",
            str(output),
        ],
        timeout=600,
    )


def compose_video(
    storyboard_path: Path,
    stills_dir: Path,
    output_path: Path,
    *,
    voice: str = "zh-CN-XiaoxiaoNeural",
    aspect: str = "9:16",
    subtitles: bool = False,
) -> Result:
    """Compose per-scene segments into a single summary MP4."""
    if not shutil.which("ffmpeg"):
        return error_result(
            E.COMPOSE_FFMPEG_MISSING,
            "ffmpeg not found on PATH",
            next_actions=["Install FFmpeg and ensure it is on PATH"],
        )

    if not storyboard_path.is_file():
        return error_result(
            E.COMPOSE_STORYBOARD_MISSING,
            f"Storyboard not found: {storyboard_path}",
            next_actions=["novel-suite video storyboard --project ... --json"],
        )
    if not stills_dir.is_dir():
        return error_result(
            E.COMPOSE_STILLS_MISSING,
            f"Stills dir not found: {stills_dir}",
            next_actions=["novel-suite video stills generate --mode proof --json"],
        )

    sb = json.loads(storyboard_path.read_text(encoding="utf-8"))
    schema_errors = validate_storyboard(sb)
    if schema_errors:
        return error_result(
            E.COMPOSE_STORYBOARD_INVALID,
            f"Storyboard schema invalid: {schema_errors[0]}",
            next_actions=["novel-suite video storyboard --project ... --json"],
            validation_errors=schema_errors,
        )

    scenes = sb.get("scenes", [])
    if not scenes:
        return error_result(E.COMPOSE_NO_SCENES, "Storyboard has no scenes")

    voice = str(sb.get("voice", voice))
    aspect = str(sb.get("aspect", aspect))
    w, h = _aspect_size(aspect)
    compose_mod = load_video_script("compose_ffmpeg")

    temp_dir = output_path.parent / ".compose_temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    segment_files: list[Path] = []

    try:
        for i, scene in enumerate(scenes):
            scene_id = str(scene.get("id", f"scene_{i}"))
            still_path = _resolve_still(stills_dir, scene_id, i)
            if still_path is None:
                continue

            narration = str(scene.get("narration", "") or scene.get("description", "")).strip()
            audio_path = temp_dir / f"seg_{i:02d}_audio.mp3"
            seg_path = temp_dir / f"seg_{i:02d}_final.mp4"

            _synthesize_tts(narration, audio_path, voice=voice, temp_dir=temp_dir)
            compose_mod.compose_scene_segment(
                still_path.resolve(),
                audio_path.resolve(),
                seg_path.resolve(),
                w,
                h,
            )
            segment_files.append(seg_path)

        if not segment_files:
            return error_result(
                E.COMPOSE_NO_SEGMENTS,
                "No segments composed — check stills filenames (scene_<id>.png)",
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        merged = temp_dir / "merged.mp4"
        concat_err = _validate_concat_clips(segment_files, temp_dir)
        if concat_err:
            return error_result(E.COMPOSE_CONCAT_PATH_INVALID, concat_err)
        compose_mod.concat_scene_clips(segment_files, merged)

        final_path = output_path
        if subtitles:
            srt_path = temp_dir / "subtitles.srt"
            _write_srt(scenes, srt_path)
            if srt_path.is_file() and srt_path.stat().st_size > 0:
                subbed = output_path.with_name(f"{output_path.stem}_subtitled{output_path.suffix}")
                _burn_subtitles(merged, srt_path, subbed)
                final_path = subbed
            else:
                shutil.copy(merged, output_path)
                final_path = output_path
        else:
            shutil.copy(merged, output_path)

    except (OSError, RuntimeError, FileNotFoundError) as exc:
        return error_result(E.COMPOSE_FAILED, str(exc))

    root = suite_root()
    try:
        rel = final_path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        rel = str(final_path.resolve())

    return ok_result(
        E.COMPOSE_OK,
        f"Video composed: {len(segment_files)} scene(s) → {final_path.name}",
        artifacts=[artifact(rel, kind="video", label="final")],
        segment_count=len(segment_files),
        aspect=aspect,
        subtitles=subtitles,
        output_path=rel,
    )
