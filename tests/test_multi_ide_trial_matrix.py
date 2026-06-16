"""B6 multi-IDE trial matrix — rules pack distribution and trial cards."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from novel_suite.core.rules_pack import AGENT_ENTRY_FILES, AGENT_IDS

REPO = Path(__file__).resolve().parents[1]
MATRIX = REPO / "docs" / "NOVEL_SUITE_B6_IDE_TRIAL_MATRIX.md"
TRIAL_DIR = REPO / "novel-suite" / "trial-cards"
AGENT_RULES = REPO / ".agent-rules"
INSTALL_PS1 = REPO / "platforms" / "install-rules-packs.ps1"

TRIAL_CARD_FILES = {
    "cursor": "cursor.md",
    "codex": "codex.md",
    "trae-cn": "trae-cn.md",
    "qoder": "qoder.md",
    "openclaw": "openclaw.md",
    "generic-agent": "generic-agent.md",
}

REQUIRED_CARD_PHRASES = (
    "doctor --core-contracts",
    "product validate",
    "product list",
    "默认关闭",
    "人工确认",
)

GLOBAL_IDE_PATH_PATTERNS = (
    r"%USERPROFILE%\\\.cursor",
    r"%USERPROFILE%\\\.codex",
    r"%USERPROFILE%\\\.qoder",
    r"\.cursor\\rules",
)


def test_matrix_doc_exists_and_lists_six_environments():
    assert MATRIX.is_file()
    text = MATRIX.read_text(encoding="utf-8")
    for name in ("Cursor", "Codex", "TRAE CN", "Qoder", "OpenClaw", "Generic Agent"):
        assert name in text, name


def test_trial_cards_readme_and_six_cards_exist():
    assert (TRIAL_DIR / "README.md").is_file()
    for agent, filename in TRIAL_CARD_FILES.items():
        path = TRIAL_DIR / filename
        assert path.is_file(), agent


@pytest.mark.parametrize("agent,filename", list(TRIAL_CARD_FILES.items()))
def test_trial_card_required_phrases(agent: str, filename: str):
    text = (TRIAL_DIR / filename).read_text(encoding="utf-8")
    for phrase in REQUIRED_CARD_PHRASES:
        assert phrase in text, f"{agent}: missing {phrase!r}"


@pytest.mark.parametrize("agent", AGENT_IDS)
def test_rules_pack_source_entry_exists(agent: str):
    entry = AGENT_ENTRY_FILES[agent]
    path = REPO / "novel-suite" / "rules-packs" / agent / entry
    assert path.is_file(), f"missing {path}"


@pytest.mark.parametrize("agent", AGENT_IDS)
def test_rules_pack_boundary_semantics(agent: str):
    entry = AGENT_ENTRY_FILES[agent]
    text = (REPO / "novel-suite" / "rules-packs" / agent / entry).read_text(encoding="utf-8")
    assert "默认关闭" in text or "默认关闭" in text.lower()
    assert "人工确认" in text
    assert "product" in text.lower() or "doctor" in text.lower()
    assert "SOLO" in text or "Reasonix" in text or "外部" in text


def test_install_rules_packs_dry_run(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-File",
            str(INSTALL_PS1),
            "-DryRun",
            "-Agents",
            "cursor,codex,trae-cn,qoder,openclaw,generic-agent",
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "6 agent(s) validated" in r.stdout or "validated" in r.stdout.lower()
    for pattern in GLOBAL_IDE_PATH_PATTERNS:
        assert not re.search(pattern, r.stdout, re.IGNORECASE)


def test_agent_rules_copy_distribution(repo_root: Path):
    """Ensure仓内 .agent-rules copy exists (run install if missing in fresh checkout)."""
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    missing = [
        a
        for a in AGENT_IDS
        if not (AGENT_RULES / a / AGENT_ENTRY_FILES[a]).is_file()
    ]
    if missing:
        r = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-File",
                str(INSTALL_PS1),
                "-Copy",
                "-DestRoot",
                ".agent-rules",
                "-Agents",
                "cursor,codex,trae-cn,qoder,openclaw,generic-agent",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        assert r.returncode == 0, r.stderr + r.stdout

    for agent in AGENT_IDS:
        dest_dir = AGENT_RULES / agent
        entry = AGENT_ENTRY_FILES[agent]
        assert dest_dir.is_dir(), agent
        assert (dest_dir / entry).is_file(), agent
        assert (dest_dir / "README.md").is_file(), agent


def test_no_user_global_paths_in_install_script():
    text = INSTALL_PS1.read_text(encoding="utf-8")
    assert "UseIdeDirs" in text
    assert "$env:USERPROFILE" not in text
    assert "%USERPROFILE%" not in text


def test_commercial_release_gate_still_blocks_release(repo_root: Path):
    text = (repo_root / "COMMERCIAL_RELEASE_GATE.md").read_text(encoding="utf-8")
    assert "不允许" in text or "待法律" in text
