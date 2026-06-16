"""Asset pack generation — wraps engine/scripts/character_asset_pack."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any

from novel_suite.video._legacy import load_video_script


@lru_cache(maxsize=1)
def _engine() -> ModuleType:
    return load_video_script("character_asset_pack")


def assets_root_for_chapter(project: Path, chapter_key: str = "ch01") -> Path:
    return project / "video" / chapter_key / "assets" / "characters"


def get_asset_pack_path(project: Path, chapter_key: str = "ch01") -> Path:
    """Manifest path produced by write_asset_pack (engine contract)."""
    return project / "video" / chapter_key / "character_assets.json"


def build_asset_pack(
    project: Path,
    chapter_key: str = "ch01",
    *,
    render_refs: bool = False,
    characters_filter: list[str] | None = None,
) -> dict[str, Any]:
    """Generate character asset pack via engine write_asset_pack."""
    manifest_path = _engine().write_asset_pack(
        project.resolve(),
        None,
        chapter_key=chapter_key,
        render_refs=render_refs,
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if characters_filter:
        filter_set = {name.strip() for name in characters_filter if name.strip()}
        manifest["characters"] = [
            c for c in manifest.get("characters", []) if c.get("name") in filter_set
        ]
        manifest["filter_applied"] = sorted(filter_set)

    manifest["assets_root"] = str(assets_root_for_chapter(project, chapter_key))
    manifest["manifest_path"] = str(manifest_path)
    return manifest
