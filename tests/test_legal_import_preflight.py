"""Tests for L3 legal decision import preflight."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.delivery_readiness import (
    run_legal_decision_import_preflight_validate,
    validate_legal_decision_import_preflight,
)


def test_legal_decision_import_preflight_files_exist(repo_root: Path):
    checks = validate_legal_decision_import_preflight()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 14
    assert not failed, failed


def test_legal_decision_import_preflight_sample(repo_root: Path):
    data = json.loads(
        (
            repo_root
            / "novel-suite"
            / "legal-decision-import-preflight"
            / "legal-decision-import-preflight.sample.json"
        ).read_text(encoding="utf-8")
    )
    assert data["input_legal_decision_available"] is False
    assert data["preflight_passed"] is False
    assert data["legal_conclusion_auto_generated"] is False
    assert data["auto_blocker_closure"] is False
    assert data["requires_human_signature"] is True
    assert data["verdict"] == "blocked"


def test_legal_opinion_boundary_doc(repo_root: Path):
    text = (
        repo_root / "novel-suite" / "legal-decision-import-preflight" / "legal_opinion_boundary.md"
    ).read_text(encoding="utf-8")
    assert "legal_conclusion" in text or "非" in text


def test_run_legal_import_preflight_validate_ok():
    result = run_legal_decision_import_preflight_validate()
    assert result.code == E.LEGAL_DECISION_IMPORT_PREFLIGHT_VALIDATE_OK
    assert result.details.get("auto_blocker_closure") is False
    assert result.details.get("preflight_passed") is False


def test_cli_legal_import_preflight_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "legal-decision-import-preflight", "validate", "--json"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert json.loads(r.stdout)["code"] == E.LEGAL_DECISION_IMPORT_PREFLIGHT_VALIDATE_OK
