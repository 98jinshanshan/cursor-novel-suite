"""CLI handlers for video publish."""

from __future__ import annotations

import argparse
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.paths import assert_project_in_allowed_roots
from novel_suite.core.result import Result, artifact, error_result, ok_result
from novel_suite.video.gate.cli import cmd_gate as _run_gate
from novel_suite.video.publish.cookie_manager import cookie_status
from novel_suite.platforms._registry import list_platform_keys
from novel_suite.video.publish.adapters import upload as adapter_upload
from novel_suite.video.publish.record import add_record, records_summary
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


def cmd_publish(args: argparse.Namespace) -> Result:
    """Publish chapter summary video (gate pre-check + publish record)."""
    resolved = _resolve_project(args)
    if isinstance(resolved, Result):
        return resolved

    project = resolved
    chapter_key: str = (args.chapter_key or "ch01").strip() or "ch01"
    platform: str = (getattr(args, "platform", "douyin") or "douyin").strip().lower()
    headless = not bool(getattr(args, "no_headless", False))
    skip_gate = bool(getattr(args, "skip_gate", False))

    video_path = project / "video" / chapter_key / "output" / f"{chapter_key}_summary.mp4"
    title = (getattr(args, "title", None) or "").strip() or f"Chapter {chapter_key}"

    if not video_path.is_file():
        return error_result(
            E.PUBLISH_VIDEO_NOT_FOUND,
            f"Video not found: {video_path}",
            next_actions=["novel-suite video pipeline --project ... --json"],
            chapter_key=chapter_key,
            platform=platform,
        )

    gate_report: dict | None = None
    if not skip_gate:
        gate_args = argparse.Namespace(
            project=args.project,
            chapter_key=chapter_key,
            platform=platform,
            json=getattr(args, "json", False),
        )
        gate_result = _run_gate(gate_args)
        if gate_result.status != "ok":
            return error_result(
                E.PUBLISH_GATE_BLOCKED,
                "Publish blocked by gate — fix issues first",
                gate_report=gate_result.details.get("gate_report"),
                chapter_key=chapter_key,
                platform=platform,
                next_actions=[
                    "novel-suite video gate --project ... --chapter-key ... --json",
                    "Or use --skip-gate to force publish (not recommended)",
                ],
            )
        gate_report = gate_result.details.get("gate_report")

    video_platforms = set(list_platform_keys(platform_type="video"))
    if platform not in video_platforms:
        return error_result(
            E.PUBLISH_PLATFORM_UNSUPPORTED,
            f"Platform not supported for video publish: {platform}",
            platform=platform,
            supported=sorted(video_platforms),
        )

    pub_result = adapter_upload(platform, video_path, title, headless=headless)

    record_entry = {
        "platform": platform,
        "video": str(video_path),
        "title": title,
        "ok": pub_result.get("ok", False),
        "url": pub_result.get("url", ""),
        "error": pub_result.get("error"),
        "note": pub_result.get("note"),
        "gate_skipped": skip_gate,
        "gate_report": gate_report,
    }
    add_record(project, chapter_key, record_entry)

    if pub_result.get("ok"):
        return ok_result(
            E.PUBLISH_OK,
            f"Published to {platform}",
            artifacts=[artifact(str(video_path), kind="video", label="published")],
            publish_result=pub_result,
            chapter_key=chapter_key,
            platform=platform,
            record=record_entry,
        )

    return error_result(
        E.PUBLISH_FAILED,
        str(pub_result.get("error", "Unknown publish error")),
        publish_result=pub_result,
        chapter_key=chapter_key,
        platform=platform,
        record=record_entry,
    )


def cmd_publish_list(args: argparse.Namespace) -> Result:
    """List publish history for a chapter."""
    resolved = _resolve_project(args)
    if isinstance(resolved, Result):
        return resolved

    project = resolved
    chapter_key: str = (args.chapter_key or "ch01").strip() or "ch01"
    summary = records_summary(project, chapter_key)
    return ok_result(
        E.PUBLISH_LIST_OK,
        f"{summary['total']} publish record(s) for {chapter_key}",
        records=summary["records"],
        summary={k: v for k, v in summary.items() if k != "records"},
        chapter_key=chapter_key,
    )


def cmd_cookie(args: argparse.Namespace) -> Result:
    """Report platform cookie validity."""
    platform: str = (getattr(args, "platform", "douyin") or "douyin").strip().lower()
    status = cookie_status(platform)
    if status["valid"]:
        return ok_result(E.COOKIE_OK, f"Cookie valid for {platform}", cookie_status=status)
    return error_result(
        E.COOKIE_EXPIRED,
        f"Cookie for {platform}: {status.get('reason', 'invalid')}",
        cookie_status=status,
        next_actions=[
            "novel-suite video publish upload --platform douyin --no-headless --json",
        ],
    )
