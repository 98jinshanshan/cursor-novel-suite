"""Generate per-scene keyframe images from storyboard."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from novel_suite.core import errors as E
from novel_suite.core.paths import suite_root
from novel_suite.core.result import Result, artifact, error_result, ok_result
from novel_suite.video._legacy import load_video_script
from novel_suite.video.character.asset_packer import get_asset_pack_path
from novel_suite.video.stills.renderer import StillBackend, get_backend

_DEFAULT_WIDTH = 1080
_DEFAULT_HEIGHT = 1920
_GLOBAL_NEGATIVE = (
    "western caucasian face, anime, cartoon, deformed face, blurry, low quality, watermark"
)


def _aspect_size(aspect: str) -> tuple[int, int]:
    if aspect == "16:9":
        return 1920, 1080
    if aspect == "1:1":
        return 1080, 1080
    return _DEFAULT_WIDTH, _DEFAULT_HEIGHT


def _run_command(cmd: list[str], *, timeout: float = 120.0) -> None:
    run_command = load_video_script("subprocess_safe").run_command
    proc = run_command(cmd, check=True, timeout=timeout, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "command failed")


def _load_character_prompts(manifest_path: Path) -> dict[str, str]:
    if not manifest_path.is_file():
        return {}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    prompts: dict[str, str] = {}
    for char in manifest.get("characters", []):
        name = str(char.get("name", "")).strip()
        pos = str(char.get("ref_prompt_positive", "")).strip()
        if name and pos:
            prompts[name] = pos
    return prompts


def _make_title_card(
    text: str,
    output_path: Path,
    *,
    width: int,
    height: int,
) -> None:
    script = video_scripts_dir() / "make_title_card.py"
    if not script.is_file():
        raise FileNotFoundError(f"make_title_card.py missing: {script}")
    _run_command(
        [
            sys.executable,
            str(script),
            "--text",
            text[:200],
            "--output",
            str(output_path),
            "--width",
            str(width),
            "--height",
            str(height),
        ],
        timeout=60,
    )


def _render_comfyui(
    prompt: str,
    output_path: Path,
    backend: StillBackend,
    *,
    width: int,
    height: int,
    negative: str = _GLOBAL_NEGATIVE,
) -> None:
    if backend.script is None or not backend.script.is_file():
        raise FileNotFoundError("ComfyUI render script not found")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if backend.name == "wan":
        _run_command(
            [
                sys.executable,
                str(backend.script),
                "--prompt",
                prompt[:500],
                "--negative",
                negative,
                "--output",
                str(output_path),
                "--width",
                str(min(width, 832)),
                "--height",
                str(min(height, 832)),
            ],
            timeout=600,
        )
        return
    cmd = [
        sys.executable,
        str(backend.script),
        "--prompt",
        prompt[:500],
        "--negative",
        negative,
        "--output",
        str(output_path),
        "--profile",
        "minimal",
    ]
    _run_command(cmd, timeout=600)


def video_scripts_dir() -> Path:
    from novel_suite.core.paths import video_root

    return video_root() / "engine" / "scripts"


def generate_stills(
    storyboard_path: Path,
    output_dir: Path,
    *,
    mode: str = "proof",
    manifest_path: Path | None = None,
    aspect: str = "9:16",
    backend: StillBackend | None = None,
) -> Result:
    """Generate per-scene keyframe PNGs from storyboard.json."""
    if not storyboard_path.is_file():
        return error_result(
            E.STILLS_STORYBOARD_MISSING,
            f"Storyboard not found: {storyboard_path}",
            next_actions=["novel-suite video storyboard --project ... --json"],
        )

    sb = json.loads(storyboard_path.read_text(encoding="utf-8"))
    scenes = sb.get("scenes", [])
    if not scenes:
        return error_result(E.STILLS_NO_SCENES, "Storyboard has no scenes")

    if manifest_path is None:
        chapter_key = storyboard_path.parent.name
        project = storyboard_path.parent.parent.parent
        manifest_path = get_asset_pack_path(project, chapter_key)

    char_prompts = _load_character_prompts(manifest_path)
    width, height = _aspect_size(str(sb.get("aspect", aspect)))
    detected = backend or get_backend()
    use_comfy = mode == "final" and detected.available and detected.name != "title_card"
    active_backend = detected.name if use_comfy else "title_card"

    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[dict[str, Any]] = []
    root = suite_root()

    for scene in scenes:
        scene_id = str(scene.get("id", f"scene_{len(generated)}"))
        narration = str(scene.get("narration", "") or scene.get("description", "")).strip()
        description = narration or scene_id
        output_path = output_dir / f"scene_{scene_id}.png"

        try:
            if use_comfy:
                char_name = str(scene.get("character", "")).strip()
                char_prompt = char_prompts.get(char_name, "")
                full_prompt = f"{char_prompt}, {description}" if char_prompt else description
                _render_comfyui(
                    full_prompt,
                    output_path,
                    detected,
                    width=width,
                    height=height,
                )
            else:
                _make_title_card(description[:80], output_path, width=width, height=height)
        except (OSError, RuntimeError, FileNotFoundError) as exc:
            return error_result(
                E.STILLS_RENDER_FAILED,
                f"Failed to render scene {scene_id}: {exc}",
                details={"scene_id": scene_id, "backend": active_backend},
            )

        try:
            rel = output_path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            rel = str(output_path.resolve())

        generated.append(
            {
                "scene_id": scene_id,
                "output": rel,
                "backend": active_backend,
                "mode": mode,
            }
        )

    artifacts = [
        artifact(item["output"], kind="image", label=f"scene_{item['scene_id']}")
        for item in generated
        if (output_dir / f"scene_{item['scene_id']}.png").is_file()
    ]

    return ok_result(
        E.STILLS_GENERATE_OK,
        f"Generated {len(generated)} still(s) via {active_backend} ({mode})",
        artifacts=artifacts,
        stills=generated,
        stills_count=len(generated),
        backend=active_backend,
        mode=mode,
    )
