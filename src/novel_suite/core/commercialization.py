"""C6–C9 commercial preflight — read-only validation (no network)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from novel_suite.core import errors as E
from novel_suite.core.contracts import novel_suite_root
from novel_suite.core.paths import suite_root
from novel_suite.core.result import Result, error_result, ok_result

_ASSET_REQUIRED = frozenset(
    {
        "asset_id",
        "source_type",
        "license_status",
        "commercial_allowed",
        "upload_allowed",
        "review_status",
        "risk_level",
    }
)

_C6_DOCS = (
    "video-production/commercial-review/README.md",
    "video-production/commercial-review/sample-package-review.md",
    "video-production/commercial-review/asset-rights-review.md",
    "video-production/commercial-review/prompt-and-copy-originality-review.md",
    "video-production/commercial-review/adapter-risk-review.md",
    "video-production/commercial-review/quality-gate-review.md",
    "video-production/commercial-review/manual-review-checklist.md",
    "video-production/commercial-review/release-blockers.md",
    "video-production/commercial-review/sample-package-manifest.schema.json",
    "video-production/commercial-review/sample-package-manifest.sample.json",
)

_C7_DOCS = (
    "commercialization/README.md",
    "commercialization/sales-page-preflight.md",
    "commercialization/claims-allowed.md",
    "commercialization/claims-forbidden.md",
    "commercialization/delivery-package-design.md",
    "commercialization/delivery-package-checklist.md",
    "commercialization/pricing-and-offer-notes.md",
    "commercialization/buyer-onboarding-flow.md",
    "commercialization/refund-and-support-boundary.md",
    "commercialization/multi-ide-delivery-notes.md",
    "commercialization/prelaunch-gate.md",
)

_C8_DOCS = (
    "video-production/adapter-security-review/README.md",
    "video-production/adapter-security-review/adapter-activation-policy.md",
    "video-production/adapter-security-review/adapter-permission-levels.md",
    "video-production/adapter-security-review/adapter-threat-model.md",
    "video-production/adapter-security-review/adapter-data-flow-review.md",
    "video-production/adapter-security-review/adapter-secret-handling-policy.md",
    "video-production/adapter-security-review/adapter-network-policy.md",
    "video-production/adapter-security-review/adapter-local-process-policy.md",
    "video-production/adapter-security-review/adapter-output-sandbox-policy.md",
    "video-production/adapter-security-review/adapter-human-approval-checklist.md",
    "video-production/adapter-security-review/adapter-audit-log-requirements.md",
    "video-production/adapter-security-review/adapter-readiness-matrix.md",
)

_C9_DOCS = (
    "commercial-release-candidate/README.md",
    "commercial-release-candidate/candidate-package-scope.md",
    "commercial-release-candidate/candidate-package-manifest.schema.json",
    "commercial-release-candidate/candidate-package-manifest.sample.json",
    "commercial-release-candidate/package-file-inclusion-list.md",
    "commercial-release-candidate/package-file-exclusion-list.md",
    "commercial-release-candidate/final-release-gate.md",
    "commercial-release-candidate/final-legal-review-checklist.md",
    "commercial-release-candidate/final-technical-qc-checklist.md",
    "commercial-release-candidate/final-sales-claims-checklist.md",
    "commercial-release-candidate/final-demo-only-boundary.md",
    "commercial-release-candidate/known-blockers.md",
)

_HANDOFF_MANIFEST = (
    "video-production/examples/cold_case_echo_short_drama/handoff/asset_manifest.sample.json"
)

_ALLOWED_VERDICTS = frozenset({"demo_only", "blocked", "needs_manual_review"})


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _check_file(checks: list[dict[str, Any]], root: Path, ns: Path, rel: str) -> None:
    path = ns / Path(rel)
    checks.append(
        {
            "name": f"commercial.{rel.replace('/', '.')}",
            "ok": path.is_file(),
            "path": _rel(root, path) if path.is_file() else str(path),
            **({} if path.is_file() else {"error": "missing"}),
        }
    )


def _validate_asset_manifest_file(
    checks: list[dict[str, Any]],
    manifest_path: Path,
    *,
    check_name: str,
) -> None:
    if not manifest_path.is_file():
        checks.append({"name": check_name, "ok": False, "error": "missing"})
        return
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        checks.append({"name": check_name, "ok": False, "error": str(exc)})
        return

    ok = True
    details: list[str] = []
    if data.get("commercial_blocked") is not True:
        ok = False
        details.append("commercial_blocked must be true")
    for idx, asset in enumerate(data.get("assets", [])):
        missing = _ASSET_REQUIRED - set(asset.keys())
        if missing:
            ok = False
            details.append(f"asset[{idx}] missing: {sorted(missing)}")
    checks.append(
        {
            "name": check_name,
            "ok": ok,
            "path": str(manifest_path),
            **({"details": details} if details else {}),
        }
    )


def _validate_sample_manifest(checks: list[dict[str, Any]], manifest_path: Path) -> None:
    name = "commercial.sample_package_manifest"
    if not manifest_path.is_file():
        checks.append({"name": name, "ok": False, "error": "missing manifest"})
        return
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        checks.append({"name": name, "ok": False, "error": str(exc)})
        return

    ok = True
    details: list[str] = []
    if data.get("verdict") not in _ALLOWED_VERDICTS:
        ok = False
        details.append(f"invalid verdict: {data.get('verdict')!r}")
    if data.get("verdict") == "commercial_ready":
        ok = False
        details.append("commercial_ready is forbidden")
    if data.get("commercial_blocked") is not True:
        ok = False
        details.append("commercial_blocked must be true for sample package")
    policy = data.get("adapter_policy", {})
    if policy.get("enabled") is not False:
        ok = False
        details.append("adapter_policy.enabled must be false")
    if policy.get("external_call_performed") is not False:
        ok = False
        details.append("adapter_policy.external_call_performed must be false")

    for idx, asset in enumerate(data.get("assets", [])):
        missing = _ASSET_REQUIRED - set(asset.keys())
        if missing:
            ok = False
            details.append(f"asset[{idx}] missing: {sorted(missing)}")

    checks.append(
        {
            "name": name,
            "ok": ok,
            "path": str(manifest_path),
            **({"details": details} if details else {}),
        }
    )


def _validate_c8_readiness_matrix(checks: list[dict[str, Any]], ns: Path, root: Path) -> None:
    path = ns / "video-production" / "adapter-security-review" / "adapter-readiness-matrix.md"
    name = "commercial.c8.readiness_matrix"
    if not path.is_file():
        checks.append({"name": name, "ok": False, "error": "missing"})
        return
    text = path.read_text(encoding="utf-8")
    ok = "blocked_until_C8_review_and_user_confirmation" in text
    checks.append(
        {
            "name": name,
            "ok": ok,
            "path": _rel(root, path),
            **({} if ok else {"error": "missing blocked status phrase"}),
        }
    )


def _validate_candidate_manifest(checks: list[dict[str, Any]], manifest_path: Path) -> None:
    name = "commercial.candidate_package_manifest"
    if not manifest_path.is_file():
        checks.append({"name": name, "ok": False, "error": "missing"})
        return
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        checks.append({"name": name, "ok": False, "error": str(exc)})
        return

    ok = True
    details: list[str] = []
    if data.get("commercial_release_allowed") is not False:
        ok = False
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") not in ("blocked", "needs_manual_review", "demo_only"):
        ok = False
        details.append(f"invalid verdict: {data.get('verdict')!r}")
    if data.get("verdict") == "ready":
        ok = False
        details.append("verdict ready is forbidden in C9")
    if data.get("adapter_max_level") not in ("A0", "A1"):
        ok = False
        details.append("adapter_max_level must be A0 or A1")

    checks.append(
        {
            "name": name,
            "ok": ok,
            "path": str(manifest_path),
            **({"details": details} if details else {}),
        }
    )


def _validate_final_gate_doc(checks: list[dict[str, Any]], ns: Path, root: Path) -> None:
    path = ns / "commercial-release-candidate" / "final-release-gate.md"
    name = "commercial.c9.final_release_gate"
    if not path.is_file():
        checks.append({"name": name, "ok": False, "error": "missing"})
        return
    text = path.read_text(encoding="utf-8")
    ok = (
        "commercial_release_allowed: false" in text
        and "verdict: blocked" in text
    )
    checks.append(
        {
            "name": name,
            "ok": ok,
            "path": _rel(root, path),
            **({} if ok else {"error": "gate must declare blocked"}),
        }
    )


def validate_commercial_review() -> list[dict[str, Any]]:
    """Validate C6/C7/C8 docs, manifests, and handoff asset fields (read-only)."""
    checks: list[dict[str, Any]] = []
    root = suite_root()
    ns = novel_suite_root()
    gate_path = root / "COMMERCIAL_RELEASE_GATE.md"

    for rel in _C6_DOCS + _C7_DOCS + _C8_DOCS:
        _check_file(checks, root, ns, rel)

    _validate_sample_manifest(
        checks,
        ns / "video-production" / "commercial-review" / "sample-package-manifest.sample.json",
    )
    _validate_asset_manifest_file(
        checks,
        ns / Path(_HANDOFF_MANIFEST),
        check_name="commercial.handoff_asset_manifest",
    )
    _validate_c8_readiness_matrix(checks, ns, root)

    blockers = ns / "video-production" / "commercial-review" / "release-blockers.md"
    if blockers.is_file():
        text = blockers.read_text(encoding="utf-8")
        for phrase in ("商业发布", "仍不允许", "B01", "B05-resolved"):
            checks.append(
                {
                    "name": f"commercial.release_blockers.contains_{phrase}",
                    "ok": phrase in text,
                    "path": _rel(root, blockers),
                }
            )
    else:
        checks.append(
            {"name": "commercial.release_blockers", "ok": False, "error": "missing"}
        )

    forbidden = ns / "commercialization" / "claims-forbidden.md"
    if forbidden.is_file():
        text = forbidden.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "commercial.claims_forbidden.no_commercial_ready_claim",
                "ok": "已可商业发布" in text or "商业发布" in text,
                "path": _rel(root, forbidden),
            }
        )

    if gate_path.is_file():
        gate = gate_path.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "commercial.release_gate.not_allowed",
                "ok": "不允许" in gate,
                "path": _rel(root, gate_path),
            }
        )

    return checks


def validate_commercial_release_candidate() -> list[dict[str, Any]]:
    """Validate C9 commercial release candidate package docs and gate (read-only)."""
    checks: list[dict[str, Any]] = []
    root = suite_root()
    ns = novel_suite_root()

    for rel in _C9_DOCS:
        _check_file(checks, root, ns, rel)

    _validate_candidate_manifest(
        checks,
        ns / "commercial-release-candidate" / "candidate-package-manifest.sample.json",
    )
    _validate_final_gate_doc(checks, ns, root)

    known = ns / "commercial-release-candidate" / "known-blockers.md"
    if known.is_file():
        text = known.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "commercial.c9.known_blockers.b01_open",
                "ok": "B01" in text and "open" in text.lower(),
                "path": _rel(root, known),
            }
        )

    return checks


def run_commercial_review_validate() -> Result:
    checks = validate_commercial_review()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.COMMERCIAL_REVIEW_VALIDATE_FAIL,
            f"Commercial review: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.COMMERCIAL_REVIEW_VALIDATE_OK,
        "Commercial preflight validation passed (C6/C7/C8; legal review still pending)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="demo_only",
        next_actions=[
            "novel-suite commercial-review validate --json",
            "novel-suite commercial-release-candidate validate --json",
        ],
    )


def run_commercial_release_candidate_validate() -> Result:
    checks = validate_commercial_release_candidate()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.CANDIDATE_GATE_VALIDATE_FAIL,
            f"Release candidate gate: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
            verdict="blocked",
        )
    return ok_result(
        E.CANDIDATE_GATE_VALIDATE_OK,
        "Release candidate gate validation passed (verdict remains blocked)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        adapter_max_level="A1",
    )
