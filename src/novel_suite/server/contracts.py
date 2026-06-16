"""API contract paths and route registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from novel_suite.core.contracts import novel_suite_root

CONTRACT_REL = "server/api-contract.json"
WORKBENCH_REL = "ui-agent-workbench"
WORKBENCH_STATIC = "ui-agent-workbench/static/index.html"

REQUIRED_ROUTES: tuple[tuple[str, str], ...] = (
    ("GET", "/api/doctor"),
    ("GET", "/api/projects"),
    ("GET", "/api/projects/active"),
    ("POST", "/api/projects/use"),
    ("GET", "/api/projects/{slug}/status"),
    ("POST", "/api/agents/market-scan/run"),
    ("POST", "/api/agents/ip-to-short-drama/run"),
    ("POST", "/api/agents/novel-review/run"),
    ("POST", "/api/agents/realgen/run"),
    ("GET", "/api/artifacts"),
    ("GET", "/api/events"),
)


def api_contract_path() -> Path:
    return novel_suite_root() / "server" / "api-contract.json"


def workbench_root() -> Path:
    return novel_suite_root() / WORKBENCH_REL


def load_api_contract() -> dict[str, Any]:
    path = api_contract_path()
    return json.loads(path.read_text(encoding="utf-8"))


def contract_routes() -> list[dict[str, Any]]:
    data = load_api_contract()
    return list(data.get("routes", []))


def commercial_blocked_unchanged() -> bool:
    data = load_api_contract()
    return (
        data.get("commercial_release_allowed") is False
        and data.get("verdict") == "blocked"
    )
