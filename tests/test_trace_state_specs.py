"""Tests for F3 trace/state specs (read-only validation)."""



from __future__ import annotations



import json

import os

import subprocess

import sys

from pathlib import Path



from novel_suite.core import errors as E

from novel_suite.core.trace_state import run_trace_state_validate, validate_trace_state_specs





def test_trace_state_files_exist(repo_root: Path):

    checks = validate_trace_state_specs()

    failed = [c for c in checks if not c.get("ok")]

    assert len(checks) >= 15

    assert not failed, failed





def test_trace_jsonl_samples_boundary(repo_root: Path):

    examples = repo_root / "novel-suite" / "trace-state" / "examples"

    for path in examples.glob("*.trace.jsonl"):

        for line in path.read_text(encoding="utf-8").splitlines():

            if not line.strip():

                continue

            data = json.loads(line)

            assert data["external_call_performed"] is False, path.name

            assert data["commercial_release_allowed"] is False, path.name

            assert data.get("run_id"), path.name

            assert data.get("trace_id"), path.name





def test_run_trace_state_validate_ok():

    result = run_trace_state_validate()

    assert result.status == "ok"

    assert result.code == E.TRACE_STATE_VALIDATE_OK

    assert result.details.get("commercial_release_allowed") is False





def test_cli_trace_state_validate(repo_root: Path):

    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}

    r = subprocess.run(

        [sys.executable, "-m", "novel_suite.cli", "trace-state", "validate", "--json"],

        cwd=str(repo_root),

        capture_output=True,

        text=True,

        env=env,

    )

    assert r.returncode == 0, r.stderr + r.stdout

    data = json.loads(r.stdout)

    assert data["code"] == E.TRACE_STATE_VALIDATE_OK

