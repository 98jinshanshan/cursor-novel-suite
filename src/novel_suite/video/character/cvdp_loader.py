"""Load and index Character Visual Design Profile (CVDP)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any

from novel_suite.video._legacy import load_video_script


@lru_cache(maxsize=1)
def _engine() -> ModuleType:
    return load_video_script("character_visual_design")


def cvdp_path_for_chapter(project: Path, chapter_key: str = "ch01") -> Path:
    return _engine().cvdp_path_for_chapter(project, chapter_key)


def load_cvdp(project: Path, chapter_key: str = "ch01") -> dict[str, Any]:
    return _engine().load_cvdp(project, chapter_key)


def index_characters(cvdp: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return _engine().index_characters(cvdp)


def list_characters(
    project: Path,
    chapter_key: str = "ch01",
) -> list[dict[str, Any]]:
    """Load CVDP and return character summaries (no full prompt bodies)."""
    cvdp = load_cvdp(project, chapter_key)
    by_name = index_characters(cvdp)
    summary: list[dict[str, Any]] = []
    for name, char in sorted(by_name.items()):
        summary.append(
            {
                "id": char["id"],
                "name": name,
                "role": char.get("role", ""),
                "age": char.get("age", ""),
                "appearance_class": char.get("appearance_class", "live"),
                "consistency_token": char.get("consistency_token", ""),
                "has_ref_prompt": bool(char.get("ref_prompt_positive")),
            }
        )
    return summary


def get_character_names(project: Path, chapter_key: str = "ch01") -> list[str]:
    """Return character names for storyboard / pack pipelines."""
    cvdp = load_cvdp(project, chapter_key)
    by_name = index_characters(cvdp)
    return list(by_name.keys())
