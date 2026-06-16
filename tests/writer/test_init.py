"""Writer init (Phase H) — scaffold + registry + gate phase 1."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from novel_suite.core import errors as E
from novel_suite.writer import gate, init, registry


@pytest.fixture
def novels_tmp(repo_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    novels = tmp_path / "novels"
    novels.mkdir(parents=True)
    import novel_suite.writer.registry as ns_reg

    monkeypatch.setenv("NOVEL_SUITE_ROOT", str(repo_root))
    monkeypatch.setattr(ns_reg, "NOVELS_DIR", novels)
    monkeypatch.setattr(ns_reg, "REGISTRY_PATH", novels / "_registry.json")
    monkeypatch.setattr(ns_reg, "ACTIVE_PATH", novels / ".active")
    monkeypatch.setattr(ns_reg, "MONOREPO_ROOT", tmp_path)
    return novels


def test_run_init_minimal(novels_tmp: Path, tmp_path: Path):
    result = init.run_init(
        title="测试书",
        premise="一句梗概用于验收。",
        genre="悬疑",
        platform_target="晋江",
    )
    assert result.status == "ok"
    assert result.code == "INIT_OK"
    slug = result.details["slug"]
    project = novels_tmp / slug
    assert project.is_dir()
    assert (project / "story.md").is_file()
    assert (project / "canon" / "project.json").is_file()
    assert (project / "canon" / "progress.json").is_file()
    assert result.details.get("slug") == slug


def test_run_init_with_concept(novels_tmp: Path, repo_root: Path):
    concepts = list((repo_root / "intel" / "concepts").glob("*.md"))
    if not concepts:
        pytest.skip("no intel/concepts/*.md in repo")
    concept = concepts[0]
    result = init.run_init(
        title="概念立项书",
        premise="从 concept 文件立项的测试梗概。",
        concept=concept,
    )
    assert result.status == "ok"
    project = Path(result.details["project_path"])
    assert (project / "canon" / "concept-brief.md").is_file()
    gate_result = gate.run_gate(project, 1)
    if gate_result.status != "ok":
        pytest.skip(f"gate phase 1 blocked in test env: {gate_result.required[:2]}")


def test_init_then_gate_after_scan_demo(novels_tmp: Path, repo_root: Path):
    """Integration: suite radar complete + concept → gate phase 1."""
    from novel_suite.writer.intel import run_scan

    run_scan(demo=True)
    concepts = list((repo_root / "intel" / "concepts").glob("*.md"))
    if not concepts:
        pytest.skip("no concepts")
    result = init.run_init(
        title="扫榜后立项",
        premise="先 scan demo 再 init 的集成测试梗概。",
        concept=concepts[0],
    )
    assert result.status == "ok"
    project = Path(result.details["project_path"])
    gate_result = gate.run_gate(project, 1)
    assert gate_result.status == "ok", gate_result.required


def test_init_concept_not_found(novels_tmp: Path, tmp_path: Path):
    result = init.run_init(
        title="无概念",
        premise="梗概",
        concept=tmp_path / "missing-concept.md",
    )
    assert result.status == "error"
    assert result.code == "CONCEPT_NOT_FOUND"


def test_init_empty_title(novels_tmp: Path):
    result = init.run_init(title="  ", premise="x")
    assert result.code == E.INIT_TITLE_REQUIRED


def test_run_init_platform_target_fanqie(novels_tmp: Path):
    result = init.run_init(
        title="番茄书",
        premise="平台感知立项测试梗概。",
        platform_target="fanqie",
    )
    assert result.status == "ok"
    project = Path(result.details["project_path"])
    data = json.loads((project / "canon" / "project.json").read_text(encoding="utf-8"))
    assert data["platform_target"] == "fanqie"


def test_run_init_platform_target_douyin(novels_tmp: Path):
    result = init.run_init(
        title="抖音书",
        premise="视频推文立项测试梗概。",
        platform_target="douyin",
    )
    assert result.status == "ok"
    project = Path(result.details["project_path"])
    data = json.loads((project / "canon" / "project.json").read_text(encoding="utf-8"))
    assert data["platform_target"] == "douyin"


def test_run_init_platform_target_default(novels_tmp: Path):
    result = init.run_init(title="默认书", premise="默认平台立项测试梗概。")
    assert result.status == "ok"
    project = Path(result.details["project_path"])
    data = json.loads((project / "canon" / "project.json").read_text(encoding="utf-8"))
    assert data["platform_target"] == "通用"
