"""G1/G2/G3 delivery, demo, and legal review packages — read-only validation."""



from __future__ import annotations



import json

from pathlib import Path

from typing import Any



from novel_suite.core import errors as E

from novel_suite.core.contracts import novel_suite_root

from novel_suite.core.paths import suite_root

from novel_suite.core.result import Result, error_result, ok_result



_G1_DIR = "delivery-hub"

_G2_DIR = "demo-roadmap"

_G3_DIR = "legal-release-review"



_G1_CORE = (

    "README.md",

    "start-here.md",

    "delivery-map.md",

    "capability-index.md",

    "safe-demo-path.md",

    "cold-start-checklist.md",

    "role-based-onboarding.md",

    "ide-entrypoints.md",

    "what-is-included.md",

    "what-is-not-included.md",

    "known-blockers-summary.md",

    "glossary.md",

    "delivery-hub.schema.json",

    "delivery-hub.sample.json",

)



_G2_CORE = (

    "README.md",

    "demo_scope.md",

    "demo_storyline.md",

    "demo_script_15min.md",

    "demo_script_45min.md",

    "demo_checklist.md",

    "manual_trial_plan.md",

    "demo_artifact_list.md",

    "demo_success_criteria.md",

    "demo_failure_playbook.md",

    "demo_claims_boundary.md",

    "demo_no_external_call_checklist.md",

    "demo_feedback_capture.md",

    "demo-roadmap.schema.json",

    "demo-roadmap.sample.json",

)



_G3_CORE = (

    "README.md",

    "legal_review_scope.md",

    "third_party_notices_review_checklist.md",

    "license_review_checklist.md",

    "asset_rights_review_checklist.md",

    "prompt_pack_originality_review.md",

    "sales_claims_legal_review.md",

    "adapter_legal_review.md",

    "platform_publish_review.md",

    "commercial_release_decision_record.md",

    "release_approval_required_signatures.md",

    "blocker_closure_policy.md",

    "legal-release-review.schema.json",

    "legal-release-review.sample.json",

)





def delivery_hub_root() -> Path:

    return novel_suite_root() / _G1_DIR





def demo_roadmap_root() -> Path:

    return novel_suite_root() / _G2_DIR





def legal_release_review_root() -> Path:

    return novel_suite_root() / _G3_DIR





def _rel(root: Path, path: Path) -> str:

    try:

        return path.resolve().relative_to(root.resolve()).as_posix()

    except ValueError:

        return str(path.resolve())





def _validate_blocked_manifest(data: dict[str, Any], *, source: str) -> tuple[bool, list[str]]:

    details: list[str] = []

    if data.get("commercial_release_allowed") is not False:

        details.append(f"{source}: commercial_release_allowed must be false")

    if data.get("verdict") != "blocked":

        details.append(f"{source}: verdict must be blocked")

    return not details, details





def _validate_g1_sample(path: Path) -> tuple[bool, list[str]]:

    details: list[str] = []

    try:

        data = json.loads(path.read_text(encoding="utf-8"))

    except json.JSONDecodeError as exc:

        return False, [str(exc)]

    ok, errs = _validate_blocked_manifest(data, source="delivery-hub.sample")

    details.extend(errs)

    if data.get("safe_demo_only") is not True:

        details.append("safe_demo_only must be true")

    roles = set(data.get("roles", []))

    if not {"creator", "developer", "reviewer", "trial_user"} <= roles:

        details.append("roles must include creator, developer, reviewer, trial_user")

    return not details, details





def _validate_g2_sample(path: Path) -> tuple[bool, list[str]]:

    details: list[str] = []

    try:

        data = json.loads(path.read_text(encoding="utf-8"))

    except json.JSONDecodeError as exc:

        return False, [str(exc)]

    ok, errs = _validate_blocked_manifest(data, source="demo-roadmap.sample")

    details.extend(errs)

    if data.get("external_calls_allowed") is not False:

        details.append("external_calls_allowed must be false")

    claims = data.get("claims_forbidden", [])

    if len(claims) < 4:

        details.append("claims_forbidden must have at least 4 entries")

    return not details, details





def _validate_g3_sample(path: Path) -> tuple[bool, list[str]]:

    details: list[str] = []

    try:

        data = json.loads(path.read_text(encoding="utf-8"))

    except json.JSONDecodeError as exc:

        return False, [str(exc)]

    ok, errs = _validate_blocked_manifest(data, source="legal-release-review.sample")

    details.extend(errs)

    if data.get("legal_conclusion_auto_generated") is not False:

        details.append("legal_conclusion_auto_generated must be false")

    sigs = data.get("signatures_required", [])

    if len(sigs) < 2:

        details.append("signatures_required must list at least 2 roles")

    return not details, details





def _append_dir_checks(

    checks: list[dict[str, Any]],

    root: Path,

    base: Path,

    prefix: str,

    files: tuple[str, ...],

) -> None:

    if not base.is_dir():

        checks.append({"name": f"{prefix}.dir", "ok": False, "error": "missing"})

        return

    for name in files:

        path = base / name

        checks.append(

            {

                "name": f"{prefix}.{name.replace('/', '.')}",

                "ok": path.is_file(),

                "path": _rel(root, path) if path.is_file() else str(path),

            }

        )





def validate_delivery_hub() -> list[dict[str, Any]]:

    checks: list[dict[str, Any]] = []

    root = suite_root()

    g1 = delivery_hub_root()

    _append_dir_checks(checks, root, g1, "delivery_hub", _G1_CORE)



    sample = g1 / "delivery-hub.sample.json"

    if sample.is_file():

        ok, details = _validate_g1_sample(sample)

        checks.append(

            {

                "name": "delivery_hub.delivery-hub.sample.json",

                "ok": ok,

                "path": _rel(root, sample),

                **({"details": details} if details else {}),

            }

        )



    blockers = g1 / "known-blockers-summary.md"

    if blockers.is_file():

        text = blockers.read_text(encoding="utf-8")

        checks.append(

            {

                "name": "delivery_hub.known_blockers_present",

                "ok": "B01" in text and "B05" in text and "blocked" in text,

                "path": _rel(root, blockers),

            }

        )



    return checks





def validate_demo_roadmap() -> list[dict[str, Any]]:

    checks: list[dict[str, Any]] = []

    root = suite_root()

    g2 = demo_roadmap_root()

    _append_dir_checks(checks, root, g2, "demo_roadmap", _G2_CORE)



    sample = g2 / "demo-roadmap.sample.json"

    if sample.is_file():

        ok, details = _validate_g2_sample(sample)

        checks.append(

            {

                "name": "demo_roadmap.demo-roadmap.sample.json",

                "ok": ok,

                "path": _rel(root, sample),

                **({"details": details} if details else {}),

            }

        )



    checklist = g2 / "demo_no_external_call_checklist.md"

    checks.append(

        {

            "name": "demo_roadmap.demo_no_external_call_checklist",

            "ok": checklist.is_file(),

            "path": _rel(root, checklist) if checklist.is_file() else str(checklist),

        }

    )



    return checks





def validate_legal_release_review() -> list[dict[str, Any]]:

    checks: list[dict[str, Any]] = []

    root = suite_root()

    g3 = legal_release_review_root()

    _append_dir_checks(checks, root, g3, "legal_release_review", _G3_CORE)



    sample = g3 / "legal-release-review.sample.json"

    if sample.is_file():

        ok, details = _validate_g3_sample(sample)

        checks.append(

            {

                "name": "legal_release_review.legal-release-review.sample.json",

                "ok": ok,

                "path": _rel(root, sample),

                **({"details": details} if details else {}),

            }

        )



    sigs = g3 / "release_approval_required_signatures.md"

    if sigs.is_file():

        text = sigs.read_text(encoding="utf-8")

        checks.append(

            {

                "name": "legal_release_review.signatures_required_doc",

                "ok": "签字" in text or "signature" in text.lower(),

                "path": _rel(root, sigs),

            }

        )



    policy = g3 / "blocker_closure_policy.md"

    if policy.is_file():

        text = policy.read_text(encoding="utf-8")

        for bid in ("B01", "B02", "B03", "B04", "B05"):

            checks.append(

                {

                    "name": f"legal_release_review.blocker_policy.{bid}",

                    "ok": bid in text,

                    "path": _rel(root, policy),

                }

            )



    return checks





def run_delivery_hub_validate() -> Result:

    checks = validate_delivery_hub()

    failed = [c for c in checks if not c.get("ok")]

    if failed:

        return error_result(

            E.DELIVERY_HUB_VALIDATE_FAIL,

            f"Delivery hub: {len(failed)} check(s) failed",

            required=[c["name"] for c in failed],

            checks=checks,

            commercial_release_allowed=False,

        )

    return ok_result(

        E.DELIVERY_HUB_VALIDATE_OK,

        "Delivery hub validation passed (G1 index; not commercial release)",

        checks=checks,

        commercial_release_allowed=False,

        verdict="blocked",

        next_actions=["novel-suite delivery-hub validate --json"],

    )





def run_demo_roadmap_validate() -> Result:

    checks = validate_demo_roadmap()

    failed = [c for c in checks if not c.get("ok")]

    if failed:

        return error_result(

            E.DEMO_ROADMAP_VALIDATE_FAIL,

            f"Demo roadmap: {len(failed)} check(s) failed",

            required=[c["name"] for c in failed],

            checks=checks,

            commercial_release_allowed=False,

        )

    return ok_result(

        E.DEMO_ROADMAP_VALIDATE_OK,

        "Demo roadmap validation passed (G2 scripts; no external demo)",

        checks=checks,

        commercial_release_allowed=False,

        verdict="blocked",

        next_actions=["novel-suite demo-roadmap validate --json"],

    )





def run_legal_release_review_validate() -> Result:

    checks = validate_legal_release_review()

    failed = [c for c in checks if not c.get("ok")]

    if failed:

        return error_result(

            E.LEGAL_RELEASE_REVIEW_VALIDATE_FAIL,

            f"Legal release review: {len(failed)} check(s) failed",

            required=[c["name"] for c in failed],

            checks=checks,

            commercial_release_allowed=False,

        )

    return ok_result(

        E.LEGAL_RELEASE_REVIEW_VALIDATE_OK,

        "Legal release review validation passed (G3 checklists; manual signatures required)",

        checks=checks,

        commercial_release_allowed=False,

        verdict="blocked",

        legal_conclusion_auto_generated=False,

        next_actions=["novel-suite legal-release-review validate --json"],

    )


_H1_DIR = "human-trial-runbook"
_H2_DIR = "package-freeze-candidate"
_H3_PKT_DIR = "legal-review-packet"

_H1_CORE = (
    "README.md",
    "trial_scope.md",
    "participant_roles.md",
    "pre_trial_checklist.md",
    "trial_session_script_30min.md",
    "trial_session_script_90min.md",
    "observer_note_template.md",
    "participant_feedback_form.md",
    "feedback_submission_local_only.md",
    "trial_artifact_checklist.md",
    "trial_failure_triage.md",
    "no_external_call_attestation.md",
    "privacy_and_data_boundary.md",
    "human-trial-runbook.schema.json",
    "human-trial-runbook.sample.json",
)

_H2_CORE = (
    "README.md",
    "freeze_scope.md",
    "version_naming_policy.md",
    "package_layers.md",
    "included_files_manifest.md",
    "excluded_files_manifest.md",
    "freeze_candidate_manifest.schema.json",
    "freeze_candidate_manifest.sample.json",
    "checksum_manifest_policy.md",
    "reproducible_packaging_notes.md",
    "package_review_checklist.md",
    "rollback_and_unfreeze_policy.md",
    "freeze_blockers.md",
    "demo_only_distribution_boundary.md",
)

_H3_PKT_CORE = (
    "README.md",
    "review_packet_cover.md",
    "legal_questions_for_counsel.md",
    "rights_chain_summary_template.md",
    "third_party_dependency_summary.md",
    "license_risk_summary.md",
    "adapter_execution_risk_summary.md",
    "sales_claims_review_packet.md",
    "demo_script_legal_review_packet.md",
    "data_privacy_review_packet.md",
    "platform_policy_review_packet.md",
    "unresolved_questions.md",
    "required_signatures_packet.md",
    "legal-review-packet.schema.json",
    "legal-review-packet.sample.json",
)


def human_trial_runbook_root() -> Path:
    return novel_suite_root() / _H1_DIR


def package_freeze_candidate_root() -> Path:
    return novel_suite_root() / _H2_DIR


def legal_review_packet_root() -> Path:
    return novel_suite_root() / _H3_PKT_DIR


def _validate_h1_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("external_call_performed") is not False:
        details.append("external_call_performed must be false")
    if data.get("telemetry_collected") is not False:
        details.append("telemetry_collected must be false")
    if data.get("feedback_storage") != "local_only":
        details.append("feedback_storage must be local_only")
    return not details, details


def _validate_h2_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    if data.get("package_status") != "freeze_candidate_only":
        details.append("package_status must be freeze_candidate_only")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    if data.get("legal_review_required") is not True:
        details.append("legal_review_required must be true")
    ver = data.get("package_version", "")
    if "demo-freeze-candidate" not in ver:
        details.append("package_version must contain demo-freeze-candidate")
    return not details, details


def _validate_h3_packet_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("legal_conclusion_auto_generated") is not False:
        details.append("legal_conclusion_auto_generated must be false")
    if data.get("requires_human_or_legal_review") is not True:
        details.append("requires_human_or_legal_review must be true")
    blockers = data.get("blockers_for_counsel", {})
    for bid in ("B01", "B02", "B03", "B04", "B05"):
        if bid not in blockers:
            details.append(f"blockers_for_counsel missing {bid}")
    return not details, details


def validate_human_trial_runbook() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    h1 = human_trial_runbook_root()
    _append_dir_checks(checks, root, h1, "human_trial_runbook", _H1_CORE)
    sample = h1 / "human-trial-runbook.sample.json"
    if sample.is_file():
        ok, details = _validate_h1_sample(sample)
        checks.append(
            {
                "name": "human_trial_runbook.human-trial-runbook.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    privacy = h1 / "privacy_and_data_boundary.md"
    if privacy.is_file():
        text = privacy.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "human_trial_runbook.no_telemetry_doc",
                "ok": "telemetry" in text.lower(),
                "path": _rel(root, privacy),
            }
        )
    return checks


def validate_package_freeze_candidate() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    h2 = package_freeze_candidate_root()
    _append_dir_checks(checks, root, h2, "package_freeze_candidate", _H2_CORE)
    sample = h2 / "freeze_candidate_manifest.sample.json"
    if sample.is_file():
        ok, details = _validate_h2_sample(sample)
        checks.append(
            {
                "name": "package_freeze_candidate.freeze_candidate_manifest.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    excluded = h2 / "excluded_files_manifest.md"
    if excluded.is_file():
        text = excluded.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "package_freeze_candidate.excludes_secrets",
                "ok": ".env" in text or "密钥" in text,
                "path": _rel(root, excluded),
            }
        )
    return checks


def validate_legal_review_packet() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    h3 = legal_review_packet_root()
    _append_dir_checks(checks, root, h3, "legal_review_packet", _H3_PKT_CORE)
    sample = h3 / "legal-review-packet.sample.json"
    if sample.is_file():
        ok, details = _validate_h3_packet_sample(sample)
        checks.append(
            {
                "name": "legal_review_packet.legal-review-packet.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    cover = h3 / "review_packet_cover.md"
    if cover.is_file():
        text = cover.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "legal_review_packet.not_legal_opinion",
                "ok": "非" in text or "not" in text.lower(),
                "path": _rel(root, cover),
            }
        )
    return checks


def run_human_trial_runbook_validate() -> Result:
    checks = validate_human_trial_runbook()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.HUMAN_TRIAL_RUNBOOK_VALIDATE_FAIL,
            f"Human trial runbook: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.HUMAN_TRIAL_RUNBOOK_VALIDATE_OK,
        "Human trial runbook validation passed (local feedback only; no telemetry)",
        checks=checks,
        commercial_release_allowed=False,
        telemetry_collected=False,
        next_actions=["novel-suite human-trial-runbook validate --json"],
    )


def run_package_freeze_candidate_validate() -> Result:
    checks = validate_package_freeze_candidate()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.PACKAGE_FREEZE_CANDIDATE_VALIDATE_FAIL,
            f"Package freeze candidate: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.PACKAGE_FREEZE_CANDIDATE_VALIDATE_OK,
        "Package freeze candidate validation passed (freeze_candidate_only; no zip/release)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        package_status="freeze_candidate_only",
        next_actions=["novel-suite package-freeze-candidate validate --json"],
    )


def run_legal_review_packet_validate() -> Result:
    checks = validate_legal_review_packet()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.LEGAL_REVIEW_PACKET_VALIDATE_FAIL,
            f"Legal review packet: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.LEGAL_REVIEW_PACKET_VALIDATE_OK,
        "Legal review packet validation passed (materials only; not legal advice)",
        checks=checks,
        commercial_release_allowed=False,
        legal_conclusion_auto_generated=False,
        requires_human_or_legal_review=True,
        next_actions=["novel-suite legal-review-packet validate --json"],
    )


_I1_DIR = "trial-results-intake"
_I2_DIR = "freeze-version-alignment"
_I3_DIR = "legal-review-response-intake"

_I1_CORE = (
    "README.md",
    "intake_scope.md",
    "trial_session_record_template.md",
    "participant_feedback_intake_template.md",
    "observer_notes_intake_template.md",
    "feedback_classification_mapping.md",
    "issue_triage_rules.md",
    "revision_recommendation_template.md",
    "local_storage_policy.md",
    "pii_redaction_checklist.md",
    "no_telemetry_attestation.md",
    "trial-results-intake.schema.json",
    "trial-results-intake.sample.json",
)

_I2_CORE = (
    "README.md",
    "alignment_scope.md",
    "version_alignment_record.md",
    "manifest_alignment_checklist.md",
    "file_inventory_snapshot_template.md",
    "checksum_record_template.md",
    "git_tag_recommendation.md",
    "no_release_attestation.md",
    "package_diff_review_template.md",
    "freeze_unfreeze_decision_template.md",
    "freeze-version-alignment.schema.json",
    "freeze-version-alignment.sample.json",
)

_I3_CORE = (
    "README.md",
    "response_intake_scope.md",
    "counsel_response_record_template.md",
    "blocker_response_mapping.md",
    "unresolved_risk_register.md",
    "signature_record_template.md",
    "legal_decision_change_request_template.md",
    "release_gate_change_request_template.md",
    "no_auto_approval_policy.md",
    "legal-review-response-intake.schema.json",
    "legal-review-response-intake.sample.json",
)


def trial_results_intake_root() -> Path:
    return novel_suite_root() / _I1_DIR


def freeze_version_alignment_root() -> Path:
    return novel_suite_root() / _I2_DIR


def legal_review_response_intake_root() -> Path:
    return novel_suite_root() / _I3_DIR


def _validate_i1_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field, val in (
        ("telemetry_collected", False),
        ("external_call_performed", False),
        ("commercial_release_allowed", False),
        ("revision_auto_applied", False),
    ):
        if data.get(field) is not val:
            details.append(f"{field} must be {val}")
    if data.get("feedback_storage") != "local_only":
        details.append("feedback_storage must be local_only")
    return not details, details


def _validate_i2_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    if data.get("recommended_version") != "0.1.0-demo-freeze-candidate":
        details.append("recommended_version must be 0.1.0-demo-freeze-candidate")
    for field in ("tag_created", "zip_created", "release_created"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    return not details, details


def _validate_i3_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    if data.get("legal_conclusion_auto_generated") is not False:
        details.append("legal_conclusion_auto_generated must be false")
    if data.get("auto_blocker_closure") is not False:
        details.append("auto_blocker_closure must be false")
    if data.get("requires_human_signature") is not True:
        details.append("requires_human_signature must be true")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    blockers = data.get("blocker_responses", {})
    for bid in ("B01", "B02", "B03", "B04", "B05"):
        if bid not in blockers:
            details.append(f"blocker_responses missing {bid}")
    return not details, details


def validate_trial_results_intake() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    i1 = trial_results_intake_root()
    _append_dir_checks(checks, root, i1, "trial_results_intake", _I1_CORE)
    sample = i1 / "trial-results-intake.sample.json"
    if sample.is_file():
        ok, details = _validate_i1_sample(sample)
        checks.append(
            {
                "name": "trial_results_intake.trial-results-intake.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    return checks


def validate_freeze_version_alignment() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    i2 = freeze_version_alignment_root()
    _append_dir_checks(checks, root, i2, "freeze_version_alignment", _I2_CORE)
    sample = i2 / "freeze-version-alignment.sample.json"
    if sample.is_file():
        ok, details = _validate_i2_sample(sample)
        checks.append(
            {
                "name": "freeze_version_alignment.freeze-version-alignment.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    tag_doc = i2 / "git_tag_recommendation.md"
    if tag_doc.is_file():
        text = tag_doc.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "freeze_version_alignment.no_auto_git_tag",
                "ok": "不得" in text or "must not" in text.lower() or "false" in text,
                "path": _rel(root, tag_doc),
            }
        )
    return checks


def validate_legal_review_response_intake() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    i3 = legal_review_response_intake_root()
    _append_dir_checks(checks, root, i3, "legal_review_response_intake", _I3_CORE)
    sample = i3 / "legal-review-response-intake.sample.json"
    if sample.is_file():
        ok, details = _validate_i3_sample(sample)
        checks.append(
            {
                "name": "legal_review_response_intake.legal-review-response-intake.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    policy = i3 / "no_auto_approval_policy.md"
    if policy.is_file():
        text = policy.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "legal_review_response_intake.no_auto_approval_doc",
                "ok": "auto_blocker_closure" in text,
                "path": _rel(root, policy),
            }
        )
    return checks


def run_trial_results_intake_validate() -> Result:
    checks = validate_trial_results_intake()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.TRIAL_RESULTS_INTAKE_VALIDATE_FAIL,
            f"Trial results intake: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.TRIAL_RESULTS_INTAKE_VALIDATE_OK,
        "Trial results intake validation passed (local only; no auto revision)",
        checks=checks,
        commercial_release_allowed=False,
        telemetry_collected=False,
        next_actions=["novel-suite trial-results-intake validate --json"],
    )


def run_freeze_version_alignment_validate() -> Result:
    checks = validate_freeze_version_alignment()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.FREEZE_VERSION_ALIGNMENT_VALIDATE_FAIL,
            f"Freeze version alignment: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.FREEZE_VERSION_ALIGNMENT_VALIDATE_OK,
        "Freeze version alignment validation passed (no tag/zip/release)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        tag_created=False,
        zip_created=False,
        release_created=False,
        next_actions=["novel-suite freeze-version-alignment validate --json"],
    )


def run_legal_review_response_intake_validate() -> Result:
    checks = validate_legal_review_response_intake()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.LEGAL_REVIEW_RESPONSE_INTAKE_VALIDATE_FAIL,
            f"Legal review response intake: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.LEGAL_REVIEW_RESPONSE_INTAKE_VALIDATE_OK,
        "Legal review response intake validation passed (no auto blocker closure)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        legal_conclusion_auto_generated=False,
        auto_blocker_closure=False,
        next_actions=["novel-suite legal-review-response-intake validate --json"],
    )


_J1_DIR = "first-trial-session-kit"
_J2_DIR = "freeze-review-meeting"
_J3_DIR = "legal-review-meeting"

_J1_CORE = (
    "README.md",
    "session_scope.md",
    "facilitator_script.md",
    "participant_instruction_sheet.md",
    "trial_record_blank.md",
    "feedback_form_blank.md",
    "observer_notes_blank.md",
    "pii_redaction_before_storage.md",
    "local_tmp_folder_layout.md",
    "trial_completion_checklist.md",
    "no_fake_feedback_policy.md",
    "first-trial-session-kit.schema.json",
    "first-trial-session-kit.sample.json",
)

_J2_CORE = (
    "README.md",
    "meeting_scope.md",
    "agenda.md",
    "version_alignment_decision_blank.md",
    "manifest_review_blank.md",
    "checksum_review_blank.md",
    "manual_git_tag_decision_blank.md",
    "no_release_attestation_blank.md",
    "freeze_decision_outcomes.md",
    "post_meeting_actions.md",
    "freeze-review-meeting.schema.json",
    "freeze-review-meeting.sample.json",
)

_J3_CORE = (
    "README.md",
    "meeting_scope.md",
    "counsel_review_agenda.md",
    "blocker_review_table_blank.md",
    "counsel_response_summary_blank.md",
    "change_request_draft_blank.md",
    "signature_collection_blank.md",
    "unresolved_risk_decision_blank.md",
    "no_auto_blocker_closure_policy.md",
    "post_legal_review_actions.md",
    "legal-review-meeting.schema.json",
    "legal-review-meeting.sample.json",
)


def first_trial_session_kit_root() -> Path:
    return novel_suite_root() / _J1_DIR


def freeze_review_meeting_root() -> Path:
    return novel_suite_root() / _J2_DIR


def legal_review_meeting_root() -> Path:
    return novel_suite_root() / _J3_DIR


def _validate_j1_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field in ("trial_executed", "fake_feedback_generated", "telemetry_collected", "external_call_performed"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("feedback_storage") != "local_only":
        details.append("feedback_storage must be local_only")
    return not details, details


def _validate_j2_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    if data.get("meeting_held") is not False:
        details.append("meeting_held must be false")
    for field in ("tag_created", "zip_created", "release_created"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    return not details, details


def _validate_j3_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    if data.get("meeting_held") is not False:
        details.append("meeting_held must be false")
    if data.get("legal_conclusion_auto_generated") is not False:
        details.append("legal_conclusion_auto_generated must be false")
    if data.get("auto_blocker_closure") is not False:
        details.append("auto_blocker_closure must be false")
    if data.get("requires_human_signature") is not True:
        details.append("requires_human_signature must be true")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    blockers = data.get("blocker_discussion", {})
    for bid in ("B01", "B02", "B03", "B04", "B05"):
        if bid not in blockers:
            details.append(f"blocker_discussion missing {bid}")
    return not details, details


def validate_first_trial_session_kit() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    j1 = first_trial_session_kit_root()
    _append_dir_checks(checks, root, j1, "first_trial_session_kit", _J1_CORE)
    sample = j1 / "first-trial-session-kit.sample.json"
    if sample.is_file():
        ok, details = _validate_j1_sample(sample)
        checks.append(
            {
                "name": "first_trial_session_kit.first-trial-session-kit.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    policy = j1 / "no_fake_feedback_policy.md"
    if policy.is_file():
        text = policy.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "first_trial_session_kit.no_fake_feedback_policy",
                "ok": "fake_feedback" in text,
                "path": _rel(root, policy),
            }
        )
    tmp_readme = root / ".tmp" / "novel-suite-j" / "trial-results-intake" / "README.md"
    checks.append(
        {
            "name": "first_trial_session_kit.tmp_readme",
            "ok": tmp_readme.is_file(),
            "path": _rel(root, tmp_readme),
        }
    )
    return checks


def validate_freeze_review_meeting() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    j2 = freeze_review_meeting_root()
    _append_dir_checks(checks, root, j2, "freeze_review_meeting", _J2_CORE)
    sample = j2 / "freeze-review-meeting.sample.json"
    if sample.is_file():
        ok, details = _validate_j2_sample(sample)
        checks.append(
            {
                "name": "freeze_review_meeting.freeze-review-meeting.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    tag_doc = j2 / "manual_git_tag_decision_blank.md"
    if tag_doc.is_file():
        text = tag_doc.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "freeze_review_meeting.no_auto_git_tag",
                "ok": "不得" in text or "must not" in text.lower() or "不执行" in text,
                "path": _rel(root, tag_doc),
            }
        )
    return checks


def validate_legal_review_meeting() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    j3 = legal_review_meeting_root()
    _append_dir_checks(checks, root, j3, "legal_review_meeting", _J3_CORE)
    sample = j3 / "legal-review-meeting.sample.json"
    if sample.is_file():
        ok, details = _validate_j3_sample(sample)
        checks.append(
            {
                "name": "legal_review_meeting.legal-review-meeting.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    policy = j3 / "no_auto_blocker_closure_policy.md"
    if policy.is_file():
        text = policy.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "legal_review_meeting.no_auto_blocker_closure_doc",
                "ok": "auto_blocker_closure" in text,
                "path": _rel(root, policy),
            }
        )
    return checks


def run_first_trial_session_kit_validate() -> Result:
    checks = validate_first_trial_session_kit()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.FIRST_TRIAL_SESSION_KIT_VALIDATE_FAIL,
            f"First trial session kit: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.FIRST_TRIAL_SESSION_KIT_VALIDATE_OK,
        "First trial session kit validation passed (blank forms; no fake feedback)",
        checks=checks,
        commercial_release_allowed=False,
        trial_executed=False,
        fake_feedback_generated=False,
        telemetry_collected=False,
        next_actions=["novel-suite first-trial-session-kit validate --json"],
    )


def run_freeze_review_meeting_validate() -> Result:
    checks = validate_freeze_review_meeting()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.FREEZE_REVIEW_MEETING_VALIDATE_FAIL,
            f"Freeze review meeting: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.FREEZE_REVIEW_MEETING_VALIDATE_OK,
        "Freeze review meeting validation passed (no tag/zip/release)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        meeting_held=False,
        tag_created=False,
        zip_created=False,
        release_created=False,
        next_actions=["novel-suite freeze-review-meeting validate --json"],
    )


def run_legal_review_meeting_validate() -> Result:
    checks = validate_legal_review_meeting()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.LEGAL_REVIEW_MEETING_VALIDATE_FAIL,
            f"Legal review meeting: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.LEGAL_REVIEW_MEETING_VALIDATE_OK,
        "Legal review meeting validation passed (materials only; no blocker closure)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        meeting_held=False,
        legal_conclusion_auto_generated=False,
        auto_blocker_closure=False,
        next_actions=["novel-suite legal-review-meeting validate --json"],
    )


_K1_DIR = "trial-result-review"
_K2_DIR = "freeze-decision-record"
_K3_DIR = "legal-decision-record"

_K1_CORE = (
    "README.md",
    "review_scope.md",
    "raw_input_location_policy.md",
    "pii_redaction_result_checklist.md",
    "trial_result_summary_template.md",
    "feedback_theme_extraction_template.md",
    "issue_priority_matrix.md",
    "revision_backlog_update_template.md",
    "trial_result_decision_record.md",
    "no_auto_product_change_policy.md",
    "trial-result-review.schema.json",
    "trial-result-review.sample.json",
)

_K2_CORE = (
    "README.md",
    "decision_scope.md",
    "meeting_result_record_template.md",
    "manifest_review_result_template.md",
    "checksum_review_result_template.md",
    "manual_tag_decision_record_template.md",
    "no_agent_tag_policy.md",
    "release_not_created_attestation.md",
    "freeze_decision_change_request_template.md",
    "next_manual_actions_template.md",
    "freeze-decision-record.schema.json",
    "freeze-decision-record.sample.json",
)

_K3_CORE = (
    "README.md",
    "decision_scope.md",
    "counsel_response_intake_template.md",
    "blocker_status_recommendation_template.md",
    "legal_risk_register_update_template.md",
    "release_gate_change_request_template.md",
    "signature_evidence_record_template.md",
    "no_auto_legal_conclusion_policy.md",
    "no_auto_blocker_closure_policy.md",
    "next_review_board_actions_template.md",
    "legal-decision-record.schema.json",
    "legal-decision-record.sample.json",
)


def trial_result_review_root() -> Path:
    return novel_suite_root() / _K1_DIR


def freeze_decision_record_root() -> Path:
    return novel_suite_root() / _K2_DIR


def legal_decision_record_root() -> Path:
    return novel_suite_root() / _K3_DIR


def _validate_k1_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field in (
        "trial_executed_by_human",
        "trial_results_available",
        "fake_feedback_generated",
        "telemetry_collected",
        "revision_auto_applied",
    ):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    return not details, details


def _validate_k2_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field in ("meeting_held_by_human", "meeting_result_available"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    for field in ("tag_created", "zip_created", "release_created"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    return not details, details


def _validate_k3_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field in ("legal_meeting_held_by_human", "legal_meeting_result_available"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("legal_conclusion_auto_generated") is not False:
        details.append("legal_conclusion_auto_generated must be false")
    if data.get("auto_blocker_closure") is not False:
        details.append("auto_blocker_closure must be false")
    if data.get("requires_human_signature") is not True:
        details.append("requires_human_signature must be true")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    recs = data.get("blocker_recommendations", {})
    for bid in ("B01", "B02", "B03", "B04", "B05"):
        if bid not in recs:
            details.append(f"blocker_recommendations missing {bid}")
    return not details, details


def validate_trial_result_review() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    k1 = trial_result_review_root()
    _append_dir_checks(checks, root, k1, "trial_result_review", _K1_CORE)
    sample = k1 / "trial-result-review.sample.json"
    if sample.is_file():
        ok, details = _validate_k1_sample(sample)
        checks.append(
            {
                "name": "trial_result_review.trial-result-review.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    policy = k1 / "no_auto_product_change_policy.md"
    if policy.is_file():
        text = policy.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "trial_result_review.no_auto_product_change",
                "ok": "revision_auto_applied" in text,
                "path": _rel(root, policy),
            }
        )
    tmp_readme = root / ".tmp" / "novel-suite-k" / "trial-result-review" / "README.md"
    checks.append(
        {
            "name": "trial_result_review.tmp_k_readme",
            "ok": tmp_readme.is_file(),
            "path": _rel(root, tmp_readme),
        }
    )
    return checks


def validate_freeze_decision_record() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    k2 = freeze_decision_record_root()
    _append_dir_checks(checks, root, k2, "freeze_decision_record", _K2_CORE)
    sample = k2 / "freeze-decision-record.sample.json"
    if sample.is_file():
        ok, details = _validate_k2_sample(sample)
        checks.append(
            {
                "name": "freeze_decision_record.freeze-decision-record.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    tag_policy = k2 / "no_agent_tag_policy.md"
    if tag_policy.is_file():
        text = tag_policy.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "freeze_decision_record.no_agent_tag_policy",
                "ok": "tag" in text.lower(),
                "path": _rel(root, tag_policy),
            }
        )
    return checks


def validate_legal_decision_record() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    k3 = legal_decision_record_root()
    _append_dir_checks(checks, root, k3, "legal_decision_record", _K3_CORE)
    sample = k3 / "legal-decision-record.sample.json"
    if sample.is_file():
        ok, details = _validate_k3_sample(sample)
        checks.append(
            {
                "name": "legal_decision_record.legal-decision-record.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    for doc_name, check_key in (
        ("no_auto_blocker_closure_policy.md", "auto_blocker_closure"),
        ("no_auto_legal_conclusion_policy.md", "legal_conclusion"),
    ):
        doc = k3 / doc_name
        if doc.is_file():
            text = doc.read_text(encoding="utf-8")
            checks.append(
                {
                    "name": f"legal_decision_record.{doc_name}",
                    "ok": check_key in text,
                    "path": _rel(root, doc),
                }
            )
    return checks


def run_trial_result_review_validate() -> Result:
    checks = validate_trial_result_review()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.TRIAL_RESULT_REVIEW_VALIDATE_FAIL,
            f"Trial result review: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.TRIAL_RESULT_REVIEW_VALIDATE_OK,
        "Trial result review validation passed (no fake feedback; no auto revision)",
        checks=checks,
        commercial_release_allowed=False,
        trial_results_available=False,
        fake_feedback_generated=False,
        revision_auto_applied=False,
        next_actions=["novel-suite trial-result-review validate --json"],
    )


def run_freeze_decision_record_validate() -> Result:
    checks = validate_freeze_decision_record()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.FREEZE_DECISION_RECORD_VALIDATE_FAIL,
            f"Freeze decision record: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.FREEZE_DECISION_RECORD_VALIDATE_OK,
        "Freeze decision record validation passed (no tag/zip/release)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        meeting_result_available=False,
        tag_created=False,
        zip_created=False,
        release_created=False,
        next_actions=["novel-suite freeze-decision-record validate --json"],
    )


def run_legal_decision_record_validate() -> Result:
    checks = validate_legal_decision_record()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.LEGAL_DECISION_RECORD_VALIDATE_FAIL,
            f"Legal decision record: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.LEGAL_DECISION_RECORD_VALIDATE_OK,
        "Legal decision record validation passed (no auto blocker closure)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        legal_meeting_result_available=False,
        legal_conclusion_auto_generated=False,
        auto_blocker_closure=False,
        next_actions=["novel-suite legal-decision-record validate --json"],
    )


_L1_DIR = "trial-result-import-preflight"
_L2_DIR = "freeze-decision-import-preflight"
_L3_DIR = "legal-decision-import-preflight"

_L1_CORE = (
    "README.md",
    "preflight_scope.md",
    "allowed_input_locations.md",
    "disallowed_input_policy.md",
    "pii_redaction_preflight_checklist.md",
    "feedback_schema_preflight.md",
    "backlog_mapping_preflight.md",
    "import_rejection_reasons.md",
    "no_auto_revision_policy.md",
    "import_decision_record_template.md",
    "trial-result-import-preflight.schema.json",
    "trial-result-import-preflight.sample.json",
)

_L2_CORE = (
    "README.md",
    "preflight_scope.md",
    "allowed_input_locations.md",
    "version_record_preflight.md",
    "manifest_checksum_preflight.md",
    "manual_tag_decision_preflight.md",
    "release_creation_prohibited.md",
    "import_rejection_reasons.md",
    "freeze_change_request_template.md",
    "import_decision_record_template.md",
    "freeze-decision-import-preflight.schema.json",
    "freeze-decision-import-preflight.sample.json",
)

_L3_CORE = (
    "README.md",
    "preflight_scope.md",
    "allowed_input_locations.md",
    "counsel_response_preflight.md",
    "signature_evidence_preflight.md",
    "blocker_change_request_preflight.md",
    "release_gate_change_preflight.md",
    "legal_opinion_boundary.md",
    "import_rejection_reasons.md",
    "import_decision_record_template.md",
    "legal-decision-import-preflight.schema.json",
    "legal-decision-import-preflight.sample.json",
)


def trial_result_import_preflight_root() -> Path:
    return novel_suite_root() / _L1_DIR


def freeze_decision_import_preflight_root() -> Path:
    return novel_suite_root() / _L2_DIR


def legal_decision_import_preflight_root() -> Path:
    return novel_suite_root() / _L3_DIR


def _validate_l1_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field in (
        "input_results_available",
        "preflight_passed",
        "pii_redaction_verified",
        "telemetry_collected",
        "revision_auto_applied",
    ):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    return not details, details


def _validate_l2_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field in ("input_decision_available", "preflight_passed"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    for field in ("tag_created", "zip_created", "release_created"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    return not details, details


def _validate_l3_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field in ("input_legal_decision_available", "preflight_passed"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("legal_conclusion_auto_generated") is not False:
        details.append("legal_conclusion_auto_generated must be false")
    if data.get("auto_blocker_closure") is not False:
        details.append("auto_blocker_closure must be false")
    if data.get("requires_human_signature") is not True:
        details.append("requires_human_signature must be true")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    return not details, details


def validate_trial_result_import_preflight() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    l1 = trial_result_import_preflight_root()
    _append_dir_checks(checks, root, l1, "trial_result_import_preflight", _L1_CORE)
    sample = l1 / "trial-result-import-preflight.sample.json"
    if sample.is_file():
        ok, details = _validate_l1_sample(sample)
        checks.append(
            {
                "name": "trial_result_import_preflight.trial-result-import-preflight.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    policy = l1 / "no_auto_revision_policy.md"
    if policy.is_file():
        text = policy.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "trial_result_import_preflight.no_auto_revision",
                "ok": "revision_auto_applied" in text,
                "path": _rel(root, policy),
            }
        )
    disallowed = l1 / "disallowed_input_policy.md"
    if disallowed.is_file():
        text = disallowed.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "trial_result_import_preflight.disallowed_input",
                "ok": "私密" in text or "private" in text.lower() or "拒收" in text,
                "path": _rel(root, disallowed),
            }
        )
    tmp_readme = root / ".tmp" / "novel-suite-l" / "trial-result-import-preflight" / "README.md"
    checks.append(
        {
            "name": "trial_result_import_preflight.tmp_l_readme",
            "ok": tmp_readme.is_file(),
            "path": _rel(root, tmp_readme),
        }
    )
    return checks


def validate_freeze_decision_import_preflight() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    l2 = freeze_decision_import_preflight_root()
    _append_dir_checks(checks, root, l2, "freeze_decision_import_preflight", _L2_CORE)
    sample = l2 / "freeze-decision-import-preflight.sample.json"
    if sample.is_file():
        ok, details = _validate_l2_sample(sample)
        checks.append(
            {
                "name": "freeze_decision_import_preflight.freeze-decision-import-preflight.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    tag_doc = l2 / "manual_tag_decision_preflight.md"
    if tag_doc.is_file():
        text = tag_doc.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "freeze_decision_import_preflight.no_auto_git_tag",
                "ok": "不得" in text or "must not" in text.lower() or "不执行" in text,
                "path": _rel(root, tag_doc),
            }
        )
    return checks


def validate_legal_decision_import_preflight() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    l3 = legal_decision_import_preflight_root()
    _append_dir_checks(checks, root, l3, "legal_decision_import_preflight", _L3_CORE)
    sample = l3 / "legal-decision-import-preflight.sample.json"
    if sample.is_file():
        ok, details = _validate_l3_sample(sample)
        checks.append(
            {
                "name": "legal_decision_import_preflight.legal-decision-import-preflight.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    boundary = l3 / "legal_opinion_boundary.md"
    if boundary.is_file():
        text = boundary.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "legal_decision_import_preflight.legal_opinion_boundary",
                "ok": "legal_conclusion" in text or "非" in text,
                "path": _rel(root, boundary),
            }
        )
    for doc_name in ("blocker_change_request_preflight.md",):
        doc = l3 / doc_name
        if doc.is_file():
            text = doc.read_text(encoding="utf-8")
            checks.append(
                {
                    "name": f"legal_decision_import_preflight.{doc_name}",
                    "ok": "auto_blocker_closure" in text,
                    "path": _rel(root, doc),
                }
            )
    return checks


def run_trial_result_import_preflight_validate() -> Result:
    checks = validate_trial_result_import_preflight()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.TRIAL_RESULT_IMPORT_PREFLIGHT_VALIDATE_FAIL,
            f"Trial result import preflight: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.TRIAL_RESULT_IMPORT_PREFLIGHT_VALIDATE_OK,
        "Trial result import preflight validation passed (no import; no auto revision)",
        checks=checks,
        commercial_release_allowed=False,
        input_results_available=False,
        preflight_passed=False,
        revision_auto_applied=False,
        next_actions=["novel-suite trial-result-import-preflight validate --json"],
    )


def run_freeze_decision_import_preflight_validate() -> Result:
    checks = validate_freeze_decision_import_preflight()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.FREEZE_DECISION_IMPORT_PREFLIGHT_VALIDATE_FAIL,
            f"Freeze decision import preflight: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.FREEZE_DECISION_IMPORT_PREFLIGHT_VALIDATE_OK,
        "Freeze decision import preflight validation passed (no tag/zip/release)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        input_decision_available=False,
        preflight_passed=False,
        tag_created=False,
        zip_created=False,
        release_created=False,
        next_actions=["novel-suite freeze-decision-import-preflight validate --json"],
    )


def run_legal_decision_import_preflight_validate() -> Result:
    checks = validate_legal_decision_import_preflight()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.LEGAL_DECISION_IMPORT_PREFLIGHT_VALIDATE_FAIL,
            f"Legal decision import preflight: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.LEGAL_DECISION_IMPORT_PREFLIGHT_VALIDATE_OK,
        "Legal decision import preflight validation passed (no import; no blocker closure)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        input_legal_decision_available=False,
        preflight_passed=False,
        legal_conclusion_auto_generated=False,
        auto_blocker_closure=False,
        next_actions=["novel-suite legal-decision-import-preflight validate --json"],
    )


_M1_DIR = "trial-import-decision-record"
_M2_DIR = "freeze-import-decision-record"
_M3_DIR = "legal-import-decision-board"

_M1_CORE = (
    "README.md",
    "decision_scope.md",
    "preflight_result_record_template.md",
    "pii_redaction_decision_template.md",
    "import_acceptance_criteria.md",
    "import_rejection_decision_template.md",
    "backlog_change_request_template.md",
    "no_auto_backlog_apply_policy.md",
    "next_human_review_actions.md",
    "trial-import-decision-record.schema.json",
    "trial-import-decision-record.sample.json",
)

_M2_CORE = (
    "README.md",
    "decision_scope.md",
    "preflight_result_record_template.md",
    "manifest_acceptance_criteria.md",
    "checksum_acceptance_criteria.md",
    "manual_tag_decision_followup_template.md",
    "release_prohibited_policy.md",
    "freeze_change_request_template.md",
    "next_manual_actions.md",
    "freeze-import-decision-record.schema.json",
    "freeze-import-decision-record.sample.json",
)

_M3_CORE = (
    "README.md",
    "board_scope.md",
    "preflight_result_record_template.md",
    "blocker_change_request_board_template.md",
    "release_gate_change_request_board_template.md",
    "risk_acceptance_decision_template.md",
    "signature_requirement_template.md",
    "no_auto_gate_change_policy.md",
    "no_legal_opinion_policy.md",
    "next_board_actions.md",
    "legal-import-decision-board.schema.json",
    "legal-import-decision-board.sample.json",
)


def trial_import_decision_record_root() -> Path:
    return novel_suite_root() / _M1_DIR


def freeze_import_decision_record_root() -> Path:
    return novel_suite_root() / _M2_DIR


def legal_import_decision_board_root() -> Path:
    return novel_suite_root() / _M3_DIR


def _validate_m1_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field in (
        "preflight_result_available",
        "import_approved",
        "pii_redaction_verified",
        "backlog_auto_applied",
    ):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    return not details, details


def _validate_m2_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field in ("preflight_result_available", "import_approved"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    for field in ("tag_created", "zip_created", "release_created"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    return not details, details


def _validate_m3_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field in ("preflight_result_available", "board_decision_available", "release_gate_changed"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("legal_conclusion_auto_generated") is not False:
        details.append("legal_conclusion_auto_generated must be false")
    if data.get("auto_blocker_closure") is not False:
        details.append("auto_blocker_closure must be false")
    if data.get("requires_human_signature") is not True:
        details.append("requires_human_signature must be true")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    return not details, details


def validate_trial_import_decision_record() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    m1 = trial_import_decision_record_root()
    _append_dir_checks(checks, root, m1, "trial_import_decision_record", _M1_CORE)
    sample = m1 / "trial-import-decision-record.sample.json"
    if sample.is_file():
        ok, details = _validate_m1_sample(sample)
        checks.append(
            {
                "name": "trial_import_decision_record.trial-import-decision-record.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    policy = m1 / "no_auto_backlog_apply_policy.md"
    if policy.is_file():
        text = policy.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "trial_import_decision_record.no_auto_backlog",
                "ok": "backlog_auto_applied" in text,
                "path": _rel(root, policy),
            }
        )
    tmp_readme = root / ".tmp" / "novel-suite-m" / "trial-import-decision-record" / "README.md"
    checks.append(
        {
            "name": "trial_import_decision_record.tmp_m_readme",
            "ok": tmp_readme.is_file(),
            "path": _rel(root, tmp_readme),
        }
    )
    return checks


def validate_freeze_import_decision_record() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    m2 = freeze_import_decision_record_root()
    _append_dir_checks(checks, root, m2, "freeze_import_decision_record", _M2_CORE)
    sample = m2 / "freeze-import-decision-record.sample.json"
    if sample.is_file():
        ok, details = _validate_m2_sample(sample)
        checks.append(
            {
                "name": "freeze_import_decision_record.freeze-import-decision-record.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    tag_doc = m2 / "manual_tag_decision_followup_template.md"
    if tag_doc.is_file():
        text = tag_doc.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "freeze_import_decision_record.no_auto_git_tag",
                "ok": "不执行" in text or "must not" in text.lower() or "不得" in text,
                "path": _rel(root, tag_doc),
            }
        )
    return checks


def validate_legal_import_decision_board() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    m3 = legal_import_decision_board_root()
    _append_dir_checks(checks, root, m3, "legal_import_decision_board", _M3_CORE)
    sample = m3 / "legal-import-decision-board.sample.json"
    if sample.is_file():
        ok, details = _validate_m3_sample(sample)
        checks.append(
            {
                "name": "legal_import_decision_board.legal-import-decision-board.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    for doc_name, key in (
        ("no_auto_gate_change_policy.md", "release_gate_changed"),
        ("no_legal_opinion_policy.md", "legal_conclusion"),
    ):
        doc = m3 / doc_name
        if doc.is_file():
            text = doc.read_text(encoding="utf-8")
            checks.append(
                {
                    "name": f"legal_import_decision_board.{doc_name}",
                    "ok": key in text,
                    "path": _rel(root, doc),
                }
            )
    gate_tpl = m3 / "release_gate_change_request_board_template.md"
    if gate_tpl.is_file():
        text = gate_tpl.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "legal_import_decision_board.no_direct_gate_edit",
                "ok": "不修改" in text or "must not" in text.lower() or "false" in text,
                "path": _rel(root, gate_tpl),
            }
        )
    return checks


def run_trial_import_decision_record_validate() -> Result:
    checks = validate_trial_import_decision_record()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.TRIAL_IMPORT_DECISION_RECORD_VALIDATE_FAIL,
            f"Trial import decision record: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.TRIAL_IMPORT_DECISION_RECORD_VALIDATE_OK,
        "Trial import decision record validation passed (no import; no auto backlog)",
        checks=checks,
        commercial_release_allowed=False,
        preflight_result_available=False,
        import_approved=False,
        backlog_auto_applied=False,
        next_actions=["novel-suite trial-import-decision-record validate --json"],
    )


def run_freeze_import_decision_record_validate() -> Result:
    checks = validate_freeze_import_decision_record()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.FREEZE_IMPORT_DECISION_RECORD_VALIDATE_FAIL,
            f"Freeze import decision record: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.FREEZE_IMPORT_DECISION_RECORD_VALIDATE_OK,
        "Freeze import decision record validation passed (no tag/zip/release)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        preflight_result_available=False,
        import_approved=False,
        tag_created=False,
        zip_created=False,
        release_created=False,
        next_actions=["novel-suite freeze-import-decision-record validate --json"],
    )


def run_legal_import_decision_board_validate() -> Result:
    checks = validate_legal_import_decision_board()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.LEGAL_IMPORT_DECISION_BOARD_VALIDATE_FAIL,
            f"Legal import decision board: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.LEGAL_IMPORT_DECISION_BOARD_VALIDATE_OK,
        "Legal import decision board validation passed (no gate change; no blocker closure)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        preflight_result_available=False,
        board_decision_available=False,
        release_gate_changed=False,
        legal_conclusion_auto_generated=False,
        auto_blocker_closure=False,
        next_actions=["novel-suite legal-import-decision-board validate --json"],
    )


_N1_DIR = "trial-decision-fill-kit"
_N2_DIR = "freeze-decision-fill-kit"
_N3_DIR = "legal-board-execution-kit"

_N1_CORE = (
    "README.md",
    "fill_scope.md",
    "allowed_input_paths.md",
    "pii_redaction_checklist.md",
    "blank_trial_decision_record.md",
    "rejection_reason_selection.md",
    "backlog_change_request_fill_template.md",
    "no_fake_feedback_policy.md",
    "no_auto_backlog_apply_policy.md",
    "next_reviewer_actions.md",
    "trial-decision-fill-kit.schema.json",
    "trial-decision-fill-kit.sample.json",
)

_N2_CORE = (
    "README.md",
    "fill_scope.md",
    "manifest_review_blank_record.md",
    "checksum_review_blank_record.md",
    "freeze_decision_blank_record.md",
    "manual_tag_decision_reference.md",
    "release_creation_prohibited.md",
    "no_agent_tag_policy.md",
    "next_owner_actions.md",
    "freeze-decision-fill-kit.schema.json",
    "freeze-decision-fill-kit.sample.json",
)

_N3_CORE = (
    "README.md",
    "board_execution_scope.md",
    "meeting_agenda_template.md",
    "blocker_review_blank_record.md",
    "change_request_deliberation_template.md",
    "signature_collection_checklist.md",
    "defer_or_reject_decision_template.md",
    "no_legal_opinion_policy.md",
    "no_auto_gate_change_policy.md",
    "next_committee_actions.md",
    "legal-board-execution-kit.schema.json",
    "legal-board-execution-kit.sample.json",
)


def trial_decision_fill_kit_root() -> Path:
    return novel_suite_root() / _N1_DIR


def freeze_decision_fill_kit_root() -> Path:
    return novel_suite_root() / _N2_DIR


def legal_board_execution_kit_root() -> Path:
    return novel_suite_root() / _N3_DIR


def _validate_n1_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field in ("trial_result_available", "import_approved", "fake_feedback_generated", "backlog_auto_applied"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    return not details, details


def _validate_n2_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    if data.get("freeze_decision_available") is not False:
        details.append("freeze_decision_available must be false")
    if data.get("import_approved") is not False:
        details.append("import_approved must be false")
    for field in ("tag_created", "zip_created", "release_created"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    return not details, details


def _validate_n3_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field in ("board_decision_available", "legal_conclusion_auto_generated", "auto_blocker_closure", "release_gate_changed"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("requires_human_signature") is not True:
        details.append("requires_human_signature must be true")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    return not details, details


def validate_trial_decision_fill_kit() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    n1 = trial_decision_fill_kit_root()
    _append_dir_checks(checks, root, n1, "trial_decision_fill_kit", _N1_CORE)
    sample = n1 / "trial-decision-fill-kit.sample.json"
    if sample.is_file():
        ok, details = _validate_n1_sample(sample)
        checks.append(
            {
                "name": "trial_decision_fill_kit.trial-decision-fill-kit.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    for doc_name, key in (("no_fake_feedback_policy.md", "fake_feedback"), ("no_auto_backlog_apply_policy.md", "backlog_auto_applied")):
        doc = n1 / doc_name
        if doc.is_file():
            checks.append(
                {
                    "name": f"trial_decision_fill_kit.{doc_name}",
                    "ok": key in doc.read_text(encoding="utf-8"),
                    "path": _rel(root, doc),
                }
            )
    tmp_readme = root / ".tmp" / "novel-suite-n" / "trial-decision-fill-kit" / "README.md"
    checks.append(
        {
            "name": "trial_decision_fill_kit.tmp_n_readme",
            "ok": tmp_readme.is_file(),
            "path": _rel(root, tmp_readme),
        }
    )
    return checks


def validate_freeze_decision_fill_kit() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    n2 = freeze_decision_fill_kit_root()
    _append_dir_checks(checks, root, n2, "freeze_decision_fill_kit", _N2_CORE)
    sample = n2 / "freeze-decision-fill-kit.sample.json"
    if sample.is_file():
        ok, details = _validate_n2_sample(sample)
        checks.append(
            {
                "name": "freeze_decision_fill_kit.freeze-decision-fill-kit.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    tag_doc = n2 / "no_agent_tag_policy.md"
    if tag_doc.is_file():
        text = tag_doc.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "freeze_decision_fill_kit.no_agent_tag_policy",
                "ok": "tag" in text.lower(),
                "path": _rel(root, tag_doc),
            }
        )
    tmp_readme = root / ".tmp" / "novel-suite-n" / "freeze-decision-fill-kit" / "README.md"
    checks.append(
        {
            "name": "freeze_decision_fill_kit.tmp_n_readme",
            "ok": tmp_readme.is_file(),
            "path": _rel(root, tmp_readme),
        }
    )
    return checks


def validate_legal_board_execution_kit() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    n3 = legal_board_execution_kit_root()
    _append_dir_checks(checks, root, n3, "legal_board_execution_kit", _N3_CORE)
    sample = n3 / "legal-board-execution-kit.sample.json"
    if sample.is_file():
        ok, details = _validate_n3_sample(sample)
        checks.append(
            {
                "name": "legal_board_execution_kit.legal-board-execution-kit.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    for doc_name, key in (
        ("no_legal_opinion_policy.md", "legal_conclusion"),
        ("no_auto_gate_change_policy.md", "release_gate_changed"),
    ):
        doc = n3 / doc_name
        if doc.is_file():
            checks.append(
                {
                    "name": f"legal_board_execution_kit.{doc_name}",
                    "ok": key in doc.read_text(encoding="utf-8"),
                    "path": _rel(root, doc),
                }
            )
    tmp_readme = root / ".tmp" / "novel-suite-n" / "legal-board-execution-kit" / "README.md"
    checks.append(
        {
            "name": "legal_board_execution_kit.tmp_n_readme",
            "ok": tmp_readme.is_file(),
            "path": _rel(root, tmp_readme),
        }
    )
    return checks


def run_trial_decision_fill_kit_validate() -> Result:
    checks = validate_trial_decision_fill_kit()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.TRIAL_DECISION_FILL_KIT_VALIDATE_FAIL,
            f"Trial decision fill kit: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.TRIAL_DECISION_FILL_KIT_VALIDATE_OK,
        "Trial decision fill kit validation passed (blank fill; no fake feedback)",
        checks=checks,
        commercial_release_allowed=False,
        trial_result_available=False,
        import_approved=False,
        fake_feedback_generated=False,
        next_actions=["novel-suite trial-decision-fill-kit validate --json"],
    )


def run_freeze_decision_fill_kit_validate() -> Result:
    checks = validate_freeze_decision_fill_kit()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.FREEZE_DECISION_FILL_KIT_VALIDATE_FAIL,
            f"Freeze decision fill kit: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.FREEZE_DECISION_FILL_KIT_VALIDATE_OK,
        "Freeze decision fill kit validation passed (no tag/zip/release)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        freeze_decision_available=False,
        tag_created=False,
        zip_created=False,
        release_created=False,
        next_actions=["novel-suite freeze-decision-fill-kit validate --json"],
    )


def run_legal_board_execution_kit_validate() -> Result:
    checks = validate_legal_board_execution_kit()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.LEGAL_BOARD_EXECUTION_KIT_VALIDATE_FAIL,
            f"Legal board execution kit: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.LEGAL_BOARD_EXECUTION_KIT_VALIDATE_OK,
        "Legal board execution kit validation passed (no gate change; no blocker closure)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        board_decision_available=False,
        release_gate_changed=False,
        legal_conclusion_auto_generated=False,
        auto_blocker_closure=False,
        next_actions=["novel-suite legal-board-execution-kit validate --json"],
    )


_O2_SOLO_DIR = "solo-founder-freeze-self-check"
_O3_SOLO_DIR = "solo-founder-compliance-self-check"
_O_DECL_DIR = "solo-founder-release-blocked-declaration"

_O2_SOLO_CORE = (
    "README.md",
    "freeze_scope_self_check.md",
    "no_release_declaration.md",
    "manual_tag_prohibited_for_agent.md",
    "solo-founder-freeze-self-check.schema.json",
    "solo-founder-freeze-self-check.sample.json",
)

_O3_SOLO_CORE = (
    "README.md",
    "compliance_boundary_self_check.md",
    "no_legal_opinion_declaration.md",
    "blocker_retention_record.md",
    "solo-founder-compliance-self-check.schema.json",
    "solo-founder-compliance-self-check.sample.json",
)

_O_DECL_CORE = (
    "README.md",
    "continue_allowed_scope.md",
    "prohibited_scope.md",
    "next_real_review_triggers.md",
    "solo-founder-release-blocked-declaration.schema.json",
    "solo-founder-release-blocked-declaration.sample.json",
)


def solo_founder_freeze_self_check_root() -> Path:
    return novel_suite_root() / _O2_SOLO_DIR


def solo_founder_compliance_self_check_root() -> Path:
    return novel_suite_root() / _O3_SOLO_DIR


def solo_founder_release_blocked_declaration_root() -> Path:
    return novel_suite_root() / _O_DECL_DIR


def _validate_o2_solo_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    if data.get("freeze_candidate_only") is not True:
        details.append("freeze_candidate_only must be true")
    for field in ("tag_created", "zip_created", "release_created", "agent_may_create_tag"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    return not details, details


def _validate_o3_solo_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field in ("legal_conclusion_auto_generated", "legal_review_completed", "auto_blocker_closure"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    for field, expected in (
        ("blocker_B01", "open"),
        ("blocker_B03", "open"),
        ("blocker_B04", "open"),
        ("blocker_B05", "resolved-demo-only"),
    ):
        if data.get(field) != expected:
            details.append(f"{field} must be {expected}")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    return not details, details


def _validate_o_decl_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    if data.get("personal_dev_continue_allowed") is not True:
        details.append("personal_dev_continue_allowed must be true")
    for field in (
        "tag_created",
        "zip_created",
        "release_created",
        "legal_conclusion_auto_generated",
        "auto_blocker_closure",
    ):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    return not details, details


def validate_solo_founder_freeze_self_check() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    o2 = solo_founder_freeze_self_check_root()
    _append_dir_checks(checks, root, o2, "solo_founder_freeze_self_check", _O2_SOLO_CORE)
    sample = o2 / "solo-founder-freeze-self-check.sample.json"
    if sample.is_file():
        ok, details = _validate_o2_solo_sample(sample)
        checks.append(
            {
                "name": "solo_founder_freeze_self_check.solo-founder-freeze-self-check.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    tag_doc = o2 / "manual_tag_prohibited_for_agent.md"
    if tag_doc.is_file():
        checks.append(
            {
                "name": "solo_founder_freeze_self_check.manual_tag_prohibited_for_agent",
                "ok": "agent_may_create_tag" in tag_doc.read_text(encoding="utf-8"),
                "path": _rel(root, tag_doc),
            }
        )
    return checks


def validate_solo_founder_compliance_self_check() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    o3 = solo_founder_compliance_self_check_root()
    _append_dir_checks(checks, root, o3, "solo_founder_compliance_self_check", _O3_SOLO_CORE)
    sample = o3 / "solo-founder-compliance-self-check.sample.json"
    if sample.is_file():
        ok, details = _validate_o3_solo_sample(sample)
        checks.append(
            {
                "name": "solo_founder_compliance_self_check.solo-founder-compliance-self-check.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    for doc_name, key in (
        ("no_legal_opinion_declaration.md", "legal_conclusion_auto_generated"),
        ("blocker_retention_record.md", "auto_blocker_closure"),
    ):
        doc = o3 / doc_name
        if doc.is_file():
            checks.append(
                {
                    "name": f"solo_founder_compliance_self_check.{doc_name}",
                    "ok": key in doc.read_text(encoding="utf-8"),
                    "path": _rel(root, doc),
                }
            )
    return checks


def validate_solo_founder_release_blocked_declaration() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    decl = solo_founder_release_blocked_declaration_root()
    _append_dir_checks(checks, root, decl, "solo_founder_release_blocked_declaration", _O_DECL_CORE)
    sample = decl / "solo-founder-release-blocked-declaration.sample.json"
    if sample.is_file():
        ok, details = _validate_o_decl_sample(sample)
        checks.append(
            {
                "name": "solo_founder_release_blocked_declaration.solo-founder-release-blocked-declaration.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    for doc_name, key in (
        ("continue_allowed_scope.md", "personal_dev_continue_allowed"),
        ("prohibited_scope.md", "commercial_release_allowed"),
    ):
        doc = decl / doc_name
        if doc.is_file():
            checks.append(
                {
                    "name": f"solo_founder_release_blocked_declaration.{doc_name}",
                    "ok": key in doc.read_text(encoding="utf-8") or "blocked" in doc.read_text(encoding="utf-8"),
                    "path": _rel(root, doc),
                }
            )
    return checks


def run_solo_founder_freeze_self_check_validate() -> Result:
    checks = validate_solo_founder_freeze_self_check()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.SOLO_FOUNDER_FREEZE_SELF_CHECK_VALIDATE_FAIL,
            f"Solo founder freeze self-check: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.SOLO_FOUNDER_FREEZE_SELF_CHECK_VALIDATE_OK,
        "Solo founder freeze self-check passed (no tag/zip/release; not team meeting)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        freeze_candidate_only=True,
        tag_created=False,
        zip_created=False,
        release_created=False,
        agent_may_create_tag=False,
        next_actions=["novel-suite solo-founder-freeze-self-check validate --json"],
    )


def run_solo_founder_compliance_self_check_validate() -> Result:
    checks = validate_solo_founder_compliance_self_check()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.SOLO_FOUNDER_COMPLIANCE_SELF_CHECK_VALIDATE_FAIL,
            f"Solo founder compliance self-check: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.SOLO_FOUNDER_COMPLIANCE_SELF_CHECK_VALIDATE_OK,
        "Solo founder compliance self-check passed (no legal opinion; no blocker closure)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        legal_conclusion_auto_generated=False,
        legal_review_completed=False,
        auto_blocker_closure=False,
        next_actions=["novel-suite solo-founder-compliance-self-check validate --json"],
    )


def run_solo_founder_release_blocked_declaration_validate() -> Result:
    checks = validate_solo_founder_release_blocked_declaration()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.SOLO_FOUNDER_RELEASE_BLOCKED_DECLARATION_VALIDATE_FAIL,
            f"Solo founder release blocked declaration: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.SOLO_FOUNDER_RELEASE_BLOCKED_DECLARATION_VALIDATE_OK,
        "Solo founder release blocked declaration passed (personal dev allowed; commercial blocked)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        personal_dev_continue_allowed=True,
        tag_created=False,
        zip_created=False,
        release_created=False,
        legal_conclusion_auto_generated=False,
        auto_blocker_closure=False,
        next_actions=["novel-suite solo-founder-release-blocked-declaration validate --json"],
    )


_P1_DIR = "solo-demo-15min"
_P2_DIR = "promptpack-first-run"
_P3_DIR = "multi-ide-dry-run-feedback"

_P1_CORE = (
    "README.md",
    "demo_script_15min.md",
    "demo_checklist.md",
    "safe_commands.md",
    "blocked_boundary.md",
    "solo-demo-15min.schema.json",
    "solo-demo-15min.sample.json",
)

_P2_CORE = (
    "README.md",
    "pp001_first_run_guide.md",
    "pp002_review_first_run_guide.md",
    "pp003_video_first_run_guide.md",
    "input_output_examples.md",
    "common_confusions.md",
    "promptpack-first-run.schema.json",
    "promptpack-first-run.sample.json",
)

_P3_CORE = (
    "README.md",
    "feedback_template.md",
    "ide_matrix.md",
    "local_collection_policy.md",
    "no_telemetry_policy.md",
    "multi-ide-dry-run-feedback.schema.json",
    "multi-ide-dry-run-feedback.sample.json",
)


def solo_demo_15min_root() -> Path:
    return novel_suite_root() / _P1_DIR


def promptpack_first_run_root() -> Path:
    return novel_suite_root() / _P2_DIR


def multi_ide_dry_run_feedback_root() -> Path:
    return novel_suite_root() / _P3_DIR


def _validate_p1_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    if data.get("demo_type") != "local_readonly_dry_run":
        details.append("demo_type must be local_readonly_dry_run")
    if data.get("external_call_performed") is not False:
        details.append("external_call_performed must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    return not details, details


def _validate_p2_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    if data.get("new_user_start_pack") != "PP-001":
        details.append("new_user_start_pack must be PP-001")
    if data.get("commercial_claim_allowed") is not False:
        details.append("commercial_claim_allowed must be false")
    if data.get("external_call_performed") is not False:
        details.append("external_call_performed must be false")
    return not details, details


def _validate_p3_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field in ("telemetry_collected", "external_call_performed", "private_project_read"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    ides = data.get("supported_ides", [])
    if not isinstance(ides, list) or len(ides) < 6:
        details.append("supported_ides must list at least 6 IDEs")
    return not details, details


def validate_solo_demo_15min() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    p1 = solo_demo_15min_root()
    _append_dir_checks(checks, root, p1, "solo_demo_15min", _P1_CORE)
    sample = p1 / "solo-demo-15min.sample.json"
    if sample.is_file():
        ok, details = _validate_p1_sample(sample)
        checks.append(
            {
                "name": "solo_demo_15min.solo-demo-15min.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    blocked = p1 / "blocked_boundary.md"
    if blocked.is_file():
        text = blocked.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "solo_demo_15min.blocked_boundary",
                "ok": "commercial_release_allowed" in text and "blocked" in text,
                "path": _rel(root, blocked),
            }
        )
    safe = p1 / "safe_commands.md"
    if safe.is_file():
        text = safe.read_text(encoding="utf-8").lower()
        checks.append(
            {
                "name": "solo_demo_15min.safe_commands_readonly",
                "ok": "validate" in text and "ffmpeg" in text,
                "path": _rel(root, safe),
            }
        )
    return checks


def validate_promptpack_first_run() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    p2 = promptpack_first_run_root()
    _append_dir_checks(checks, root, p2, "promptpack_first_run", _P2_CORE)
    sample = p2 / "promptpack-first-run.sample.json"
    if sample.is_file():
        ok, details = _validate_p2_sample(sample)
        checks.append(
            {
                "name": "promptpack_first_run.promptpack-first-run.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    for guide in ("pp001_first_run_guide.md", "pp002_review_first_run_guide.md", "pp003_video_first_run_guide.md"):
        doc = p2 / guide
        if doc.is_file():
            text = doc.read_text(encoding="utf-8")
            checks.append(
                {
                    "name": f"promptpack_first_run.{guide}.sections",
                    "ok": all(k in text for k in ("适用对象", "输入材料", "禁止承诺")),
                    "path": _rel(root, doc),
                }
            )
    conf = p2 / "common_confusions.md"
    if conf.is_file():
        text = conf.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "promptpack_first_run.common_confusions",
                "ok": all(k in text for k in ("PromptPack", "demo-only", "dry-run", "一键成片")),
                "path": _rel(root, conf),
            }
        )
    return checks


def validate_multi_ide_dry_run_feedback() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    p3 = multi_ide_dry_run_feedback_root()
    _append_dir_checks(checks, root, p3, "multi_ide_dry_run_feedback", _P3_CORE)
    sample = p3 / "multi-ide-dry-run-feedback.sample.json"
    if sample.is_file():
        ok, details = _validate_p3_sample(sample)
        checks.append(
            {
                "name": "multi_ide_dry_run_feedback.multi-ide-dry-run-feedback.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    matrix = p3 / "ide_matrix.md"
    if matrix.is_file():
        text = matrix.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "multi_ide_dry_run_feedback.ide_matrix_coverage",
                "ok": all(ide in text for ide in ("Cursor", "Codex", "TRAE", "Qoder", "OpenClaw", "Generic")),
                "path": _rel(root, matrix),
            }
        )
    for doc_name, key in (
        ("local_collection_policy.md", "本地"),
        ("no_telemetry_policy.md", "telemetry_collected"),
    ):
        doc = p3 / doc_name
        if doc.is_file():
            checks.append(
                {
                    "name": f"multi_ide_dry_run_feedback.{doc_name}",
                    "ok": key in doc.read_text(encoding="utf-8"),
                    "path": _rel(root, doc),
                }
            )
    return checks


def run_solo_demo_15min_validate() -> Result:
    checks = validate_solo_demo_15min()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.SOLO_DEMO_15MIN_VALIDATE_FAIL,
            f"Solo demo 15min: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.SOLO_DEMO_15MIN_VALIDATE_OK,
        "Solo demo 15min validation passed (readonly dry-run; commercial blocked)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        demo_type="local_readonly_dry_run",
        external_call_performed=False,
        next_actions=["novel-suite solo-demo-15min validate --json"],
    )


def run_promptpack_first_run_validate() -> Result:
    checks = validate_promptpack_first_run()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.PROMPTPACK_FIRST_RUN_VALIDATE_FAIL,
            f"Promptpack first run: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.PROMPTPACK_FIRST_RUN_VALIDATE_OK,
        "Promptpack first run validation passed (PP-001 entry; no commercial claims)",
        checks=checks,
        new_user_start_pack="PP-001",
        commercial_claim_allowed=False,
        external_call_performed=False,
        next_actions=["novel-suite promptpack-first-run validate --json"],
    )


def run_multi_ide_dry_run_feedback_validate() -> Result:
    checks = validate_multi_ide_dry_run_feedback()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.MULTI_IDE_DRY_RUN_FEEDBACK_VALIDATE_FAIL,
            f"Multi-IDE dry-run feedback: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.MULTI_IDE_DRY_RUN_FEEDBACK_VALIDATE_OK,
        "Multi-IDE dry-run feedback validation passed (local only; no telemetry)",
        checks=checks,
        telemetry_collected=False,
        external_call_performed=False,
        private_project_read=False,
        next_actions=["novel-suite multi-ide-dry-run-feedback validate --json"],
    )


_Q1_DIR = "solo-demo-trial-intake"
_Q2_DIR = "promptpack-friction-review"
_Q3_DIR = "multi-ide-feedback-backlog"
_Q_TMP = ".tmp/novel-suite-q"

_Q1_CORE = (
    "README.md",
    "trial_record_template.md",
    "trial_result_summary_template.md",
    "no_fake_trial_policy.md",
    "solo-demo-trial-intake.schema.json",
    "solo-demo-trial-intake.sample.json",
)

_Q2_CORE = (
    "README.md",
    "friction_record_template.md",
    "revision_candidate_template.md",
    "no_auto_promptpack_change_policy.md",
    "promptpack-friction-review.schema.json",
    "promptpack-friction-review.sample.json",
)

_Q3_CORE = (
    "README.md",
    "backlog_taxonomy.md",
    "backlog_item_template.md",
    "triage_rules.md",
    "no_auto_backlog_apply_policy.md",
    "multi-ide-feedback-backlog.schema.json",
    "multi-ide-feedback-backlog.sample.json",
)


def solo_demo_trial_intake_root() -> Path:
    return novel_suite_root() / _Q1_DIR


def promptpack_friction_review_root() -> Path:
    return novel_suite_root() / _Q2_DIR


def multi_ide_feedback_backlog_root() -> Path:
    return novel_suite_root() / _Q3_DIR


def _validate_q1_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    if data.get("sample_only") is not True:
        details.append("sample_only must be true")
    for field in ("trial_executed", "fake_feedback_generated", "external_call_performed"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    return not details, details


def _validate_q2_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    if data.get("real_friction_available") is not False:
        details.append("real_friction_available must be false")
    if data.get("auto_promptpack_changed") is not False:
        details.append("auto_promptpack_changed must be false")
    if data.get("revision_candidate_only") is not True:
        details.append("revision_candidate_only must be true")
    if data.get("external_call_performed") is not False:
        details.append("external_call_performed must be false")
    return not details, details


def _validate_q3_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    for field in ("feedback_imported", "backlog_auto_applied", "telemetry_collected", "private_project_read"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    taxonomy = data.get("taxonomy_ids", [])
    if not isinstance(taxonomy, list) or len(taxonomy) < 10:
        details.append("taxonomy_ids must list at least 10 categories")
    return not details, details


def _append_q_tmp_check(
    checks: list[dict[str, Any]],
    root: Path,
    subdir: str,
    prefix: str,
) -> None:
    tmp_readme = root / _Q_TMP / subdir / "README.md"
    checks.append(
        {
            "name": f"{prefix}.tmp_q_readme",
            "ok": tmp_readme.is_file(),
            "path": _rel(root, tmp_readme),
        }
    )
    tmp_keep = root / _Q_TMP / subdir / ".gitkeep"
    checks.append(
        {
            "name": f"{prefix}.tmp_q_gitkeep",
            "ok": tmp_keep.is_file(),
            "path": _rel(root, tmp_keep),
        }
    )


def validate_solo_demo_trial_intake() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    q1 = solo_demo_trial_intake_root()
    _append_dir_checks(checks, root, q1, "solo_demo_trial_intake", _Q1_CORE)
    sample = q1 / "solo-demo-trial-intake.sample.json"
    if sample.is_file():
        ok, details = _validate_q1_sample(sample)
        checks.append(
            {
                "name": "solo_demo_trial_intake.solo-demo-trial-intake.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    policy = q1 / "no_fake_trial_policy.md"
    if policy.is_file():
        checks.append(
            {
                "name": "solo_demo_trial_intake.no_fake_trial_policy",
                "ok": "fake_feedback_generated" in policy.read_text(encoding="utf-8"),
                "path": _rel(root, policy),
            }
        )
    _append_q_tmp_check(checks, root, "solo-demo-trial-intake", "solo_demo_trial_intake")
    return checks


def validate_promptpack_friction_review() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    q2 = promptpack_friction_review_root()
    _append_dir_checks(checks, root, q2, "promptpack_friction_review", _Q2_CORE)
    sample = q2 / "promptpack-friction-review.sample.json"
    if sample.is_file():
        ok, details = _validate_q2_sample(sample)
        checks.append(
            {
                "name": "promptpack_friction_review.promptpack-friction-review.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    rev = q2 / "revision_candidate_template.md"
    if rev.is_file():
        text = rev.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "promptpack_friction_review.revision_candidate_types",
                "ok": all(k in text for k in ("文案澄清", "输入字段补充", "边界声明增强")),
                "path": _rel(root, rev),
            }
        )
    policy = q2 / "no_auto_promptpack_change_policy.md"
    if policy.is_file():
        checks.append(
            {
                "name": "promptpack_friction_review.no_auto_promptpack_change_policy",
                "ok": "auto_promptpack_changed" in policy.read_text(encoding="utf-8"),
                "path": _rel(root, policy),
            }
        )
    _append_q_tmp_check(checks, root, "promptpack-friction-review", "promptpack_friction_review")
    return checks


def validate_multi_ide_feedback_backlog() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    q3 = multi_ide_feedback_backlog_root()
    _append_dir_checks(checks, root, q3, "multi_ide_feedback_backlog", _Q3_CORE)
    sample = q3 / "multi-ide-feedback-backlog.sample.json"
    if sample.is_file():
        ok, details = _validate_q3_sample(sample)
        checks.append(
            {
                "name": "multi_ide_feedback_backlog.multi-ide-feedback-backlog.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    tax = q3 / "backlog_taxonomy.md"
    if tax.is_file():
        text = tax.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "multi_ide_feedback_backlog.backlog_taxonomy",
                "ok": all(k in text for k in ("入口不清", "PromptPack 卡点", "商业/法律误解", "视频侧误解")),
                "path": _rel(root, tax),
            }
        )
    triage = q3 / "triage_rules.md"
    if triage.is_file():
        text = triage.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "multi_ide_feedback_backlog.triage_rules",
                "ok": all(k in text for k in ("P0", "P1", "P2", "P3")),
                "path": _rel(root, triage),
            }
        )
    policy = q3 / "no_auto_backlog_apply_policy.md"
    if policy.is_file():
        checks.append(
            {
                "name": "multi_ide_feedback_backlog.no_auto_backlog_apply_policy",
                "ok": "backlog_auto_applied" in policy.read_text(encoding="utf-8"),
                "path": _rel(root, policy),
            }
        )
    matrix_ide = q3 / "README.md"
    if matrix_ide.is_file():
        text = matrix_ide.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "multi_ide_feedback_backlog.ide_coverage",
                "ok": all(ide in text for ide in ("Cursor", "Codex", "TRAE", "Qoder", "OpenClaw", "Generic")),
                "path": _rel(root, matrix_ide),
            }
        )
    _append_q_tmp_check(checks, root, "multi-ide-feedback-backlog", "multi_ide_feedback_backlog")
    return checks


def run_solo_demo_trial_intake_validate() -> Result:
    checks = validate_solo_demo_trial_intake()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.SOLO_DEMO_TRIAL_INTAKE_VALIDATE_FAIL,
            f"Solo demo trial intake: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.SOLO_DEMO_TRIAL_INTAKE_VALIDATE_OK,
        "Solo demo trial intake passed (no fake feedback; trial not executed)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        trial_executed=False,
        fake_feedback_generated=False,
        external_call_performed=False,
        next_actions=["novel-suite solo-demo-trial-intake validate --json"],
    )


def run_promptpack_friction_review_validate() -> Result:
    checks = validate_promptpack_friction_review()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.PROMPTPACK_FRICTION_REVIEW_VALIDATE_FAIL,
            f"Promptpack friction review: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.PROMPTPACK_FRICTION_REVIEW_VALIDATE_OK,
        "Promptpack friction review passed (revision candidates only; no auto edit)",
        checks=checks,
        real_friction_available=False,
        auto_promptpack_changed=False,
        revision_candidate_only=True,
        external_call_performed=False,
        next_actions=["novel-suite promptpack-friction-review validate --json"],
    )


def run_multi_ide_feedback_backlog_validate() -> Result:
    checks = validate_multi_ide_feedback_backlog()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.MULTI_IDE_FEEDBACK_BACKLOG_VALIDATE_FAIL,
            f"Multi-IDE feedback backlog: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.MULTI_IDE_FEEDBACK_BACKLOG_VALIDATE_OK,
        "Multi-IDE feedback backlog passed (no auto apply; no telemetry)",
        checks=checks,
        feedback_imported=False,
        backlog_auto_applied=False,
        telemetry_collected=False,
        private_project_read=False,
        next_actions=["novel-suite multi-ide-feedback-backlog validate --json"],
    )


_OFC_DIR = "openclaw-feedback-consolidation"

_OFC_CORE = (
    "README.md",
    "source_feedback_inventory.md",
    "consolidated_findings.md",
    "prioritized_revision_candidates.md",
    "duplicate_issue_merge_table.md",
    "no_auto_apply_policy.md",
    "openclaw-feedback-consolidation.schema.json",
    "openclaw-feedback-consolidation.sample.json",
)


def openclaw_feedback_consolidation_root() -> Path:
    return novel_suite_root() / _OFC_DIR


def _validate_ofc_sample(path: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [str(exc)]
    if data.get("feedback_consolidated") is not True:
        details.append("feedback_consolidated must be true")
    for field in ("auto_apply", "promptpack_changed", "gate_changed", "backlog_auto_applied"):
        if data.get(field) is not False:
            details.append(f"{field} must be false")
    if data.get("commercial_release_allowed") is not False:
        details.append("commercial_release_allowed must be false")
    if data.get("verdict") != "blocked":
        details.append("verdict must be blocked")
    if data.get("p0_candidate_count", 0) < 2:
        details.append("p0_candidate_count must be >= 2")
    if data.get("p1_candidate_count", 0) < 2:
        details.append("p1_candidate_count must be >= 2")
    if data.get("p2_candidate_count", 0) < 1:
        details.append("p2_candidate_count must be >= 1")
    ids = data.get("consolidated_ids", [])
    if not isinstance(ids, list) or len(ids) < 5:
        details.append("consolidated_ids must list at least 5 items")
    return not details, details


def validate_openclaw_feedback_consolidation() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    ofc = openclaw_feedback_consolidation_root()
    _append_dir_checks(checks, root, ofc, "openclaw_feedback_consolidation", _OFC_CORE)
    sample = ofc / "openclaw-feedback-consolidation.sample.json"
    if sample.is_file():
        ok, details = _validate_ofc_sample(sample)
        checks.append(
            {
                "name": "openclaw_feedback_consolidation.openclaw-feedback-consolidation.sample.json",
                "ok": ok,
                "path": _rel(root, sample),
                **({"details": details} if details else {}),
            }
        )
    candidates = ofc / "prioritized_revision_candidates.md"
    if candidates.is_file():
        text = candidates.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "openclaw_feedback_consolidation.p0_p1_p2_candidates",
                "ok": all(
                    k in text
                    for k in (
                        "RC-CONSOL-001",
                        "RC-CONSOL-002",
                        "RC-CONSOL-003",
                        "RC-CONSOL-004",
                        "RC-CONSOL-005",
                        "P0",
                        "P1",
                        "P2",
                    )
                ),
                "path": _rel(root, candidates),
            }
        )
    policy = ofc / "no_auto_apply_policy.md"
    if policy.is_file():
        text = policy.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "openclaw_feedback_consolidation.no_auto_apply_policy",
                "ok": all(k in text for k in ("auto_apply", "promptpack_changed", "gate_changed")),
                "path": _rel(root, policy),
            }
        )
    inventory = ofc / "source_feedback_inventory.md"
    if inventory.is_file():
        text = inventory.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "openclaw_feedback_consolidation.source_inventory",
                "ok": "novel-suite-q" in text and "trial-decision-fill-kit" in text,
                "path": _rel(root, inventory),
            }
        )
    return checks


def run_openclaw_feedback_consolidation_validate() -> Result:
    checks = validate_openclaw_feedback_consolidation()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.OPENCLAW_FEEDBACK_CONSOLIDATION_VALIDATE_FAIL,
            f"OpenClaw feedback consolidation: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
            commercial_release_allowed=False,
        )
    return ok_result(
        E.OPENCLAW_FEEDBACK_CONSOLIDATION_VALIDATE_OK,
        "OpenClaw feedback consolidation passed (merged candidates; no auto apply)",
        checks=checks,
        feedback_consolidated=True,
        auto_apply=False,
        promptpack_changed=False,
        gate_changed=False,
        backlog_auto_applied=False,
        commercial_release_allowed=False,
        verdict="blocked",
        p0_candidate_count=2,
        p1_candidate_count=2,
        p2_candidate_count=1,
        next_actions=["novel-suite openclaw-feedback-consolidation validate --json"],
    )

