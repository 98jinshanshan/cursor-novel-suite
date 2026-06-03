"""Chapter draft CLI — happy path and gate failure."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from novel_suite.core import errors as E
from novel_suite.writer import chapter, gate


@pytest.fixture
def allow_skip_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(E.ENV_ALLOW_SKIP_GATE, "1")


def test_count_cjk_chars():
    assert chapter.count_cjk_chars("你好世界") == 4
    assert chapter.count_cjk_chars("hello") == 0


def test_chapter_draft_skip_gate(tmp_path: Path, allow_skip_gate: None):
    project = tmp_path / "novel"
    project.mkdir()
    (project / "chapters").mkdir()
    (project / "canon" / "snapshots").mkdir(parents=True)
    inp = tmp_path / "draft.md"
    inp.write_text("# 第二章\n\n她踏入雾港。雨丝如针。\n", encoding="utf-8")

    result = chapter.run_chapter_draft(
        project,
        chapter=2,
        title="雾港雨夜",
        input_path=inp,
        skip_gate=True,
    )
    assert result.status == "ok"
    assert result.code == "CHAPTER_DRAFT_OK"
    ch = project / "chapters" / "02_雾港雨夜.md"
    assert ch.is_file()
    prog = json.loads((project / "canon" / "progress.json").read_text(encoding="utf-8"))
    assert prog["total_words"] >= 4
    assert (project / "canon" / "snapshots" / "ch02-after.md").is_file()


def test_skip_gate_requires_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(E.ENV_ALLOW_SKIP_GATE, raising=False)
    project = tmp_path / "novel"
    project.mkdir()
    inp = tmp_path / "d.md"
    inp.write_text("测试。", encoding="utf-8")
    result = chapter.run_chapter_draft(
        project, chapter=1, title="测", input_path=inp, skip_gate=True
    )
    assert result.status == "error"
    assert result.code == E.SKIP_GATE_NOT_ALLOWED


def test_chapter_draft_gate_blocked(tmp_path: Path):
    project = tmp_path / "empty"
    project.mkdir()
    (project / "task_plan.md").write_text("- [ ] Phase 0: x\n", encoding="utf-8")
    inp = tmp_path / "d.md"
    inp.write_text("测试章节内容。", encoding="utf-8")
    result = chapter.run_chapter_draft(
        project, chapter=1, title="测", input_path=inp, skip_gate=False
    )
    assert result.status == "error"
    assert result.code == E.GATE_PHASE5_BLOCKED


def test_invalid_chapter_number(tmp_path: Path, allow_skip_gate: None):
    project = tmp_path / "novel"
    project.mkdir()
    inp = tmp_path / "d.md"
    inp.write_text("字", encoding="utf-8")
    for bad in (0, -1, 1000):
        result = chapter.run_chapter_draft(
            project, chapter=bad, title="x", input_path=inp, skip_gate=True
        )
        assert result.code == E.INVALID_CHAPTER_NUMBER


def test_chapter_already_exists(tmp_path: Path, allow_skip_gate: None):
    project = tmp_path / "novel"
    (project / "chapters").mkdir(parents=True)
    existing = project / "chapters" / "01_已有.md"
    existing.write_text("旧文", encoding="utf-8")
    inp = tmp_path / "new.md"
    inp.write_text("新章节正文在这里。", encoding="utf-8")
    result = chapter.run_chapter_draft(
        project, chapter=1, title="已有", input_path=inp, skip_gate=True
    )
    assert result.status == "error"
    assert result.code == E.CHAPTER_ALREADY_EXISTS
    assert existing.read_text(encoding="utf-8") == "旧文"


def test_chapter_force_overwrite(tmp_path: Path, allow_skip_gate: None):
    project = tmp_path / "novel"
    (project / "chapters").mkdir(parents=True)
    (project / "canon" / "snapshots").mkdir(parents=True)
    existing = project / "chapters" / "01_覆写.md"
    existing.write_text("旧", encoding="utf-8")
    inp = tmp_path / "new.md"
    inp.write_text("覆写后的正文内容。", encoding="utf-8")
    result = chapter.run_chapter_draft(
        project, chapter=1, title="覆写", input_path=inp, skip_gate=True, force=True
    )
    assert result.status == "ok"
    assert "覆写" in existing.read_text(encoding="utf-8")


def test_snapshot_input_not_found(tmp_path: Path, allow_skip_gate: None):
    project = tmp_path / "novel"
    (project / "chapters").mkdir(parents=True)
    (project / "canon" / "snapshots").mkdir(parents=True)
    inp = tmp_path / "ch.md"
    inp.write_text("章节内容测试。", encoding="utf-8")
    result = chapter.run_chapter_draft(
        project,
        chapter=1,
        title="章",
        input_path=inp,
        snapshot_input=tmp_path / "missing-snap.md",
        snapshot_input_given=True,
        skip_gate=True,
    )
    assert result.status == "error"
    assert result.code == E.SNAPSHOT_INPUT_NOT_FOUND


def test_chapter_draft_progress_schema_valid(tmp_path: Path, allow_skip_gate: None):
    project = tmp_path / "novel"
    (project / "chapters").mkdir(parents=True)
    (project / "canon" / "snapshots").mkdir(parents=True)
    inp = tmp_path / "ch.md"
    inp.write_text("第一章完整正文用于 schema 校验。", encoding="utf-8")
    result = chapter.run_chapter_draft(
        project, chapter=1, title="schema", input_path=inp, skip_gate=True
    )
    assert result.status == "ok"
    errors = chapter.validate_progress_against_schema(project)
    assert errors == [], errors


def test_chapter_draft_demo_chapter2(demo_project: Path, tmp_path: Path):
    """Integration: demo-novel passes phase 5 gate and accepts ch02 draft."""
    gate_result = gate.run_gate(demo_project, 5)
    if gate_result.status != "ok":
        pytest.skip(f"demo gate 5 not ok: {gate_result.required}")

    inp = tmp_path / "ch02.md"
    inp.write_text(
        "# 封存编号\n\n陈薇把索引卡摊在灯下。编号尽头是林默。\n\n"
        "（试写第二章，仅供 smoke。）\n",
        encoding="utf-8",
    )
    snap = tmp_path / "snap.md"
    snap.write_text("# 快照\n\n## 下章钩子\n\n编号未解。\n", encoding="utf-8")

    out_name = "02_封存编号.md"
    target = demo_project / "chapters" / out_name
    backup = None
    if target.is_file():
        backup = target.read_text(encoding="utf-8")

    progress_path = demo_project / "canon" / "progress.json"
    progress_backup = (
        progress_path.read_text(encoding="utf-8") if progress_path.is_file() else None
    )
    phase5_manifest = demo_project / "canon" / "nodes" / "phase-5.completion.json"
    phase5_backup = (
        phase5_manifest.read_text(encoding="utf-8") if phase5_manifest.is_file() else None
    )

    try:
        result = chapter.run_chapter_draft(
            demo_project,
            chapter=2,
            title="封存编号",
            input_path=inp,
            snapshot_input=snap,
            snapshot_input_given=True,
            force=backup is not None,
        )
        assert result.status == "ok"
        assert target.is_file()
        assert result.details.get("word_count", 0) > 0
        assert chapter.validate_progress_against_schema(demo_project) == []
    finally:
        if backup is not None:
            target.write_text(backup, encoding="utf-8")
        elif target.is_file():
            target.unlink()
        if progress_backup is not None:
            progress_path.write_text(progress_backup, encoding="utf-8")
        if phase5_backup is not None:
            phase5_manifest.write_text(phase5_backup, encoding="utf-8")


def test_chapter_promote(tmp_path: Path):
    project = tmp_path / "p"
    drafts = project / "chapters" / ".drafts"
    drafts.mkdir(parents=True)
    (drafts / "03_x.md").write_text("正文", encoding="utf-8")
    result = chapter.run_chapter_promote(project, chapter_file="03_x.md")
    assert result.status == "ok"
    assert (project / "chapters" / "03_x.md").is_file()
