"""Tests for H1 human trial runbook and H2 package freeze candidate."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.delivery_readiness import (
    run_human_trial_runbook_validate,
    run_package_freeze_candidate_validate,
    validate_human_trial_runbook,
    validate_package_freeze_candidate,
)


def test_human_trial_runbook_files_exist(repo_root: Path):
    checks = validate_human_trial_runbook()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 16
    assert not failed, failed


def test_human_trial_sample_boundaries(repo_root: Path):
    data = json.loads(
        (repo_root / "novel-suite" / "human-trial-runbook" / "human-trial-runbook.sample.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["external_call_performed"] is False
    assert data["telemetry_collected"] is False
    assert data["commercial_release_allowed"] is False
    assert data["feedback_storage"] == "local_only"


def test_four_participant_roles(repo_root: Path):
    text = (repo_root / "novel-suite" / "human-trial-runbook" / "participant_roles.md").read_text(
        encoding="utf-8"
    )
    for role in ("creator", "content_ops", "tech_integrator", "reviewer"):
        assert role in text


def test_package_freeze_candidate_files(repo_root: Path):
    checks = validate_package_freeze_candidate()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 15
    assert not failed, failed


def test_freeze_manifest_sample(repo_root: Path):
    data = json.loads(
        (
            repo_root / "novel-suite" / "package-freeze-candidate" / "freeze_candidate_manifest.sample.json"
        ).read_text(encoding="utf-8")
    )
    assert data["package_status"] == "freeze_candidate_only"
    assert data["verdict"] == "blocked"
    assert data["legal_review_required"] is True
    assert "demo-freeze-candidate" in data["package_version"]


def test_run_h1_h2_validate_ok():
    assert run_human_trial_runbook_validate().code == E.HUMAN_TRIAL_RUNBOOK_VALIDATE_OK
    r = run_package_freeze_candidate_validate()
    assert r.code == E.PACKAGE_FREEZE_CANDIDATE_VALIDATE_OK
    assert r.details.get("package_status") == "freeze_candidate_only"


def test_cli_h1_h2_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    for cmd, code in (
        (["human-trial-runbook", "validate"], E.HUMAN_TRIAL_RUNBOOK_VALIDATE_OK),
        (["package-freeze-candidate", "validate"], E.PACKAGE_FREEZE_CANDIDATE_VALIDATE_OK),
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
