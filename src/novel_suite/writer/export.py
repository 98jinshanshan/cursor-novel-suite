"""Manuscript export — markdown/txt/epub with Phase 9 gate (Phase I)."""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path
from typing import Literal

from novel_suite.core import errors as E
from novel_suite.core.json_stdout import capture_legacy_output
from novel_suite.core.paths import assert_project_in_allowed_roots, suite_root, writer_root
from novel_suite.core.result import Result, artifact, error_result, ok_result
from novel_suite.writer import gate
from novel_suite.writer.chapter import skip_gate_allowed

ExportFormat = Literal["markdown", "txt", "epub"]
EXPORT_FORMATS: frozenset[str] = frozenset({"markdown", "txt", "epub"})


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _parse_story_meta(story_path: Path) -> dict[str, str]:
    if not story_path.is_file():
        return {}
    text = story_path.read_text(encoding="utf-8")
    meta: dict[str, str] = {}
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
    return meta


def _chapter_sort_key(path: Path) -> tuple[int, str]:
    m = re.match(r"^(\d+)", path.stem)
    return (int(m.group(1)) if m else 9999, path.name)


def collect_chapters(project: Path) -> list[Path]:
    ch_dir = project / "chapters"
    if not ch_dir.is_dir():
        return []
    files = [p for p in ch_dir.glob("*.md") if not p.name.startswith("_")]
    return sorted(files, key=_chapter_sort_key)


def _project_title(project: Path) -> str:
    story = project / "story.md"
    meta = _parse_story_meta(story) if story.is_file() else {}
    title = (meta.get("title") or project.name).strip()
    return title or project.name


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]', "", name).strip()
    return cleaned[:80] or "manuscript"


def _markdown_to_plain(md: str) -> str:
    lines: list[str] = []
    for line in md.splitlines():
        if line.startswith("# "):
            lines.append(line[2:].strip())
            lines.append("")
        elif line.startswith("## "):
            lines.append(line[3:].strip())
            lines.append("")
        elif line.strip() == "---":
            lines.append("")
        else:
            lines.append(line)
    return "\n".join(lines).strip() + "\n"


def _build_markdown(chapters: list[Path]) -> str:
    parts: list[str] = []
    for i, ch in enumerate(chapters):
        if i:
            parts.append("\n\n---\n\n")
        parts.append(ch.read_text(encoding="utf-8").strip())
    return "".join(parts) + "\n"


def _epub_dependency_ok() -> bool:
    return importlib.util.find_spec("ebooklib") is not None


def _run_create_epub(project: Path, output: Path) -> tuple[int, list[str]]:
    script = writer_root() / "engine" / "scripts" / "create_epub.py"
    cmd = [sys.executable, str(script), "--project", str(project), "--output", str(output)]
    legacy: list[str] = []
    with capture_legacy_output() as captured:
        proc = subprocess.run(cmd, cwd=str(writer_root()), text=True)
        legacy = captured
    return proc.returncode, legacy


def run_export(
    project: Path,
    *,
    fmt: str,
    output: Path | None = None,
    skip_gate: bool = False,
) -> Result:
    project = project.resolve()
    root = suite_root()

    try:
        project = assert_project_in_allowed_roots(project)
    except ValueError as exc:
        return error_result(
            E.PROJECT_PATH_OUT_OF_BOUNDS,
            str(exc),
            next_actions=["Use --project under novels/ or writer examples/"],
        )

    if not project.is_dir():
        return error_result(
            E.PROJECT_NOT_FOUND,
            f"Not a directory: {project}",
            next_actions=["Pass --project novels/<slug> or set active novel"],
        )

    normalized = fmt.strip().lower()
    if normalized not in EXPORT_FORMATS:
        return error_result(
            E.INVALID_EXPORT_FORMAT,
            f"Unsupported export format: {fmt}",
            next_actions=[f"Use one of: {', '.join(sorted(EXPORT_FORMATS))}"],
            format=fmt,
        )

    if skip_gate and not skip_gate_allowed():
        return error_result(
            E.SKIP_GATE_NOT_ALLOWED,
            "Skipping Phase 9 gate is not allowed",
            next_actions=[f"Unset --skip-gate, or set {E.ENV_ALLOW_SKIP_GATE}=1 for tests only"],
        )

    if not skip_gate:
        gate_result = gate.run_gate(project, 9)
        if gate_result.status != "ok":
            return error_result(
                E.EXPORT_BLOCKED,
                "Cannot export: Phase 9 gate not satisfied",
                required=gate_result.required,
                next_actions=gate_result.next_actions or gate_result.details.get("next_actions", []),
                artifacts=gate_result.artifacts,
                gate_phase=9,
            )

    chapters = collect_chapters(project)
    if not chapters:
        return error_result(
            E.EXPORT_FAILED,
            "No chapters found under chapters/",
            next_actions=["Write at least one chapter under chapters/*.md"],
            project_path=_rel(root, project),
            format=normalized,
        )

    title = _project_title(project)
    dist = project / "dist"
    dist.mkdir(parents=True, exist_ok=True)

    if output is not None:
        out_path = output.expanduser()
        if not out_path.is_absolute():
            out_path = (root / out_path).resolve()
        else:
            out_path = out_path.resolve()
    elif normalized == "epub":
        out_path = dist / f"{_safe_filename(title)}.epub"
    elif normalized == "txt":
        out_path = dist / f"{_safe_filename(title)}.txt"
    else:
        out_path = dist / f"{_safe_filename(title)}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_output: list[str] = []
    warnings: list[str] = []

    try:
        if normalized == "markdown":
            out_path.write_text(_build_markdown(chapters), encoding="utf-8")
        elif normalized == "txt":
            body = _build_markdown(chapters)
            out_path.write_text(_markdown_to_plain(body), encoding="utf-8")
        else:
            if not _epub_dependency_ok():
                return error_result(
                    E.EPUB_DEPENDENCY_MISSING,
                    "EPUB export requires ebooklib (pip install ebooklib)",
                    next_actions=["pip install ebooklib", "Or export --format markdown|txt"],
                    artifacts=[artifact(_rel(root, project), label="project")],
                    project_path=_rel(root, project),
                    format=normalized,
                    warnings=["ebooklib not installed"],
                )
            rc, legacy_output = _run_create_epub(project, out_path)
            if rc != 0:
                hint = " ".join(legacy_output) if legacy_output else "create_epub.py failed"
                return error_result(
                    E.EXPORT_FAILED,
                    f"EPUB export failed: {hint}",
                    next_actions=["pip install ebooklib", "Check chapters/ and story.md"],
                    project_path=_rel(root, project),
                    format=normalized,
                    legacy_output=legacy_output or None,
                )
            if not out_path.is_file():
                return error_result(
                    E.EXPORT_FAILED,
                    "EPUB export did not produce an output file",
                    project_path=_rel(root, project),
                    format=normalized,
                    legacy_output=legacy_output or None,
                )
    except OSError as exc:
        return error_result(
            E.EXPORT_FAILED,
            str(exc),
            project_path=_rel(root, project),
            format=normalized,
        )

    rel_out = _rel(root, out_path)
    arts = [
        artifact(rel_out, label="exported"),
        artifact(_rel(root, project), kind="directory", label="project"),
    ]

    details: dict = {
        "project_path": _rel(root, project),
        "format": normalized,
        "chapter_count": len(chapters),
        "output_path": rel_out,
    }
    if legacy_output:
        details["legacy_output"] = legacy_output
    if warnings:
        details["warnings"] = warnings

    return ok_result(
        E.EXPORT_OK,
        f"Exported {len(chapters)} chapter(s) as {normalized} -> {rel_out}",
        artifacts=arts,
        next_actions=[
            "novel-suite writer gate --phase 9 --json (verify)",
            "Optional: novel-marketing skill for blurb",
        ],
        **details,
    )
