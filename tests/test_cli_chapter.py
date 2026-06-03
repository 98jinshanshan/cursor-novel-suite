"""CLI smoke for writer chapter draft."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_chapter_draft_json_skip_gate(tmp_path: Path):
    project = tmp_path / "novel"
    project.mkdir()
    (project / "chapters").mkdir()
    (project / "canon" / "snapshots").mkdir(parents=True)
    inp = tmp_path / "in.md"
    inp.write_text("第一章试写。雾气很重。", encoding="utf-8")
    env = {
        **os.environ,
        "NOVEL_SUITE_ROOT": str(REPO),
        "NOVEL_SUITE_ALLOW_SKIP_GATE": "1",
    }
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "novel_suite.cli",
            "writer",
            "chapter",
            "draft",
            "--project",
            str(project),
            "--chapter",
            "1",
            "--title",
            "试章",
            "--input",
            str(inp),
            "--skip-gate",
            "--json",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    data = json.loads(r.stdout)
    assert data["code"] == "CHAPTER_DRAFT_OK"


def test_chapter_draft_skip_gate_denied_without_env(tmp_path: Path):
    project = tmp_path / "novel"
    project.mkdir()
    inp = tmp_path / "in.md"
    inp.write_text("测试", encoding="utf-8")
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(REPO)}
    env.pop("NOVEL_SUITE_ALLOW_SKIP_GATE", None)
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "novel_suite.cli",
            "writer",
            "chapter",
            "draft",
            "--project",
            str(project),
            "--chapter",
            "1",
            "--title",
            "试",
            "--input",
            str(inp),
            "--skip-gate",
            "--json",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 1
    data = json.loads(r.stdout)
    assert data["code"] == "SKIP_GATE_NOT_ALLOWED"
