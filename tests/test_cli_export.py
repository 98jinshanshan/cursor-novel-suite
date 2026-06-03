"""CLI: writer export --json pure stdout and happy path."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEMO = REPO / "cursor-novel-writer" / "examples" / "demo-novel"


def test_export_json_stdout_is_pure_json():
    out = DEMO / "dist" / "_cli_export_json_test.md"
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(REPO)}
    try:
        r = subprocess.run(
            [
                sys.executable,
                "-m",
                "novel_suite.cli",
                "writer",
                "export",
                "--project",
                str(DEMO),
                "--format",
                "markdown",
                "--output",
                str(out),
                "--json",
            ],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            env=env,
        )
        assert r.returncode == 0, r.stderr + r.stdout
        raw = r.stdout.strip()
        assert raw[0] == "{", f"stdout must be pure JSON, got: {raw[:120]!r}"
        data = json.loads(raw)
        assert data["status"] == "ok"
        assert data["code"] == "EXPORT_OK"
        assert data["details"]["format"] == "markdown"
        assert out.is_file()
    finally:
        if out.is_file():
            out.unlink()


def test_export_gate_blocked_json(tmp_path: Path):
    project = tmp_path / "blocked"
    project.mkdir()
    (project / "chapters").mkdir()
    (project / "chapters" / "01_x.md").write_text("# x\n\ny\n", encoding="utf-8")
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(REPO)}
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "novel_suite.cli",
            "writer",
            "export",
            "--project",
            str(project),
            "--format",
            "markdown",
            "--json",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 1
    data = json.loads(r.stdout)
    assert data["code"] == "EXPORT_BLOCKED"
