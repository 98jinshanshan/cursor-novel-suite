#!/usr/bin/env python3
"""VideoRender-1 — ch02 motion-drama local render orchestrator (honest route B/C)."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CH02 = ROOT / "novels" / "novel-837dd4f1" / "video" / "ch02"
LOCAL_ACCEL = ROOT / "tools" / "local-accel" / "local_accel.py"
TTS = ROOT / "cursor-novel-video" / "engine" / "scripts" / "tts_edge.py"
KEN_BURNS = ROOT / "cursor-novel-video" / "engine" / "scripts" / "ken_burns.py"
BURN_SUB = ROOT / "cursor-novel-video" / "engine" / "scripts" / "burn_subtitles.py"


def _run_json(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"raw": proc.stdout, "stderr": proc.stderr, "code": proc.returncode}


def write_local_accel_report() -> dict:
    py = sys.executable
    doctor = _run_json([py, str(LOCAL_ACCEL), "doctor", "--json"])
    lines = [
        "# Local Accel Report — Ch.02 VideoRender-1",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## GPU",
        f"- available: {doctor.get('gpu', {}).get('available')}",
        f"- name: {doctor.get('gpu', {}).get('name')}",
        "",
        "## FFmpeg",
        f"- available: {doctor.get('ffmpeg', {}).get('available')}",
        f"- nvenc: {doctor.get('ffmpeg', {}).get('nvenc', [])}",
        "",
        "## ComfyUI",
        f"- available: {doctor.get('comfyui', {}).get('available')}",
        f"- detail: {doctor.get('comfyui', {})}",
        "",
        "## Ollama",
        f"- available: {doctor.get('ollama', {}).get('available')}",
        "",
        "## Note",
        "Detection only; services not started by this script.",
        "",
        "```json",
        json.dumps(doctor, ensure_ascii=False, indent=2),
        "```",
    ]
    CH02.mkdir(parents=True, exist_ok=True)
    (CH02 / "local_accel_report.md").write_text("\n".join(lines), encoding="utf-8")
    return doctor


def _placeholder_png(path: Path, *, hue: int, label: str) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        # Minimal PPM via raw bytes if no PIL — skip
        path.parent.mkdir(parents=True, exist_ok=True)
        # 1080x1920 dark frame via ffmpeg instead
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x{hue:06x}:s=1080x1920:d=1",
                "-frames:v", "1", str(path.with_suffix(".png")),
            ],
            capture_output=True,
            timeout=60,
            check=False,
        )
        return
    img = Image.new("RGB", (1080, 1920), color=((hue >> 16) & 255, (hue >> 8) & 255, hue & 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([80, 800, 1000, 1120], outline=(200, 200, 200), width=3)
    draw.text((120, 860), label[:40], fill=(230, 230, 230))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def generate_visuals(doctor: dict) -> tuple[list[Path], str]:
    visuals_dir = CH02 / "visuals"
    visuals_dir.mkdir(parents=True, exist_ok=True)
    hues = [0x0f1419, 0x1a2332, 0x15202b, 0x1c2a3a, 0x101820, 0x182430, 0x141c28, 0x1e2836, 0x121a24, 0x16202c]
    shots: list[Path] = []
    comfy = doctor.get("comfyui", {}).get("available")
    source = "comfyui" if comfy else "placeholder_non_ai"
    with (CH02 / "shot_list.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for i, row in enumerate(rows[:10]):
        sid = row["shot_id"]
        out = visuals_dir / f"shot_{sid}.png"
        label = f"{sid} {row.get('location_id','')}"
        _placeholder_png(out, hue=hues[i % len(hues)], label=label)
        if out.is_file():
            shots.append(out)
    return shots, source


def generate_tts() -> tuple[Path | None, str]:
    script = CH02 / "narration_script.md"
    if not script.is_file():
        return None, "missing_narration_script"
    text_lines = []
    for line in script.read_text(encoding="utf-8").splitlines():
        if line.startswith("**VO:**") or line.startswith("**对白"):
            text_lines.append(line.split(":", 1)[-1].strip())
    text = "\n".join(text_lines)[:4000]
    audio_dir = CH02 / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    out = audio_dir / "narration.mp3"
    txt = audio_dir / "narration_input.txt"
    txt.write_text(text, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(TTS), "--text-file", str(txt), "--output", str(out), "--voice", "zh-CN-YunxiNeural"],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if proc.returncode == 0 and out.is_file() and out.stat().st_size > 500:
        return out, "edge_tts_ok"
    return None, f"tts_blocked: {(proc.stderr or proc.stdout or '')[:200]}"


def compose_mp4(visuals: list[Path], audio: Path | None, doctor: dict) -> tuple[Path | None, dict]:
    out_dir = CH02 / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = out_dir / "ch02_motion_drama_9x16.mp4"
    if not visuals:
        return None, {"error": "no_visuals"}
    seg_dir = CH02 / "segments"
    seg_dir.mkdir(exist_ok=True)
    clips: list[Path] = []
    dur_each = 6.0
    for i, img in enumerate(visuals[:8]):
        seg = seg_dir / f"seg_{i:02d}.mp4"
        subprocess.run(
            [
                "ffmpeg", "-y", "-loop", "1", "-i", str(img),
                "-t", str(dur_each), "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", str(seg),
            ],
            capture_output=True,
            timeout=120,
            check=False,
        )
        if seg.is_file():
            clips.append(seg)
    if not clips:
        return None, {"error": "no_segments"}
    list_f = seg_dir / "concat.txt"
    list_f.write_text("\n".join(f"file '{p.resolve()}'" for p in clips), encoding="utf-8")
    merged = seg_dir / "merged.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_f), "-c", "copy", str(merged)],
        capture_output=True,
        timeout=120,
        check=False,
    )
    if not merged.is_file():
        return None, {"error": "concat_failed"}
    nvenc = doctor.get("ffmpeg", {}).get("nvenc", [])
    vcodec = "h264_nvenc" if "h264_nvenc" in nvenc else "libx264"
    cmd = ["ffmpeg", "-y", "-i", str(merged)]
    if audio and audio.is_file():
        cmd.extend(["-i", str(audio)])
    cmd.extend(["-map", "0:v:0"])
    if audio and audio.is_file():
        cmd.extend(["-map", "1:a:0", "-c:a", "aac", "-shortest"])
    else:
        cmd.append("-an")
    cmd.extend(["-c:v", vcodec, "-pix_fmt", "yuv420p", str(out_mp4)])
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=False)
    meta = {"vcodec": vcodec, "returncode": proc.returncode, "stderr_tail": (proc.stderr or "")[-300:]}
    if out_mp4.is_file() and out_mp4.stat().st_size > 1000:
        return out_mp4, meta
    return None, meta


def ffprobe_meta(path: Path) -> dict:
    proc = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration,size",
            "-show_entries", "stream=codec_type,width,height",
            "-of", "json", str(path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {}


def write_qc_and_nvp(
    doctor: dict,
    *,
    route: str,
    visuals: list[Path],
    audio_status: str,
    mp4: Path | None,
    visual_source: str,
) -> str:
    comfy = doctor.get("comfyui", {}).get("available")
    has_tts = audio_status == "edge_tts_ok"
    # Hard rule: ComfyUI not run → max C
    video_level = "C"
    not_ai = True
    probe = ffprobe_meta(mp4) if mp4 and mp4.is_file() else {}
    duration = probe.get("format", {}).get("duration", "n/a")
    size = probe.get("format", {}).get("size", "n/a")
    streams = probe.get("streams", [])
    has_video = any(s.get("codec_type") == "video" for s in streams)
    has_audio = any(s.get("codec_type") == "audio" for s in streams)

    qc = f"""# Video QC Report — Ch.02 双签 (VideoRender-1)

## Execute

- Route: **{route}**
- ComfyUI available: {comfy}
- Visual source: {visual_source}
- TTS status: {audio_status}

## Checks

| 检查 | 结果 |
| --- | --- |
| 母版 MP4 | {'pass' if mp4 and mp4.is_file() else 'fail'} |
| 路径 | `{mp4}` |
| 大小 bytes | {size} |
| 时长 sec | {duration} |
| video stream | {has_video} |
| audio stream | {has_audio} |
| visuals count | {len(visuals)} |
| ComfyUI ch02 invoke | **fail** |
| 真实 AI 短剧 | **fail** |

## Summary

video_level: {video_level}
not_ai_short_drama: {str(not_ai).lower()}
reason: ComfyUI unavailable; placeholder_non_ai visuals; not motion-drama I2V

## Verdict

- verdict: blocked
- commercial_release_allowed: false
- video_level: {video_level}
- handoff_allowed: false

## Handoff

1. Start ComfyUI at 127.0.0.1:8188 or 8000
2. Regenerate visuals/shot_*.png via ComfyUI (not placeholders)
3. Re-run Wan I2V + TTS; target video_level A/B
"""
    (CH02 / "video_qc_report.md").write_text(qc, encoding="utf-8")

    v1d = f"""# NVP-V1D Motion Drama Result — Ch.02

## Verdict: **fail** (grade C)

- ComfyUI: {comfy}
- I2V segments: none
- visuals: {len(visuals)} placeholder frames
- not_ai_short_drama: true
"""
    (CH02 / "NVP-V1D-motion-drama.result.md").write_text(v1d, encoding="utf-8")
    reports = ROOT / "novels" / "novel-837dd4f1" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    v2 = f"""# NVP-V2 Video Export QC Result — Ch.02

## Verdict: **fail** (grade C)

- video_level: C
- mp4: {mp4}
- ComfyUI/TTS not sufficient for A/B
"""
    (reports / "NVP-V2-video-export-qc.result.md").write_text(v2, encoding="utf-8")
    (CH02 / "NVP-V2-video-export-qc.result.md").write_text(v2, encoding="utf-8")

    blockers = f"""# Video Generation Blockers — Ch.02 (updated VideoRender-1)

| ID | blocker | status |
| --- | --- | --- |
| B1 | ComfyUI not reachable (8188/8000) | **open** |
| B2 | TTS: {audio_status} | {'closed' if has_tts else 'open'} |
| B3 | No Wan I2V segments | **open** |
| B4 | Placeholder visuals only | **open** |
| B5 | video_level capped at C | **open** |

## Honest Status

- Engineering preview MP4 may exist; **NOT** AI short drama.
- not_ai_short_drama: true
"""
    (CH02 / "video_generation_blockers.md").write_text(blockers, encoding="utf-8")
    return video_level


def write_manifest(route: str, doctor: dict, visuals: list[Path], audio_status: str, mp4: Path | None, video_level: str) -> None:
    manifest = {
        "pipeline": "VideoRender-1",
        "route": route,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "comfyui_available": doctor.get("comfyui", {}).get("available"),
        "ffmpeg_available": doctor.get("ffmpeg", {}).get("available"),
        "nvenc": doctor.get("ffmpeg", {}).get("nvenc", []),
        "visuals_count": len(visuals),
        "audio_status": audio_status,
        "output_mp4": str(mp4) if mp4 else None,
        "video_level": video_level,
        "not_ai_short_drama": True,
        "commercial_release_allowed": False,
        "verdict": "blocked",
    }
    (CH02 / "render_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    doctor = write_local_accel_report()
    comfy = doctor.get("comfyui", {}).get("available")
    ffmpeg_ok = doctor.get("ffmpeg", {}).get("available")
    if not ffmpeg_ok:
        ps1 = CH02 / "generate_ch02_motion_drama.ps1"
        ps1.write_text(
            "# Requires FFmpeg + ComfyUI\nWrite-Error 'FFmpeg missing'\n",
            encoding="utf-8",
        )
        (CH02 / "render_blocked_report.md").write_text("# Render blocked\nFFmpeg missing\n", encoding="utf-8")
        print(json.dumps({"status": "blocked", "reason": "ffmpeg_missing"}, ensure_ascii=False))
        return 1

    route = "A" if comfy else "B"
    visuals, visual_source = generate_visuals(doctor)
    audio, audio_status = generate_tts()
    mp4, compose_meta = compose_mp4(visuals, audio, doctor)
    if mp4 and (CH02 / "subtitles.srt").is_file():
        sub_out = CH02 / "output" / "ch02_motion_drama_9x16_subtitled.mp4"
        subprocess.run(
            [sys.executable, str(BURN_SUB), "--video", str(mp4), "--srt", str(CH02 / "subtitles.srt"), "--output", str(sub_out)],
            capture_output=True,
            timeout=300,
            check=False,
        )

    video_level = write_qc_and_nvp(
        doctor, route=route, visuals=visuals, audio_status=audio_status, mp4=mp4, visual_source=visual_source
    )
    write_manifest(route, doctor, visuals, audio_status, mp4, video_level)

    # Update project manifest overall grade stays C
    rep = ROOT / "novels" / "novel-837dd4f1" / "reports" / "realpipeline_2b_nvp_manifest.json"
    if rep.is_file():
        data = json.loads(rep.read_text(encoding="utf-8"))
        data["video_level"] = video_level
        data["overall_grade"] = "C"
        data["weakest_link"] = "video"
        data["videorender_1"] = True
        rep.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    result = {
        "status": "ok" if mp4 else "partial",
        "route": route,
        "video_level": video_level,
        "mp4": str(mp4) if mp4 else None,
        "visuals": len(visuals),
        "audio_status": audio_status,
        "compose": compose_meta,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if mp4 else 2


if __name__ == "__main__":
    raise SystemExit(main())
