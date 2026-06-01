#!/usr/bin/env python3
"""Bind video jobs to novel projects via registry + storyboard metadata."""

from __future__ import annotations

import importlib
import importlib.util
import json
import sys
import types
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_WRITER_ENGINE: Path | None = None
_REG: Any = None
_SP: Any = None


def _writer_engine() -> Path:
    global _WRITER_ENGINE
    if _WRITER_ENGINE is None:
        video_root = Path(__file__).resolve().parents[2]
        suite_root = video_root.parent
        writer_cli = suite_root / "cursor-novel-writer" / "engine" / "novel_cli.py"
        if (suite_root / ".novel-suite-root").is_file() and writer_cli.is_file():
            _WRITER_ENGINE = suite_root / "cursor-novel-writer" / "engine"
        else:
            _WRITER_ENGINE = suite_root / "cursor-novel-writer" / "engine"
    return _WRITER_ENGINE


def _suite_paths_module():
    """Load writer suite_paths without colliding with cursor-novel-video/scripts."""
    global _SP
    if _SP is not None:
        return _SP
    engine = _writer_engine()
    path = engine / "scripts" / "suite_paths.py"
    spec = importlib.util.spec_from_file_location("novel_writer_suite_paths", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load suite_paths from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _SP = mod
    return mod


def _registry_module():
    """Load writer project_registry (depends on suite_paths)."""
    global _REG
    if _REG is not None:
        return _REG
    engine = _writer_engine()
    saved_path = sys.path[:]
    scripts_snapshot = sys.modules.get("scripts")
    try:
        sys.path.insert(0, str(engine))
        for key in list(sys.modules):
            if key == "scripts" or key.startswith("scripts."):
                mod = sys.modules[key]
                mod_file = getattr(mod, "__file__", "") or ""
                if "cursor-novel-video" in mod_file.replace("\\", "/"):
                    del sys.modules[key]
        if "scripts" not in sys.modules:
            pkg = types.ModuleType("scripts")
            pkg.__path__ = [str(engine / "scripts")]
            sys.modules["scripts"] = pkg
        _REG = importlib.import_module("scripts.project_registry")
        return _REG
    finally:
        sys.path[:] = saved_path
        if scripts_snapshot is not None and "scripts" not in sys.modules:
            sys.modules["scripts"] = scripts_snapshot


def _suite_root() -> Path:
    return _suite_paths_module().suite_root()


def _slug_in_registry(slug: str) -> bool:
    reg_path = _suite_root() / "novels" / "_registry.json"
    if not reg_path.is_file():
        return False
    try:
        data = json.loads(reg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return any(n.get("slug") == slug for n in data.get("novels", []))


def infer_novel_binding(chapter: Path, *, project: Path | None = None) -> dict[str, Any] | None:
    """Resolve novel slug/project from chapter path or explicit --project."""
    chapter = chapter.resolve()
    if project is not None:
        root = project.resolve()
        try:
            rel_chapter = chapter.relative_to(root)
        except ValueError:
            if chapter.parent.name == "chapters":
                root = chapter.parent.parent
                rel_chapter = chapter.relative_to(root)
            else:
                return None
    else:
        root = None
        rel_chapter = None
        for anc in chapter.parents:
            canon = anc / "canon" / "project.json"
            if canon.is_file():
                root = anc
                rel_chapter = chapter.relative_to(root)
                break
        if root is None:
            return None

    meta_path = root / "canon" / "project.json"
    slug = root.name
    title = slug
    if meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            slug = str(meta.get("slug") or slug)
            title = str(meta.get("title") or title)
        except json.JSONDecodeError:
            pass

    suite_root = _suite_root()
    try:
        rel_to_monorepo = root.relative_to(suite_root.resolve()).as_posix()
    except ValueError:
        rel_to_monorepo = root.as_posix()

    chapter_rel = rel_chapter.as_posix() if rel_chapter else chapter.name
    return {
        "novel_slug": slug,
        "novel_title": title,
        "novel_project": rel_to_monorepo,
        "source_chapter": chapter_rel,
        "in_registry": _slug_in_registry(slug),
    }


def job_dir_rel(job_dir: Path) -> str:
    try:
        return job_dir.resolve().relative_to(_suite_root().resolve()).as_posix()
    except ValueError:
        return job_dir.resolve().as_posix()


def record_video_job(
    binding: dict[str, Any],
    *,
    job_id: str,
    job_dir: Path,
    mode: str,
    status: str = "running",
    artifact: str | None = None,
) -> bool:
    if not binding.get("in_registry"):
        return False
    reg = _registry_module()
    data = reg.load_registry()
    slug = binding["novel_slug"]
    now = datetime.now(timezone.utc).isoformat()
    record = {
        "job_id": job_id,
        "mode": mode,
        "chapter": binding["source_chapter"],
        "status": status,
        "job_dir": job_dir_rel(job_dir),
        "updated_at": now,
    }
    if artifact:
        record["artifact"] = artifact

    updated = False
    for entry in data.get("novels", []):
        if entry.get("slug") != slug:
            continue
        jobs: list[dict[str, Any]] = list(entry.get("video_jobs") or [])
        existing = next((j for j in jobs if j.get("job_id") == job_id), None)
        jobs = [j for j in jobs if j.get("job_id") != job_id]
        record["created_at"] = existing.get("created_at", now) if existing else now
        jobs.append(record)
        entry["video_jobs"] = jobs
        updated = True
        break
    if updated:
        reg.save_registry(data)
    return updated


def storyboard_novel_block(binding: dict[str, Any]) -> dict[str, Any]:
    return {
        "slug": binding["novel_slug"],
        "title": binding.get("novel_title"),
        "project": binding["novel_project"],
        "chapter": binding["source_chapter"],
        "in_registry": binding.get("in_registry", False),
    }
