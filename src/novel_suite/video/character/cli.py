"""CLI handlers for novel-suite video character (Sprint 2.2)."""

from __future__ import annotations

import argparse
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.paths import assert_project_in_allowed_roots, suite_root
from novel_suite.core.result import Result, artifact, error_result, ok_result
from novel_suite.video.character.asset_packer import (
    assets_root_for_chapter,
    build_asset_pack,
    get_asset_pack_path,
)
from novel_suite.video.character.cvdp_loader import cvdp_path_for_chapter, list_characters
from novel_suite.video.character.qc import run_character_qc
from novel_suite.writer import registry


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def cmd_character_list(args: argparse.Namespace) -> Result:
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
    cvdp_path = cvdp_path_for_chapter(project, chapter_key)

    try:
        characters = list_characters(project, chapter_key)
    except FileNotFoundError as exc:
        return error_result(
            E.CHARACTER_CVDP_NOT_FOUND,
            str(exc),
            next_actions=[
                f"Ensure CVDP exists at: {project / 'video' / chapter_key / 'character_visual_design.json'}",
                "Run character visual design skill before listing",
            ],
        )

    root = suite_root()
    return ok_result(
        E.CHARACTER_LIST_OK,
        f"{len(characters)} character(s) loaded from CVDP ({chapter_key})",
        artifacts=[artifact(_rel(root, cvdp_path), kind="file", label="cvdp")],
        characters=characters,
        count=len(characters),
        chapter_key=chapter_key,
    )


def cmd_character_pack(args: argparse.Namespace) -> Result:
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
    render_refs: bool = bool(getattr(args, "render_refs", False))
    characters: list[str] | None = None
    raw_chars = getattr(args, "characters", "") or ""
    if raw_chars.strip():
        characters = [c.strip() for c in raw_chars.split(",") if c.strip()]

    try:
        manifest = build_asset_pack(
            project,
            chapter_key=chapter_key,
            render_refs=render_refs,
            characters_filter=characters,
        )
    except FileNotFoundError as exc:
        return error_result(
            E.CHARACTER_CVDP_NOT_FOUND,
            str(exc),
            next_actions=[
                "Ensure CVDP exists — run: novel-suite video character list ...",
            ],
        )
    except ImportError as exc:
        return error_result(
            E.CHARACTER_RENDERER_UNAVAILABLE,
            str(exc),
            next_actions=[
                "Install ComfyUI adapters, or omit --render-refs",
                "See cursor-novel-video/adapters/README.md",
            ],
        )

    root = suite_root()
    manifest_path = get_asset_pack_path(project, chapter_key)
    char_count = len(manifest.get("characters", []))
    assets_root = manifest.get("assets_root", str(assets_root_for_chapter(project, chapter_key)))

    return ok_result(
        E.CHARACTER_PACK_OK,
        f"Asset pack built: {char_count} character(s)",
        artifacts=[
            artifact(_rel(root, Path(assets_root)), kind="directory", label="assets_root"),
            artifact(_rel(root, manifest_path), kind="file", label="manifest"),
        ],
        manifest=manifest,
        character_count=char_count,
        render_refs=render_refs,
        chapter_key=chapter_key,
    )


def cmd_character_qc(args: argparse.Namespace) -> Result:
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
    report = run_character_qc(project, chapter_key)
    root = suite_root()
    pack_path = Path(report.get("asset_pack_source") or get_asset_pack_path(project, chapter_key))

    if report.get("ok"):
        summary = report.get("summary", {})
        return ok_result(
            E.CHARACTER_QC_OK,
            f"QC passed: {summary.get('passed', 0)}/{summary.get('total', 0)} characters OK",
            artifacts=[
                artifact(_rel(root, pack_path), kind="file", label="manifest"),
            ],
            qc_report=report,
            chapter_key=chapter_key,
        )

    summary = report.get("summary", {})
    return error_result(
        E.CHARACTER_QC_FAILED,
        f"QC failed: {summary.get('failed', len(report.get('errors', [])))} issue(s) found",
        required=list(report.get("errors", [])),
        next_actions=[
            "Fix CVDP issues listed in qc_report.errors",
            "Re-run: novel-suite video character pack ...",
        ],
        qc_report=report,
        chapter_key=chapter_key,
    )
