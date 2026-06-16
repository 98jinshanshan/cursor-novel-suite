"""CLI handlers for novel-suite video compose."""

from __future__ import annotations

import argparse

from novel_suite.core import errors as E
from novel_suite.core.paths import assert_project_in_allowed_roots, suite_root
from novel_suite.core.result import Result, artifact, error_result, ok_result
from novel_suite.video.character.asset_packer import get_asset_pack_path
from novel_suite.video.compose.pipeline import compose_video
from novel_suite.video.compose.qc import run_platform_qc, run_video_qc
from novel_suite.video.stills.generator import generate_stills
from novel_suite.writer import registry


def cmd_compose_run(args: argparse.Namespace) -> Result:
    try:
        project = registry.resolve_project(args.project)
        project = assert_project_in_allowed_roots(project)
    except ValueError as exc:
        code = (
            E.PROJECT_PATH_OUT_OF_BOUNDS
            if E.PROJECT_PATH_OUT_OF_BOUNDS in str(exc)
            else E.NO_ACTIVE_NOVEL
        )
        return error_result(code, str(exc))

    chapter_key: str = (args.chapter_key or "ch01").strip() or "ch01"
    storyboard_path = project / "video" / chapter_key / "storyboard.json"
    stills_dir = project / "video" / chapter_key / "stills"
    output_path = project / "video" / chapter_key / "output" / f"{chapter_key}_summary.mp4"

    return compose_video(
        storyboard_path=storyboard_path,
        stills_dir=stills_dir,
        output_path=output_path,
        voice=getattr(args, "voice", "zh-CN-XiaoxiaoNeural") or "zh-CN-XiaoxiaoNeural",
        aspect=getattr(args, "aspect", "9:16") or "9:16",
        subtitles=bool(getattr(args, "subtitles", False)),
    )


def cmd_pipeline_run(args: argparse.Namespace) -> Result:
    """One-shot E2E: storyboard → stills → compose → QC."""
    try:
        project = registry.resolve_project(args.project)
        project = assert_project_in_allowed_roots(project)
    except ValueError as exc:
        code = (
            E.PROJECT_PATH_OUT_OF_BOUNDS
            if E.PROJECT_PATH_OUT_OF_BOUNDS in str(exc)
            else E.NO_ACTIVE_NOVEL
        )
        return error_result(code, str(exc))

    chapter_key: str = (args.chapter_key or "ch01").strip() or "ch01"
    mode: str = (getattr(args, "mode", "proof") or "proof").strip().lower()

    storyboard_path = project / "video" / chapter_key / "storyboard.json"
    if not storyboard_path.is_file():
        return error_result(
            E.PIPELINE_STORYBOARD_MISSING,
            f"Storyboard not found: {storyboard_path}",
            next_actions=[
                f"novel-suite video storyboard --project {project} --chapter-key {chapter_key} --json",
            ],
        )

    stills_dir = project / "video" / chapter_key / "stills"
    manifest_path = get_asset_pack_path(project, chapter_key)
    stills_result = generate_stills(
        storyboard_path=storyboard_path,
        output_dir=stills_dir,
        mode=mode,
        manifest_path=manifest_path,
        aspect=getattr(args, "aspect", "9:16") or "9:16",
    )
    if stills_result.status != "ok":
        return stills_result

    output_path = project / "video" / chapter_key / "output" / f"{chapter_key}_summary.mp4"
    compose_result = compose_video(
        storyboard_path=storyboard_path,
        stills_dir=stills_dir,
        output_path=output_path,
        voice=getattr(args, "voice", "zh-CN-XiaoxiaoNeural") or "zh-CN-XiaoxiaoNeural",
        aspect=getattr(args, "aspect", "9:16") or "9:16",
        subtitles=bool(getattr(args, "subtitles", False)),
    )
    if compose_result.status != "ok":
        return compose_result

    qc_report = run_video_qc(output_path)
    platform_qc_report = run_platform_qc(output_path, getattr(args, "platform", "douyin") or "douyin")

    warnings: list[str] = []
    if not qc_report.get("ok"):
        warnings.append(f"Video QC: {len(qc_report.get('errors', []))} issue(s)")
    if not platform_qc_report.get("ok"):
        warnings.append(f"Platform QC: {len(platform_qc_report.get('errors', []))} issue(s)")

    root = suite_root()
    try:
        rel_out = output_path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        rel_out = str(output_path.resolve())

    details: dict = {
        "stills_count": stills_result.details.get("stills_count", 0),
        "segment_count": compose_result.details.get("segment_count", 0),
        "output_path": rel_out,
        "mode": mode,
        "qc": qc_report,
        "platform_qc": platform_qc_report,
    }
    if warnings:
        details["warnings"] = warnings

    return ok_result(
        E.PIPELINE_OK,
        f"Pipeline complete: {output_path.name}",
        artifacts=compose_result.artifacts or [artifact(rel_out, kind="video", label="final")],
        chapter_key=chapter_key,
        **details,
    )
