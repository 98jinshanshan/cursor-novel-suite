"""Video QC — wraps engine/scripts/qc_video.py + platform_technical_qc.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from novel_suite.core.paths import video_root
from novel_suite.video._legacy import load_video_script


def _run_command(cmd: list[str], *, timeout: float = 120.0) -> str:
    run_command = load_video_script("subprocess_safe").run_command
    proc = run_command(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    return proc.stdout or ""


def _engine_script(name: str) -> Path:
    return video_root() / "engine" / "scripts" / f"{name}.py"


def _platform_mode(platform: str) -> str:
    if platform.lower() in ("motion-drama", "drama", "motion_drama"):
        return "motion-drama"
    return "motion-comic"


def run_video_qc(video_path: Path) -> dict[str, Any]:
    """Run basic video QC (codec, duration, streams)."""
    if not video_path.is_file():
        return {"ok": False, "errors": [f"Video not found: {video_path}"], "warnings": []}

    script = _engine_script("qc_video")
    try:
        stdout = _run_command([sys.executable, str(script), str(video_path.resolve())])
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            return {"ok": True, "stdout": stdout, "warnings": []}
    except (OSError, RuntimeError, ValueError) as exc:
        return {"ok": False, "errors": [str(exc)], "warnings": []}


def run_platform_qc(video_path: Path, platform: str = "douyin") -> dict[str, Any]:
    """Run platform technical spec QC (engine gate_export)."""
    if not video_path.is_file():
        return {"ok": False, "errors": [f"Video not found: {video_path}"], "warnings": []}

    try:
        mod = load_video_script("platform_technical_qc")
        mode = _platform_mode(platform)
        return dict(mod.gate_export(video_path.resolve(), mode=mode))
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        return {"ok": False, "errors": [str(exc)], "warnings": []}
