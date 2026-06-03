"""Pipeline gate with structured Result Contract."""

from __future__ import annotations

from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.paths import suite_root
from novel_suite.core.result import Result, artifact, emit, error_result, ok_result
from novel_suite.writer import registry as reg
from novel_suite.writer._legacy import load_script_module


def classify_error(msg: str) -> str:
    lower = msg.lower()
    if "phase 0" in lower:
        return E.PHASE0_NOT_COMPLETE
    if "task_plan" in lower and "not marked" in lower:
        return E.TASK_PLAN_PHASE_NOT_MARKED
    if "concept-brief" in lower or "concept brief" in lower:
        return E.MISSING_CONCEPT_BRIEF
    if "project.json" in lower:
        return E.MISSING_PROJECT_JSON
    if "progress.json" in lower:
        return E.MISSING_PROGRESS_JSON
    if "character" in lower:
        return E.MISSING_CHARACTER_PROFILES
    if "worldbuilding" in lower or "location" in lower or "system" in lower:
        return E.MISSING_WORLDBUILDING
    if "chapter" in lower:
        return E.MISSING_CHAPTER
    if "blocker" in lower:
        return E.OPEN_REVIEW_BLOCKERS
    return E.GATE_FAIL


def gate_next_actions(phase: int, errors: list[str]) -> list[str]:
    actions: list[str] = []
    codes = {classify_error(e) for e in errors}
    if E.PHASE0_NOT_COMPLETE in codes:
        actions.extend(
            [
                "Run: novel-suite writer scan --demo (or approve a concept)",
                "Init with: novel-suite writer init --concept intel/concepts/<file>.md",
                "Mark Phase 0 [x] in task_plan.md",
            ]
        )
    if E.TASK_PLAN_PHASE_NOT_MARKED in codes:
        actions.append(f"Complete prior phases in task_plan.md before entering phase {phase}")
    if E.MISSING_CHARACTER_PROFILES in codes or E.MISSING_WORLDBUILDING in codes:
        actions.append("Run worldbuilding + character-management skills for this project")
    if E.MISSING_CHAPTER in codes:
        actions.append("Write chapter under chapters/ and update canon/progress.json")
    if E.OPEN_REVIEW_BLOCKERS in codes:
        actions.append("Resolve blockers in reviews/chNN-review.md before continuing")
    if not actions:
        actions.append("Fix gate errors listed in required/details")
    return actions[:6]


def validate_gate(project: Path, phase: int) -> tuple[bool, list[str]]:
    pg = load_script_module("pipeline_gate")
    return pg.validate_gate(project, phase)


def run_gate(project: Path, phase: int) -> Result:
    project = project.resolve()
    rel = str(project)
    try:
        rel = str(project.relative_to(suite_root()))
    except ValueError:
        pass

    ok, errors = validate_gate(project, phase)
    if ok:
        return ok_result(
            "GATE_OK",
            f"Phase gate passed (enter phase>={phase})",
            artifacts=[artifact(rel, label="project")],
            phase=phase,
        )

    primary = classify_error(errors[0]) if errors else E.GATE_FAIL
    return error_result(
        primary,
        f"Phase gate failed for phase>={phase}",
        required=errors,
        next_actions=gate_next_actions(phase, errors),
        artifacts=[artifact(rel, label="project")],
        phase=phase,
        error_codes=[classify_error(e) for e in errors],
    )


def cmd_gate(*, project: Path | None, phase: int, json_out: bool) -> int:
    try:
        resolved = reg.resolve_project(project)
    except ValueError as exc:
        msg = str(exc)
        code = E.NO_ACTIVE_NOVEL if E.NO_ACTIVE_NOVEL in msg else E.PROJECT_PATH_OUT_OF_BOUNDS
        return emit(
            error_result(code, msg, next_actions=["novel-suite writer use <slug> --json"]),
            json_out=json_out,
        )
    return emit(run_gate(resolved, phase), json_out=json_out)


def run_validate(project: Path, *, include_registry: bool = False) -> Result:
    pg = load_script_module("pipeline_gate")
    errors = pg.validate_project_schemas(project)
    if include_registry:
        errors.extend(pg.validate_registry())
    rel = str(project)
    if errors:
        return error_result(
            E.GATE_FAIL,
            "Project schema validation failed",
            required=errors,
            artifacts=[artifact(rel, label="project")],
        )
    return ok_result("VALIDATE_OK", f"Schema OK: {project}", artifacts=[artifact(rel, label="project")])
