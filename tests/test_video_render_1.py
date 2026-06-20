"""VideoRender-1 — ch02 local render + NVP-V2 validation."""

from __future__ import annotations

import json
import re
from pathlib import Path

from novel_suite.core.commercialization import run_commercial_release_candidate_validate
from novel_suite.core.paths import suite_root
from novel_suite.core.realpipeline import validate_realpipeline

CH02 = suite_root() / "novels" / "novel-837dd4f1" / "video" / "ch02"
PROJECT = "novels/novel-837dd4f1"


def test_local_accel_report_exists():
    assert (CH02 / "local_accel_report.md").is_file()


def test_render_manifest_exists():
    manifest = CH02 / "render_manifest.json"
    assert manifest.is_file()
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data.get("pipeline") == "VideoRender-1"
    assert data.get("not_ai_short_drama") is True
    assert data.get("commercial_release_allowed") is False


def test_visuals_or_blocker():
    visuals = list((CH02 / "visuals").glob("shot_*.png")) if (CH02 / "visuals").is_dir() else []
    blockers = CH02 / "render_blocked_report.md"
    assert len(visuals) >= 5 or blockers.is_file()


def test_output_mp4_or_blocker():
    mp4 = CH02 / "output" / "ch02_motion_drama_9x16.mp4"
    blocked = CH02 / "render_blocked_report.md"
    assert mp4.is_file() or blocked.is_file()
    if mp4.is_file():
        assert mp4.stat().st_size > 1000


def test_video_qc_report_grade():
    qc = (CH02 / "video_qc_report.md").read_text(encoding="utf-8")
    m = re.search(r"video_level:\s*([ABCD][+-]?)", qc, re.I)
    assert m, "video_qc_report must declare video_level"
    level = m.group(1).upper()
    comfy_manifest = CH02 / "comfyui_render_manifest.json"
    comfy_verified = False
    if comfy_manifest.is_file():
        cm = json.loads(comfy_manifest.read_text(encoding="utf-8"))
        shots = cm.get("rendered_shots") or []
        comfy_verified = len(shots) >= 5 and all(
            (s.get("source") == "comfyui" and s.get("prompt_id")) for s in shots[:5]
        )
    if comfy_verified and level in ("B", "B-"):
        return
    manifest = json.loads((CH02 / "render_manifest.json").read_text(encoding="utf-8"))
    comfy = manifest.get("comfyui_available") is True
    if not comfy:
        assert level in "CD", "without ComfyUI cannot be A/B"


def test_nvp_v2_results_exist():
    assert (CH02 / "NVP-V2-video-export-qc.result.md").is_file()
    assert (suite_root() / "novels" / "novel-837dd4f1" / "reports" / "NVP-V2-video-export-qc.result.md").is_file()


def test_commercial_still_blocked():
    assert run_commercial_release_candidate_validate().details.get("verdict") == "blocked"


def test_realpipeline_still_validates():
    result = validate_realpipeline(PROJECT)
    assert result.details.get("verdict") == "blocked"
