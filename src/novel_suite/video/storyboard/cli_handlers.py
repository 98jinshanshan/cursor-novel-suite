"""CLI handlers for `novel-suite video storyboard` (Sprint 2.1c)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from novel_suite.core import errors as E
from novel_suite.core.paths import assert_project_in_allowed_roots, suite_root
from novel_suite.core.result import Result, artifact, error_result, ok_result
from novel_suite.video.chapter_paths import format_chapter_hints, resolve_chapter_path
from novel_suite.video.storyboard.generator import (
    StoryboardOptions,
    generate_storyboard,
    load_character_context,
)
from novel_suite.video.storyboard.schema import validate_storyboard
from novel_suite.writer import registry


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def derive_chapter_key(chapter_path: Path, explicit: str = "") -> str:
    if explicit.strip():
        return explicit.strip()
    stem = chapter_path.stem
    match = re.match(r"^(\d+)", stem)
    if match:
        return f"ch{int(match.group(1)):02d}" if len(match.group(1)) == 1 else f"ch{match.group(1)}"
    safe = re.sub(r"[^\w-]", "-", stem).strip("-")
    return safe or "ch01"


def storyboard_output_path(project: Path, chapter_key: str) -> Path:
    return project / "video" / chapter_key / "storyboard.json"


def _load_novel_meta(project: Path, chapter_path: Path, root: Path) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "project": _rel(root, project),
        "chapter": _rel(project, chapter_path),
        "in_registry": False,
    }
    project_json = project / "canon" / "project.json"
    if project_json.is_file():
        try:
            data = json.loads(project_json.read_text(encoding="utf-8"))
            meta["slug"] = str(data.get("slug") or data.get("novel_id") or project.name)
            meta["title"] = str(data.get("title") or "")
        except json.JSONDecodeError:
            pass
    resolved = project.resolve()
    for entry in registry.load_registry().get("novels", []):
        try:
            if registry.resolve_project_path(entry).resolve() == resolved:
                meta["slug"] = str(entry.get("slug") or meta.get("slug", project.name))
                meta["in_registry"] = True
                break
        except ValueError:
            continue
    if "slug" not in meta:
        meta["slug"] = project.name
    return meta


def run_storyboard(args: argparse.Namespace) -> Result:
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

    mode = str(args.mode or "summary").strip().lower()
    if mode not in ("summary", "drama"):
        return error_result(
            E.STORYBOARD_FAILED,
            f"Unsupported --mode {args.mode!r}; use summary or drama",
        )
    if mode == "drama":
        return error_result(
            E.STORYBOARD_FAILED,
            "mode=drama delegates to motion-drama pipeline (Sprint 2.2); use summary for now",
            next_actions=["novel-suite video storyboard --mode summary ..."],
        )

    try:
        chapter_path = resolve_chapter_path(args.chapter, project)
    except Exception as exc:  # noqa: BLE001 — legacy resolver errors vary
        return error_result(E.VIDEO_CHAPTER_NOT_FOUND, str(exc))

    if not chapter_path.is_file():
        hints = format_chapter_hints(project)
        next_actions = [
            f"--chapter {h}" for h in hints[:5]
        ] or [f"--chapter <file> under {project / 'chapters'}"]
        if "chapters/chapters" in chapter_path.as_posix():
            message = (
                f"Chapter path double-prefixed (chapters/chapters/): {chapter_path}. "
                "Use bare filename or chapters/<file>.md"
            )
        else:
            message = f"Chapter not found: {chapter_path}"
        return error_result(
            E.VIDEO_CHAPTER_NOT_FOUND,
            message,
            required=[f"--chapter under {project}"],
            next_actions=next_actions,
        )

    chapter_key = derive_chapter_key(chapter_path, getattr(args, "chapter_key", "") or "")
    root = suite_root()
    out_path = storyboard_output_path(project, chapter_key)

    try:
        chapter_text = chapter_path.read_text(encoding="utf-8")
    except OSError as exc:
        return error_result(E.STORYBOARD_FAILED, f"Cannot read chapter: {exc}")

    opts = StoryboardOptions(
        job_id=f"{chapter_key}-storyboard",
        source_chapter=chapter_key,
        chapter_key=chapter_key,
        mode=mode,
        aspect=args.aspect,
        target_duration_sec=int(args.target_duration),
        min_scenes=int(args.min_scenes),
        max_scenes=int(args.max_scenes),
        novel_meta=_load_novel_meta(project, chapter_path, root),
    )

    try:
        board, source = generate_storyboard(
            chapter_text,
            use_llm=bool(args.llm),
            options=opts,
            project=project,
        )
    except RuntimeError as exc:
        code = str(exc) if str(exc) in (
            E.STORYBOARD_FAILED,
            E.STORYBOARD_LLM_UNAVAILABLE,
        ) else E.STORYBOARD_FAILED
        return error_result(code, str(exc))

    errors = validate_storyboard(board)
    if errors:
        return error_result(
            E.STORYBOARD_SCHEMA_INVALID,
            "Generated storyboard failed schema validation",
            details={"errors": errors[:5], "generator": source},
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(board, ensure_ascii=False, indent=2), encoding="utf-8")

    rel_out = _rel(root, out_path)
    return ok_result(
        E.STORYBOARD_OK,
        f"Storyboard written ({len(board.get('scenes', []))} scenes, {source})",
        artifacts=[artifact(rel_out, kind="file", label="storyboard")],
        next_actions=[
            "novel-suite video create-summary --chapter ... (optional)",
            "novel-suite video character list --chapter-key ... (Sprint 2.2)",
        ],
        chapter_key=chapter_key,
        generator=source,
        scene_count=len(board.get("scenes", [])),
        output=rel_out,
    )
