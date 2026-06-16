"""Tests for X1/X2/X3 UI Workbench extensions."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core.agent_entry_menu import run_agent_entry_menu_validate
from novel_suite.core.commercialization import run_commercial_release_candidate_validate
from novel_suite.core.contracts import novel_suite_root
from novel_suite.core.ip_production_demo import run_ip_production_demo, run_ip_production_demo_validate
from novel_suite.server.app import dispatch


def test_openclaw_retest_prompt_boundaries(repo_root: Path):
    path = repo_root / "novel-suite/ui-agent-workbench/openclaw_retest_prompt.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    for phrase in (
        "SOLO小说项目",
        "Reasonix",
        "不联网",
        "tag / zip / release",
        "agent-entry-menu validate",
        "server validate",
        "writer scan --demo",
    ):
        assert phrase in text


def test_runbooks_dual_routes(repo_root: Path):
    ui = (repo_root / "novel-suite/ui-agent-workbench/runbook.md").read_text(encoding="utf-8")
    srv = (repo_root / "novel-suite/server/runbook.md").read_text(encoding="utf-8")
    for text in (ui, srv):
        assert "路线 A" in text or "stdlib" in text
        assert "contract-only" in text.lower() or "validate" in text
        assert "FastAPI" in text or "uvicorn" in text
        assert "不自动" in text or "默认不安装" in text or "不自动安装" in text


def test_ip_to_short_drama_demo_runnable_in_menu():
    result = run_agent_entry_menu_validate()
    assert result.status == "ok"
    names = {c["name"] for c in result.details.get("checks", [])}
    assert "agent_entry_menu.ip_to_short_drama_demo_runnable" in names
    assert "agent_entry_menu.ip_json_demo_runnable" in names


def test_ip_production_demo_returns_artifacts():
    result = run_ip_production_demo()
    assert result.status == "ok"
    assert result.code == "IP_PRODUCTION_DEMO_RUN_OK"
    arts = result.artifacts
    assert len(arts) == 8
    labels = {a.get("label") for a in arts}
    assert "scene_package.json" in labels
    assert "handoff_manifest.json" in labels
    assert result.details.get("adapter_enabled") is False
    assert result.details.get("external_call_performed") is False
    assert result.details.get("commercial_release_allowed") is False


def test_ip_api_route_demo_only():
    status, payload = dispatch("POST", "/api/agents/ip-to-short-drama/run", body=b"{}")
    assert status == 200
    assert payload.get("status") == "ok"
    assert len(payload.get("artifacts", [])) == 8
    assert payload.get("adapter_enabled") is False
    assert payload.get("external_call_performed") is False
    assert payload.get("commercial_release_allowed") is False

    status2, payload2 = dispatch("POST", "/api/agents/ip-to-short-drama/run", body=b'{"adapter": true}')
    assert payload2.get("status") == "error"


def test_commercial_still_blocked():
    result = run_commercial_release_candidate_validate()
    assert result.status == "ok"
    assert result.details.get("verdict") == "blocked"


def test_ip_production_demo_validate_cli(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root), "PYTHONPATH": str(repo_root / "src")}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "ip-production-demo", "validate", "--json"],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["status"] == "ok"


def test_menu_ip_json_file_exists():
    p = novel_suite_root() / "agent-entry-menu/menu_items/ip.to_short_drama.json"
    assert p.is_file()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["status"] == "demo-runnable"
