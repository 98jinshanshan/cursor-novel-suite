"""Smoke tests for cursor-novel-writer."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
SCRIPTS = ENGINE / "scripts"
DEMO = ROOT / "examples" / "demo-novel"


def test_demo_novel_structure():
    assert (DEMO / "story.md").is_file()
    assert (DEMO / "characters" / "chen-wei.md").is_file()
    assert (DEMO / "worldbuilding" / "systems" / "archive-seal-system.md").is_file()
    assert (DEMO / "plot" / "arcs" / "arc-main-letter.md").is_file()
    assert len(list((DEMO / "characters").glob("*.md"))) >= 3


def test_novel_cli_project_after_subcommand():
    r = subprocess.run(
        [sys.executable, str(ENGINE / "novel_cli.py"), "status", "--project", str(DEMO)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0
    assert "雾港来信" in r.stdout


def test_graphify_bridge_offline_status():
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "graphify_bridge.py"),
            "status",
            "--project",
            str(DEMO),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0


def test_skill_wrapper_create_epub(tmp_path: Path):
    out = tmp_path / "out.epub"
    r = subprocess.run(
        [
            sys.executable,
            str(ROOT / "skills" / "novel-export" / "scripts" / "create_epub.py"),
            "--project",
            str(DEMO),
            "--output",
            str(out),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr
    assert out.is_file()
    assert out.stat().st_size > 500


def test_progress_json_valid():
    data = json.loads((DEMO / "canon" / "progress.json").read_text(encoding="utf-8"))
    assert data["title"] == "雾港来信"
    assert len(data["chapters"]) >= 1
