"""Character asset quality control — wraps engine/scripts/character_ref_qc."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any

from novel_suite.video._legacy import load_video_script
from novel_suite.video.character.asset_packer import get_asset_pack_path
from novel_suite.video.character.cvdp_loader import cvdp_path_for_chapter, load_cvdp


@lru_cache(maxsize=1)
def _engine() -> ModuleType:
    return load_video_script("character_ref_qc")


def chapter_job_dir(project: Path, chapter_key: str = "ch01") -> Path:
    """Directory holding character_assets.json (engine qc_cvdp_cards contract)."""
    return project / "video" / chapter_key


def run_character_qc(
    project: Path,
    chapter_key: str = "ch01",
) -> dict[str, Any]:
    """Run CVDP + asset pack quality checks."""
    cvdp_path = cvdp_path_for_chapter(project, chapter_key)
    if not cvdp_path.is_file():
        return {
            "ok": False,
            "errors": [f"CVDP not found: {cvdp_path}"],
            "warnings": [],
            "summary": {"total": 0, "passed": 0, "failed": 1},
            "cvdp_source": str(cvdp_path),
            "asset_pack_source": "",
        }

    pack_path = get_asset_pack_path(project, chapter_key)
    if not pack_path.is_file():
        return {
            "ok": False,
            "errors": [
                f"Asset pack not found: {pack_path}. Run 'novel-suite video character pack' first.",
            ],
            "warnings": [],
            "summary": {"total": 0, "passed": 0, "failed": 1},
            "cvdp_source": str(cvdp_path),
            "asset_pack_source": str(pack_path),
        }

    cvdp = load_cvdp(project, chapter_key)
    job_dir = chapter_job_dir(project, chapter_key)
    result = dict(_engine().qc_cvdp_cards(job_dir, cvdp))

    total = len(cvdp.get("characters", []))
    errors = list(result.get("errors", []))
    result["summary"] = {
        "total": total,
        "passed": max(0, total - len(errors)),
        "failed": len(errors),
    }
    result["cvdp_source"] = str(cvdp_path)
    result["asset_pack_source"] = str(pack_path)
    return result
