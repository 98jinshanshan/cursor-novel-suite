"""Tests for P1/P2/P3 solo demo, promptpack first-run, and multi-IDE feedback."""

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
    run_multi_ide_dry_run_feedback_validate,
    run_promptpack_first_run_validate,
    run_solo_demo_15min_validate,
    validate_multi_ide_dry_run_feedback,
    validate_promptpack_first_run,
    validate_solo_demo_15min,
)


def _schema_validate(sample_path: Path, schema_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validate(instance=sample, schema=schema)


def test_solo_demo_15min_files_exist(repo_root: Path):
    checks = validate_solo_demo_15min()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 9
    assert not failed, failed


def test_promptpack_first_run_files_exist(repo_root: Path):
    checks = validate_promptpack_first_run()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 12
    assert not failed, failed


def test_multi_ide_dry_run_feedback_files_exist(repo_root: Path):
    checks = validate_multi_ide_dry_run_feedback()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 10
    assert not failed, failed


def test_p1_sample_schema_and_blocked_fields(repo_root: Path):
    base = repo_root / "novel-suite" / "solo-demo-15min"
    _schema_validate(
        base / "solo-demo-15min.sample.json",
        base / "solo-demo-15min.schema.json",
    )
    data = json.loads((base / "solo-demo-15min.sample.json").read_text(encoding="utf-8"))
    assert data["demo_type"] == "local_readonly_dry_run"
    assert data["external_call_performed"] is False
    assert data["commercial_release_allowed"] is False
    assert data["verdict"] == "blocked"


def test_p2_sample_schema_and_pp001_entry(repo_root: Path):
    base = repo_root / "novel-suite" / "promptpack-first-run"
    _schema_validate(
        base / "promptpack-first-run.sample.json",
        base / "promptpack-first-run.schema.json",
    )
    data = json.loads((base / "promptpack-first-run.sample.json").read_text(encoding="utf-8"))
    assert data["new_user_start_pack"] == "PP-001"
    assert data["commercial_claim_allowed"] is False
    assert data["external_call_performed"] is False


def test_p3_sample_schema_and_no_telemetry(repo_root: Path):
    base = repo_root / "novel-suite" / "multi-ide-dry-run-feedback"
    _schema_validate(
        base / "multi-ide-dry-run-feedback.sample.json",
        base / "multi-ide-dry-run-feedback.schema.json",
    )
    data = json.loads((base / "multi-ide-dry-run-feedback.sample.json").read_text(encoding="utf-8"))
    assert data["telemetry_collected"] is False
    assert data["external_call_performed"] is False
    assert data["private_project_read"] is False
    assert len(data["supported_ides"]) >= 6


def test_run_p1p2p3_validates_ok():
    p1 = run_solo_demo_15min_validate()
    assert p1.code == E.SOLO_DEMO_15MIN_VALIDATE_OK
    assert p1.details.get("verdict") == "blocked"
    assert p1.details.get("commercial_release_allowed") is False

    p2 = run_promptpack_first_run_validate()
    assert p2.code == E.PROMPTPACK_FIRST_RUN_VALIDATE_OK
    assert p2.details.get("new_user_start_pack") == "PP-001"
    assert p2.details.get("commercial_claim_allowed") is False

    p3 = run_multi_ide_dry_run_feedback_validate()
    assert p3.code == E.MULTI_IDE_DRY_RUN_FEEDBACK_VALIDATE_OK
    assert p3.details.get("telemetry_collected") is False


def test_commercial_release_candidate_still_blocked():
    result = run_commercial_release_candidate_validate()
    assert result.status == "ok"
    assert result.details.get("verdict") == "blocked"
    assert result.details.get("commercial_release_allowed") is False


@pytest.mark.parametrize(
    "cmd,code",
    [
        ("solo-demo-15min", E.SOLO_DEMO_15MIN_VALIDATE_OK),
        ("promptpack-first-run", E.PROMPTPACK_FIRST_RUN_VALIDATE_OK),
        ("multi-ide-dry-run-feedback", E.MULTI_IDE_DRY_RUN_FEEDBACK_VALIDATE_OK),
    ],
)
def test_cli_p1p2p3_validates(repo_root: Path, cmd: str, code: str):
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
