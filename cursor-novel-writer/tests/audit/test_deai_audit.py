"""NEC-11: deai_audit smoke tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ENGINE = Path(__file__).resolve().parents[2] / "engine"
SCRIPTS = ENGINE / "scripts"
DEMO = ENGINE.parent / "examples" / "demo-novel"
DEAI = SCRIPTS / "deai_audit.py"


def _run_deai(chapter: Path, *, project: Path = DEMO) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(DEAI),
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


@pytest.mark.parametrize("chapter", [DEMO / "chapters" / "01_试章.md"])
def test_deai_demo_chapter_runs(chapter: Path) -> None:
    proc = _run_deai(chapter)
    assert proc.returncode in (0, 1)
    payload = _parse_audit(proc.stdout)
    assert payload["mode"] == "deai"
    assert payload["status"] in ("ok", "warn", "error")


def test_deai_hits_synthetic_lexicon(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    (project / "chapters").mkdir(parents=True)
    ch = project / "chapters" / "01_test.md"
    ch.write_text(
        "# 第1章\n\n---\n\n　　值得注意的是，他不禁感到一阵不安。\n\n---\n\n（第1章完）\n",
        encoding="utf-8",
    )
    (project / "story.md").write_text(
        "---\nwords_per_chapter: 4000\n---\n",
        encoding="utf-8",
    )
    proc = _run_deai(ch, project=project)
    assert proc.returncode in (0, 1), proc.stderr
    payload = _parse_audit(proc.stdout)
    assert payload["summary"].get("total_hits", 0) >= 1
    assert any("deai.lexicon" in h.get("rule_id", "") for h in payload.get("hits", []))
