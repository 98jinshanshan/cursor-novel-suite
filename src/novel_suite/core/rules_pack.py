"""Rules Pack distribution metadata (novel-suite/rules-packs/)."""

from __future__ import annotations

from pathlib import Path

from novel_suite.core.paths import suite_root

AGENT_IDS = (
    "cursor",
    "codex",
    "trae-cn",
    "qoder",
    "openclaw",
    "generic-agent",
)

AGENT_ENTRY_FILES: dict[str, str] = {
    "cursor": "rules.md",
    "codex": "AGENTS.md",
    "trae-cn": "rules.md",
    "qoder": "rules.md",
    "openclaw": "rules.md",
    "generic-agent": "rules.md",
}


def rules_packs_source_dir() -> Path:
    return suite_root() / "novel-suite" / "rules-packs"


def install_script_path() -> Path:
    return suite_root() / "platforms" / "install-rules-packs.ps1"


def list_agent_sources() -> list[dict[str, str | bool]]:
    src = rules_packs_source_dir()
    out: list[dict[str, str | bool]] = []
    for agent in AGENT_IDS:
        entry = AGENT_ENTRY_FILES[agent]
        agent_dir = src / agent
        entry_path = agent_dir / entry
        out.append(
            {
                "agent": agent,
                "dir": str(agent_dir),
                "entry": entry,
                "dir_ok": agent_dir.is_dir(),
                "entry_ok": entry_path.is_file(),
            }
        )
    return out


def validate_rules_pack_sources() -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not rules_packs_source_dir().is_dir():
        errors.append(f"missing rules-packs dir: {rules_packs_source_dir()}")
    script = install_script_path()
    if not script.is_file():
        errors.append(f"missing install script: {script}")
    for item in list_agent_sources():
        if not item["dir_ok"]:
            errors.append(f"missing agent dir: {item['agent']}")
        elif not item["entry_ok"]:
            errors.append(f"missing entry {item['entry']} for {item['agent']}")
    return len(errors) == 0, errors
