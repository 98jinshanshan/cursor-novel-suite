"""Tests for J3 legal review meeting."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.delivery_readiness import (
    run_legal_review_meeting_validate,
    validate_legal_review_meeting,
)


def test_legal_review_meeting_files_exist(repo_root: Path):
    checks = validate_legal_review_meeting()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 13
    assert not failed, failed


def test_legal_review_meeting_sample(repo_root: Path):
    data = json.loads(
        (repo_root / "novel-suite" / "legal-review-meeting" / "legal-review-meeting.sample.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["meeting_held"] is False
    assert data["legal_conclusion_auto_generated"] is False
    assert data["auto_blocker_closure"] is False
    assert data["requires_human_signature"] is True
    assert data["verdict"] == "blocked"
    assert "B01" in data["blocker_discussion"]


def test_no_auto_blocker_closure_doc(repo_root: Path):
    text = (repo_root / "novel-suite" / "legal-review-meeting" / "no_auto_blocker_closure_policy.md").read_text(
        encoding="utf-8"
    )
    assert "auto_blocker_closure" in text
    for bid in ("B01", "B05"):
        assert bid in text or "blocker" in text.lower()


def test_run_legal_review_meeting_validate_ok():
    result = run_legal_review_meeting_validate()
    assert result.code == E.LEGAL_REVIEW_MEETING_VALIDATE_OK
    assert result.details.get("auto_blocker_closure") is False
    assert result.details.get("meeting_held") is False


def test_cli_legal_review_meeting_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "legal-review-meeting", "validate", "--json"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert json.loads(r.stdout)["code"] == E.LEGAL_REVIEW_MEETING_VALIDATE_OK
