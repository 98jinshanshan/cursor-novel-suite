"""Tests for F2 workflow contracts (read-only validation)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.workflow_contracts import (
    run_workflow_contract_validate,
    validate_workflow_contracts,
)


def test_schema_and_samples_exist(repo_root: Path):
    checks = validate_workflow_contracts()
    failed = [c for c in checks if not c.get("ok")]
    assert len(checks) >= 11
    assert not failed, failed


def test_all_samples_external_calls_disabled(repo_root: Path):
    examples = repo_root / "novel-suite" / "workflow-contracts" / "examples"
    for path in examples.glob("*.contract.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["external_calls"]["allowed"] is False, path.name
        assert data["commercial_boundary"]["commercial_release_allowed"] is False, path.name
        assert data.get("permission_level", "").strip(), path.name
        assert data.get("workflow_id"), path.name
        assert data.get("trace_fields"), path.name


def test_release_candidate_maps_c8c9_blockers(repo_root: Path):
    data = json.loads(
        (
            repo_root
            / "novel-suite"
            / "workflow-contracts"
            / "examples"
            / "commercial_release_candidate.contract.json"
        ).read_text(encoding="utf-8")
    )
    comm = data["commercial_boundary"]
    assert comm["verdict"] == "blocked"
    assert comm["commercial_release_allowed"] is False
    blockers = comm["blockers"]
    assert blockers["B01"] == "open"
    assert blockers["B04"] == "open"
    assert blockers["B05"] == "resolved-demo-only"
    assert "B05" in comm.get("B05_note", "") or "resolved" in comm.get("B05_note", "").lower()


def test_adapter_dry_run_is_p1_a1(repo_root: Path):
    data = json.loads(
        (repo_root / "novel-suite" / "workflow-contracts" / "examples" / "adapter_dry_run.contract.json").read_text(
            encoding="utf-8"
        )
    )
    assert "P1" in data["permission_level"]
    assert data["adapter_level"] == "A1"


def test_run_workflow_contract_validate_ok():
    result = run_workflow_contract_validate()
    assert result.status == "ok"
    assert result.code == E.WORKFLOW_CONTRACT_VALIDATE_OK
    assert result.details.get("commercial_release_allowed") is False


def test_cli_workflow_contract_validate(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "workflow-contract", "validate", "--json"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    data = json.loads(r.stdout)
    assert data["code"] == E.WORKFLOW_CONTRACT_VALIDATE_OK


def test_product_read_workflow_contract(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "novel_suite.cli",
            "product",
            "read",
            "--category",
            "workflow_contracts",
            "--name",
            "chapter_writing",
            "--json",
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    data = json.loads(r.stdout)
    assert data["status"] == "ok"
    assert data["details"]["asset"]["name"] == "chapter_writing"
