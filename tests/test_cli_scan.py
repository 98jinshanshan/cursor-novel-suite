"""CLI smoke for writer scan --demo --json."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_writer_scan_demo_json(tmp_path: Path):
    radar = tmp_path / "out" / "radar.md"
    concepts = tmp_path / "out" / "concepts"
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(REPO)}
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "novel_suite.cli",
            "writer",
            "scan",
            "--demo",
            "--period",
            "week",
            "--radar",
            str(radar),
            "--concepts-dir",
            str(concepts),
            "--json",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    data = json.loads(r.stdout)
    assert data["status"] == "ok"
    assert data["code"] == "SCAN_OK"
    assert data["details"]["source_type"] == "demo_fixture"
    assert data["details"]["themes"]
    assert radar.is_file()
