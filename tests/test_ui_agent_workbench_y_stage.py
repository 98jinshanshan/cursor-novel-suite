"""Tests for Y1/Y2/Y3 UI result cards and onboarding."""

from __future__ import annotations

import json
from pathlib import Path

from novel_suite.core.agent_entry_menu import run_agent_entry_menu_list
from novel_suite.core.commercialization import run_commercial_release_candidate_validate
from novel_suite.core.contracts import novel_suite_root


def _read(rel: str) -> str:
    return (novel_suite_root().parent / rel).read_text(encoding="utf-8")


def test_onboarding_recommended_flow(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    assert "推荐流程" in html
    assert "运行 Doctor" in html
    assert "IP 转短剧" in html
    assert "章节审稿" in html or "结果卡片" in html


def test_status_badges_in_html(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    for badge in ("demo-runnable", "planned", "blocked"):
        assert badge in html
    assert 'data-status="demo-runnable"' in html
    assert 'data-status="planned"' in html


def test_artifact_chinese_labels_in_app_js(repo_root: Path):
    js = (repo_root / "novel-suite/ui-agent-workbench/static/app.js").read_text(encoding="utf-8")
    mapping = {
        "chapter_review.md": "章节分析",
        "story_beats.md": "短剧节拍",
        "scene_package.json": "场景包",
        "shot_list.csv": "镜头清单",
        "asset_requirements.md": "素材需求",
        "timeline_package.json": "时间线包",
        "risk_check.md": "风险检查",
        "handoff_manifest.json": "交付清单",
    }
    for key, label in mapping.items():
        assert key in js
        assert label in js


def test_summary_card_and_dev_details(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    js = (repo_root / "novel-suite/ui-agent-workbench/static/app.js").read_text(encoding="utf-8")
    assert "summary-card" in html
    assert "summary-status" in html
    assert "renderSummaryCard" in js
    assert "开发者详情" in html
    assert "dev-details" in html


def test_blocked_boundary_copy(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    for phrase in (
        "不可发布",
        "不可外部调用",
        "不生成真实视频",
        "tag/zip/release",
        "commercial_release_allowed=false",
        "verdict=blocked",
    ):
        assert phrase in html


def test_ip_drama_production_package_notice(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    js = (repo_root / "novel-suite/ui-agent-workbench/static/app.js").read_text(encoding="utf-8")
    assert "短剧生产包" in html or "短剧生产包" in js
    assert "不生成真实视频" in html or "不生成真实视频" in js
    assert "handoff-summary" in html


def test_planned_agents_explanations(repo_root: Path):
    js = (repo_root / "novel-suite/ui-agent-workbench/static/app.js").read_text(encoding="utf-8")
    for agent_id in (
        "novel.create",
        "asset.manage",
        "agent.workflow",
        "release.preflight",
    ):
        assert agent_id in js
    assert "PLANNED_INFO" in js
    assert "前置条件" in js or "prereq" in js


def test_novel_review_demo_runnable_in_menu():
    result = run_agent_entry_menu_list()
    items = result.details.get("menu_items", [])
    review = next((i for i in items if i.get("id") == "novel.review"), None)
    assert review is not None
    assert review.get("status") == "demo-runnable"


def test_commercial_still_blocked():
    result = run_commercial_release_candidate_validate()
    assert result.status == "ok"
    assert result.details.get("verdict") == "blocked"


def test_ux_notes_exists(repo_root: Path):
    path = repo_root / "novel-suite/ui-agent-workbench/ux_notes.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "摘要卡片" in text
    assert "novel.review" in text
