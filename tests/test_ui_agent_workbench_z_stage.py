"""Tests for Z stage: demo success gate, semantic fixes, mobile planning."""

from __future__ import annotations

import json
from pathlib import Path

from novel_suite.core.agent_entry_menu import (
    run_agent_entry_menu_list,
    run_agent_entry_menu_validate,
)
from novel_suite.core.commercialization import run_commercial_release_candidate_validate


def test_demo_success_gate_doc(repo_root: Path):
    path = repo_root / "novel-suite/ui-agent-workbench/demo_success_gate.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "本地 UI Agent Workbench Demo 闭环成立" in text
    assert "Doctor → 市场调研 demo → IP 转短剧 demo → novel.review demo" in text
    assert "市场调研 demo → ip.to_short_drama demo → novel.review demo" in text
    assert "asset.manage" not in text or "不扩" in text


def test_mobile_app_readiness_plan(repo_root: Path):
    path = repo_root / "novel-suite/ui-agent-workbench/mobile_app_readiness_plan.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "PWA" in text
    assert "AA Mobile-Ready PWA" in text
    assert "不上架" in text or "不登录" in text


def test_release_preflight_planned_but_blocked(repo_root: Path):
    manifest = json.loads(
        (repo_root / "novel-suite/agent-entry-menu/agent-ui-manifest.sample.json").read_text(
            encoding="utf-8"
        )
    )
    item = next(i for i in manifest["menu_items"] if i["id"] == "release.preflight")
    assert item["status"] == "planned-but-blocked"

    item_json = json.loads(
        (repo_root / "novel-suite/agent-entry-menu/menu_items/release.preflight.json").read_text(
            encoding="utf-8"
        )
    )
    assert item_json["status"] == "planned-but-blocked"
    assert item_json["verdict"] == "blocked"


def test_menu_stats_legend_in_html(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    assert "manifest 6 项" in html
    assert "UI 侧栏" in html
    assert "planned-but-blocked" in html


def test_manual_rewrite_hint(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    js = (repo_root / "novel-suite/ui-agent-workbench/static/app.js").read_text(encoding="utf-8")
    assert "改稿建议需人工采用，不自动写回" in html
    assert "manual-rewrite-banner" in html
    assert "manual-rewrite-banner" in js


def test_four_entry_onboarding(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    assert "btn-market-scan" in html
    assert "市场调研 demo" in html


def test_agent_entry_menu_validate_z_checks():
    result = run_agent_entry_menu_validate()
    assert result.status == "ok", result.message
    names = {c["name"] for c in result.details.get("checks", [])}
    assert "agent_entry_menu.release_preflight_planned_but_blocked" in names
    assert "agent_entry_menu.release_preflight_json_planned_but_blocked" in names


def test_commercial_still_blocked():
    result = run_commercial_release_candidate_validate()
    assert result.status == "ok"
    assert result.details.get("verdict") == "blocked"


def test_list_release_preflight_status():
    result = run_agent_entry_menu_list()
    items = result.details.get("menu_items", [])
    preflight = next(i for i in items if i.get("id") == "release.preflight")
    assert preflight.get("status") == "planned-but-blocked"
