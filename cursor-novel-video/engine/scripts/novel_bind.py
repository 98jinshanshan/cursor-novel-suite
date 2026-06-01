#!/usr/bin/env python3
"""Bind video jobs to novel projects via registry + storyboard metadata."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_WRITER_ENGINE = None
_REG: Any = None


def _writer_engine() -> Path:
    global _WRITER_ENGINE
    if _WRITER_ENGINE is None:
        video_root = Path(__file__).resolve().parents[2]
        suite_root = video_root.parent
        marker = suite_root / ".novel-suite-root"
        writer_cli = suite_root / "cursor-novel-writer" / "engine" / "novel_cli.py"
        if marker.is_file() and writer_cli.is_file():
            _WRITER_ENGINE = suite_root / "cursor-novel-writer" / "engine"
        else:
            _WRITER_ENGINE = suite_root / "cursor-novel-writer" / "engine"
    return _WRITER_ENGINE


def _registry_module():
    global _REG
    if _REG is not None:
        return _REG
    engine = _writer_engine()
    mod_path = engine / "scripts" / "project_registry.py"
    import importlib.util

    spec = importlib.util.spec_from_file_location("novel_project_registry", mod_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load project_registry from {mod_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _REG = mod
    return mod


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

    reg = _registry_module()
    in_registry = reg.find_by_slug(slug) is not None
    try:
        rel_to_monorepo = root.relative_to(reg.MONOREPO_ROOT.resolve()).as_posix()
    except ValueError:
        rel_to_monorepo = root.as_posix()

    chapter_rel = rel_chapter.as_posix() if rel_chapter else chapter.name
    return {
        "novel_slug": slug,
        "novel_title": title,
        "novel_project": rel_to_monorepo,
        "source_chapter": chapter_rel,
        "in_registry": in_registry,
    }


def job_dir_rel(job_dir: Path) -> str:
    reg = _registry_module()
    try:
        return job_dir.resolve().relative_to(reg.MONOREPO_ROOT.resolve()).as_posix()
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
