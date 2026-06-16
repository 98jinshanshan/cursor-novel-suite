"""CLI handlers for video gate — unified compliance + consistency entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from novel_suite.core import errors as E
from novel_suite.core.paths import assert_project_in_allowed_roots
from novel_suite.core.result import Result, error_result, ok_result
from novel_suite.video.character.asset_packer import get_asset_pack_path
from novel_suite.video.character.cvdp_loader import cvdp_path_for_chapter, index_characters
from novel_suite.video.gate.compliance import run_compliance_check
from novel_suite.video.gate.consistency import check_character_consistency
from novel_suite.writer import registry


def _resolve_project(args: argparse.Namespace) -> Result | Path:
    try:
        project = registry.resolve_project(args.project)
        return assert_project_in_allowed_roots(project)
    except ValueError as exc:
        code = (
            E.PROJECT_PATH_OUT_OF_BOUNDS
            if E.PROJECT_PATH_OUT_OF_BOUNDS in str(exc)
            else E.NO_ACTIVE_NOVEL
        )
        return error_result(code, str(exc))


def _load_character_profiles(project: Path, chapter_key: str) -> dict[str, Any]:
    profiles: dict[str, Any] = {}
    manifest_path = get_asset_pack_path(project, chapter_key)
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for char in manifest.get("characters", []):
            name = char.get("name")
            if name:
                profiles[str(name)] = char
        return profiles

    cvdp_path = cvdp_path_for_chapter(project, chapter_key)
    if cvdp_path.is_file():
        cvdp = json.loads(cvdp_path.read_text(encoding="utf-8"))
        profiles.update(index_characters(cvdp))
    return profiles


def cmd_gate(args: argparse.Namespace) -> Result:
    """Unified publish gate: compliance + character consistency."""
    resolved = _resolve_project(args)
    if isinstance(resolved, Result):
        return resolved

    project = resolved
    chapter_key: str = (args.chapter_key or "ch01").strip() or "ch01"
    platform: str = (getattr(args, "platform", "douyin") or "douyin").strip().lower()

    video_path = project / "video" / chapter_key / "output" / f"{chapter_key}_summary.mp4"
    storyboard_path = project / "video" / chapter_key / "storyboard.json"

    if not video_path.is_file():
        return error_result(
            E.GATE_VIDEO_NOT_FOUND,
            f"Video not found: {video_path}",
            next_actions=["novel-suite video pipeline --project ... --chapter-key ... --json"],
            chapter_key=chapter_key,
            platform=platform,
        )

    compliance = run_compliance_check(video_path, storyboard_path, platform)

    scenes: list[dict[str, Any]] = []
    if storyboard_path.is_file():
        sb = json.loads(storyboard_path.read_text(encoding="utf-8"))
        scenes = sb.get("scenes", [])

    char_profiles = _load_character_profiles(project, chapter_key)
    consistency = check_character_consistency(char_profiles, scenes)

    all_passed = compliance["passed"] and consistency["passed"]
    report = {
        "passed": all_passed,
        "platform": platform,
        "checks": {
            "compliance": compliance,
            "consistency": consistency,
        },
    }

    if all_passed:
        return ok_result(
            E.GATE_OK,
            f"All gates passed for {platform}",
            gate_report=report,
            chapter_key=chapter_key,
            platform=platform,
        )

    failed_checks: list[str] = []
    if not compliance["passed"]:
        failed_checks.append("compliance")
    if not consistency["passed"]:
        failed_checks.append("consistency")

    return error_result(
        E.GATE_FAILED,
        f"Gate failed for {platform}: {', '.join(failed_checks)}",
        required=[f"{check}: see gate_report for details" for check in failed_checks],
        gate_report=report,
        chapter_key=chapter_key,
        platform=platform,
        next_actions=[
            "Check gate_report.checks for details",
            "Fix compliance: review sensitive content or platform requirements",
            "Fix consistency: run 'novel-suite video character pack --render-refs'",
        ],
    )


def cmd_gate_check(args: argparse.Namespace) -> Result:
    """Compliance-only gate (Day 3 handler, kept for tests and direct import)."""
    resolved = _resolve_project(args)
    if isinstance(resolved, Result):
        return resolved

    project = resolved
    chapter_key: str = (args.chapter_key or "ch01").strip() or "ch01"
    platform: str = (getattr(args, "platform", "douyin") or "douyin").strip().lower()

    video_path = project / "video" / chapter_key / "output" / f"{chapter_key}_summary.mp4"
    storyboard_path = project / "video" / chapter_key / "storyboard.json"

    if not video_path.is_file():
        return error_result(
            E.GATE_VIDEO_NOT_FOUND,
            f"Video not found: {video_path}",
            next_actions=["novel-suite video pipeline --project ... --chapter-key ... --json"],
        )

    report = run_compliance_check(video_path, storyboard_path, platform)

    if report["passed"]:
        return ok_result(
            E.GATE_OK,
            f"Compliance gate passed for {platform}",
            gate_report=report,
            chapter_key=chapter_key,
            platform=platform,
        )

    failed = [k for k, v in report["checks"].items() if not v.get("passed")]
    return error_result(
        E.GATE_FAILED,
        f"Compliance gate failed for {platform}",
        required=[f"{k}: failed" for k in failed],
        gate_report=report,
        chapter_key=chapter_key,
        platform=platform,
        next_actions=["Fix issues in gate_report.checks", "Re-run gate check"],
    )
