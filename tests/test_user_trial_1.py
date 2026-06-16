"""UserTrial-1 real user scenario trial preparation package."""

from __future__ import annotations

import re
from pathlib import Path

from novel_suite.core.commercialization import run_commercial_release_candidate_validate
from novel_suite.core.product_layer import run_product_validate


TRIAL_FILES = (
    "README.md",
    "scenario_brief.md",
    "sample_chapter.md",
    "trial_runbook.md",
    "observer_checklist.md",
    "user_feedback_form.md",
    "success_metrics.md",
    "boundary_notice.md",
)

FORBIDDEN_SAMPLE_MARKERS = (
    "SOLO",
    "Reasonix",
    "抖音热榜",
    "真实平台",
)


def test_user_trial_1_files_exist(repo_root: Path):
    base = repo_root / "novel-suite/user-trial-1"
    for name in TRIAL_FILES:
        assert (base / name).is_file(), name


def test_sample_chapter_fictional_and_length(repo_root: Path):
    text = (repo_root / "novel-suite/user-trial-1/sample_chapter.md").read_text(encoding="utf-8")
    for marker in FORBIDDEN_SAMPLE_MARKERS:
        assert marker not in text
    assert "虚构" in text or "原创" in text
    body = re.sub(r"#+.*", "", text)
    body = re.sub(r"[>\-\s`*]", "", body)
    char_count = len(re.findall(r"[\u4e00-\u9fff]", body))
    assert 800 <= char_count <= 1500, f"sample length {char_count} not in 800-1500"


def test_scenario_focuses_review_and_ip_drama(repo_root: Path):
    brief = (repo_root / "novel-suite/user-trial-1/scenario_brief.md").read_text(encoding="utf-8")
    runbook = (repo_root / "novel-suite/user-trial-1/trial_runbook.md").read_text(encoding="utf-8")
    assert "章节审稿" in brief
    assert "短剧" in brief or "IP 转短剧" in brief
    assert "章节审稿" in runbook
    assert "IP 转短剧" in runbook


def test_feedback_form_has_scores(repo_root: Path):
    form = (repo_root / "novel-suite/user-trial-1/user_feedback_form.md").read_text(encoding="utf-8")
    assert "容易上手" in form
    assert "付费" in form or "付费意愿" in form
    assert "最困惑" in form


def test_workbench_user_trial_entry(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    assert "UserTrial-1" in html
    assert "user-trial-guide" in html
    assert "btn-user-trial-guide" in html


def test_boundary_notice_blocked(repo_root: Path):
    notice = (repo_root / "novel-suite/user-trial-1/boundary_notice.md").read_text(encoding="utf-8")
    assert "commercial_release_allowed=false" in notice
    assert "verdict=blocked" in notice
    assert "不生成真实视频" in notice


def test_product_validate_includes_user_trial():
    result = run_product_validate()
    assert result.status == "ok"
    names = {c["name"] for c in result.details.get("checks", [])}
    assert "product.user-trial-1.README.md" in names


def test_commercial_still_blocked():
    result = run_commercial_release_candidate_validate()
    assert result.details.get("verdict") == "blocked"
