"""CLI: video create-summary / status --json pure stdout."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DEMO_PROJECT = "cursor-novel-writer/examples/demo-novel"


def test_video_create_summary_json_stdout():
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(REPO)}
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "novel_suite.cli",
            "video",
            "create-summary",
            "--chapter",
            "01_试章.md",
            "--project",
            DEMO_PROJECT,
            "--json",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )
    if r.returncode != 0 and "not found" in (r.stderr + r.stdout).lower():
        pytest.skip("demo chapter missing")
    assert r.returncode == 0, r.stderr + r.stdout
    raw = r.stdout.strip()
    assert raw[0] == "{"
    data = json.loads(raw)
    assert data["code"] == "VIDEO_CREATE_OK"
    job_id = data["details"]["job_id"]
    assert job_id

    r2 = subprocess.run(
        [
            sys.executable,
            "-m",
            "novel_suite.cli",
            "video",
            "status",
            "--job",
            job_id,
            "--json",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r2.returncode == 0, r2.stderr + r2.stdout
    st = json.loads(r2.stdout)
    assert st["details"]["status"] == "pending"
