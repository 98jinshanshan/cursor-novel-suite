"""Tests for M3 legal import decision board."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.delivery_readiness import (
    run_legal_import_decision_board_validate,
    validate_legal_import_decision_board,
)


def test_legal_import_decision_board_files_exist(repo_root: Path):
    checks = validate_legal_import_decision_board()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 15
    assert not failed, failed


def test_legal_import_decision_board_sample(repo_root: Path):
    data = json.loads(
        (
            repo_root
            / "novel-suite"
            / "legal-import-decision-board"
            / "legal-import-decision-board.sample.json"
        ).read_text(encoding="utf-8")
    )
    assert data["preflight_result_available"] is False
    assert data["board_decision_available"] is False
    assert data["release_gate_changed"] is False
    assert data["legal_conclusion_auto_generated"] is False
    assert data["auto_blocker_closure"] is False
    assert data["requires_human_signature"] is True
    assert data["verdict"] == "blocked"


def test_no_auto_gate_policies(repo_root: Path):
    base = repo_root / "novel-suite" / "legal-import-decision-board"
    assert "release_gate_changed" in (base / "no_auto_gate_change_policy.md").read_text(encoding="utf-8")
    assert "legal_conclusion" in (base / "no_legal_opinion_policy.md").read_text(encoding="utf-8")


def test_run_legal_import_decision_board_validate_ok():
    result = run_legal_import_decision_board_validate()
    assert result.code == E.LEGAL_IMPORT_DECISION_BOARD_VALIDATE_OK
    assert result.details.get("release_gate_changed") is False
    assert result.details.get("board_decision_available") is False


def test_cli_legal_import_decision_board_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "legal-import-decision-board", "validate", "--json"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert json.loads(r.stdout)["code"] == E.LEGAL_IMPORT_DECISION_BOARD_VALIDATE_OK
