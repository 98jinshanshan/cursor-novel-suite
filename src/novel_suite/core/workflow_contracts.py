"""F2 Workflow Contract — read-only validation (no runner, no network)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from novel_suite.core import errors as E
from novel_suite.core.contracts import novel_suite_root
from novel_suite.core.paths import suite_root
from novel_suite.core.result import Result, error_result, ok_result

_CONTRACTS_DIR = "workflow-contracts"
_EXAMPLES_DIR = "examples"

_CORE_FIELDS = frozenset(
    {
        "contract_version",
        "workflow_id",
        "workflow_type",
        "permission_level",
        "external_calls",
        "commercial_boundary",
        "trace_fields",
    }
)

_SAMPLE_CONTRACTS = (
    "chapter_writing.contract.json",
    "chapter_review.contract.json",
    "novel_to_video.contract.json",
    "novel_to_short_drama.contract.json",
    "adapter_dry_run.contract.json",
    "commercial_preflight.contract.json",
    "commercial_release_candidate.contract.json",
)

_SCHEMA_FILES = (
    "workflow_contract.schema.json",
    "workflow_contract_minimal.schema.json",
    "workflow_contract.schema.md",
    "README.md",
)


def workflow_contracts_root() -> Path:
    return novel_suite_root() / _CONTRACTS_DIR


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _validate_contract_file(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]

    missing = _CORE_FIELDS - set(data.keys())
    if missing:
        details.append(f"missing core fields: {sorted(missing)}")
    if not (data.get("permission_level") or "").strip():
        details.append("permission_level empty")

    ext = data.get("external_calls", {})
    if ext.get("allowed") is not False:
        details.append("external_calls.allowed must be false")

    comm = data.get("commercial_boundary", {})
    if comm.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")

    if path.name == "commercial_release_candidate.contract.json":
        if comm.get("verdict") != "blocked":
            details.append("release candidate verdict must be blocked")
        blockers = comm.get("blockers", {})
        for bid in ("B01", "B02", "B03", "B04"):
            if blockers.get(bid) != "open":
                details.append(f"blocker {bid} must be open")
        if blockers.get("B05") not in ("resolved-demo-only", "resolved-demo-manifest-fields-only"):
            details.append("B05 must be resolved-demo-only")

    if path.name == "adapter_dry_run.contract.json":
        if data.get("adapter_level") != "A1":
            details.append("adapter_dry_run must be A1")

    trace = data.get("trace_fields", [])
    for required in ("workflow_id",):
        if "trace_fields" in data and not trace:
            details.append("trace_fields must not be empty")

    return not details, details


def validate_workflow_contracts() -> list[dict[str, Any]]:
    """Validate F2 schema files and sample contracts (read-only)."""
    checks: list[dict[str, Any]] = []
    root = suite_root()
    wc = workflow_contracts_root()

    if not wc.is_dir():
        checks.append({"name": "workflow_contracts.dir", "ok": False, "error": "missing"})
        return checks

    for name in _SCHEMA_FILES:
        path = wc / name
        checks.append(
            {
                "name": f"workflow_contracts.{name}",
                "ok": path.is_file(),
                "path": _rel(root, path) if path.is_file() else str(path),
            }
        )

    examples = wc / _EXAMPLES_DIR
    for name in _SAMPLE_CONTRACTS:
        path = examples / name
        if not path.is_file():
            checks.append(
                {"name": f"workflow_contracts.example.{name}", "ok": False, "error": "missing"}
            )
            continue
        ok, details = _validate_contract_file(path)
        checks.append(
            {
                "name": f"workflow_contracts.example.{name}",
                "ok": ok,
                "path": _rel(root, path),
                **({"details": details} if details else {}),
            }
        )

    return checks


def run_workflow_contract_validate() -> Result:
    checks = validate_workflow_contracts()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.WORKFLOW_CONTRACT_VALIDATE_FAIL,
            f"Workflow contracts: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.WORKFLOW_CONTRACT_VALIDATE_OK,
        "Workflow contract validation passed (schema + 7 samples; no runner)",
        checks=checks,
        commercial_release_allowed=False,
        sample_count=len(_SAMPLE_CONTRACTS),
        next_actions=["novel-suite workflow-contract validate --json"],
    )


def read_workflow_contract_example(name: str) -> dict[str, Any]:
    """Read a sample contract by stem name (e.g. chapter_writing)."""
    safe = (name or "").strip().replace(".contract.json", "")
    if not safe or ".." in safe or "/" in safe:
        raise ValueError(f"{E.WORKFLOW_CONTRACT_INVALID_NAME}: {name!r}")
    path = workflow_contracts_root() / _EXAMPLES_DIR / f"{safe}.contract.json"
    if not path.is_file():
        raise FileNotFoundError(f"{E.WORKFLOW_CONTRACT_NOT_FOUND}: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
