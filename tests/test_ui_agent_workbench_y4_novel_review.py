"""Tests for Y4 novel.review offline demo Agent and UI fixes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core.agent_entry_menu import run_agent_entry_menu_list, run_agent_entry_menu_validate
from novel_suite.core.commercialization import run_commercial_release_candidate_validate
from novel_suite.core.novel_review_demo import run_novel_review_demo, run_novel_review_demo_validate
from novel_suite.server.app import dispatch


def test_novel_review_demo_runnable_in_menu():
    result = run_agent_entry_menu_validate()
    assert result.status == "ok"
    names = {c["name"] for c in result.details.get("checks", [])}
    assert "agent_entry_menu.novel_review_demo_runnable" in names


def test_novel_review_list_demo_runnable():
    result = run_agent_entry_menu_list()
    items = result.details.get("menu_items", [])
    review = next(i for i in items if i.get("id") == "novel.review")
    assert review.get("status") == "demo-runnable"
    assert review.get("auto_rewrite_allowed") is False


def test_novel_review_demo_six_artifacts():
    result = run_novel_review_demo()
    assert result.status == "ok"
    assert result.code == "NOVEL_REVIEW_DEMO_RUN_OK"
    assert len(result.artifacts) == 6
    labels = {a.get("label") for a in result.artifacts}
    assert "revision_suggestions.md" in labels
    assert result.details.get("auto_rewrite_allowed") is False
    assert result.details.get("commercial_release_allowed") is False


def test_novel_review_api_route():
    status, payload = dispatch("POST", "/api/agents/novel-review/run", body=b"{}")
    assert status == 200
    assert payload.get("status") == "ok"
    assert len(payload.get("artifacts", [])) == 6


def test_ui_run_vs_commercial_semantics(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    js = (repo_root / "novel-suite/ui-agent-workbench/static/app.js").read_text(encoding="utf-8")
    assert "运行状态" in html
    assert "商业边界" in html
    assert "summary-run-blockers" in html
    assert "summary-commercial" in html
    assert "运行 OK ≠ 商业可用" in html or "运行成功 ≠ 商业可用" in html
    assert "runStatus" in js
    assert "COMMERCIAL_BOUNDARY" in js


def test_ui_novel_create_clickable_planned(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    assert 'data-id="novel.create"' in html
    assert "disabled" not in html.split('data-id="novel.create"')[1].split(">")[0]
    assert "planned-exec-hint" in html


def test_ui_handoff_scene_package_order(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    assert "场景包" in html
    idx_beats = html.find("短剧节拍")
    idx_scene = html.find("场景包")
    idx_shot = html.find("镜头清单")
    assert idx_beats < idx_scene < idx_shot


def test_ui_review_artifact_labels(repo_root: Path):
    js = (repo_root / "novel-suite/ui-agent-workbench/static/app.js").read_text(encoding="utf-8")
    for key, label in (
        ("review_summary.md", "审稿摘要"),
        ("continuity_check.md", "连续性检查"),
        ("deai_checklist.md", "去 AI 味检查"),
        ("revision_suggestions.md", "改稿建议"),
    ):
        assert key in js
        assert label in js


def test_ui_dev_json_collapsed(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    assert "开发者详情" in html
    assert "dev-details" in html


def test_revision_suggestions_no_auto_rewrite(repo_root: Path):
    text = (repo_root / "novel-suite/novel-review-demo/revision_suggestions.md").read_text(encoding="utf-8")
    assert "不自动" in text
    assert "建议" in text


def test_commercial_still_blocked():
    result = run_commercial_release_candidate_validate()
    assert result.details.get("verdict") == "blocked"


def test_cli_novel_review_demo(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root), "PYTHONPATH": str(repo_root / "src")}
    for cmd in (["novel-review-demo", "validate"], ["novel-review-demo", "run"]):
        r = subprocess.run(
            [sys.executable, "-m", "novel_suite.cli", *cmd, "--json"],
            cwd=repo_root,
            env=env,
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, r.stderr
        assert json.loads(r.stdout)["status"] == "ok"
