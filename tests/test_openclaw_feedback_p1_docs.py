"""Tests for U1/U2 OpenClaw light document fixes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core.commercialization import run_commercial_release_candidate_validate

RUNBOOK = Path(
    r"G:\Users\admin\Documents\AI_Workspace_OS\02_Projects_项目区\Project_10_Workflow_OS\docs\80_阶段报告与验证记录\O1真实试用Runbook.md"
)


def _read(repo_root: Path, rel: str) -> str:
    return (repo_root / rel).read_text(encoding="utf-8")


def test_o1_runbook_no_legacy_pp001_path(repo_root: Path):
    assert RUNBOOK.is_file()
    text = RUNBOOK.read_text(encoding="utf-8")
    assert "PP-001_小说立项" not in text
    assert "PP-001_novel_project_init.md" in text
    assert "pp001_first_run_guide.md" in text


def test_o2_o3_allow_vs_prohibit_tables(repo_root: Path):
    for rel in (
        "novel-suite/solo-founder-freeze-self-check/README.md",
        "novel-suite/solo-founder-compliance-self-check/README.md",
        "novel-suite/solo-founder-release-blocked-declaration/README.md",
    ):
        text = _read(repo_root, rel)
        assert "允许继续" in text
        assert "仍禁止" in text
        assert "本地 demo" in text
        assert "商业发布" in text
        assert "tag/zip/release" in text


def test_safe_commands_dual_fallback_scenarios(repo_root: Path):
    safe = _read(repo_root, "novel-suite/solo-demo-15min/safe_commands.md")
    assert "已安装可执行入口" in safe
    assert "未注册 PATH" in safe
    assert ".venv\\Scripts\\python.exe" in safe or ".venv/Scripts/python.exe" in safe
    assert "-m novel_suite.cli" in safe


def test_openclaw_rules_dual_fallback(repo_root: Path):
    rules = _read(repo_root, "novel-suite/rules-packs/openclaw/rules.md")
    assert "已安装可执行入口" in rules
    assert "未注册 PATH" in rules
    assert ".venv\\Scripts\\python.exe" in rules or ".venv/Scripts/python.exe" in rules


def test_s3_retest_checklist_u_items(repo_root: Path):
    text = _read(repo_root, "novel-suite/openclaw-feedback-consolidation/s3_retest_checklist.md")
    assert "PP-001_小说立项" in text  # checklist says must NOT contain
    assert "允许继续 vs 仍禁止" in text


def test_commercial_release_candidate_still_blocked():
    result = run_commercial_release_candidate_validate()
    assert result.status == "ok"
    assert result.details.get("verdict") == "blocked"


def test_cli_product_validate_ok(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "product", "validate", "--json"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert json.loads(r.stdout)["status"] == "ok"
