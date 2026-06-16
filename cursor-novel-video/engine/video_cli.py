#!/usr/bin/env python3
"""Novel-to-video CLI."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
VIDEO_ROOT = ROOT.parent
ADAPTERS = VIDEO_ROOT / "adapters"
COMFYUI_RENDER = ADAPTERS / "comfyui_render.py"
COMFYUI_I2V = ADAPTERS / "comfyui_i2v.py"
DEFAULT_JOBS = VIDEO_ROOT / "tmp" / "video_jobs"

sys.path.insert(0, str(SCRIPTS))
from novel_bind import infer_novel_binding, job_dir_rel, record_video_job, storyboard_novel_block
from result_contract import emit_error, emit_result


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


def resolve_chapter(chapter: str | Path, project: Path | None) -> Path:
    try:
        from novel_suite.video.chapter_paths import resolve_chapter_path

        return resolve_chapter_path(str(chapter), project)
    except ImportError:
        ch = Path(chapter)
        if project is not None:
            root = project.resolve()
            if ch.is_absolute():
                return ch.resolve()
            direct = (root / ch).resolve()
            if direct.is_file():
                return direct
            if len(ch.parts) == 1:
                return (root / "chapters" / ch).resolve()
            return direct
        return ch.resolve()


def create_job(
    mode: str,
    chapter: Path,
    aspect: str,
    *,
    binding: dict | None = None,
    visual_backend: str = "static",
    comfyui_profile: str = "minimal",
) -> Path:
    job_id = f"{chapter.stem}_{uuid.uuid4().hex[:8]}"
    job_dir = DEFAULT_JOBS / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    text = read_chapter(chapter)
    if mode == "summary":
        narration = summarize_chapter(text, 350)
        scenes = [{"id": "s01", "narration": narration, "visual_job": "mechanism", "duration_target": 60}]
    elif mode in ("motion-comic", "motion-drama"):
        narration = ""
        scenes = []
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
        "target_duration_sec": 90
        if mode == "summary"
        else (90 if mode == "motion-drama" else (180 if mode == "motion-comic" else 240)),
        "voice": "zh-CN-XiaoxiaoNeural",
        "visual_backend": visual_backend,
        "scenes": scenes,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if visual_backend == "comfyui":
        if mode in ("motion-comic", "motion-drama"):
            sb["comfyui"] = {"profile": comfyui_profile, "style": "realistic", "pipeline": "still+i2v"}
        else:
            narration_preview = narration[:200] if mode == "summary" else (scenes[0]["narration"][:200] if scenes else "")
            sb["comfyui"] = {
                "profile": comfyui_profile,
                "positive_prompt": f"cinematic photorealistic police suspense, cold tone, {narration_preview}",
            }
    if binding:
        sb["novel"] = storyboard_novel_block(binding)
        sb["source_chapter"] = binding.get("source_chapter", chapter.name)
    (job_dir / "storyboard.json").write_text(json.dumps(sb, ensure_ascii=False, indent=2), encoding="utf-8")
    (job_dir / "script.md").write_text(narration if mode == "summary" else narration, encoding="utf-8")
    state: dict = {"status": "running", "stage": "intake", "job_id": job_id}
    if binding:
        state["novel_slug"] = binding["novel_slug"]
        state["novel_project"] = binding["novel_project"]
        state["source_chapter"] = binding["source_chapter"]
    (job_dir / "job_state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if binding:
        record_video_job(binding, job_id=job_id, job_dir=job_dir, mode=mode, status="running")
    return job_dir


def run_platform_gate(
    phase: str,
    *,
    project: Path | None,
    chapter: Path | None = None,
    job_dir: Path | None = None,
    mode: str = "motion-comic",
    video: Path | None = None,
) -> int:
    cmd = [sys.executable, str(SCRIPTS / "platform_publish_gate.py"), "--phase", phase, "--mode", mode]
    if project:
        cmd.extend(["--project", str(project)])
    if chapter:
        cmd.extend(["--chapter", str(chapter)])
    if job_dir:
        cmd.extend(["--job", str(job_dir)])
    if video:
        cmd.extend(["--video", str(video)])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.stderr.strip():
        print(r.stderr.strip(), file=sys.stderr)
    return r.returncode


def build_character_assets(
    job_dir: Path,
    project: Path,
    *,
    chapter_key: str = "ch01",
    render_refs: bool = False,
) -> int:
    cmd = [
        sys.executable,
        str(SCRIPTS / "character_asset_pack.py"),
        "--project",
        str(project),
        "--job",
        str(job_dir),
        "--chapter-key",
        chapter_key,
    ]
    if render_refs:
        cmd.append("--render-refs")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.stderr.strip():
        print(r.stderr.strip(), file=sys.stderr)
    return r.returncode


def run_character_ref_qc(job_dir: Path, project: Path, *, chapter_key: str = "ch01") -> int:
    cvdp = project / "video" / chapter_key / "character_visual_design.json"
    if not cvdp.is_file():
        print(f"WARN: CVDP missing, skip character_ref_qc: {cvdp}", file=sys.stderr)
        return 0
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "character_ref_qc.py"),
            "--job",
            str(job_dir),
            "--cvdp",
            str(cvdp),
        ],
        capture_output=True,
        text=True,
    )
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.stderr.strip():
        print(r.stderr.strip(), file=sys.stderr)
    return r.returncode


def build_motion_drama_shots(job_dir: Path, chapter: Path, project: Path) -> int:
    chapter_dir = project / "video" / "ch01"
    shots_json = chapter_dir / "shots.json"
    if shots_json.is_file():
        r = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "screenplay_to_shots.py"),
                "--project",
                str(project),
                "--chapter-dir",
                str(chapter_dir),
                "--job",
                str(job_dir),
            ],
            capture_output=True,
            text=True,
        )
    else:
        r = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "script_to_shots.py"),
                "--chapter",
                str(chapter),
                "--project",
                str(project),
                "--job",
                str(job_dir),
            ],
            capture_output=True,
            text=True,
        )
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr.strip(), file=sys.stderr)
    return r.returncode


def build_motion_comic_storyboard(job_dir: Path, chapter: Path, project: Path) -> int:
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "storyboard_from_chapter.py"),
            "--chapter",
            str(chapter),
            "--project",
            str(project),
            "--job",
            str(job_dir),
        ],
        capture_output=True,
        text=True,
    )
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr.strip(), file=sys.stderr)
    return r.returncode


def run_comfyui_scene(job_dir: Path, scene: dict, *, strict: bool = False) -> Path | None:
    """Render one scene still to assets/{id}.png."""
    sb = json.loads((job_dir / "storyboard.json").read_text(encoding="utf-8"))
    if sb.get("visual_backend") != "comfyui":
        return None
    sid = scene["id"]
    assets = job_dir / "assets"
    assets.mkdir(exist_ok=True)
    out = assets / f"{sid}.png"
    positive = scene.get("visual_positive") or scene.get("static_prompt") or scene.get("narration", "")[:200]
    profile = (sb.get("comfyui") or {}).get("profile", "minimal")
    os.environ["COMFYUI_STYLE"] = "realistic"
    brief_path = job_dir / "visual-brief.json"
    if brief_path.is_file():
        brief = json.loads(brief_path.read_text(encoding="utf-8"))
        for ckpt in brief.get("checkpoint_preference", []):
            os.environ["COMFYUI_CKPT"] = ckpt
            break
    wf: Path | None = None
    if os.environ.get("COMFYUI_WORKFLOW_JSON"):
        wf = Path(os.environ["COMFYUI_WORKFLOW_JSON"])
    shot_size = str(scene.get("shot_size", "")).lower()
    portrait = "close" in shot_size or "face" in shot_size
    cmd = [
        sys.executable,
        str(COMFYUI_RENDER),
        "--prompt",
        positive,
        "--output",
        str(out),
        "--profile",
        profile,
    ]
    if portrait:
        cmd.append("--portrait")
    if wf and wf.is_file():
        cmd.extend(["--workflow", str(wf)])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.returncode != 0 or not out.is_file():
        msg = f"ComfyUI still failed for {sid}: {r.stderr.strip()}"
        if strict:
            raise RuntimeError(msg)
        print(f"WARN: {msg}", file=sys.stderr)
        return None
    return out


def run_comfyui_i2v(job_dir: Path, scene: dict, still: Path, *, strict: bool = False) -> Path | None:
    sid = scene["id"]
    i2v_dir = job_dir / "scenes" / "i2v"
    i2v_dir.mkdir(parents=True, exist_ok=True)
    out = i2v_dir / f"{sid}.mp4"
    motion = scene.get("motion_prompt") or "subtle cinematic motion, environmental movement"
    dur = float(scene.get("duration_target", scene.get("duration_sec", 4)))
    cmd = [
        sys.executable,
        str(COMFYUI_I2V),
        "--image",
        str(still),
        "--output",
        str(out),
        "--motion-prompt",
        motion,
        "--duration",
        str(dur),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.stderr.strip():
        print(r.stderr.strip(), file=sys.stderr)
    if r.returncode != 0 or not out.is_file():
        msg = f"ComfyUI i2v failed for {sid}"
        if strict:
            raise RuntimeError(msg)
        return None
    return out


def run_comfyui_visual(job_dir: Path) -> bool:
    """Queue ComfyUI image to assets/comfyui_slide.png. False → compose uses title card."""
    sb = json.loads((job_dir / "storyboard.json").read_text(encoding="utf-8"))
    if sb.get("visual_backend") != "comfyui":
        return False
    assets = job_dir / "assets"
    assets.mkdir(exist_ok=True)
    out = assets / "comfyui_slide.png"
    comfy = sb.get("comfyui") or {}
    positive = comfy.get("positive_prompt") or (job_dir / "script.md").read_text(encoding="utf-8")[:200]
    profile = comfy.get("profile", "minimal")
    wf: Path | None = None
    wf_env = os.environ.get("COMFYUI_WORKFLOW_JSON")
    if wf_env:
        wf = Path(wf_env)
    elif comfy.get("workflow_json"):
        wf = Path(str(comfy["workflow_json"]))
    cmd = [
        sys.executable,
        str(COMFYUI_RENDER),
        "--prompt",
        positive,
        "--output",
        str(out),
        "--profile",
        profile,
    ]
    if wf and wf.is_file():
        cmd.extend(["--workflow", str(wf)])
    _write_job_state(job_dir, {"status": "running", "stage": "comfyui", "job_id": job_dir.name})
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.returncode != 0:
        print(f"WARN: ComfyUI render failed ({r.stderr.strip()}); using title card", file=sys.stderr)
        return False
    return out.is_file()


def run_motion_drama_segments(job_dir: Path, aspect: str, *, visual_backend: str = "comfyui") -> None:
    """Per-shot: TTS → still (required) → I2V (required) → mux. No title-card fallback."""
    sb = json.loads((job_dir / "storyboard.json").read_text(encoding="utf-8"))
    visual_backend = sb.get("visual_backend", visual_backend)
    if visual_backend != "comfyui":
        raise RuntimeError("motion-drama requires --visual-backend comfyui")
    scenes_dir = job_dir / "scenes"
    segments_dir = job_dir / "segments"
    scenes_dir.mkdir(exist_ok=True)
    segments_dir.mkdir(exist_ok=True)
    voice = sb.get("voice", "zh-CN-XiaoxiaoNeural")
    strict = True

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
        still = run_comfyui_scene(job_dir, sc, strict=strict)
        if not still:
            raise RuntimeError(f"missing still for {sid}")
        i2v = run_comfyui_i2v(job_dir, sc, still, strict=strict)
        if not i2v:
            raise RuntimeError(f"missing i2v for {sid}")
        clip = scenes_dir / f"scene_{sid}.mp4"
        subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "compose_ffmpeg.py"),
                "segment_video",
                "--input",
                str(i2v),
                "--audio",
                str(seg_audio),
                "--output",
                str(clip),
            ],
            check=True,
        )


def run_drama_segments(
    job_dir: Path,
    aspect: str,
    *,
    visual_backend: str = "static",
    forbid_title_card: bool = False,
) -> None:
    """Per-scene TTS + visual + mux (knowledge-video style)."""
    sb = json.loads((job_dir / "storyboard.json").read_text(encoding="utf-8"))
    visual_backend = sb.get("visual_backend", visual_backend)
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
        if visual_backend == "comfyui":
            img = run_comfyui_scene(job_dir, sc, strict=forbid_title_card)
            if img:
                card = img
            elif forbid_title_card:
                raise RuntimeError(f"ComfyUI still required for {sid}; title-card fallback disabled")
            else:
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
        elif forbid_title_card:
            raise RuntimeError(f"static backend not allowed for strict mode ({sid})")
        else:
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


def _load_binding(job_dir: Path) -> dict | None:
    sb_path = job_dir / "storyboard.json"
    if not sb_path.is_file():
        return None
    sb = json.loads(sb_path.read_text(encoding="utf-8"))
    novel = sb.get("novel")
    if not isinstance(novel, dict) or not novel.get("slug"):
        return None
    return {
        "novel_slug": novel["slug"],
        "novel_title": novel.get("title"),
        "novel_project": novel.get("project", ""),
        "source_chapter": novel.get("chapter") or sb.get("source_chapter", ""),
        "in_registry": bool(novel.get("in_registry")),
    }


def _write_failed_completion(job_dir: Path, note: str, mode: str) -> None:
    try:
        from video_node_completion import write_job_completion_failed  # noqa: PLC0415

        write_job_completion_failed(job_dir, note=note, mode=mode)
    except Exception as exc:  # noqa: BLE001
        print(f"WARN: node.completion.json (failed) not written: {exc}", file=sys.stderr)


def _write_job_state(job_dir: Path, payload: dict) -> None:
    binding = _load_binding(job_dir)
    if binding:
        payload.setdefault("novel_slug", binding["novel_slug"])
        payload.setdefault("novel_project", binding["novel_project"])
        payload.setdefault("source_chapter", binding["source_chapter"])
    (job_dir / "job_state.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if binding:
        artifact = None
        arts = payload.get("artifacts")
        if isinstance(arts, list) and arts:
            artifact = arts[0].get("path") if isinstance(arts[0], dict) else None
        record_video_job(
            binding,
            job_id=job_dir.name,
            job_dir=job_dir,
            mode=json.loads((job_dir / "storyboard.json").read_text(encoding="utf-8")).get("mode", "summary"),
            status=str(payload.get("status", "running")),
            artifact=artifact,
        )


def run_pipeline(
    job_dir: Path,
    mode: str,
    aspect: str,
    subtitles: bool = False,
    *,
    visual_backend: str = "static",
) -> int:
    script = job_dir / "script.md"
    try:
        if mode == "motion-drama":
            run_motion_drama_segments(job_dir, aspect, visual_backend=visual_backend)
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
        elif mode in ("drama", "motion-comic"):
            forbid_tc = mode == "motion-comic" and os.environ.get("MOTION_COMIC_ALLOW_TITLE_CARD") != "1"
            run_drama_segments(job_dir, aspect, visual_backend=visual_backend, forbid_title_card=forbid_tc)
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
            if visual_backend == "comfyui":
                run_comfyui_visual(job_dir)
            subprocess.run(
                [sys.executable, str(SCRIPTS / "compose_ffmpeg.py"), "summary", "--job", str(job_dir), "--aspect", aspect],
                check=True,
            )
    except subprocess.CalledProcessError as exc:
        msg = f"PIPELINE FAIL: stage command exited {exc.returncode}"
        _write_job_state(job_dir, {"status": "failed", "stage": "render", "reason": msg, "job_id": job_dir.name})
        _write_failed_completion(job_dir, msg, mode)
        emit_error(msg, mode=mode, job_id=job_dir.name)
        return 1

    outputs = list((job_dir / "output").glob("*.mp4"))
    if not outputs:
        msg = "PIPELINE FAIL: no output mp4 produced"
        _write_job_state(job_dir, {"status": "failed", "stage": "export", "reason": msg, "job_id": job_dir.name})
        _write_failed_completion(job_dir, msg, mode)
        emit_error(msg, mode=mode, job_id=job_dir.name)
        return 1

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
    if mode in ("motion-comic", "motion-drama"):
        disclosed = job_dir / "output" / f"{final.stem}_ai_disclosed.mp4"
        subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "ai_disclosure_burn.py"),
                "--video",
                str(final),
                "--output",
                str(disclosed),
            ],
            check=False,
        )
        if disclosed.exists():
            final = disclosed
    qc = subprocess.run(
        [sys.executable, str(SCRIPTS / "qc_video.py"), str(final), "--require-audio"],
        check=False,
    )
    if qc.returncode != 0:
        msg = f"PIPELINE FAIL: qc_video failed with exit {qc.returncode}"
        _write_job_state(
            job_dir,
            {
                "status": "failed",
                "stage": "qc",
                "reason": msg,
                "job_id": job_dir.name,
                "artifacts": [{"type": "video", "path": str(final)}],
            },
        )
        _write_failed_completion(job_dir, msg, mode)
        emit_error(msg, mode=mode, job_id=job_dir.name, artifact=str(final))
        return 1

    if mode in ("motion-comic", "motion-drama"):
        dq = subprocess.run(
            [sys.executable, str(SCRIPTS / "drama_quality_gate.py"), "--job", str(job_dir), "--video", str(final)],
            capture_output=True,
            text=True,
        )
        if dq.stdout.strip():
            print(dq.stdout.strip())
        if dq.returncode != 0 and os.environ.get("DRAMA_GATE_RELAX") != "1":
            msg = "PIPELINE FAIL: drama_quality_gate failed"
            _write_job_state(
                job_dir,
                {"status": "failed", "stage": "drama_qc", "reason": msg, "job_id": job_dir.name},
            )
            emit_error(msg, mode=mode, job_id=job_dir.name, artifact=str(final))
            return 1
        ptqc = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "platform_technical_qc.py"),
                str(final),
                "--mode",
                mode,
            ],
            capture_output=True,
            text=True,
        )
        if ptqc.stdout.strip():
            print(ptqc.stdout.strip())
        if ptqc.returncode != 0:
            msg = "PIPELINE FAIL: platform_technical_qc failed"
            _write_job_state(
                job_dir,
                {
                    "status": "failed",
                    "stage": "platform_qc",
                    "reason": msg,
                    "job_id": job_dir.name,
                    "artifacts": [{"type": "video", "path": str(final)}],
                },
            )
            emit_error(msg, mode=mode, job_id=job_dir.name, artifact=str(final))
            return 1
        project = None
        binding = _load_binding(job_dir)
        if binding and binding.get("novel_project"):
            project = Path(binding["novel_project"])
            if not project.is_absolute():
                project = VIDEO_ROOT.parent / project
        run_platform_gate(
            "manifest",
            project=project.resolve() if project and project.exists() else None,
            job_dir=job_dir,
            mode=mode,
            video=final,
        )

    _write_job_state(
        job_dir,
        {
            "status": "succeeded",
            "stage": "export",
            "job_id": job_dir.name,
            "artifacts": [{"type": "video", "path": str(final)}],
        },
    )
    try:
        from video_node_completion import write_job_completion  # noqa: PLC0415

        write_job_completion(job_dir, artifact=final, qc_ok=True, mode=mode)
        print(f"OK: completion -> {job_dir / 'node.completion.json'}")
    except Exception as exc:  # noqa: BLE001
        print(f"WARN: node.completion.json not written: {exc}", file=sys.stderr)
    print(f"OK: {final}")
    emit_result("ok", artifact=str(final), mode=mode, job_id=job_dir.name)
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve() if getattr(args, "project", None) else None
    ch = resolve_chapter(args.chapter, project)
    if not ch.exists():
        emit_error(f"ERROR: chapter not found {ch}", mode="summary")
        return 1
    binding = infer_novel_binding(ch, project=project)
    visual_backend = getattr(args, "visual_backend", "static")
    comfyui_profile = getattr(args, "comfyui_profile", "minimal")
    job = create_job(
        "summary",
        ch,
        args.aspect,
        binding=binding,
        visual_backend=visual_backend,
        comfyui_profile=comfyui_profile,
    )
    return run_pipeline(
        job,
        "summary",
        args.aspect,
        subtitles=args.subtitles,
        visual_backend=visual_backend,
    )


def cmd_motion_comic(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve() if getattr(args, "project", None) else None
    if project is None:
        emit_error("ERROR: motion-comic requires --project", mode="motion-comic")
        return 1
    ch = resolve_chapter(args.chapter, project)
    if not ch.exists():
        emit_error(f"ERROR: chapter not found {ch}", mode="motion-comic")
        return 1
    if run_platform_gate("intake", project=project, chapter=ch, mode="motion-comic") != 0:
        emit_error("ERROR: platform_publish_gate intake failed", mode="motion-comic")
        return 1
    binding = infer_novel_binding(ch, project=project)
    visual_backend = getattr(args, "visual_backend", "comfyui")
    comfyui_profile = getattr(args, "comfyui_profile", "minimal")
    job = create_job(
        "motion-comic",
        ch,
        args.aspect,
        binding=binding,
        visual_backend=visual_backend,
        comfyui_profile=comfyui_profile,
    )
    if build_motion_comic_storyboard(job, ch, project) != 0:
        emit_error("ERROR: storyboard_from_chapter failed", mode="motion-comic", job_id=job.name)
        return 1
    if run_platform_gate("storyboard", project=project, job_dir=job, mode="motion-comic") != 0:
        emit_error("ERROR: platform_publish_gate storyboard failed", mode="motion-comic", job_id=job.name)
        return 1
    return run_pipeline(
        job,
        "motion-comic",
        args.aspect,
        subtitles=args.subtitles,
        visual_backend=visual_backend,
    )


def cmd_motion_drama(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    ch = resolve_chapter(args.chapter, project)
    if not ch.exists():
        emit_error(f"ERROR: chapter not found {ch}", mode="motion-drama")
        return 1
    if run_platform_gate("intake", project=project, chapter=ch, mode="motion-drama") != 0:
        emit_error("ERROR: platform_publish_gate intake failed", mode="motion-drama")
        return 1
    binding = infer_novel_binding(ch, project=project)
    visual_backend = getattr(args, "visual_backend", "comfyui")
    comfyui_profile = getattr(args, "comfyui_profile", "minimal")
    job = create_job(
        "motion-drama",
        ch,
        args.aspect,
        binding=binding,
        visual_backend=visual_backend,
        comfyui_profile=comfyui_profile,
    )
    if build_character_assets(
        job,
        project,
        render_refs=getattr(args, "render_refs", False),
    ) != 0:
        emit_error("ERROR: character_asset_pack failed", mode="motion-drama", job_id=job.name)
        return 1
    if build_motion_drama_shots(job, ch, project) != 0:
        emit_error("ERROR: script_to_shots failed", mode="motion-drama", job_id=job.name)
        return 1
    if run_platform_gate("storyboard", project=project, job_dir=job, mode="motion-drama") != 0:
        emit_error("ERROR: platform_publish_gate storyboard failed", mode="motion-drama", job_id=job.name)
        return 1
    if not getattr(args, "skip_ref_qc", False):
        if run_character_ref_qc(job, project) != 0:
            emit_error(
                "ERROR: character_ref_qc failed — run with --render-refs or generate chapter refs first",
                mode="motion-drama",
                job_id=job.name,
            )
            return 1
    return run_pipeline(
        job,
        "motion-drama",
        args.aspect,
        subtitles=args.subtitles,
        visual_backend=visual_backend,
    )


def cmd_drama(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve() if getattr(args, "project", None) else None
    ch = resolve_chapter(args.chapter, project)
    if not ch.exists():
        emit_error(f"ERROR: chapter not found {ch}", mode="drama")
        return 1
    binding = infer_novel_binding(ch, project=project)
    job = create_job("drama", ch, args.aspect, binding=binding)
    return run_pipeline(job, "drama", args.aspect, subtitles=args.subtitles)


def main() -> int:
    p = argparse.ArgumentParser(prog="novel-video")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("summary")
    s.add_argument("--chapter", required=True, help="Chapter path or filename with --project")
    s.add_argument("--project", default=None, help="Novel project dir (binds job to registry slug)")
    s.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1"])
    s.add_argument("--subtitles", action="store_true", help="Generate SRT and burn into output")
    s.add_argument(
        "--visual-backend",
        default="static",
        choices=["static", "comfyui"],
        help="Visual source: static title card or ComfyUI image (needs COMFYUI_URL)",
    )
    s.add_argument(
        "--comfyui-profile",
        default="minimal",
        choices=["minimal", "image", "full"],
        help="ComfyUI workflow profile when --visual-backend comfyui",
    )
    s.set_defaults(func=cmd_summary)
    d = sub.add_parser("drama")
    d.add_argument("--chapter", required=True, help="Chapter path or filename with --project")
    d.add_argument("--project", default=None, help="Novel project dir (binds job to registry slug)")
    d.add_argument("--aspect", default="9:16")
    d.add_argument("--subtitles", action="store_true")
    d.set_defaults(func=cmd_drama)
    m = sub.add_parser("motion-comic", help="Multi-shot motion comic (platform gate + per-scene visuals)")
    m.add_argument("--chapter", required=True)
    m.add_argument("--project", required=True, help="Novel project dir (required)")
    m.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1"])
    m.add_argument("--subtitles", action="store_true")
    m.add_argument(
        "--visual-backend",
        default="comfyui",
        choices=["static", "comfyui"],
    )
    m.add_argument("--comfyui-profile", default="minimal", choices=["minimal", "image", "full"])
    m.set_defaults(func=cmd_motion_comic)
    md = sub.add_parser("motion-drama", help="Platform motion drama: 40+ shots, still+i2v, CVDP refs")
    md.add_argument("--chapter", required=True)
    md.add_argument("--project", required=True)
    md.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1"])
    md.add_argument("--subtitles", action="store_true")
    md.add_argument("--visual-backend", default="comfyui", choices=["comfyui"])
    md.add_argument("--comfyui-profile", default="minimal", choices=["minimal", "image", "full"])
    md.add_argument("--render-refs", action="store_true", help="Generate CVDP ref portraits via ComfyUI before QC")
    md.add_argument("--skip-ref-qc", action="store_true", help="Skip character_ref_qc (dev only)")
    md.set_defaults(func=cmd_motion_drama)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
