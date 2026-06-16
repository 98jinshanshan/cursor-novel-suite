"""Tests for OpenClaw feedback consolidation package."""

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
    run_openclaw_feedback_consolidation_validate,
    validate_openclaw_feedback_consolidation,
)


def _schema_validate(sample_path: Path, schema_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validate(instance=sample, schema=schema)


def test_openclaw_feedback_consolidation_files_exist(repo_root: Path):
    checks = validate_openclaw_feedback_consolidation()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 11
    assert not failed, failed


def test_sample_schema_and_forbidden_fields(repo_root: Path):
    base = repo_root / "novel-suite" / "openclaw-feedback-consolidation"
    _schema_validate(
        base / "openclaw-feedback-consolidation.sample.json",
        base / "openclaw-feedback-consolidation.schema.json",
    )
    data = json.loads((base / "openclaw-feedback-consolidation.sample.json").read_text(encoding="utf-8"))
    assert data["feedback_consolidated"] is True
    assert data["auto_apply"] is False
    assert data["promptpack_changed"] is False
    assert data["gate_changed"] is False
    assert data["backlog_auto_applied"] is False
    assert data["commercial_release_allowed"] is False
    assert data["verdict"] == "blocked"
    assert data["p0_candidate_count"] >= 2
    assert data["p1_candidate_count"] >= 2
    assert data["p2_candidate_count"] >= 1


def test_p0_p1_p2_candidates_documented(repo_root: Path):
    text = (
        repo_root
        / "novel-suite"
        / "openclaw-feedback-consolidation"
        / "prioritized_revision_candidates.md"
    ).read_text(encoding="utf-8")
    for cid in (
        "RC-CONSOL-001",
        "RC-CONSOL-002",
        "RC-CONSOL-003",
        "RC-CONSOL-004",
        "RC-CONSOL-005",
    ):
        assert cid in text
    assert "python -m novel_suite.cli" in text
    assert "PP-001_novel_project_init.md" in text


def test_run_openclaw_feedback_consolidation_validate_ok():
    result = run_openclaw_feedback_consolidation_validate()
    assert result.code == E.OPENCLAW_FEEDBACK_CONSOLIDATION_VALIDATE_OK
    assert result.details.get("auto_apply") is False
    assert result.details.get("promptpack_changed") is False
    assert result.details.get("gate_changed") is False
    assert result.details.get("verdict") == "blocked"


def test_commercial_release_candidate_still_blocked():
    result = run_commercial_release_candidate_validate()
    assert result.status == "ok"
    assert result.details.get("verdict") == "blocked"


def test_cli_openclaw_feedback_consolidation_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "novel_suite.cli",
            "openclaw-feedback-consolidation",
            "validate",
            "--json",
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert json.loads(r.stdout)["code"] == E.OPENCLAW_FEEDBACK_CONSOLIDATION_VALIDATE_OK
