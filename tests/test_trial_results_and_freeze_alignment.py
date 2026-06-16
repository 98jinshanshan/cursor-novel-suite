"""Tests for I1 trial results intake and I2 freeze version alignment."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.delivery_readiness import (
    run_freeze_version_alignment_validate,
    run_trial_results_intake_validate,
    validate_freeze_version_alignment,
    validate_trial_results_intake,
)


def test_trial_results_intake_files_exist(repo_root: Path):
    checks = validate_trial_results_intake()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 14
    assert not failed, failed


def test_trial_results_intake_sample(repo_root: Path):
    data = json.loads(
        (repo_root / "novel-suite" / "trial-results-intake" / "trial-results-intake.sample.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["telemetry_collected"] is False
    assert data["external_call_performed"] is False
    assert data["feedback_storage"] == "local_only"
    assert data["revision_auto_applied"] is False


def test_freeze_alignment_files_exist(repo_root: Path):
    checks = validate_freeze_version_alignment()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 13
    assert not failed, failed


def test_freeze_alignment_sample_no_release(repo_root: Path):
    data = json.loads(
        (
            repo_root / "novel-suite" / "freeze-version-alignment" / "freeze-version-alignment.sample.json"
        ).read_text(encoding="utf-8")
    )
    assert data["recommended_version"] == "0.1.0-demo-freeze-candidate"
    assert data["tag_created"] is False
    assert data["zip_created"] is False
    assert data["release_created"] is False
    assert data["verdict"] == "blocked"


def test_run_i1_i2_validate_ok():
    assert run_trial_results_intake_validate().code == E.TRIAL_RESULTS_INTAKE_VALIDATE_OK
    r = run_freeze_version_alignment_validate()
    assert r.code == E.FREEZE_VERSION_ALIGNMENT_VALIDATE_OK
    assert r.details.get("tag_created") is False


def test_cli_i1_i2_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    for cmd, code in (
        (["trial-results-intake", "validate"], E.TRIAL_RESULTS_INTAKE_VALIDATE_OK),
        (["freeze-version-alignment", "validate"], E.FREEZE_VERSION_ALIGNMENT_VALIDATE_OK),
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
