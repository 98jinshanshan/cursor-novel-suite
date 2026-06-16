"""Multi-novel project registry with path bounds checks."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.paths import assert_project_in_allowed_roots, novels_dir, suite_root

REGISTRY_NAME = "_registry.json"
ACTIVE_NAME = ".active"

# Monkeypatch targets for legacy tests (project_registry / novel_bind)
NOVELS_DIR: Path | None = None
REGISTRY_PATH: Path | None = None
ACTIVE_PATH: Path | None = None
MONOREPO_ROOT: Path | None = None


def _novels_dir() -> Path:
    return NOVELS_DIR if NOVELS_DIR is not None else novels_dir()


def _registry_path() -> Path:
    return REGISTRY_PATH if REGISTRY_PATH is not None else _novels_dir() / REGISTRY_NAME


def _active_path() -> Path:
    return ACTIVE_PATH if ACTIVE_PATH is not None else _novels_dir() / ACTIVE_NAME


def _monorepo_root() -> Path:
    return MONOREPO_ROOT if MONOREPO_ROOT is not None else suite_root()


def slug_from_title(title: str) -> str:
    raw = title.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", raw, flags=re.UNICODE)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    if slug and re.search(r"[a-z0-9]", slug):
        return slug[:60]
    digest = uuid.uuid5(uuid.NAMESPACE_DNS, title.strip()).hex[:8]
    return f"novel-{digest}"


def _empty_registry() -> dict:
    return {"version": 1, "novels": [], "active_slug": None}


def load_registry() -> dict:
    path = _registry_path()
    _novels_dir()
    if not path.is_file():
        return _empty_registry()
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_registry(data: dict) -> None:
    _novels_dir()
    _registry_path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def list_slugs(data: dict | None = None) -> set[str]:
    reg = data if data is not None else load_registry()
    return {n["slug"] for n in reg.get("novels", [])}


def allocate_slug(title: str, data: dict | None = None) -> str:
    reg = data if data is not None else load_registry()
    used = list_slugs(reg)
    base = slug_from_title(title)
    candidate = base
    n = 2
    while candidate in used:
        candidate = f"{base}-{n}"
        n += 1
    return candidate


def resolve_project_path(entry: dict) -> Path:
    p = Path(entry["path"])
    if p.is_absolute():
        resolved = p.resolve()
    else:
        resolved = (_monorepo_root() / p).resolve()
    return assert_project_in_allowed_roots(resolved)


def unregister_novel(slug: str) -> dict | None:
    """Remove a novel from registry; clear active slug if needed."""
    reg = load_registry()
    match = next((n for n in reg.get("novels", []) if n.get("slug") == slug), None)
    if not match:
        return None
    reg["novels"] = [n for n in reg.get("novels", []) if n.get("slug") != slug]
    if reg.get("active_slug") == slug:
        reg["active_slug"] = reg["novels"][-1]["slug"] if reg["novels"] else None
    save_registry(reg)
    active_slug = reg.get("active_slug")
    if active_slug:
        _active_path().write_text(active_slug + "\n", encoding="utf-8")
    elif _active_path().is_file():
        _active_path().unlink(missing_ok=True)
    return match


def register_novel(
    project_path: Path,
    title: str,
    slug: str,
    *,
    platform_target: str = "通用",
) -> dict:
    project_path = project_path.resolve()
    if NOVELS_DIR is not None:
        try:
            project_path.relative_to(NOVELS_DIR.resolve())
        except ValueError as exc:
            raise ValueError(
                f"{E.PROJECT_PATH_OUT_OF_BOUNDS}: project must be under NOVELS_DIR"
            ) from exc
    else:
        project_path = assert_project_in_allowed_roots(project_path)
    reg = load_registry()
    root = _monorepo_root().resolve()
    try:
        path_str = project_path.relative_to(root).as_posix()
    except ValueError:
        path_str = project_path.as_posix()

    entry = {
        "id": str(uuid.uuid4()),
        "slug": slug,
        "title": title,
        "path": path_str,
        "platform_target": platform_target,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    reg["novels"] = [n for n in reg.get("novels", []) if n.get("slug") != slug]
    reg["novels"].append(entry)
    reg["active_slug"] = slug
    save_registry(reg)
    _active_path().write_text(slug + "\n", encoding="utf-8")
    return entry


def set_active(slug: str) -> Path:
    reg = load_registry()
    match = next((n for n in reg.get("novels", []) if n.get("slug") == slug), None)
    if not match:
        raise ValueError(f"{E.UNKNOWN_NOVEL_SLUG}: {slug}")
    reg["active_slug"] = slug
    save_registry(reg)
    _active_path().write_text(slug + "\n", encoding="utf-8")
    return resolve_project_path(match)


def get_active_slug() -> str | None:
    if _active_path().is_file():
        slug = _active_path().read_text(encoding="utf-8").strip()
        if slug:
            return slug
    reg = load_registry()
    return reg.get("active_slug")


def find_by_slug(slug: str) -> Path | None:
    reg = load_registry()
    match = next((n for n in reg.get("novels", []) if n.get("slug") == slug), None)
    if not match:
        return None
    return resolve_project_path(match)


def resolve_project(explicit: Path | None = None) -> Path:
    """Resolve project dir. Explicit ``--project`` keeps legacy behavior (any path)."""
    if explicit is not None:
        return explicit.resolve()
    slug = get_active_slug()
    if slug:
        path = find_by_slug(slug)
        if path and path.is_dir():
            return path
    raise ValueError(
        f"{E.NO_ACTIVE_NOVEL}: no --project and no active novel. "
        "Run: novel-suite writer init OR writer use <slug>"
    )


def default_novel_path(title: str) -> tuple[Path, str]:
    slug = allocate_slug(title)
    return _novels_dir() / slug, slug


def validate_registry_schema() -> list[str]:
    from novel_suite.writer._legacy import load_script_module

    gate = load_script_module("pipeline_gate")
    return gate.validate_registry()
