"""Publish readiness — agent/MCP-friendly preflight checks."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from novel_suite.auth.token_store import token_status as auth_token_status
from novel_suite.platforms._registry import get_platform, validate_platform
from novel_suite.video.gate.cli import cmd_gate as _run_gate
from novel_suite.video.publish.cookie_manager import cookie_status


def _auth_logged_in(platform: str) -> tuple[bool, str, dict[str, Any]]:
    """Return (logged_in, source, status_dict). Prefers encrypted token over legacy cookie."""
    token = auth_token_status(platform)
    if token.get("valid"):
        return True, "token", token
    cookie = cookie_status(platform)
    if cookie.get("valid"):
        return True, "cookie", cookie
    return False, "none", token


def _video_path(project: Path, chapter_key: str) -> Path:
    return project / "video" / chapter_key / "output" / f"{chapter_key}_summary.mp4"


def publish_readiness(
    platform: str,
    project: Path,
    *,
    chapter_key: str = "ch01",
    skip_gate: bool = False,
) -> dict[str, Any]:
    """Return whether a platform is ready to publish and what is missing."""
    key = platform.strip().lower()
    if not validate_platform(key):
        return {
            "platform": key,
            "ready": False,
            "error": f"Unknown platform: {platform}",
            "missing": [{"item": "platform", "action": "publish.platforms"}],
        }

    info = get_platform(key) or {}
    ptype = str(info.get("type", "video"))
    chapter_key = chapter_key.strip() or "ch01"

    logged_in, auth_source, auth_status = _auth_logged_in(key)
    video_path = _video_path(project, chapter_key)
    has_video = video_path.is_file() if ptype == "video" else None

    missing: list[dict[str, str]] = []
    if not logged_in:
        missing.append(
            {
                "item": "auth",
                "action": "auth.login",
                "description": f"Login to {info.get('name', key)}",
                "cli": f"novel-suite auth login --platform {key} --json",
            }
        )

    if ptype == "video" and not has_video:
        missing.append(
            {
                "item": "video",
                "action": "video.pipeline",
                "description": "Generate chapter summary video",
                "cli": f"novel-suite video pipeline --project {project} --chapter-key {chapter_key} --json",
            }
        )

    gate_passed: bool | None = None
    gate_report: dict[str, Any] | None = None
    if ptype == "video" and has_video and not skip_gate:
        gate_args = argparse.Namespace(
            project=project,
            chapter_key=chapter_key,
            platform=key,
            json=False,
        )
        gate_result = _run_gate(gate_args)
        gate_passed = gate_result.status == "ok"
        gate_report = gate_result.details.get("gate_report")
        if not gate_passed:
            missing.append(
                {
                    "item": "gate",
                    "action": "video.gate",
                    "description": "Fix compliance or consistency issues",
                    "cli": f"novel-suite video gate --project {project} --chapter-key {chapter_key} --json",
                }
            )
    elif skip_gate:
        gate_passed = None

    ready = logged_in and (ptype != "video" or bool(has_video)) and (
        skip_gate or gate_passed is not False
    )

    return {
        "platform": key,
        "platform_name": info.get("name", key),
        "platform_type": ptype,
        "chapter_key": chapter_key,
        "project": str(project.resolve()),
        "ready": ready,
        "logged_in": logged_in,
        "auth_source": auth_source,
        "auth_status": auth_status,
        "has_video": has_video,
        "video_path": str(video_path) if ptype == "video" else None,
        "gate_passed": gate_passed,
        "gate_report": gate_report,
        "gate_skipped": skip_gate,
        "missing": missing,
        "next_action": missing[0]["action"] if missing else "publish.upload",
    }
