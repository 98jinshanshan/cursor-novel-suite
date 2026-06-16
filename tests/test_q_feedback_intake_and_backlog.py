"""Tests for Q1/Q2/Q3 feedback intake and backlog."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from novel_suite.core import errors as E
from novel_suite.core.commercialization import run_commercial_release_candidate_validate
from novel_suite.core.delivery_readiness import (
    run_multi_ide_feedback_backlog_validate,
    run_promptpack_friction_review_validate,
    run_solo_demo_trial_intake_validate,
    validate_multi_ide_feedback_backlog,
    validate_promptpack_friction_review,
    validate_solo_demo_trial_intake,
)


def _schema_validate(sample_path: Path, schema_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validate(instance=sample, schema=schema)


def test_solo_demo_trial_intake_files_and_tmp(repo_root: Path):
    checks = validate_solo_demo_trial_intake()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 10
    assert not failed, failed
    assert (repo_root / ".tmp" / "novel-suite-q" / "solo-demo-trial-intake" / "README.md").is_file()


def test_promptpack_friction_review_files_and_tmp(repo_root: Path):
    checks = validate_promptpack_friction_review()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 10
    assert not failed, failed
    assert (repo_root / ".tmp" / "novel-suite-q" / "promptpack-friction-review" / "README.md").is_file()


def test_multi_ide_feedback_backlog_files_and_tmp(repo_root: Path):
    checks = validate_multi_ide_feedback_backlog()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 14
    assert not failed, failed
    assert (repo_root / ".tmp" / "novel-suite-q" / "multi-ide-feedback-backlog" / "README.md").is_file()


def test_q1_sample_schema_and_forbidden_fields(repo_root: Path):
    base = repo_root / "novel-suite" / "solo-demo-trial-intake"
    _schema_validate(
        base / "solo-demo-trial-intake.sample.json",
        base / "solo-demo-trial-intake.schema.json",
    )
    data = json.loads((base / "solo-demo-trial-intake.sample.json").read_text(encoding="utf-8"))
    assert data["sample_only"] is True
    assert data["trial_executed"] is False
    assert data["fake_feedback_generated"] is False
    assert data["commercial_release_allowed"] is False
    assert data["verdict"] == "blocked"


def test_q2_sample_schema_and_forbidden_fields(repo_root: Path):
    base = repo_root / "novel-suite" / "promptpack-friction-review"
    _schema_validate(
        base / "promptpack-friction-review.sample.json",
        base / "promptpack-friction-review.schema.json",
    )
    data = json.loads((base / "promptpack-friction-review.sample.json").read_text(encoding="utf-8"))
    assert data["auto_promptpack_changed"] is False
    assert data["revision_candidate_only"] is True
    assert data["real_friction_available"] is False


def test_q3_sample_schema_and_forbidden_fields(repo_root: Path):
    base = repo_root / "novel-suite" / "multi-ide-feedback-backlog"
    _schema_validate(
        base / "multi-ide-feedback-backlog.sample.json",
        base / "multi-ide-feedback-backlog.schema.json",
    )
    data = json.loads((base / "multi-ide-feedback-backlog.sample.json").read_text(encoding="utf-8"))
    assert data["backlog_auto_applied"] is False
    assert data["telemetry_collected"] is False
    assert data["feedback_imported"] is False
    assert len(data["taxonomy_ids"]) >= 10


def test_run_q_validates_ok():
    q1 = run_solo_demo_trial_intake_validate()
    assert q1.code == E.SOLO_DEMO_TRIAL_INTAKE_VALIDATE_OK
    assert q1.details.get("trial_executed") is False
    assert q1.details.get("fake_feedback_generated") is False

    q2 = run_promptpack_friction_review_validate()
    assert q2.code == E.PROMPTPACK_FRICTION_REVIEW_VALIDATE_OK
    assert q2.details.get("auto_promptpack_changed") is False
    assert q2.details.get("revision_candidate_only") is True

    q3 = run_multi_ide_feedback_backlog_validate()
    assert q3.code == E.MULTI_IDE_FEEDBACK_BACKLOG_VALIDATE_OK
    assert q3.details.get("backlog_auto_applied") is False
    assert q3.details.get("telemetry_collected") is False


def test_commercial_release_candidate_still_blocked():
    result = run_commercial_release_candidate_validate()
    assert result.status == "ok"
    assert result.details.get("verdict") == "blocked"
    assert result.details.get("commercial_release_allowed") is False


@pytest.mark.parametrize(
    "cmd,code",
    [
        ("solo-demo-trial-intake", E.SOLO_DEMO_TRIAL_INTAKE_VALIDATE_OK),
        ("promptpack-friction-review", E.PROMPTPACK_FRICTION_REVIEW_VALIDATE_OK),
        ("multi-ide-feedback-backlog", E.MULTI_IDE_FEEDBACK_BACKLOG_VALIDATE_OK),
    ],
)
def test_cli_q_validates(repo_root: Path, cmd: str, code: str):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", cmd, "validate", "--json"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert json.loads(r.stdout)["code"] == code
