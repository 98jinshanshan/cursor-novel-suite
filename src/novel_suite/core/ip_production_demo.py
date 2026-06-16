"""IP production demo — offline ip.to_short_drama runner (no adapter/video)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from novel_suite.core.contracts import novel_suite_root
from novel_suite.core.errors import (
    IP_PRODUCTION_DEMO_RUN_OK,
    IP_PRODUCTION_DEMO_VALIDATE_FAIL,
    IP_PRODUCTION_DEMO_VALIDATE_OK,
)
from novel_suite.core.paths import suite_root
from novel_suite.core.result import artifact, error_result, ok_result, Result

_DEMO_DIR = "ip-production-demo"
_MANIFEST = "ip-production-demo.sample.json"
_EXAMPLE_BASE = "novel-suite/video-production/examples/cold_case_echo_short_drama"

# Logical artifact names → paths under suite root (reuse cold_case where equivalent)
_ARTIFACT_PATHS: dict[str, str] = {
    "chapter_review.md": "novel-suite/ip-production-demo/chapter_review.md",
    "story_beats.md": "novel-suite/ip-production-demo/story_beats.md",
    "scene_package.json": f"{_EXAMPLE_BASE}/scene_package.sample.json",
    "shot_list.csv": f"{_EXAMPLE_BASE}/shot_list.sample.csv",
    "asset_requirements.md": "novel-suite/ip-production-demo/asset_requirements.md",
    "timeline_package.json": f"{_EXAMPLE_BASE}/timeline_package.sample.json",
    "risk_check.md": "novel-suite/ip-production-demo/risk_check.md",
    "handoff_manifest.json": "novel-suite/ip-production-demo/handoff_manifest.json",
}

_CORE_FILES = (
    "README.md",
    "ip-production-demo.schema.json",
    _MANIFEST,
    "chapter_review.md",
    "story_beats.md",
    "asset_requirements.md",
    "risk_check.md",
    "handoff_manifest.json",
)


def ip_production_demo_root() -> Path:
    return novel_suite_root() / _DEMO_DIR


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def artifact_paths() -> dict[str, Path]:
    root = suite_root()
    return {name: root / rel for name, rel in _ARTIFACT_PATHS.items()}


def validate_ip_production_demo() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    demo = ip_production_demo_root()
    for name in _CORE_FILES:
        p = demo / name
        checks.append(
            {
                "name": f"ip_production_demo.{name.replace('/', '.')}",
                "ok": p.is_file(),
                "path": _rel(root, p),
            }
        )
    for logical, rel in _ARTIFACT_PATHS.items():
        p = root / rel
        checks.append(
            {
                "name": f"ip_production_demo.artifact.{logical}",
                "ok": p.is_file(),
                "path": _rel(root, p),
            }
        )
    manifest = demo / _MANIFEST
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            blocked = (
                data.get("commercial_release_allowed") is False
                and data.get("verdict") == "blocked"
                and data.get("adapter_enabled") is False
                and data.get("external_call_performed") is False
            )
            checks.append(
                {
                    "name": "ip_production_demo.manifest_blocked",
                    "ok": blocked,
                    "path": _rel(root, manifest),
                }
            )
        except json.JSONDecodeError as exc:
            checks.append(
                {
                    "name": "ip_production_demo.manifest_json",
                    "ok": False,
                    "path": _rel(root, manifest),
                    "details": [str(exc)],
                }
            )
    return checks


def run_ip_production_demo_validate() -> Result:
    checks = validate_ip_production_demo()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            IP_PRODUCTION_DEMO_VALIDATE_FAIL,
            f"IP production demo: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
            verdict="blocked",
        )
    return ok_result(
        IP_PRODUCTION_DEMO_VALIDATE_OK,
        "IP production demo validation passed (8 artifacts; commercial blocked)",
        checks=checks,
        artifact_count=len(_ARTIFACT_PATHS),
        commercial_release_allowed=False,
        verdict="blocked",
        adapter_enabled=False,
        external_call_performed=False,
        next_actions=[
            "novel-suite ip-production-demo run --json",
            "POST /api/agents/ip-to-short-drama/run",
        ],
    )


def run_ip_production_demo() -> Result:
    validate = run_ip_production_demo_validate()
    if validate.status != "ok":
        return validate

    root = suite_root()
    arts: list[dict[str, Any]] = []
    for logical, rel in _ARTIFACT_PATHS.items():
        p = root / rel
        arts.append(
            artifact(
                _rel(root, p),
                kind="file",
                label=logical,
            )
        )

    return ok_result(
        IP_PRODUCTION_DEMO_RUN_OK,
        "IP to short drama demo package assembled (offline; no video/adapter)",
        artifacts=arts,
        package_id="cold_case_echo_short_drama",
        adapter_enabled=False,
        external_call_performed=False,
        commercial_release_allowed=False,
        verdict="blocked",
        next_actions=[
            "novel-suite product read --category vp_examples --name cold_case_echo_short_drama --json",
            "Review handoff_manifest.json — manual execution only",
        ],
        blocker=["commercial_blocked", "adapter_disabled"],
    )
