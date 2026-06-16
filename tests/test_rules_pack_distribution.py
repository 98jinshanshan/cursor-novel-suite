"""Rules Pack source layout and install-rules-packs.ps1."""

from __future__ import annotations

from pathlib import Path

from novel_suite.core.rules_pack import (
    AGENT_IDS,
    install_script_path,
    list_agent_sources,
    rules_packs_source_dir,
    validate_rules_pack_sources,
)

REPO = Path(__file__).resolve().parents[1]


def test_rules_pack_sources_complete():
    ok, errors = validate_rules_pack_sources()
    assert ok, errors


def test_list_agent_sources_six_agents():
    items = list_agent_sources()
    assert len(items) == len(AGENT_IDS)
    assert all(i["dir_ok"] and i["entry_ok"] for i in items)


def test_install_rules_packs_script_exists_and_documents_agents():
    script = install_script_path()
    assert script.is_file()
    text = script.read_text(encoding="utf-8")
    for agent in AGENT_IDS:
        assert agent in text
    assert "novel-suite\\rules-packs" in text or "novel-suite/rules-packs" in text
    assert "DryRun" in text


def test_rules_packs_readme_exists():
    readme = rules_packs_source_dir() / "README.md"
    assert readme.is_file()
