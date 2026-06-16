"""Tests for C9 commercial release candidate gate (read-only)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.commercialization import (
    run_commercial_release_candidate_validate,
    validate_commercial_release_candidate,
)


def test_c9_docs_exist(repo_root: Path):
    checks = validate_commercial_release_candidate()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 14
    assert not failed, failed


def test_candidate_manifest_blocked(repo_root: Path):
    data = json.loads(
        (
            repo_root
            / "novel-suite"
            / "commercial-release-candidate"
            / "candidate-package-manifest.sample.json"
        ).read_text(encoding="utf-8")
    )
    assert data["commercial_release_allowed"] is False
    assert data["verdict"] == "blocked"
    assert data["adapter_max_level"] == "A1"


def test_final_release_gate_declares_blocked(repo_root: Path):
    text = (
        repo_root
        / "novel-suite"
        / "commercial-release-candidate"
        / "final-release-gate.md"
    ).read_text(encoding="utf-8")
    assert "commercial_release_allowed: false" in text
    assert "verdict: blocked" in text


def test_run_candidate_validate_ok():
    result = run_commercial_release_candidate_validate()
    assert result.status == "ok"
    assert result.code == E.CANDIDATE_GATE_VALIDATE_OK
    assert result.details.get("commercial_release_allowed") is False
    assert result.details.get("verdict") == "blocked"


def test_cli_candidate_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "novel_suite.cli",
            "commercial-release-candidate",
            "validate",
            "--json",
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    data = json.loads(r.stdout)
    assert data["code"] == E.CANDIDATE_GATE_VALIDATE_OK
    assert data["details"]["commercial_release_allowed"] is False
