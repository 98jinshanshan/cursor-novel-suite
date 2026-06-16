"""Tests for L1 trial import preflight and L2 freeze import preflight."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.delivery_readiness import (
    run_freeze_decision_import_preflight_validate,
    run_trial_result_import_preflight_validate,
    validate_freeze_decision_import_preflight,
    validate_trial_result_import_preflight,
)


def test_trial_result_import_preflight_files_exist(repo_root: Path):
    checks = validate_trial_result_import_preflight()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 15
    assert not failed, failed


def test_trial_result_import_preflight_sample(repo_root: Path):
    data = json.loads(
        (
            repo_root
            / "novel-suite"
            / "trial-result-import-preflight"
            / "trial-result-import-preflight.sample.json"
        ).read_text(encoding="utf-8")
    )
    assert data["input_results_available"] is False
    assert data["preflight_passed"] is False
    assert data["pii_redaction_verified"] is False
    assert data["revision_auto_applied"] is False


def test_tmp_l_readme_exists(repo_root: Path):
    readme = repo_root / ".tmp" / "novel-suite-l" / "trial-result-import-preflight" / "README.md"
    assert readme.is_file()


def test_freeze_decision_import_preflight_files_exist(repo_root: Path):
    checks = validate_freeze_decision_import_preflight()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 14
    assert not failed, failed


def test_freeze_decision_import_preflight_sample(repo_root: Path):
    data = json.loads(
        (
            repo_root
            / "novel-suite"
            / "freeze-decision-import-preflight"
            / "freeze-decision-import-preflight.sample.json"
        ).read_text(encoding="utf-8")
    )
    assert data["input_decision_available"] is False
    assert data["preflight_passed"] is False
    assert data["tag_created"] is False
    assert data["verdict"] == "blocked"


def test_run_l1_l2_validate_ok():
    assert run_trial_result_import_preflight_validate().code == E.TRIAL_RESULT_IMPORT_PREFLIGHT_VALIDATE_OK
    r = run_freeze_decision_import_preflight_validate()
    assert r.code == E.FREEZE_DECISION_IMPORT_PREFLIGHT_VALIDATE_OK
    assert r.details.get("preflight_passed") is False


def test_cli_l1_l2_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    for cmd, code in (
        (["trial-result-import-preflight", "validate"], E.TRIAL_RESULT_IMPORT_PREFLIGHT_VALIDATE_OK),
        (["freeze-decision-import-preflight", "validate"], E.FREEZE_DECISION_IMPORT_PREFLIGHT_VALIDATE_OK),
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
