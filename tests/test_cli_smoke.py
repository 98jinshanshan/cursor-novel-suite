"""CLI subprocess smoke for novel-suite entry point."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    import os

    env = {**os.environ, "NOVEL_SUITE_ROOT": str(REPO)}
    return subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", *args],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )


def test_version_json():
    r = _run("version", "--json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["status"] == "ok"
    assert data["code"] == "VERSION_OK"


def test_doctor_core_json():
    r = _run("doctor", "--core-only", "--json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["status"] == "ok"


def test_writer_gate_demo_json():
    rel = "cursor-novel-writer/examples/demo-novel"
    r = _run("writer", "gate", "--project", rel, "--phase", "1", "--json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["code"] == "GATE_OK"
