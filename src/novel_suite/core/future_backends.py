"""F4/F5/C11 design & research packages — read-only validation (no LangGraph/RAG/runtime)."""



from __future__ import annotations



import json

from pathlib import Path

from typing import Any



from novel_suite.core import errors as E

from novel_suite.core.contracts import novel_suite_root

from novel_suite.core.paths import suite_root

from novel_suite.core.result import Result, error_result, ok_result



_F4_DIR = "orchestrator-poc-design"

_F5_DIR = "knowledge-backend-research"

_C11_DIR = "trial-feedback-review"



_F4_CORE = (

    "README.md",

    "langgraph_poc_scope.md",

    "langgraph_poc_non_goals.md",

    "langgraph_node_mapping.md",

    "workflow_contract_to_graph_mapping.md",

    "trace_state_to_checkpoint_mapping.md",

    "graph_interrupt_and_human_review.md",

    "graph_error_and_retry_policy.md",

    "graph_security_boundary.md",

    "graph_poc_acceptance_criteria.md",

    "graph_poc_blockers.md",

    "langgraph_dependency_decision.md",

)



_F4_EXAMPLES = (

    "examples/product_validate_graph.design.json",

    "examples/commercial_gate_graph.design.json",

    "examples/adapter_dry_run_graph.design.json",

)



_F5_CORE = (

    "README.md",

    "rag_backend_scope.md",

    "knowledge_asset_taxonomy.md",

    "story_bible_retrieval_model.md",

    "asset_registry_retrieval_model.md",

    "prompt_library_retrieval_model.md",

    "candidate_backends_matrix.md",

    "local_markdown_index_candidate.md",

    "sqlite_fts_candidate.md",

    "llamaindex_candidate.md",

    "qdrant_candidate.md",

    "chroma_candidate.md",

    "privacy_and_rights_boundary.md",

    "ingestion_safety_policy.md",

    "rag_evaluation_plan.md",

    "rag_no_go_decision.md",

)



_C11_CORE = (

    "README.md",

    "feedback_review_scope.md",

    "feedback_classification.schema.json",

    "feedback_classification.sample.json",

    "feedback_triage_matrix.md",

    "product_revision_backlog.md",

    "prompt_pack_revision_rules.md",

    "rules_pack_revision_rules.md",

    "workflow_contract_revision_rules.md",

    "trace_state_revision_rules.md",

    "commercial_claims_revision_rules.md",

    "ide_specific_issue_playbook.md",

    "user_confusion_patterns.md",

    "release_note_template.md",

    "c11_acceptance_criteria.md",

)



_C11_CATEGORIES = frozenset(

    {

        "documentation_gap",

        "prompt_confusion",

        "workflow_contract_gap",

        "trace_state_gap",

        "ide_surface_gap",

        "product_claim_risk",

        "commercial_boundary_confusion",

        "adapter_safety_confusion",

        "bug_or_validation_failure",

        "user_expectation_mismatch",

    }

)





def orchestrator_poc_design_root() -> Path:

    return novel_suite_root() / _F4_DIR





def knowledge_backend_research_root() -> Path:

    return novel_suite_root() / _F5_DIR





def trial_feedback_review_root() -> Path:

    return novel_suite_root() / _C11_DIR





def _rel(root: Path, path: Path) -> str:

    try:

        return path.resolve().relative_to(root.resolve()).as_posix()

    except ValueError:

        return str(path.resolve())





def _validate_design_json(path: Path) -> tuple[bool, list[str]]:

    details: list[str] = []

    try:

        data = json.loads(path.read_text(encoding="utf-8"))

    except json.JSONDecodeError as exc:

        return False, [str(exc)]



    if data.get("runtime_implementation") is not False:

        details.append("runtime_implementation must be false")

    if data.get("langgraph_installed") is not False:

        details.append("langgraph_installed must be false")

    if data.get("external_calls_allowed") is not False:

        details.append("external_calls_allowed must be false")

    if data.get("commercial_release_allowed") is not False:

        details.append("commercial_release_allowed must be false")

    if not data.get("graph_id"):

        details.append("graph_id required")



    return not details, details





def _validate_c11_sample(path: Path) -> tuple[bool, list[str]]:

    details: list[str] = []

    try:

        data = json.loads(path.read_text(encoding="utf-8"))

    except json.JSONDecodeError as exc:

        return False, [str(exc)]



    cats = set(data.get("categories", []))

    if not cats <= _C11_CATEGORIES:

        details.append(f"invalid categories: {cats - _C11_CATEGORIES}")

    if not cats:

        details.append("categories must not be empty")

    if data.get("commercial_release_allowed") is not False:

        details.append("commercial_release_allowed must be false")

    if data.get("external_call_attempted") is not False:

        details.append("external_call_attempted must be false")



    return not details, details





def validate_future_backend_designs() -> list[dict[str, Any]]:

    """Validate F4 orchestrator PoC design + F5 knowledge backend research (read-only)."""

    checks: list[dict[str, Any]] = []

    root = suite_root()

    f4 = orchestrator_poc_design_root()

    f5 = knowledge_backend_research_root()



    for label, base, files in (

        ("f4", f4, _F4_CORE),

        ("f5", f5, _F5_CORE),

    ):

        if not base.is_dir():

            checks.append({"name": f"{label}.dir", "ok": False, "error": "missing"})

            continue

        for name in files:

            path = base / name

            checks.append(

                {

                    "name": f"{label}.{name.replace('/', '.')}",

                    "ok": path.is_file(),

                    "path": _rel(root, path) if path.is_file() else str(path),

                }

            )



    if f4.is_dir():

        for rel in _F4_EXAMPLES:

            path = f4 / rel

            if not path.is_file():

                checks.append({"name": f"f4.{rel.replace('/', '.')}", "ok": False, "error": "missing"})

                continue

            ok, details = _validate_design_json(path)

            checks.append(

                {

                    "name": f"f4.{rel.replace('/', '.')}",

                    "ok": ok,

                    "path": _rel(root, path),

                    **({"details": details} if details else {}),

                }

            )



    return checks





def validate_trial_feedback_review() -> list[dict[str, Any]]:

    """Validate C11 trial feedback review package (read-only)."""

    checks: list[dict[str, Any]] = []

    root = suite_root()

    c11 = trial_feedback_review_root()



    if not c11.is_dir():

        checks.append({"name": "c11.dir", "ok": False, "error": "missing"})

        return checks



    for name in _C11_CORE:

        path = c11 / name

        checks.append(

            {

                "name": f"c11.{name.replace('/', '.')}",

                "ok": path.is_file(),

                "path": _rel(root, path) if path.is_file() else str(path),

            }

        )



    sample = c11 / "feedback_classification.sample.json"

    if sample.is_file():

        ok, details = _validate_c11_sample(sample)

        checks.append(

            {

                "name": "c11.feedback_classification.sample.json",

                "ok": ok,

                "path": _rel(root, sample),

                **({"details": details} if details else {}),

            }

        )



    backlog = c11 / "product_revision_backlog.md"

    if backlog.is_file():

        text = backlog.read_text(encoding="utf-8")

        has_entries = "C11-BL-" in text

        checks.append(

            {

                "name": "c11.product_revision_backlog.entries",

                "ok": has_entries,

                "path": _rel(root, backlog),

            }

        )



    return checks





def run_future_backends_validate() -> Result:

    checks = validate_future_backend_designs()

    failed = [c for c in checks if not c.get("ok")]

    if failed:

        return error_result(

            E.FUTURE_BACKENDS_VALIDATE_FAIL,

            f"Future backend designs: {len(failed)} check(s) failed",

            required=[c["name"] for c in failed],

            checks=checks,

            commercial_release_allowed=False,

        )

    return ok_result(

        E.FUTURE_BACKENDS_VALIDATE_OK,

        "F4/F5 design and research validation passed (no LangGraph/RAG runtime)",

        checks=checks,

        commercial_release_allowed=False,

        langgraph_installed=False,

        rag_runtime=False,

        next_actions=["novel-suite future-backends validate --json"],

    )





def run_trial_feedback_review_validate() -> Result:

    checks = validate_trial_feedback_review()

    failed = [c for c in checks if not c.get("ok")]

    if failed:

        return error_result(

            E.TRIAL_FEEDBACK_REVIEW_VALIDATE_FAIL,

            f"Trial feedback review: {len(failed)} check(s) failed",

            required=[c["name"] for c in failed],

            checks=checks,

            commercial_release_allowed=False,

        )

    return ok_result(

        E.TRIAL_FEEDBACK_REVIEW_VALIDATE_OK,

        "C11 trial feedback review validation passed (fictional demo; no upload)",

        checks=checks,

        commercial_release_allowed=False,

        next_actions=["novel-suite trial-feedback-review validate --json"],

    )

