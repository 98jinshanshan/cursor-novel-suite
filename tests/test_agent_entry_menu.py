"""Tests for W1 agent-entry-menu validate/list."""

from __future__ import annotations

import json
import os
import subprocess
import sys

from novel_suite.core.agent_entry_menu import (
    run_agent_entry_menu_list,
    run_agent_entry_menu_validate,
)
from novel_suite.core.commercialization import run_commercial_release_candidate_validate


def test_agent_entry_menu_validate_ok():
    result = run_agent_entry_menu_validate()
    assert result.status == "ok"
    assert result.code == "AGENT_ENTRY_MENU_VALIDATE_OK"
    assert result.details.get("menu_item_count") == 6
    assert result.details.get("commercial_release_allowed") is False
    assert result.details.get("verdict") == "blocked"


def test_agent_entry_menu_list_six_items():
    result = run_agent_entry_menu_list()
    assert result.status == "ok"
    items = result.details.get("menu_items", [])
    assert len(items) == 6
    ids = {it["id"] for it in items}
    assert "novel.create" in ids
    assert "release.preflight" in ids
    for it in items:
        assert it.get("commercial_release_allowed") is False
        assert it.get("verdict") == "blocked"


def test_cli_agent_entry_menu_validate(repo_root, monkeypatch):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root), "PYTHONPATH": str(repo_root / "src")}
    for cmd in (["agent-entry-menu", "validate"], ["agent-entry-menu", "list"]):
        r = subprocess.run(
            [sys.executable, "-m", "novel_suite.cli", *cmd, "--json"],
            cwd=repo_root,
            env=env,
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, r.stderr
        data = json.loads(r.stdout)
        assert data["status"] == "ok"


def test_commercial_still_blocked():
    result = run_commercial_release_candidate_validate()
    assert result.status == "ok"
    assert result.details.get("verdict") == "blocked"
