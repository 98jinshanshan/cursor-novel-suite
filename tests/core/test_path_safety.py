"""Security helpers — path bounds and graphify token sanitization."""

from __future__ import annotations

from pathlib import Path

import pytest

from novel_suite.core import errors as E
from novel_suite.core.path_safety import assert_chapter_input_path, sanitize_graphify_token
from novel_suite.writer import chapter

GRAPHIFY = (
    Path(__file__).resolve().parents[2]
    / "cursor-novel-writer"
    / "engine"
    / "scripts"
    / "graphify_bridge.py"
)


def test_sanitize_graphify_token_accepts_cjk():
    assert sanitize_graphify_token("林默") == "林默"


def test_sanitize_graphify_token_rejects_cli_injection():
    with pytest.raises(ValueError):
        sanitize_graphify_token("--budget")
    with pytest.raises(ValueError):
        sanitize_graphify_token("a\nb")


def test_chapter_input_under_project(tmp_path: Path):
    project = tmp_path / "novel"
    project.mkdir()
    inp = project / "outlines" / "draft.md"
    inp.parent.mkdir(parents=True)
    inp.write_text("正文", encoding="utf-8")
    resolved = assert_chapter_input_path(project, inp)
    assert resolved == inp.resolve()


def test_chapter_input_under_temp(tmp_path: Path, allow_skip_gate: None):
    project = tmp_path / "novel"
    project.mkdir()
    (project / "chapters").mkdir()
    (project / "canon" / "snapshots").mkdir(parents=True)
    inp = tmp_path / "scratch.md"
    inp.write_text("临时提纲正文。", encoding="utf-8")
    result = chapter.run_chapter_draft(
        project, chapter=1, title="测", input_path=inp, skip_gate=True
    )
    assert result.status == "ok"


def test_chapter_input_rejects_outside(
    tmp_path: Path, allow_skip_gate: None, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr("novel_suite.core.path_safety.system_temp_roots", lambda: [])
    project = tmp_path / "novel"
    project.mkdir()
    (project / "chapters").mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("不应采纳", encoding="utf-8")
    result = chapter.run_chapter_draft(
        project, chapter=1, title="测", input_path=outside, skip_gate=True
    )
    assert result.status == "error"
    assert result.code == E.CHAPTER_INPUT_OUT_OF_BOUNDS


def test_engine_graphify_sanitize_rejects_cli_like_token():
    import importlib.util

    spec = importlib.util.spec_from_file_location("graphify_bridge", GRAPHIFY)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with pytest.raises(ValueError):
        mod.sanitize_graphify_token("--evil")


@pytest.fixture
def allow_skip_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(E.ENV_ALLOW_SKIP_GATE, "1")
