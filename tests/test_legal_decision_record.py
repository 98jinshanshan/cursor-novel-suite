"""Tests for K3 legal decision record."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.delivery_readiness import (
    run_legal_decision_record_validate,
    validate_legal_decision_record,
)


def test_legal_decision_record_files_exist(repo_root: Path):
    checks = validate_legal_decision_record()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 14
    assert not failed, failed


def test_legal_decision_record_sample(repo_root: Path):
    data = json.loads(
        (repo_root / "novel-suite" / "legal-decision-record" / "legal-decision-record.sample.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["legal_meeting_held_by_human"] is False
    assert data["legal_meeting_result_available"] is False
    assert data["legal_conclusion_auto_generated"] is False
    assert data["auto_blocker_closure"] is False
    assert data["requires_human_signature"] is True
    assert data["verdict"] == "blocked"
    assert "B01" in data["blocker_recommendations"]


def test_no_auto_policies(repo_root: Path):
    base = repo_root / "novel-suite" / "legal-decision-record"
    assert "auto_blocker_closure" in (base / "no_auto_blocker_closure_policy.md").read_text(encoding="utf-8")
    assert "legal_conclusion" in (base / "no_auto_legal_conclusion_policy.md").read_text(encoding="utf-8")


def test_run_legal_decision_record_validate_ok():
    result = run_legal_decision_record_validate()
    assert result.code == E.LEGAL_DECISION_RECORD_VALIDATE_OK
    assert result.details.get("auto_blocker_closure") is False
    assert result.details.get("legal_meeting_result_available") is False


def test_cli_legal_decision_record_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "legal-decision-record", "validate", "--json"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert json.loads(r.stdout)["code"] == E.LEGAL_DECISION_RECORD_VALIDATE_OK
