"""Novel Suite product-layer contract checks (novel-suite/core/)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from novel_suite.core.paths import suite_root

CONTRACT_STEMS = (
    "story_bible",
    "chapter_context",
    "scene_to_video",
    "asset_registry",
)


def novel_suite_root() -> Path:
    return suite_root() / "novel-suite"


def contracts_dir() -> Path:
    return novel_suite_root() / "core" / "contracts"


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _check_file(root: Path, path: Path, *, name: str) -> dict[str, Any]:
    ok = path.is_file()
    item: dict[str, Any] = {
        "name": name,
        "ok": ok,
        "path": _rel(root, path) if ok else str(path),
    }
    if not ok:
        item["error"] = "missing"
    return item


def _validate_json_schema_file(path: Path) -> tuple[bool, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return False, str(exc)
    if not isinstance(data, dict):
        return False, "root must be object"
    for key in ("$schema", "title", "type", "properties"):
        if key not in data:
            return False, f"missing {key}"
    try:
        import jsonschema

        jsonschema.Draft7Validator.check_schema(data)
    except ImportError:
        pass
    except jsonschema.SchemaError as exc:
        return False, str(exc)
    return True, None


def check_contract_files() -> list[dict[str, Any]]:
    """Check .schema.md and .schema.json for each contract stem."""
    root = suite_root()
    cdir = contracts_dir()
    checks: list[dict[str, Any]] = []
    for stem in CONTRACT_STEMS:
        md = cdir / f"{stem}.schema.md"
        js = cdir / f"{stem}.schema.json"
        checks.append(_check_file(root, md, name=f"contract.{stem}.md"))
        js_item = _check_file(root, js, name=f"contract.{stem}.json")
        if js.is_file():
            valid, err = _validate_json_schema_file(js)
            js_item["ok"] = js_item["ok"] and valid
            if err:
                js_item["error"] = err
        checks.append(js_item)
    return checks


def check_core_layer_paths() -> list[dict[str, Any]]:
    """Check novel-suite product layer files required by B1 doctor."""
    root = suite_root()
    ns = novel_suite_root()
    required_files = [
        ns / "README.md",
        ns / "PRODUCT_BOUNDARY.md",
        ns / "THIRD_PARTY_BOUNDARY.md",
        ns / "prompt-packs" / "PP-001_novel_project_init.md",
        ns / "prompt-packs" / "PP-002_chapter_review.md",
        ns / "prompt-packs" / "PP-003_novel_to_video.md",
        ns / "rules-packs" / "cursor" / "rules.md",
        ns / "rules-packs" / "codex" / "AGENTS.md",
    ]
    required_globs: list[tuple[str, Path]] = [
        ("gate.*.md", ns / "core" / "gates"),
        ("workflow.*.md", ns / "core" / "workflows"),
        ("adapter.ADAPTER_DISABLED", ns / "adapters"),
    ]
    checks: list[dict[str, Any]] = []
    for path in required_files:
        name = path.relative_to(ns).as_posix()
        checks.append(_check_file(root, path, name=f"novel-suite/{name}"))

    gates = ns / "core" / "gates"
    if gates.is_dir():
        for f in sorted(gates.glob("*.md")):
            checks.append(_check_file(root, f, name=f"gate.{f.stem}"))
    else:
        checks.append({"name": "gates.dir", "ok": False, "path": str(gates), "error": "missing"})

    workflows = ns / "core" / "workflows"
    if workflows.is_dir():
        for f in sorted(workflows.glob("*.md")):
            if f.name == "README.md":
                continue
            checks.append(_check_file(root, f, name=f"workflow.{f.stem}"))
    else:
        checks.append({"name": "workflows.dir", "ok": False, "path": str(workflows), "error": "missing"})

    for adapter in ("tts", "image-generation", "video-export", "platform-publishing"):
        p = ns / "adapters" / adapter / "ADAPTER_DISABLED_BY_DEFAULT.md"
        checks.append(_check_file(root, p, name=f"adapter.{adapter}.disabled"))

    return checks


def run_core_contract_checks() -> tuple[list[dict[str, Any]], int]:
    checks = check_contract_files() + check_core_layer_paths()
    failed = [c for c in checks if not c.get("ok")]
    return checks, 0 if not failed else 1
