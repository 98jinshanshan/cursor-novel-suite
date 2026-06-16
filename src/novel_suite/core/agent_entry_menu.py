"""Agent entry menu — UI Workbench menu manifest validate/list."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from novel_suite.core.errors import (
    AGENT_ENTRY_MENU_LIST_OK,
    AGENT_ENTRY_MENU_VALIDATE_FAIL,
    AGENT_ENTRY_MENU_VALIDATE_OK,
)
from novel_suite.core.contracts import novel_suite_root
from novel_suite.core.paths import suite_root
from novel_suite.core.result import error_result, ok_result, Result

_MENU_DIR = "agent-entry-menu"
_MANIFEST = "agent-ui-manifest.sample.json"

_MENU_ITEMS = (
    "menu_items/novel_create.md",
    "menu_items/novel_review.md",
    "menu_items/novel.review.json",
    "menu_items/ip_to_short_drama.md",
    "menu_items/ip.to_short_drama.json",
    "menu_items/asset_manage.md",
    "menu_items/agent_workflow.md",
    "menu_items/release_preflight.md",
    "menu_items/release.preflight.json",
)

_CORE_FILES = (
    "README.md",
    "agent-ui-manifest.schema.json",
    "agent-ui-manifest.sample.json",
    "capability_menu.md",
    "boundaries/generation_boundary.md",
    "boundaries/commercial_blocked_boundary.md",
    "ide_mappings/openclaw_menu.md",
    "ide_mappings/cursor_menu.md",
    "ide_mappings/roo_cline_menu.md",
    *_MENU_ITEMS,
)

_REQUIRED_IDS = (
    "novel.create",
    "novel.review",
    "ip.to_short_drama",
    "asset.manage",
    "agent.workflow",
    "release.preflight",
)


def agent_entry_menu_root() -> Path:
    return novel_suite_root() / _MENU_DIR


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def validate_agent_entry_menu() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    menu = agent_entry_menu_root()
    for name in _CORE_FILES:
        p = menu / name
        checks.append(
            {
                "name": f"agent_entry_menu.{name.replace('/', '.')}",
                "ok": p.is_file(),
                "path": _rel(root, p),
            }
        )
    manifest = menu / _MANIFEST
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            checks.append(
                {
                    "name": "agent_entry_menu.manifest_json",
                    "ok": False,
                    "path": _rel(root, manifest),
                    "details": [str(exc)],
                }
            )
            data = {}
        items = data.get("menu_items", [])
        ids = [it.get("id") for it in items if isinstance(it, dict)]
        checks.append(
            {
                "name": "agent_entry_menu.menu_item_count",
                "ok": len(items) == 6,
                "path": _rel(root, manifest),
            }
        )
        checks.append(
            {
                "name": "agent_entry_menu.required_ids",
                "ok": all(rid in ids for rid in _REQUIRED_IDS),
                "path": _rel(root, manifest),
            }
        )
        blocked_ok = True
        demo_runnable_ip = False
        demo_runnable_review = False
        release_preflight_ok = False
        for it in items:
            if not isinstance(it, dict):
                blocked_ok = False
                break
            if it.get("id") == "ip.to_short_drama" and it.get("status") == "demo-runnable":
                demo_runnable_ip = True
            if it.get("id") == "novel.review" and it.get("status") == "demo-runnable":
                demo_runnable_review = True
            if it.get("id") == "release.preflight" and it.get("status") == "planned-but-blocked":
                release_preflight_ok = True
            for field, val in (
                ("commercial_release_allowed", False),
                ("verdict", "blocked"),
                ("adapter_enabled", False),
                ("external_call_allowed", False),
            ):
                if it.get(field) != val:
                    blocked_ok = False
        checks.append(
            {
                "name": "agent_entry_menu.blocked_fields",
                "ok": blocked_ok,
                "path": _rel(root, manifest),
            }
        )
        checks.append(
            {
                "name": "agent_entry_menu.ip_to_short_drama_demo_runnable",
                "ok": demo_runnable_ip,
                "path": _rel(root, manifest),
            }
        )
        checks.append(
            {
                "name": "agent_entry_menu.novel_review_demo_runnable",
                "ok": demo_runnable_review,
                "path": _rel(root, manifest),
            }
        )
        checks.append(
            {
                "name": "agent_entry_menu.release_preflight_planned_but_blocked",
                "ok": release_preflight_ok,
                "path": _rel(root, manifest),
            }
        )
        for json_name, check_name, expected_status in (
            ("ip.to_short_drama.json", "ip_json_demo_runnable", "demo-runnable"),
            ("novel.review.json", "novel_review_json_demo_runnable", "demo-runnable"),
            ("release.preflight.json", "release_preflight_json_planned_but_blocked", "planned-but-blocked"),
        ):
            item_json = menu / f"menu_items/{json_name}"
            if item_json.is_file():
                try:
                    item_data = json.loads(item_json.read_text(encoding="utf-8"))
                    ok = (
                        item_data.get("status") == expected_status
                        and item_data.get("adapter_enabled") is False
                    )
                    if expected_status == "demo-runnable":
                        ok = ok and item_data.get("external_call_performed") is False
                    if json_name == "novel.review.json":
                        ok = ok and item_data.get("auto_rewrite_allowed") is False
                    if json_name == "release.preflight.json":
                        ok = (
                            ok
                            and item_data.get("commercial_release_allowed") is False
                            and item_data.get("verdict") == "blocked"
                            and item_data.get("external_call_allowed") is False
                        )
                    checks.append(
                        {
                            "name": f"agent_entry_menu.{check_name}",
                            "ok": ok,
                            "path": _rel(root, item_json),
                        }
                    )
                except json.JSONDecodeError:
                    checks.append(
                        {
                            "name": f"agent_entry_menu.{check_name}_parse",
                            "ok": False,
                            "path": _rel(root, item_json),
                        }
                    )
            else:
                checks.append(
                    {
                        "name": f"agent_entry_menu.{check_name}_file",
                        "ok": False,
                        "path": _rel(root, item_json),
                    }
                )
        if data.get("commercial_release_allowed") is not False:
            checks.append(
                {
                    "name": "agent_entry_menu.manifest_commercial_blocked",
                    "ok": False,
                    "path": _rel(root, manifest),
                }
            )
        else:
            checks.append(
                {
                    "name": "agent_entry_menu.manifest_commercial_blocked",
                    "ok": True,
                    "path": _rel(root, manifest),
                }
            )
    return checks


def run_agent_entry_menu_validate() -> Result:
    checks = validate_agent_entry_menu()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            AGENT_ENTRY_MENU_VALIDATE_FAIL,
            f"Agent entry menu: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        AGENT_ENTRY_MENU_VALIDATE_OK,
        "Agent entry menu validation passed (6 items; commercial blocked)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        menu_item_count=6,
        next_actions=["novel-suite agent-entry-menu list --json"],
    )


def run_agent_entry_menu_list() -> Result:
    manifest = agent_entry_menu_root() / _MANIFEST
    if not manifest.is_file():
        return error_result(
            AGENT_ENTRY_MENU_VALIDATE_FAIL,
            "agent-ui-manifest.sample.json missing",
            next_actions=["novel-suite agent-entry-menu validate --json"],
        )
    data = json.loads(manifest.read_text(encoding="utf-8"))
    items = data.get("menu_items", [])
    return ok_result(
        AGENT_ENTRY_MENU_LIST_OK,
        f"Listed {len(items)} agent menu item(s)",
        menu_items=items,
        commercial_release_allowed=False,
        verdict="blocked",
    )
