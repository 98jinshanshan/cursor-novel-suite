"""Tests for M1 trial import decision and M2 freeze import decision."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.delivery_readiness import (
    run_freeze_import_decision_record_validate,
    run_trial_import_decision_record_validate,
    validate_freeze_import_decision_record,
    validate_trial_import_decision_record,
)


def test_trial_import_decision_record_files_exist(repo_root: Path):
    checks = validate_trial_import_decision_record()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 13
    assert not failed, failed


def test_trial_import_decision_record_sample(repo_root: Path):
    data = json.loads(
        (
            repo_root
            / "novel-suite"
            / "trial-import-decision-record"
            / "trial-import-decision-record.sample.json"
        ).read_text(encoding="utf-8")
    )
    assert data["preflight_result_available"] is False
    assert data["import_approved"] is False
    assert data["pii_redaction_verified"] is False
    assert data["backlog_auto_applied"] is False


def test_tmp_m_readme_exists(repo_root: Path):
    readme = repo_root / ".tmp" / "novel-suite-m" / "trial-import-decision-record" / "README.md"
    assert readme.is_file()


def test_freeze_import_decision_record_files_exist(repo_root: Path):
    checks = validate_freeze_import_decision_record()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 13
    assert not failed, failed


def test_freeze_import_decision_record_sample(repo_root: Path):
    data = json.loads(
        (
            repo_root
            / "novel-suite"
            / "freeze-import-decision-record"
            / "freeze-import-decision-record.sample.json"
        ).read_text(encoding="utf-8")
    )
    assert data["preflight_result_available"] is False
    assert data["import_approved"] is False
    assert data["tag_created"] is False
    assert data["verdict"] == "blocked"


def test_run_m1_m2_validate_ok():
    assert run_trial_import_decision_record_validate().code == E.TRIAL_IMPORT_DECISION_RECORD_VALIDATE_OK
    r = run_freeze_import_decision_record_validate()
    assert r.code == E.FREEZE_IMPORT_DECISION_RECORD_VALIDATE_OK
    assert r.details.get("import_approved") is False


def test_cli_m1_m2_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    for cmd, code in (
        (["trial-import-decision-record", "validate"], E.TRIAL_IMPORT_DECISION_RECORD_VALIDATE_OK),
        (["freeze-import-decision-record", "validate"], E.FREEZE_IMPORT_DECISION_RECORD_VALIDATE_OK),
    ):
        r = subprocess.run(
            [sys.executable, "-m", "novel_suite.cli", *cmd, "--json"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env,
        )
        assert r.returncode == 0, r.stderr + r.stdout
        assert json.loads(r.stdout)["code"] == code
