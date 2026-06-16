"""Tests for N1 trial decision fill kit and N2 freeze decision fill kit."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.delivery_readiness import (
    run_freeze_decision_fill_kit_validate,
    run_trial_decision_fill_kit_validate,
    validate_freeze_decision_fill_kit,
    validate_trial_decision_fill_kit,
)


def test_trial_decision_fill_kit_files_exist(repo_root: Path):
    checks = validate_trial_decision_fill_kit()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 15
    assert not failed, failed


def test_trial_decision_fill_kit_sample(repo_root: Path):
    data = json.loads(
        (repo_root / "novel-suite" / "trial-decision-fill-kit" / "trial-decision-fill-kit.sample.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["trial_result_available"] is False
    assert data["import_approved"] is False
    assert data["fake_feedback_generated"] is False


def test_tmp_n_trial_readme_exists(repo_root: Path):
    readme = repo_root / ".tmp" / "novel-suite-n" / "trial-decision-fill-kit" / "README.md"
    assert readme.is_file()


def test_freeze_decision_fill_kit_files_exist(repo_root: Path):
    checks = validate_freeze_decision_fill_kit()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 14
    assert not failed, failed


def test_freeze_decision_fill_kit_sample(repo_root: Path):
    data = json.loads(
        (repo_root / "novel-suite" / "freeze-decision-fill-kit" / "freeze-decision-fill-kit.sample.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["freeze_decision_available"] is False
    assert data["tag_created"] is False
    assert data["zip_created"] is False
    assert data["release_created"] is False
    assert data["verdict"] == "blocked"


def test_run_n1_n2_validate_ok():
    assert run_trial_decision_fill_kit_validate().code == E.TRIAL_DECISION_FILL_KIT_VALIDATE_OK
    r = run_freeze_decision_fill_kit_validate()
    assert r.code == E.FREEZE_DECISION_FILL_KIT_VALIDATE_OK
    assert r.details.get("freeze_decision_available") is False


def test_cli_n1_n2_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    for cmd, code in (
        (["trial-decision-fill-kit", "validate"], E.TRIAL_DECISION_FILL_KIT_VALIDATE_OK),
        (["freeze-decision-fill-kit", "validate"], E.FREEZE_DECISION_FILL_KIT_VALIDATE_OK),
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
