"""Tests for F4/F5 design and research packages (read-only validation)."""



from __future__ import annotations



import json

import os

import subprocess

import sys

from pathlib import Path



from novel_suite.core import errors as E

from novel_suite.core.future_backends import (

    run_future_backends_validate,

    validate_future_backend_designs,

)





def test_f4_f5_files_exist(repo_root: Path):

    checks = validate_future_backend_designs()

    failed = [c for c in checks if not c.get("ok")]

    assert len(checks) >= 28

    assert not failed, failed





def test_f4_design_json_no_runtime(repo_root: Path):

    examples = repo_root / "novel-suite" / "orchestrator-poc-design" / "examples"

    for path in examples.glob("*.design.json"):

        data = json.loads(path.read_text(encoding="utf-8"))

        assert data["runtime_implementation"] is False, path.name

        assert data["langgraph_installed"] is False, path.name

        assert data["external_calls_allowed"] is False, path.name

        assert data["commercial_release_allowed"] is False, path.name





def test_f5_matrix_covers_candidates(repo_root: Path):

    text = (

        repo_root / "novel-suite" / "knowledge-backend-research" / "candidate_backends_matrix.md"

    ).read_text(encoding="utf-8")

    for name in ("Local MD", "SQLite FTS", "LlamaIndex", "Qdrant", "Chroma"):

        assert name in text or "Markdown" in text





def test_run_future_backends_validate_ok():

    result = run_future_backends_validate()

    assert result.status == "ok"

    assert result.code == E.FUTURE_BACKENDS_VALIDATE_OK

    assert result.details.get("langgraph_installed") is False

    assert result.details.get("rag_runtime") is False





def test_cli_future_backends_validate(repo_root: Path):

    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}

    r = subprocess.run(

        [sys.executable, "-m", "novel_suite.cli", "future-backends", "validate", "--json"],

        cwd=str(repo_root),

        capture_output=True,

        text=True,

        env=env,

    )

    assert r.returncode == 0, r.stderr + r.stdout

    data = json.loads(r.stdout)

    assert data["code"] == E.FUTURE_BACKENDS_VALIDATE_OK

