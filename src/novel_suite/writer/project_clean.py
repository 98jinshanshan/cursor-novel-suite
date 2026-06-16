"""Empty novel project detection and cleanup."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from novel_suite.writer import registry


def _entry_project_path(entry: dict) -> Path | None:
    """Resolve registry entry path without suite-root bounds check."""
    raw = entry.get("path")
    if not raw:
        return None
    p = Path(str(raw))
    if p.is_absolute():
        resolved = p.resolve()
    else:
        resolved = (registry._monorepo_root() / p).resolve()
    return resolved if resolved.is_dir() else None


def chapter_count(project: Path) -> int:
    """Count published chapter files (exclude _index and .drafts)."""
    progress_path = project / "canon" / "progress.json"
    if progress_path.is_file():
        try:
            progress = json.loads(progress_path.read_text(encoding="utf-8"))
            chapters = progress.get("chapters", [])
            if isinstance(chapters, list) and chapters:
                return sum(
                    1
                    for ch in chapters
                    if isinstance(ch, dict) and ch.get("file")
                )
        except (json.JSONDecodeError, OSError):
            pass

    chapters_dir = project / "chapters"
    if not chapters_dir.is_dir():
        return 0
    return len(
        [
            f
            for f in chapters_dir.glob("*.md")
            if f.is_file() and not f.name.startswith("_")
        ]
    )


def is_empty_project(project: Path) -> bool:
    if not project.is_dir():
        return False
    return chapter_count(project) == 0


def list_empty_projects() -> list[dict[str, Any]]:
    """Return registry entries with zero chapters or missing project directories."""
    reg = registry.load_registry()
    empty: list[dict[str, Any]] = []
    for entry in reg.get("novels", []):
        raw_path = entry.get("path")
        path = _entry_project_path(entry)
        if path is None:
            empty.append(
                {
                    "slug": entry.get("slug"),
                    "title": entry.get("title"),
                    "path": str(raw_path) if raw_path else None,
                    "chapter_count": 0,
                    "orphan": True,
                }
            )
            continue
        if is_empty_project(path):
            empty.append(
                {
                    "slug": entry.get("slug"),
                    "title": entry.get("title"),
                    "path": str(path),
                    "chapter_count": 0,
                    "orphan": False,
                }
            )
    return empty


def remove_project(slug: str, *, delete_files: bool = True) -> dict[str, Any] | None:
    """Unregister a novel and optionally delete its directory."""
    reg = registry.load_registry()
    entry = next((n for n in reg.get("novels", []) if n.get("slug") == slug), None)
    if entry is None:
        return None
    try:
        path = registry.resolve_project_path(entry)
    except ValueError:
        path = None
    registry.unregister_novel(slug)
    if delete_files and path and path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    return entry


def reclaim_empty_slug(title: str, *, slug: str = "") -> list[str]:
    """Unregister and delete empty projects blocking the same title/slug."""
    removed: list[str] = []
    candidates: list[str] = []
    if slug.strip():
        candidates.append(slug.strip())
    base = registry.slug_from_title(title)
    if base not in candidates:
        candidates.append(base)
    reg = registry.load_registry()
    for candidate in candidates:
        entry = next((n for n in reg.get("novels", []) if n.get("slug") == candidate), None)
        path = _entry_project_path(entry) if entry else None
        if path and is_empty_project(path):
            if remove_project(candidate, delete_files=True):
                removed.append(candidate)
    return removed


def remove_empty_at_path(project: Path) -> bool:
    """Delete an empty project directory and registry entry if slug matches."""
    resolved = project.resolve()
    if not resolved.is_dir() or not is_empty_project(resolved):
        return False
    reg = registry.load_registry()
    match = None
    for n in reg.get("novels", []):
        entry_path = _entry_project_path(n)
        if entry_path == resolved:
            match = n
            break
    if match and match.get("slug"):
        remove_project(str(match["slug"]), delete_files=True)
        return True
    shutil.rmtree(resolved, ignore_errors=True)
    return True


def clean_empty_projects(*, dry_run: bool = False) -> dict[str, Any]:
    """Remove all registry novels with zero chapters."""
    targets = list_empty_projects()
    removed: list[dict[str, Any]] = []
    if not dry_run:
        for item in targets:
            slug = item.get("slug")
            if slug:
                entry = remove_project(str(slug), delete_files=True)
                if entry:
                    removed.append(item)
    return {
        "dry_run": dry_run,
        "found": len(targets),
        "removed": removed if not dry_run else [],
        "targets": targets,
    }
