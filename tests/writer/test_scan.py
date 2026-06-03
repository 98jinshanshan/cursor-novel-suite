"""Writer scan (Phase F) — demo fixture and metadata."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from novel_suite.writer.intel import (
    confidence_from_score,
    run_scan,
    source_type_for_run,
    theme_record,
)


def test_source_type_demo():
    assert source_type_for_run(demo=True, input_path=None) == "demo_fixture"


def test_theme_record_unverified():
    rec = theme_record(
        theme="逆袭复仇爽文",
        score=10,
        sample_size=15,
        platform_coverage=3,
        source_type="demo_fixture",
        verified=False,
    )
    assert rec["verified"] is False
    assert "source_unverified" in rec["risks"]
    assert rec["confidence"] in ("low", "medium", "high")


def test_run_scan_demo(repo_root: Path, tmp_path: Path):
    radar = tmp_path / "radar" / "2026-W99.md"
    concepts = tmp_path / "concepts"
    result = run_scan(
        period="week",
        demo=True,
        radar_path=radar,
        concepts_dir=concepts,
        concept_top=3,
    )
    assert result.status == "ok"
    assert result.code == "SCAN_OK"
    assert result.details["source_type"] == "demo_fixture"
    assert result.details["verified"] is False
    assert result.details["sample_size"] >= 1
    assert len(result.details["themes"]) >= 1
    assert radar.is_file()
    assert concepts.is_dir()
    completion = next(a for a in result.artifacts if a.get("label") == "completion")
    assert Path(repo_root / completion["path"]).is_file() or Path(completion["path"]).is_file()


def test_run_scan_demo_json_fields(repo_root: Path, tmp_path: Path):
    result = run_scan(
        demo=True,
        radar_path=tmp_path / "r.md",
        concepts_dir=tmp_path / "c",
    )
    themes = result.details["themes"]
    assert themes[0]["theme"]
    assert "score" in themes[0]
    assert "confidence" in themes[0]


def test_scan_input_missing(tmp_path: Path):
    result = run_scan(input_path=tmp_path / "nope.json")
    assert result.status == "error"
    assert result.code == "SCAN_INPUT_NOT_FOUND"
