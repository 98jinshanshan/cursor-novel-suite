"""Tests for O2/O3 solo founder alternative gates."""

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
    run_solo_founder_compliance_self_check_validate,
    run_solo_founder_freeze_self_check_validate,
    run_solo_founder_release_blocked_declaration_validate,
    validate_solo_founder_compliance_self_check,
    validate_solo_founder_freeze_self_check,
    validate_solo_founder_release_blocked_declaration,
)


def _schema_validate(sample_path: Path, schema_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validate(instance=sample, schema=schema)


def test_solo_founder_freeze_self_check_files_exist(repo_root: Path):
    checks = validate_solo_founder_freeze_self_check()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 7
    assert not failed, failed


def test_solo_founder_compliance_self_check_files_exist(repo_root: Path):
    checks = validate_solo_founder_compliance_self_check()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 8
    assert not failed, failed


def test_solo_founder_release_blocked_declaration_files_exist(repo_root: Path):
    checks = validate_solo_founder_release_blocked_declaration()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 8
    assert not failed, failed


def test_o2_sample_schema_and_forbidden_fields(repo_root: Path):
    base = repo_root / "novel-suite" / "solo-founder-freeze-self-check"
    _schema_validate(
        base / "solo-founder-freeze-self-check.sample.json",
        base / "solo-founder-freeze-self-check.schema.json",
    )
    data = json.loads((base / "solo-founder-freeze-self-check.sample.json").read_text(encoding="utf-8"))
    assert data["freeze_candidate_only"] is True
    assert data["agent_may_create_tag"] is False
    assert data["tag_created"] is False
    assert data["zip_created"] is False
    assert data["release_created"] is False
    assert data["commercial_release_allowed"] is False
    assert data["verdict"] == "blocked"


def test_o3_sample_schema_and_forbidden_fields(repo_root: Path):
    base = repo_root / "novel-suite" / "solo-founder-compliance-self-check"
    _schema_validate(
        base / "solo-founder-compliance-self-check.sample.json",
        base / "solo-founder-compliance-self-check.schema.json",
    )
    data = json.loads((base / "solo-founder-compliance-self-check.sample.json").read_text(encoding="utf-8"))
    assert data["legal_conclusion_auto_generated"] is False
    assert data["legal_review_completed"] is False
    assert data["auto_blocker_closure"] is False
    assert data["blocker_B01"] == "open"
    assert data["blocker_B05"] == "resolved-demo-only"
    assert data["commercial_release_allowed"] is False
    assert data["verdict"] == "blocked"


def test_declaration_sample_schema_and_forbidden_fields(repo_root: Path):
    base = repo_root / "novel-suite" / "solo-founder-release-blocked-declaration"
    _schema_validate(
        base / "solo-founder-release-blocked-declaration.sample.json",
        base / "solo-founder-release-blocked-declaration.schema.json",
    )
    data = json.loads((base / "solo-founder-release-blocked-declaration.sample.json").read_text(encoding="utf-8"))
    assert data["personal_dev_continue_allowed"] is True
    assert data["commercial_release_allowed"] is False
    assert data["verdict"] == "blocked"
    assert data["legal_conclusion_auto_generated"] is False
    assert data["auto_blocker_closure"] is False


def test_run_solo_founder_validates_ok():
    o2 = run_solo_founder_freeze_self_check_validate()
    assert o2.code == E.SOLO_FOUNDER_FREEZE_SELF_CHECK_VALIDATE_OK
    assert o2.details.get("verdict") == "blocked"
    assert o2.details.get("agent_may_create_tag") is False

    o3 = run_solo_founder_compliance_self_check_validate()
    assert o3.code == E.SOLO_FOUNDER_COMPLIANCE_SELF_CHECK_VALIDATE_OK
    assert o3.details.get("legal_conclusion_auto_generated") is False
    assert o3.details.get("auto_blocker_closure") is False

    decl = run_solo_founder_release_blocked_declaration_validate()
    assert decl.code == E.SOLO_FOUNDER_RELEASE_BLOCKED_DECLARATION_VALIDATE_OK
    assert decl.details.get("personal_dev_continue_allowed") is True


def test_commercial_release_candidate_still_blocked():
    result = run_commercial_release_candidate_validate()
    assert result.status == "ok"
    assert result.details.get("verdict") == "blocked"
    assert result.details.get("commercial_release_allowed") is False


@pytest.mark.parametrize(
    "cmd,code",
    [
        ("solo-founder-freeze-self-check", E.SOLO_FOUNDER_FREEZE_SELF_CHECK_VALIDATE_OK),
        ("solo-founder-compliance-self-check", E.SOLO_FOUNDER_COMPLIANCE_SELF_CHECK_VALIDATE_OK),
        ("solo-founder-release-blocked-declaration", E.SOLO_FOUNDER_RELEASE_BLOCKED_DECLARATION_VALIDATE_OK),
    ],
)
def test_cli_solo_founder_validates(repo_root: Path, cmd: str, code: str):
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
