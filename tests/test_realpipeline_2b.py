"""RealPipeline-2B — NVP mandatory full-chain validation tests."""

from __future__ import annotations

import json
import re
from pathlib import Path

from novel_suite.core.commercialization import run_commercial_release_candidate_validate
from novel_suite.core.paths import suite_root
from novel_suite.core.realpipeline import (
    ACTIVE_SLUG,
    NVP_TEMPLATES,
    count_cjk,
    find_chapter_02,
    project_root,
    validate_realpipeline,
)

PROJECT = "novels/novel-837dd4f1"
ROOT = suite_root()


def test_nvp_contract_and_templates_exist():
    assert (ROOT / "docs/standards/NODE-VERIFICATION-PROMPT-CONTRACT.md").is_file()
    for tpl in NVP_TEMPLATES:
        assert (ROOT / "docs/verification-prompts" / tpl).is_file(), tpl


def test_active_project_is_novel_837dd4f1():
    active = (ROOT / "novels" / ".active").read_text(encoding="utf-8").strip()
    reg = json.loads((ROOT / "novels" / "_registry.json").read_text(encoding="utf-8"))
    assert active == ACTIVE_SLUG
    assert reg.get("active_slug") == ACTIVE_SLUG


def test_realpipeline_validate_ok():
    result = validate_realpipeline(PROJECT)
    assert result.status == "ok", result.message
    assert result.details.get("verdict") == "blocked"
    assert result.details.get("commercial_release_allowed") is False


def test_nvp_manifest_exists():
    manifest = project_root(PROJECT) / "reports" / "realpipeline_2b_nvp_manifest.json"
    assert manifest.is_file()
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data.get("overall_grade") in ("A", "B", "C", "D")
    assert data.get("commercial_release_allowed") is False


def test_phase0_source_record():
    p = project_root(PROJECT) / "reports" / "phase0_source_record.md"
    assert p.is_file()
    text = p.read_text(encoding="utf-8")
    assert "2026-W23" in text or "radar" in text


def test_chapter_02_length_and_canon():
    ch = find_chapter_02(project_root(PROJECT))
    assert ch and ch.is_file()
    text = ch.read_text(encoding="utf-8")
    assert count_cjk(text) >= 2500
    assert "林骁" in text
    assert "陈琪" in text
    assert "林澄" not in text and "程砚" not in text


def test_review_deai_platform_triple():
    proj = project_root(PROJECT)
    assert list(proj.glob("reviews/02_*-review.md"))
    assert list(proj.glob("reviews/02_*-deai.md"))
    assert list(proj.glob("reviews/02_*-platform-compliance.md"))


def test_snapshot_ch02_after():
    snap = project_root(PROJECT) / "canon" / "snapshots" / "ch02-after.md"
    assert snap.is_file()


def test_video_ch02_package_and_qc():
    vid = project_root(PROJECT) / "video" / "ch02"
    for name in (
        "storyboard.json",
        "shot_list.csv",
        "asset_pack.md",
        "narration_script.md",
        "subtitles.srt",
        "timeline_package.json",
        "video_generation_blockers.md",
        "video_qc_report.md",
    ):
        assert (vid / name).is_file(), name
    qc = (vid / "video_qc_report.md").read_text(encoding="utf-8")
    m = re.search(r"video_level:\s*([ABCD][+-]?)", qc, re.I)
    assert m, "video_qc_report must declare video_level"
    level = m.group(1).upper()
    comfy_manifest = vid / "comfyui_render_manifest.json"
    comfy_verified = False
    if comfy_manifest.is_file():
        data = json.loads(comfy_manifest.read_text(encoding="utf-8"))
        shots = data.get("rendered_shots") or []
        comfy_verified = len(shots) >= 5 and all(s.get("prompt_id") for s in shots[:5])
    if comfy_verified and level.startswith("B"):
        assert level in ("B-", "B", "A-", "A")
    else:
        assert level in "CD", "dynamic text card / no mp4 must not be A/B without ComfyUI evidence"


def test_no_realgen_demo_success_path():
    assert not (ROOT / "novel-suite" / "realgen-demo" / "cold_case_echo_realgen_01").is_dir()


def test_commercial_still_blocked():
    result = run_commercial_release_candidate_validate()
    assert result.details.get("verdict") == "blocked"
