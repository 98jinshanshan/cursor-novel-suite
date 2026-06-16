"""CLI handlers for novel-suite video stills."""

from __future__ import annotations

import argparse
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.paths import assert_project_in_allowed_roots
from novel_suite.core.result import Result, error_result
from novel_suite.video.character.asset_packer import get_asset_pack_path
from novel_suite.video.stills.generator import generate_stills
from novel_suite.writer import registry


def cmd_stills_generate(args: argparse.Namespace) -> Result:
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
    mode: str = (args.mode or "proof").strip().lower() or "proof"
    if mode not in ("proof", "final"):
        return error_result(E.STILLS_RENDER_FAILED, f"Unsupported --mode {args.mode!r}")

    storyboard_path = project / "video" / chapter_key / "storyboard.json"
    output_dir = project / "video" / chapter_key / "stills"
    manifest_path = get_asset_pack_path(project, chapter_key)

    return generate_stills(
        storyboard_path=storyboard_path,
        output_dir=output_dir,
        mode=mode,
        manifest_path=manifest_path,
        aspect=getattr(args, "aspect", "9:16") or "9:16",
    )
