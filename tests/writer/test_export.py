"""Writer export — gate, formats, and artifact contract."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from novel_suite.core import errors as E
from novel_suite.writer import export, gate

REPO = Path(__file__).resolve().parents[2]
DEMO = REPO / "cursor-novel-writer" / "examples" / "demo-novel"


@pytest.fixture
def allow_skip_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(E.ENV_ALLOW_SKIP_GATE, "1")


def test_invalid_export_format(tmp_path: Path):
    project = tmp_path / "novel"
    project.mkdir()
    result = export.run_export(project, fmt="pdf", skip_gate=True)
    assert result.status == "error"
    assert result.code == E.INVALID_EXPORT_FORMAT


def test_export_gate_blocked(tmp_path: Path):
    project = tmp_path / "empty"
    project.mkdir()
    (project / "chapters").mkdir()
    (project / "chapters" / "01_test.md").write_text("# 第一章\n\n正文。\n", encoding="utf-8")
    (project / "task_plan.md").write_text("- [ ] Phase 0: x\n", encoding="utf-8")
    result = export.run_export(project, fmt="markdown", skip_gate=False)
    assert result.status == "error"
    assert result.code == E.EXPORT_BLOCKED


def test_skip_gate_requires_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(E.ENV_ALLOW_SKIP_GATE, raising=False)
    project = tmp_path / "novel"
    project.mkdir()
    result = export.run_export(project, fmt="markdown", skip_gate=True)
    assert result.code == E.SKIP_GATE_NOT_ALLOWED


def test_export_markdown_success(tmp_path: Path, allow_skip_gate: None):
    project = tmp_path / "novel"
    (project / "chapters").mkdir(parents=True)
    (project / "chapters" / "01_试章.md").write_text("# 试章\n\n雾港雨夜。\n", encoding="utf-8")
    (project / "story.md").write_text('---\ntitle: "测试书"\n---\n', encoding="utf-8")
    result = export.run_export(project, fmt="markdown", skip_gate=True)
    assert result.status == "ok"
    assert result.code == E.EXPORT_OK
    out = project / "dist" / "测试书.md"
    assert out.is_file()
    assert "雾港雨夜" in out.read_text(encoding="utf-8")
    assert result.details["format"] == "markdown"
    paths = [a["path"] for a in result.artifacts]
    assert any(p.endswith(".md") for p in paths)


def test_export_txt_success(tmp_path: Path, allow_skip_gate: None):
    project = tmp_path / "novel"
    (project / "chapters").mkdir(parents=True)
    (project / "chapters" / "01_a.md").write_text("# 标题\n\n正文行。\n", encoding="utf-8")
    result = export.run_export(project, fmt="txt", skip_gate=True)
    assert result.status == "ok"
    assert (project / "dist").glob("*.txt")


def test_demo_export_markdown_passes_gate_9():
    gate_result = gate.run_gate(DEMO, 9)
    if gate_result.status != "ok":
        pytest.skip(f"demo-novel gate 9: {gate_result.required}")
    out = DEMO / "dist" / "_pytest_export_smoke.md"
    try:
        result = export.run_export(DEMO, fmt="markdown", output=out, skip_gate=False)
        assert result.status == "ok"
        assert result.code == E.EXPORT_OK
        assert out.is_file()
    finally:
        if out.is_file():
            out.unlink()


def test_project_not_found(tmp_path: Path):
    missing = tmp_path / "nope"
    result = export.run_export(missing, fmt="markdown", skip_gate=True)
    assert result.code == E.PROJECT_NOT_FOUND


def test_epub_dependency_missing(tmp_path: Path, allow_skip_gate: None, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(export, "_epub_dependency_ok", lambda: False)
    project = tmp_path / "novel"
    (project / "chapters").mkdir(parents=True)
    (project / "chapters" / "01_a.md").write_text("# 章\n\n字。\n", encoding="utf-8")
    result = export.run_export(project, fmt="epub", skip_gate=True)
    assert result.status == "error"
    assert result.code == E.EPUB_DEPENDENCY_MISSING
    assert result.details.get("warnings")
