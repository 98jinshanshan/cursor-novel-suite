"""Tests for S2 OpenClaw P0 document fixes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from novel_suite.core.commercialization import run_commercial_release_candidate_validate


def _read(repo_root: Path, rel: str) -> str:
    return (repo_root / rel).read_text(encoding="utf-8")


def test_fallback_in_safe_commands_and_openclaw_rules(repo_root: Path):
    safe = _read(repo_root, "novel-suite/solo-demo-15min/safe_commands.md")
    rules = _read(repo_root, "novel-suite/rules-packs/openclaw/rules.md")
    for text in (safe, rules):
        assert "-m novel_suite.cli" in text
        assert "PYTHONPATH" in text
        assert "未注册" in text or "PATH" in text


def test_o1_runbook_pp001_path_fixed(repo_root: Path):
    runbook = Path(
        r"G:\Users\admin\Documents\AI_Workspace_OS\02_Projects_项目区\Project_10_Workflow_OS\docs\80_阶段报告与验证记录\O1真实试用Runbook.md"
    )
    if not runbook.is_file():
        runbook = (
            repo_root.parent
            / "Users"
            / "admin"
            / "Documents"
            / "AI_Workspace_OS"
            / "02_Projects_项目区"
            / "Project_10_Workflow_OS"
            / "docs"
            / "80_阶段报告与验证记录"
            / "O1真实试用Runbook.md"
        )
    text = runbook.read_text(encoding="utf-8")
    assert "PP-001_小说立项" not in text
    assert "PP-001_novel_project_init.md" in text
    assert "pp001_first_run_guide.md" in text


def test_o2_o3_readme_red_lines(repo_root: Path):
    o2 = _read(repo_root, "novel-suite/solo-founder-freeze-self-check/README.md")
    o3 = _read(repo_root, "novel-suite/solo-founder-compliance-self-check/README.md")
    decl = _read(repo_root, "novel-suite/solo-founder-release-blocked-declaration/README.md")
    for text in (o2, o3, decl):
        assert "通过本自查 ≠ 商业发布" in text
        assert "blocker 关闭" in text
    assert "不是 release freeze" in o2 or "不是** release freeze" in o2.replace("**", "")
    assert "freeze candidate" in o2


def test_o2_o3_fallback_in_readme(repo_root: Path):
    for rel in (
        "novel-suite/solo-founder-freeze-self-check/README.md",
        "novel-suite/solo-founder-compliance-self-check/README.md",
        "novel-suite/solo-founder-release-blocked-declaration/README.md",
    ):
        assert "-m novel_suite.cli" in _read(repo_root, rel)


def test_pp001_top_boundary_banner(repo_root: Path):
    pp = _read(repo_root, "novel-suite/prompt-packs/PP-001_novel_project_init.md")
    assert "不是一键成书" in pp
    assert "不代表商业可用" in pp


def test_solo_demo_15min_entry_hint(repo_root: Path):
    readme = _read(repo_root, "novel-suite/solo-demo-15min/README.md")
    assert "首次 O1" in readme
    assert "demo_script_15min.md" in readme


def test_s1_s3_artifacts_exist(repo_root: Path):
    assert (repo_root / "novel-suite/openclaw-feedback-consolidation/s1_confirmed_revision_scope.md").is_file()
    assert (repo_root / "novel-suite/openclaw-feedback-consolidation/s3_retest_checklist.md").is_file()


def test_commercial_release_candidate_still_blocked():
    result = run_commercial_release_candidate_validate()
    assert result.status == "ok"
    assert result.details.get("verdict") == "blocked"


def test_cli_validates_after_p0_docs(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    for cmd in (
        ["openclaw-feedback-consolidation", "validate"],
        ["solo-founder-freeze-self-check", "validate"],
        ["solo-demo-15min", "validate"],
    ):
        r = subprocess.run(
            [sys.executable, "-m", "novel_suite.cli", *cmd, "--json"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env,
        )
        assert r.returncode == 0, r.stderr + r.stdout
        assert json.loads(r.stdout)["status"] == "ok"
