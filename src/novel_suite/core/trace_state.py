"""F3 Trace/State + C10 Multi-IDE trials — read-only validation (no collector, no network)."""



from __future__ import annotations



import json

from pathlib import Path

from typing import Any



from novel_suite.core import errors as E

from novel_suite.core.contracts import novel_suite_root

from novel_suite.core.paths import suite_root

from novel_suite.core.result import Result, error_result, ok_result



_TRACE_DIR = "trace-state"

_TRIALS_DIR = "multi-ide-trials"



_TRACE_CORE_FIELDS = frozenset(

    {

        "trace_version",

        "run_id",

        "trace_id",

        "session_id",

        "agent_surface",

        "ide_name",

        "workflow_id",

        "phase",

        "step_id",

        "tool_name",

        "permission_level",

        "adapter_level",

        "result_status",

        "result_code",

        "gate_status",

        "commercial_release_allowed",

        "manual_confirmation_required",

        "external_call_performed",

        "created_at",

    }

)



_TRACE_SCHEMA_FILES = (

    "trace_state.schema.json",

    "trace_event_minimal.schema.json",

    "trace_state.schema.md",

    "README.md",

)



_TRACE_DOC_FILES = (

    "trace_state_lifecycle.md",

    "trace_state_storage_policy.md",

    "trace_state_privacy_policy.md",

    "trace_state_error_model.md",

    "trace_state_result_contract_mapping.md",

    "trace_state_workflow_contract_mapping.md",

    "trace_state_human_review_mapping.md",

)



_TRACE_MAPPINGS = (

    "mappings/result_contract_to_trace.md",

    "mappings/workflow_contract_to_trace.md",

    "mappings/permission_model_to_trace.md",

)



_TRACE_SAMPLES = (

    "examples/workflow_contract_validate.trace.jsonl",

    "examples/commercial_release_candidate_validate.trace.jsonl",

    "examples/adapter_dry_run.trace.jsonl",

    "examples/multi_ide_trial.trace.jsonl",

)



_TRIALS_CORE_FILES = (

    "README.md",

    "trial_scope.md",

    "trial_matrix.md",

    "user_trial_script.md",

    "trial_feedback_form.schema.json",

    "trial_feedback_form.sample.json",

    "feedback_triage_playbook.md",

    "feedback_summary_template.md",

    "ide_surface_notes.md",

    "trial_risk_boundary.md",

    "trial_success_criteria.md",

    "trial_no_external_call_checklist.md",

)



_TRIAL_CARDS = (

    "trial_cards/cursor_trial_card.md",

    "trial_cards/codex_trial_card.md",

    "trial_cards/trae_cn_trial_card.md",

    "trial_cards/qoder_trial_card.md",

    "trial_cards/openclaw_trial_card.md",

    "trial_cards/generic_agent_trial_card.md",

)



_FEEDBACK_REQUIRED = frozenset(

    {

        "trial_id",

        "ide_name",

        "agent_surface",

        "task_id",

        "workflow_id",

        "success",

        "failure_type",

        "confusion_points",

        "missing_context",

        "unexpected_behavior",

        "trace_sample_path",

        "suggested_fix",

        "risk_observed",

        "external_call_attempted",

    }

)





def trace_state_root() -> Path:

    return novel_suite_root() / _TRACE_DIR





def multi_ide_trials_root() -> Path:

    return novel_suite_root() / _TRIALS_DIR





def _rel(root: Path, path: Path) -> str:

    try:

        return path.resolve().relative_to(root.resolve()).as_posix()

    except ValueError:

        return str(path.resolve())





def _validate_trace_event(data: dict[str, Any], *, source: str) -> tuple[bool, list[str]]:

    details: list[str] = []

    missing = _TRACE_CORE_FIELDS - set(data.keys())

    if missing:

        details.append(f"{source}: missing fields {sorted(missing)}")

    if data.get("external_call_performed") is not False:

        details.append(f"{source}: external_call_performed must be false")

    if data.get("commercial_release_allowed") is not False:

        details.append(f"{source}: commercial_release_allowed must be false")

    return not details, details





def _validate_trace_jsonl(path: Path) -> tuple[bool, list[str]]:

    details: list[str] = []

    if not path.is_file():

        return False, ["missing file"]

    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]

    if not lines:

        return False, ["empty jsonl"]

    for i, line in enumerate(lines, start=1):

        try:

            data = json.loads(line)

        except json.JSONDecodeError as exc:

            details.append(f"line {i}: {exc}")

            continue

        ok, errs = _validate_trace_event(data, source=f"line {i}")

        if not ok:

            details.extend(errs)

    return not details, details





def _validate_feedback_sample(path: Path) -> tuple[bool, list[str]]:

    details: list[str] = []

    try:

        data = json.loads(path.read_text(encoding="utf-8"))

    except json.JSONDecodeError as exc:

        return False, [str(exc)]

    missing = _FEEDBACK_REQUIRED - set(data.keys())

    if missing:

        details.append(f"missing feedback fields: {sorted(missing)}")

    if data.get("external_call_attempted") is not False:

        details.append("external_call_attempted must be false")

    if "risk_observed" not in data:

        details.append("risk_observed required")

    return not details, details





def validate_trace_state_specs() -> list[dict[str, Any]]:

    """Validate F3 trace-state schema, docs, mappings, and JSONL samples."""

    checks: list[dict[str, Any]] = []

    root = suite_root()

    ts = trace_state_root()



    if not ts.is_dir():

        checks.append({"name": "trace_state.dir", "ok": False, "error": "missing"})

        return checks



    for name in _TRACE_SCHEMA_FILES:

        path = ts / name

        checks.append(

            {

                "name": f"trace_state.{name}",

                "ok": path.is_file(),

                "path": _rel(root, path) if path.is_file() else str(path),

            }

        )



    for rel in _TRACE_DOC_FILES:

        path = ts / rel

        checks.append(

            {

                "name": f"trace_state.{rel.replace('/', '.')}",

                "ok": path.is_file(),

                "path": _rel(root, path) if path.is_file() else str(path),

            }

        )



    for rel in _TRACE_MAPPINGS:

        path = ts / rel

        checks.append(

            {

                "name": f"trace_state.{rel.replace('/', '.')}",

                "ok": path.is_file(),

                "path": _rel(root, path) if path.is_file() else str(path),

            }

        )



    for rel in _TRACE_SAMPLES:

        path = ts / rel

        if not path.is_file():

            checks.append({"name": f"trace_state.{rel.replace('/', '.')}", "ok": False, "error": "missing"})

            continue

        ok, details = _validate_trace_jsonl(path)

        checks.append(

            {

                "name": f"trace_state.{rel.replace('/', '.')}",

                "ok": ok,

                "path": _rel(root, path),

                **({"details": details} if details else {}),

            }

        )



    return checks





def validate_multi_ide_trials() -> list[dict[str, Any]]:

    """Validate C10 multi-ide-trials docs, trial cards, feedback schema/sample."""

    checks: list[dict[str, Any]] = []

    root = suite_root()

    mt = multi_ide_trials_root()



    if not mt.is_dir():

        checks.append({"name": "multi_ide_trials.dir", "ok": False, "error": "missing"})

        return checks



    for name in _TRIALS_CORE_FILES:

        path = mt / name

        checks.append(

            {

                "name": f"multi_ide_trials.{name.replace('/', '.')}",

                "ok": path.is_file(),

                "path": _rel(root, path) if path.is_file() else str(path),

            }

        )



    for rel in _TRIAL_CARDS:

        path = mt / rel

        checks.append(

            {

                "name": f"multi_ide_trials.{rel.replace('/', '.')}",

                "ok": path.is_file(),

                "path": _rel(root, path) if path.is_file() else str(path),

            }

        )



    sample = mt / "trial_feedback_form.sample.json"

    if sample.is_file():

        ok, details = _validate_feedback_sample(sample)

        checks.append(

            {

                "name": "multi_ide_trials.trial_feedback_form.sample.json",

                "ok": ok,

                "path": _rel(root, sample),

                **({"details": details} if details else {}),

            }

        )



    return checks





def run_trace_state_validate() -> Result:

    checks = validate_trace_state_specs()

    failed = [c for c in checks if not c.get("ok")]

    if failed:

        return error_result(

            E.TRACE_STATE_VALIDATE_FAIL,

            f"Trace/state specs: {len(failed)} check(s) failed",

            required=[c["name"] for c in failed],

            checks=checks,

            commercial_release_allowed=False,

        )

    return ok_result(

        E.TRACE_STATE_VALIDATE_OK,

        "Trace/state validation passed (schema + 4 JSONL samples; no collector)",

        checks=checks,

        commercial_release_allowed=False,

        sample_count=len(_TRACE_SAMPLES),

        next_actions=["novel-suite trace-state validate --json"],

    )





def run_multi_ide_trials_validate() -> Result:

    checks = validate_multi_ide_trials()

    failed = [c for c in checks if not c.get("ok")]

    if failed:

        return error_result(

            E.MULTI_IDE_TRIALS_VALIDATE_FAIL,

            f"Multi-IDE trials: {len(failed)} check(s) failed",

            required=[c["name"] for c in failed],

            checks=checks,

            commercial_release_allowed=False,

        )

    return ok_result(

        E.MULTI_IDE_TRIALS_VALIDATE_OK,

        "Multi-IDE trials validation passed (cards + feedback schema; no upload)",

        checks=checks,

        commercial_release_allowed=False,

        trial_card_count=len(_TRIAL_CARDS),

        next_actions=["novel-suite multi-ide-trials validate --json"],

    )

