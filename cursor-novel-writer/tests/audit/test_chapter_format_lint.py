"""NEC-11: chapter_format_lint smoke tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ENGINE = Path(__file__).resolve().parents[2] / "engine"
SCRIPTS = ENGINE / "scripts"
DEMO = ENGINE.parent / "examples" / "demo-novel"
LINT = SCRIPTS / "chapter_format_lint.py"


def _run_format(chapter: Path, *, project: Path = DEMO) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(LINT),
            "--project",
            str(project),
            "--chapter",
            str(chapter),
            "--json",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(ENGINE.parent),
    )


def _parse_audit(stdout: str) -> dict:
    for line in stdout.splitlines():
        if line.startswith("AUDIT:"):
            return json.loads(line[6:].strip())
    raise AssertionError(f"No AUDIT line in stdout: {stdout!r}")


def test_format_demo_chapter_ok() -> None:
    ch = DEMO / "chapters" / "01_试章.md"
    proc = _run_format(ch)
    payload = _parse_audit(proc.stdout)
    assert payload["mode"] == "format"
    assert payload["status"] in ("ok", "warn")


def test_format_forbidden_section_blocker(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    (project / "chapters").mkdir(parents=True)
    ch = project / "chapters" / "01_bad.md"
    ch.write_text(
        "# 第1章\n\n---\n\n## 一、开场\n\n　　正文。\n\n---\n\n（第1章完）\n",
        encoding="utf-8",
    )
    (project / "story.md").write_text("---\nwords_per_chapter: 4000\n---\n", encoding="utf-8")
    proc = _run_format(ch, project=project)
    assert proc.returncode == 1, proc.stderr
    payload = _parse_audit(proc.stdout)
    assert any(h.get("severity") == "blocker" for h in payload.get("hits", []))
