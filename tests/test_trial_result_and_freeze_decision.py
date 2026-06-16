"""Tests for K1 trial result review and K2 freeze decision record."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.delivery_readiness import (
    run_freeze_decision_record_validate,
    run_trial_result_review_validate,
    validate_freeze_decision_record,
    validate_trial_result_review,
)


def test_trial_result_review_files_exist(repo_root: Path):
    checks = validate_trial_result_review()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 14
    assert not failed, failed


def test_trial_result_review_sample(repo_root: Path):
    data = json.loads(
        (repo_root / "novel-suite" / "trial-result-review" / "trial-result-review.sample.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["trial_executed_by_human"] is False
    assert data["trial_results_available"] is False
    assert data["fake_feedback_generated"] is False
    assert data["revision_auto_applied"] is False


def test_tmp_k_readme_exists(repo_root: Path):
    readme = repo_root / ".tmp" / "novel-suite-k" / "trial-result-review" / "README.md"
    assert readme.is_file()


def test_freeze_decision_record_files_exist(repo_root: Path):
    checks = validate_freeze_decision_record()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 14
    assert not failed, failed


def test_freeze_decision_record_sample(repo_root: Path):
    data = json.loads(
        (repo_root / "novel-suite" / "freeze-decision-record" / "freeze-decision-record.sample.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["meeting_held_by_human"] is False
    assert data["meeting_result_available"] is False
    assert data["tag_created"] is False
    assert data["verdict"] == "blocked"


def test_run_k1_k2_validate_ok():
    assert run_trial_result_review_validate().code == E.TRIAL_RESULT_REVIEW_VALIDATE_OK
    r = run_freeze_decision_record_validate()
    assert r.code == E.FREEZE_DECISION_RECORD_VALIDATE_OK
    assert r.details.get("meeting_result_available") is False


def test_cli_k1_k2_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    for cmd, code in (
        (["trial-result-review", "validate"], E.TRIAL_RESULT_REVIEW_VALIDATE_OK),
        (["freeze-decision-record", "validate"], E.FREEZE_DECISION_RECORD_VALIDATE_OK),
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
