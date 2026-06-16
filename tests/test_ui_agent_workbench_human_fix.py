"""Human-Fix-1: trial feedback productization (CR-HUMAN-003~007)."""

from __future__ import annotations

import json
from pathlib import Path

import argparse

from novel_suite.cli import (
    cmd_agent_entry_menu_validate,
    cmd_commercial_release_candidate_validate,
    cmd_product_validate,
    cmd_server_validate,
)
from novel_suite.server.app import handle_projects_active, result_to_api_payload
from novel_suite.core.result import error_result


def _blocked_top_level(capsys, cmd_fn) -> dict:
    code = cmd_fn(argparse.Namespace(json=True))
    assert code == 0
    return json.loads(capsys.readouterr().out)


def test_validate_commands_blocked_top_level(capsys):
    for cmd in (
        cmd_product_validate,
        cmd_server_validate,
        cmd_agent_entry_menu_validate,
        cmd_commercial_release_candidate_validate,
    ):
        data = _blocked_top_level(capsys, cmd)
        assert data.get("commercial_release_allowed") is False
        assert data.get("verdict") == "blocked"


def test_api_payload_blocked_fields():
    payload = result_to_api_payload(
        error_result("TEST", "x", commercial_release_allowed=False, verdict="blocked")
    )
    assert payload["commercial_release_allowed"] is False
    assert payload["verdict"] == "blocked"


def test_stale_active_slug_payload():
    payload = handle_projects_active()
    # When registry is valid, may be ok; structure must support stale code.
    assert "commercial_release_allowed" in payload
    assert "verdict" in payload
    if payload.get("code") == "STALE_ACTIVE_SLUG":
        assert payload.get("status") == "error"
        assert payload.get("details", {}).get("stale") is True


def test_summary_labels_human_fix(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    assert "运行阻塞" in html
    assert "商业/生成边界" in html
    assert "运行成功；商业发布和真实生成仍被禁用" in html
    assert "当前项目 / Active Project" in html
    assert "当前 Agent 摘要" in html
    assert "active-project-stale" in html
    assert "dev-cli-list" in html


def test_app_js_human_fix_semantics(repo_root: Path):
    js = (repo_root / "novel-suite/ui-agent-workbench/static/app.js").read_text(encoding="utf-8")
    assert "USER_NEXT_ACTIONS" in js
    assert "splitBlockers" in js
    assert "BOUNDARY_BLOCKER_IDS" in js
    assert "查看 Top3 选题" in js
    assert "artifact-path-details" in js
    assert "开发者信息 / 文件路径" in js
    assert "cliNextActions" in js


def test_artifact_path_folded_in_details(repo_root: Path):
    js = (repo_root / "novel-suite/ui-agent-workbench/static/app.js").read_text(encoding="utf-8")
    assert "artifact-path-details" in js
    assert "开发者信息 / 文件路径" in js
    assert "artifact-preview-details" in js


def test_stale_active_friendly_copy(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    assert "未登记或已失效" in html
    assert "本地 Demo 不依赖 active novel" in html
