"""Tests for H3 legal review packet materials."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.delivery_readiness import (
    run_legal_review_packet_validate,
    validate_legal_review_packet,
)


def test_legal_review_packet_files_exist(repo_root: Path):
    checks = validate_legal_review_packet()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 17
    assert not failed, failed


def test_legal_packet_sample(repo_root: Path):
    data = json.loads(
        (repo_root / "novel-suite" / "legal-review-packet" / "legal-review-packet.sample.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["legal_conclusion_auto_generated"] is False
    assert data["requires_human_or_legal_review"] is True
    assert data["commercial_release_allowed"] is False
    assert data["blockers_for_counsel"]["B01"] == "open"


def test_b01_b05_questions_doc(repo_root: Path):
    text = (repo_root / "novel-suite" / "legal-review-packet" / "legal_questions_for_counsel.md").read_text(
        encoding="utf-8"
    )
    for bid in ("B01", "B02", "B03", "B04", "B05"):
        assert bid in text


def test_run_legal_review_packet_validate_ok():
    result = run_legal_review_packet_validate()
    assert result.code == E.LEGAL_REVIEW_PACKET_VALIDATE_OK
    assert result.details.get("legal_conclusion_auto_generated") is False


def test_cli_legal_review_packet_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "legal-review-packet", "validate", "--json"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert json.loads(r.stdout)["code"] == E.LEGAL_REVIEW_PACKET_VALIDATE_OK
