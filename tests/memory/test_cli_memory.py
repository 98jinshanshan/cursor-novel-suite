"""CLI smoke for memory subcommands."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


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


def test_memory_store_search_json(novels_scratch: Path):
    slug = novels_scratch.name
    rel = f"novels/{slug}"
    store_args = [
        "memory",
        "store",
        "--project",
        rel,
        "--layer",
        "L4",
        "--tags",
        "character,林墨",
        "--text",
        "林墨：琥珀色眼睛，黑色短发",
        "--json",
    ]
    r = _run(*store_args)
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["code"] == "MEMORY_STORE_OK"

    r2 = _run(
        "memory",
        "search",
        "--project",
        rel,
        "--query",
        "眼睛颜色",
        "--layer",
        "L4",
        "--json",
    )
    assert r2.returncode == 0, r2.stderr
    data2 = json.loads(r2.stdout)
    assert data2["code"] == "MEMORY_SEARCH_OK"
    assert data2["details"]["hits"]


def test_memory_help():
    r = _run("memory", "status", "--help")
    assert r.returncode == 0


def test_memory_probe_json(novels_scratch: Path):
    slug = novels_scratch.name
    rel = f"novels/{slug}"
    r = _run("memory", "probe", "--project", rel, "--json")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["code"] == "MEMORY_PROBE_OK"
    assert "embed" in data["details"]
