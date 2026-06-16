"""Novel Suite product-layer contracts and doctor --core-contracts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from novel_suite.core.contracts import CONTRACT_STEMS, contracts_dir, run_core_contract_checks
from novel_suite.writer import doctor

REPO = Path(__file__).resolve().parents[1]


def test_contract_schema_md_and_json_exist():
    cdir = contracts_dir()
    assert cdir.is_dir()
    for stem in CONTRACT_STEMS:
        assert (cdir / f"{stem}.schema.md").is_file(), stem
        assert (cdir / f"{stem}.schema.json").is_file(), stem


def test_contract_schema_json_parseable():
    for stem in CONTRACT_STEMS:
        path = contracts_dir() / f"{stem}.schema.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["type"] == "object"
        assert "properties" in data
        assert "required" in data


def test_contract_schema_json_validates_with_jsonschema():
    jsonschema = pytest.importorskip("jsonschema")
    for stem in CONTRACT_STEMS:
        path = contracts_dir() / f"{stem}.schema.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.Draft7Validator.check_schema(data)


def test_run_core_contract_checks_passes(repo_root: Path):
    checks, code = run_core_contract_checks()
    failed = [c for c in checks if not c.get("ok")]
    assert code == 0, failed
    assert not failed


def test_doctor_core_contracts_result(repo_root: Path):
    result = doctor.run_core_contracts_doctor()
    assert result.status == "ok"
    assert result.code == "DOCTOR_CORE_OK"
    assert result.details.get("checks")


def test_cli_doctor_core_contracts_json(repo_root: Path):
    import os

    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "doctor", "--core-contracts", "--json"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    data = json.loads(r.stdout)
    assert data["status"] == "ok"
    assert data["code"] == "DOCTOR_CORE_OK"
