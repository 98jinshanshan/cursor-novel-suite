"""Tests for I3 legal review response intake."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.delivery_readiness import (
    run_legal_review_response_intake_validate,
    validate_legal_review_response_intake,
)


def test_legal_response_intake_files_exist(repo_root: Path):
    checks = validate_legal_review_response_intake()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 12
    assert not failed, failed


def test_legal_response_intake_sample(repo_root: Path):
    data = json.loads(
        (
            repo_root
            / "novel-suite"
            / "legal-review-response-intake"
            / "legal-review-response-intake.sample.json"
        ).read_text(encoding="utf-8")
    )
    assert data["legal_conclusion_auto_generated"] is False
    assert data["auto_blocker_closure"] is False
    assert data["requires_human_signature"] is True
    assert data["verdict"] == "blocked"
    assert "B01" in data["blocker_responses"]


def test_blocker_mapping_doc(repo_root: Path):
    text = (
        repo_root / "novel-suite" / "legal-review-response-intake" / "blocker_response_mapping.md"
    ).read_text(encoding="utf-8")
    for bid in ("B01", "B05"):
        assert bid in text
    assert "auto_blocker_closure" in text or "自动关闭" in text or "否" in text


def test_run_legal_response_intake_validate_ok():
    result = run_legal_review_response_intake_validate()
    assert result.code == E.LEGAL_REVIEW_RESPONSE_INTAKE_VALIDATE_OK
    assert result.details.get("auto_blocker_closure") is False


def test_cli_legal_response_intake_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "legal-review-response-intake", "validate", "--json"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert json.loads(r.stdout)["code"] == E.LEGAL_REVIEW_RESPONSE_INTAKE_VALIDATE_OK
