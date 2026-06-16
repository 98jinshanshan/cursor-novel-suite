"""Canonical chapter path resolution for video CLI (--chapter with --project)."""

from __future__ import annotations

import json
import re
from pathlib import Path


def _normalize_chapter_arg(chapter: str) -> str:
    return chapter.strip().replace("\\", "/")


def _chapter_key_number(chapter: str) -> int | None:
    m = re.fullmatch(r"ch0*(\d+)", chapter.strip(), flags=re.IGNORECASE)
    if not m:
        return None
    return int(m.group(1))


def _resolve_from_progress(project: Path, number: int) -> Path | None:
    progress_path = project / "canon" / "progress.json"
    if not progress_path.is_file():
        return None
    try:
        data = json.loads(progress_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    for entry in data.get("chapters") or []:
        if not isinstance(entry, dict):
            continue
        if int(entry.get("number", 0)) != number:
            continue
        rel_file = str(entry.get("file") or "").strip()
        if not rel_file:
            continue
        candidate = (project / rel_file).resolve()
        if candidate.is_file():
            return candidate
    return None


def list_project_chapters(project: Path) -> list[Path]:
    """Published chapter markdown files for error hints."""
    found: list[Path] = []
    progress_path = project / "canon" / "progress.json"
    if progress_path.is_file():
        try:
            data = json.loads(progress_path.read_text(encoding="utf-8"))
            for entry in data.get("chapters") or []:
                if not isinstance(entry, dict):
                    continue
                rel_file = str(entry.get("file") or "").strip()
                if not rel_file:
                    continue
                candidate = (project / rel_file).resolve()
                if candidate.is_file():
                    found.append(candidate)
        except (json.JSONDecodeError, OSError):
            pass
    chapters_dir = project / "chapters"
    if chapters_dir.is_dir():
        for md in sorted(chapters_dir.glob("*.md")):
            if md.name.startswith("_"):
                continue
            resolved = md.resolve()
            if resolved not in found:
                found.append(resolved)
    return found


def format_chapter_hints(project: Path) -> list[str]:
    hints: list[str] = []
    for path in list_project_chapters(project):
        try:
            rel = path.relative_to(project.resolve()).as_posix()
        except ValueError:
            rel = path.name
        hints.append(rel)
    return hints


def resolve_chapter_path(chapter: str | Path, project: Path | None) -> Path:
    """
    Resolve --chapter for video commands.

    Accepts:
    - bare filename: ``01_卷宗亮了.md`` → ``<project>/chapters/...``
    - project-relative: ``chapters/01_卷宗亮了.md``
    - chapter key: ``ch01`` / ``ch1`` (via canon/progress.json)
    - absolute path

    Never double-prefix ``chapters/chapters/``.
    """
    raw = _normalize_chapter_arg(str(chapter))
    rel = Path(raw)

    if project is None:
        return rel.expanduser().resolve()

    root = project.resolve()
    if rel.is_absolute():
        return rel.resolve()

    number = _chapter_key_number(raw)
    if number is not None:
        from_progress = _resolve_from_progress(root, number)
        if from_progress is not None:
            return from_progress

    direct = (root / rel).resolve()
    if direct.is_file():
        return direct

    # Bare filename only — avoid chapters/chapters/ when arg already has a path segment.
    if len(rel.parts) == 1:
        return (root / "chapters" / rel).resolve()

    return direct
