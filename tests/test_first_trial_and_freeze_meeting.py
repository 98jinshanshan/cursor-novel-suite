"""Tests for J1 first trial session kit and J2 freeze review meeting."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.delivery_readiness import (
    run_first_trial_session_kit_validate,
    run_freeze_review_meeting_validate,
    validate_first_trial_session_kit,
    validate_freeze_review_meeting,
)


def test_first_trial_session_kit_files_exist(repo_root: Path):
    checks = validate_first_trial_session_kit()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 15
    assert not failed, failed


def test_first_trial_session_kit_sample(repo_root: Path):
    data = json.loads(
        (
            repo_root
            / "novel-suite"
            / "first-trial-session-kit"
            / "first-trial-session-kit.sample.json"
        ).read_text(encoding="utf-8")
    )
    assert data["trial_executed"] is False
    assert data["fake_feedback_generated"] is False
    assert data["telemetry_collected"] is False
    assert data["external_call_performed"] is False


def test_tmp_intake_readme_exists(repo_root: Path):
    readme = repo_root / ".tmp" / "novel-suite-j" / "trial-results-intake" / "README.md"
    assert readme.is_file()


def test_freeze_review_meeting_files_exist(repo_root: Path):
    checks = validate_freeze_review_meeting()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 14
    assert not failed, failed


def test_freeze_review_meeting_sample(repo_root: Path):
    data = json.loads(
        (repo_root / "novel-suite" / "freeze-review-meeting" / "freeze-review-meeting.sample.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["meeting_held"] is False
    assert data["tag_created"] is False
    assert data["zip_created"] is False
    assert data["release_created"] is False
    assert data["verdict"] == "blocked"


def test_run_j1_j2_validate_ok():
    assert run_first_trial_session_kit_validate().code == E.FIRST_TRIAL_SESSION_KIT_VALIDATE_OK
    r = run_freeze_review_meeting_validate()
    assert r.code == E.FREEZE_REVIEW_MEETING_VALIDATE_OK
    assert r.details.get("meeting_held") is False


def test_cli_j1_j2_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    for cmd, code in (
        (["first-trial-session-kit", "validate"], E.FIRST_TRIAL_SESSION_KIT_VALIDATE_OK),
        (["freeze-review-meeting", "validate"], E.FREEZE_REVIEW_MEETING_VALIDATE_OK),
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
