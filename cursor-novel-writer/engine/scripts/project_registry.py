#!/usr/bin/env python3
"""Multi-novel registry — delegates to novel_suite.writer.registry when installed."""

from __future__ import annotations

from pathlib import Path

try:
    from novel_suite.bootstrap import ensure_src_path

    ensure_src_path()
    from novel_suite.core.paths import novels_dir as _paths_novels_dir, suite_root, writer_root
    from novel_suite.writer import registry as _reg

    _reg.NOVELS_DIR = _paths_novels_dir()
    _reg.REGISTRY_PATH = _reg.NOVELS_DIR / _reg.REGISTRY_NAME
    _reg.ACTIVE_PATH = _reg.NOVELS_DIR / _reg.ACTIVE_NAME
    _reg.MONOREPO_ROOT = suite_root()

    MONOREPO_ROOT = _reg.MONOREPO_ROOT
    WRITER_ROOT = writer_root()
    NOVELS_DIR = _reg.NOVELS_DIR
    REGISTRY_PATH = _reg.REGISTRY_PATH
    ACTIVE_PATH = _reg.ACTIVE_PATH

    monorepo_root = _reg._monorepo_root
    novels_root = _reg._novels_dir
    slug_from_title = _reg.slug_from_title
    load_registry = _reg.load_registry
    save_registry = _reg.save_registry
    list_slugs = _reg.list_slugs
    allocate_slug = _reg.allocate_slug
    register_novel = _reg.register_novel
    set_active = _reg.set_active
    get_active_slug = _reg.get_active_slug
    resolve_project_path = _reg.resolve_project_path
    find_by_slug = _reg.find_by_slug
    resolve_project = _reg.resolve_project
    default_novel_path = _reg.default_novel_path
    validate_registry_schema = _reg.validate_registry_schema
    assert_project_in_allowed_roots = _reg.assert_project_in_allowed_roots

except ImportError:
    from scripts import suite_paths as sp

    MONOREPO_ROOT = sp.suite_root()
    WRITER_ROOT = sp.writer_root()
    NOVELS_DIR = sp.novels_dir()
    REGISTRY_PATH = NOVELS_DIR / "_registry.json"
    ACTIVE_PATH = NOVELS_DIR / ".active"

    import json
    import re
    import uuid
    from datetime import datetime, timezone

    def monorepo_root() -> Path:
        return MONOREPO_ROOT

    def novels_root() -> Path:
        NOVELS_DIR.mkdir(parents=True, exist_ok=True)
        return NOVELS_DIR

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
        novels_root()
        if not REGISTRY_PATH.is_file():
            return _empty_registry()
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def save_registry(data: dict) -> None:
        novels_root()
        REGISTRY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

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

    def register_novel(project_path: Path, title: str, slug: str, *, platform_target: str = "通用") -> dict:
        reg = load_registry()
        rel = project_path.resolve()
        try:
            path_str = rel.relative_to(MONOREPO_ROOT.resolve()).as_posix()
        except ValueError:
            path_str = rel.as_posix()
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
        ACTIVE_PATH.write_text(slug + "\n", encoding="utf-8")
        return entry

    def set_active(slug: str) -> Path:
        reg = load_registry()
        match = next((n for n in reg.get("novels", []) if n.get("slug") == slug), None)
        if not match:
            raise ValueError(f"Unknown novel slug: {slug}")
        reg["active_slug"] = slug
        save_registry(reg)
        ACTIVE_PATH.write_text(slug + "\n", encoding="utf-8")
        return resolve_project_path(match)

    def get_active_slug() -> str | None:
        if ACTIVE_PATH.is_file():
            slug = ACTIVE_PATH.read_text(encoding="utf-8").strip()
            if slug:
                return slug
        reg = load_registry()
        return reg.get("active_slug")

    def resolve_project_path(entry: dict) -> Path:
        p = Path(entry["path"])
        if p.is_absolute():
            return p.resolve()
        return (MONOREPO_ROOT / p).resolve()

    def find_by_slug(slug: str) -> Path | None:
        reg = load_registry()
        match = next((n for n in reg.get("novels", []) if n.get("slug") == slug), None)
        if not match:
            return None
        return resolve_project_path(match)

    def resolve_project(explicit: Path | None = None) -> Path:
        if explicit is not None:
            return explicit.resolve()
        slug = get_active_slug()
        if slug:
            path = find_by_slug(slug)
            if path and path.is_dir():
                return path
        raise SystemExit(
            "ERROR: No --project and no active novel. "
            "Run: novel init --title '...' OR novel use <slug> OR novel init with --output"
        )

    def default_novel_path(title: str) -> tuple[Path, str]:
        slug = allocate_slug(title)
        return novels_root() / slug, slug

    def validate_registry_schema() -> list[str]:
        return []

    def assert_project_in_allowed_roots(project: Path) -> Path:
        return project.resolve()
