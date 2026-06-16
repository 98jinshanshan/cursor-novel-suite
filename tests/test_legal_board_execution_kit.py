"""Tests for N3 legal board execution kit."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.delivery_readiness import (
    run_legal_board_execution_kit_validate,
    validate_legal_board_execution_kit,
)


def test_legal_board_execution_kit_files_exist(repo_root: Path):
    checks = validate_legal_board_execution_kit()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 15
    assert not failed, failed


def test_legal_board_execution_kit_sample(repo_root: Path):
    data = json.loads(
        (
            repo_root / "novel-suite" / "legal-board-execution-kit" / "legal-board-execution-kit.sample.json"
        ).read_text(encoding="utf-8")
    )
    assert data["board_decision_available"] is False
    assert data["legal_conclusion_auto_generated"] is False
    assert data["auto_blocker_closure"] is False
    assert data["release_gate_changed"] is False
    assert data["verdict"] == "blocked"


def test_no_auto_policies(repo_root: Path):
    base = repo_root / "novel-suite" / "legal-board-execution-kit"
    assert "release_gate_changed" in (base / "no_auto_gate_change_policy.md").read_text(encoding="utf-8")
    assert "legal_conclusion" in (base / "no_legal_opinion_policy.md").read_text(encoding="utf-8")


def test_run_legal_board_execution_kit_validate_ok():
    result = run_legal_board_execution_kit_validate()
    assert result.code == E.LEGAL_BOARD_EXECUTION_KIT_VALIDATE_OK
    assert result.details.get("board_decision_available") is False
    assert result.details.get("release_gate_changed") is False


def test_cli_legal_board_execution_kit_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "legal-board-execution-kit", "validate", "--json"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert json.loads(r.stdout)["code"] == E.LEGAL_BOARD_EXECUTION_KIT_VALIDATE_OK
