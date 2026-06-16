"""Tests for W2 UI Agent server contract."""

from __future__ import annotations

import json
import os
import subprocess
import sys

from novel_suite.server.app import dispatch, handle_market_scan_run
from novel_suite.server.contracts import commercial_blocked_unchanged, load_api_contract
from novel_suite.server.runner import run_server_validate


def test_server_validate_ok():
    result = run_server_validate()
    assert result.status == "ok"
    assert result.code == "SERVER_VALIDATE_OK"
    assert result.details.get("commercial_release_allowed") is False


def test_api_contract_commercial_blocked():
    data = load_api_contract()
    assert data["commercial_release_allowed"] is False
    assert data["verdict"] == "blocked"
    assert commercial_blocked_unchanged()


def test_market_scan_demo_only():
    status, payload = dispatch("POST", "/api/agents/market-scan/run", body=b"{}")
    assert status == 200
    assert payload.get("demo_only") is True

    status2, payload2 = dispatch("POST", "/api/agents/market-scan/run", body=b'{"demo": false}')
    assert status2 == 200
    assert payload2.get("status") == "error"
    assert payload2.get("code") == "SCAN_LIVE_BLOCKED"


def test_doctor_route():
    status, payload = dispatch("GET", "/api/doctor")
    assert status == 200
    assert "code" in payload
    assert "message" in payload


def test_cli_server_validate(repo_root):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root), "PYTHONPATH": str(repo_root / "src")}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "server", "validate", "--json"],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["status"] == "ok"
    assert data["code"] == "SERVER_VALIDATE_OK"
