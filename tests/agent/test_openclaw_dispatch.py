"""OpenClaw skill package is present and documents JSON contract."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skills" / "openclaw-novel-suite" / "SKILL.md"
CONTRACT = REPO / "skills" / "openclaw-novel-suite" / "references" / "result-contract.md"


def test_openclaw_skill_exists():
    assert SKILL.is_file()
    text = SKILL.read_text(encoding="utf-8")
    assert "novel-suite doctor --json" in text
    assert "next_actions" in text.lower() or "result-contract" in text


def test_result_contract_reference():
    assert CONTRACT.is_file()
    assert "PHASE0_NOT_COMPLETE" in CONTRACT.read_text(encoding="utf-8")
