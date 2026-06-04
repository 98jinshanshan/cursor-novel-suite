#!/usr/bin/env python3
"""Schema-backed pipeline gate enforcement (X-07 / PW-11)."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator
from jsonschema.exceptions import SchemaError

from scripts import project_registry as reg
from scripts import suite_paths as sp

SCHEMA_DIR = sp.writer_root() / "schema"

CONCEPT_HEADINGS = ("## 元信息", "## 题材摘要", "## 故事内核")
REVIEW_BLOCKERS = "## blockers"
REVIEW_DEAI = "## de-ai"


def schema_dir() -> Path:
    return SCHEMA_DIR


def load_schema(name: str) -> dict:
    path = SCHEMA_DIR / name
    if not path.is_file():
        raise SchemaError(f"missing schema file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_json_data(data: Any, schema_name: str, *, label: str = "") -> list[str]:
    prefix = label or schema_name
    try:
        schema = load_schema(schema_name)
    except (SchemaError, json.JSONDecodeError) as exc:
        return [f"{prefix}: schema load failed — {exc}"]
    validator = Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        loc = ".".join(str(part) for part in err.path) or "(root)"
        errors.append(f"{prefix}: {loc} — {err.message}")
    return errors


def validate_json_file(path: Path, schema_name: str) -> list[str]:
    if not path.is_file():
        return [f"missing {path.name}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.name}: invalid JSON — {exc.msg}"]
    return validate_json_data(data, schema_name, label=path.name)


def parse_pipeline_phases(task_plan: Path) -> list[tuple[str, bool]]:
    if not task_plan.is_file():
        return []
    phases: list[tuple[str, bool]] = []
    for line in task_plan.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- [") and "Phase" in stripped:
            done = stripped.startswith("- [x]") or stripped.startswith("- [X]")
            label = stripped.split("]", 1)[-1].strip()
            phases.append((label, done))
    return phases


def phase_done(project: Path, phase: int) -> bool:
    task_plan = project / "task_plan.md"
    if not task_plan.is_file():
        return False
    pattern = re.compile(rf"^- \[(?P<mark>[xX ])\]\s*Phase\s+{phase}\s*:")
    for line in task_plan.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line.strip())
        if match:
            return match.group("mark").lower() == "x"
    return False


def phase0_complete(project: Path) -> bool:
    cb = project / "canon" / "concept-brief.md"
    if not cb.is_file():
        return False
    return phase_done(project, 0)


def latest_review_report(project: Path) -> Path | None:
    reviews_dir = project / "reviews"
    if not reviews_dir.is_dir():
        return None
    reviews = sorted(reviews_dir.glob("ch*-review.md"), key=lambda p: p.stat().st_mtime)
    return reviews[-1] if reviews else None


def has_open_blockers(report: Path) -> bool:
    lines = report.read_text(encoding="utf-8").splitlines()
    in_blockers = False
    has_any_bullets = False
    has_explicit_none = False

    for raw in lines:
        line = raw.strip()
        if line.lower().startswith("## blockers"):
            in_blockers = True
            continue
        if in_blockers and line.startswith("## "):
            break
        if not in_blockers or not line:
            continue
        if line.startswith("- [ ]"):
            return True
        if line.startswith("-"):
            has_any_bullets = True
            lower = line.lower()
            if "(none)" in lower or lower in ("- none", "- 无", "- （无）"):
                has_explicit_none = True
            else:
                return True

    if in_blockers and has_any_bullets and has_explicit_none:
        return False
    return True


def _rel(project: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project))
    except ValueError:
        return str(path)


def _markdown_has_headings(path: Path, headings: tuple[str, ...]) -> list[str]:
    if not path.is_file():
        return [f"missing {_rel(path.parent, path)}"]
    text = path.read_text(encoding="utf-8")
    missing = [h for h in headings if h not in text]
    if missing:
        return [f"{path.name}: missing sections: {', '.join(missing)}"]
    return []


def _count_md_files(folder: Path) -> int:
    if not folder.is_dir():
        return 0
    return sum(1 for p in folder.glob("*.md") if not p.name.startswith("_"))


def _chapter_files(project: Path) -> list[Path]:
    chapters = project / "chapters"
    if not chapters.is_dir():
        return []
    return sorted(p for p in chapters.glob("*.md") if not p.name.startswith("_"))


def _skip_audit_gate() -> bool:
    return os.environ.get("NOVEL_SUITE_SKIP_AUDIT_GATE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _audit_scan_status(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "error"
    return str(data.get("status", ""))


def optional_audit_scan_checks(project: Path, phase: int) -> list[str]:
    """Fail gate only when scan JSON exists and status is error (NEC-11)."""
    if _skip_audit_gate():
        return []
    chapters = _chapter_files(project)
    if not chapters:
        return []
    from scripts.audit_common import default_scan_path  # noqa: PLC0415

    latest = chapters[-1]
    errors: list[str] = []
    if phase >= 6:
        fmt = default_scan_path(project, latest, "format")
        st = _audit_scan_status(fmt)
        if st == "error":
            errors.append(f"{fmt.name}: format audit has blockers")
    if phase >= 8:
        deai = default_scan_path(project, latest, "deai")
        st = _audit_scan_status(deai)
        if st == "error":
            errors.append(f"{deai.name}: deai audit error")
    return errors


def validate_project_schemas(project: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_json_file(project / "canon" / "project.json", "project.schema.json"))
    progress = project / "canon" / "progress.json"
    if progress.is_file():
        errors.extend(validate_json_file(progress, "progress.schema.json"))
    return errors


def validate_registry() -> list[str]:
    path = reg.REGISTRY_PATH
    if not path.is_file():
        return []
    return validate_json_file(path, "registry.schema.json")


def artifact_checks(project: Path, phase: int) -> list[str]:
    """Filesystem + markdown structure checks for entering `phase`."""
    errors: list[str] = []

    if phase >= 1:
        errors.extend(_markdown_has_headings(project / "canon" / "concept-brief.md", CONCEPT_HEADINGS))

    if phase >= 2:
        if not (project / "story.md").is_file():
            errors.append("missing story.md")
        errors.extend(validate_json_file(project / "canon" / "project.json", "project.schema.json"))

    if phase >= 3:
        if _count_md_files(project / "characters") < 2:
            errors.append("Phase 2 incomplete: need ≥2 character profiles in characters/")
        locs = _count_md_files(project / "worldbuilding" / "locations")
        systems = _count_md_files(project / "worldbuilding" / "systems")
        if locs + systems < 1:
            errors.append("Phase 2 incomplete: need ≥1 location or system under worldbuilding/")

    if phase >= 4:
        arcs = _count_md_files(project / "plot" / "arcs")
        if arcs < 1:
            errors.append("Phase 3 incomplete: need ≥1 arc in plot/arcs/")
        if not (project / "plot" / "foreshadowing.md").is_file():
            errors.append("missing plot/foreshadowing.md")

    if phase >= 5:
        if not (project / "canon" / "voice-brief.md").is_file():
            errors.append("missing canon/voice-brief.md")

    if phase >= 6:
        if not _chapter_files(project):
            errors.append("Phase 5 incomplete: need ≥1 chapter in chapters/")
        errors.extend(validate_json_file(project / "canon" / "progress.json", "progress.schema.json"))

    if phase >= 7:
        review = latest_review_report(project)
        if review is None:
            errors.append("Phase 6 incomplete: missing reviews/chNN-review.md")
        elif not any(
            line.strip().lower().startswith(REVIEW_BLOCKERS)
            for line in review.read_text(encoding="utf-8").splitlines()
        ):
            errors.append(f"{review.name}: missing ## Blockers section")

    if phase >= 8:
        review = latest_review_report(project)
        if review and not any(
            line.strip().lower().startswith(REVIEW_DEAI)
            for line in review.read_text(encoding="utf-8").splitlines()
        ):
            errors.append(f"{review.name}: missing ## De-AI section (Phase 7)")

    return errors


def prior_phase_checks(project: Path, phase: int) -> list[str]:
    errors: list[str] = []
    if phase >= 1 and not phase0_complete(project):
        errors.append("Phase 0 not complete — mark Phase 0 [x] in task_plan.md or init with --concept")
    from scripts import node_completion as nec  # noqa: PLC0415

    if phase >= 1 and phase0_complete(project):
        errors.extend(nec.validate_phase0_project_gate(project))
    for p in range(1, min(phase, 9)):
        if not phase_done(project, p):
            errors.append(f"task_plan.md: Phase {p} not marked [x]")
    if phase >= 3:
        errors.extend(nec.validate_project_phase_gate(project, 2))
    if phase >= 4:
        errors.extend(nec.validate_project_phase_gate(project, 3))
    if phase >= 5:
        errors.extend(nec.validate_project_phase_gate(project, 4))
    if phase >= 6:
        errors.extend(nec.validate_project_phase_gate(project, 5))
    if phase >= 7:
        errors.extend(nec.validate_project_phase_gate(project, 6))
    if phase >= 8:
        errors.extend(nec.validate_project_phase_gate(project, 7))
    if phase >= 9:
        errors.extend(nec.validate_project_phase_gate(project, 8))
    return errors


def gate_entry_ok(project: Path, phase: int) -> tuple[bool, list[str]]:
    """Whether entering `phase` is satisfied on disk + task_plan (no manifest recursion)."""
    errors: list[str] = []
    phase = int(phase or 1)
    if phase >= 1 and not phase0_complete(project):
        errors.append("Phase 0 not complete in task_plan.md")
    for p in range(1, min(phase, 9)):
        if not phase_done(project, p):
            errors.append(f"task_plan.md: Phase {p} not marked [x]")
    errors.extend(artifact_checks(project, phase))
    errors.extend(validate_project_schemas(project))
    if phase >= 7:
        review = latest_review_report(project)
        if review is None:
            errors.append("no review report in reviews/chNN-review.md")
        elif has_open_blockers(review):
            errors.append(f"open blockers in {review.name}")
    errors.extend(optional_audit_scan_checks(project, phase))
    return len(errors) == 0, errors


def validate_gate(project: Path, phase: int) -> tuple[bool, list[str]]:
    errors: list[str] = []
    phase = int(phase or 1)

    errors.extend(prior_phase_checks(project, phase))
    errors.extend(artifact_checks(project, phase))
    errors.extend(validate_project_schemas(project))

    if phase >= 7:
        review = latest_review_report(project)
        if review is None:
            if "Phase 6 incomplete: missing reviews/chNN-review.md" not in errors:
                errors.append("no review report in reviews/chNN-review.md")
        elif has_open_blockers(review):
            errors.append(f"open blockers in {review.name}")

    errors.extend(optional_audit_scan_checks(project, phase))
    ok = len(errors) == 0
    return ok, errors


def run_gate(project: Path, phase: int) -> int:
    ok, errors = validate_gate(project, phase)
    if ok:
        print(f"GATE OK: project={project} phase>={phase}")
        return 0
    for msg in errors:
        print(f"GATE FAIL: {msg}", file=sys.stderr)
    return 1


def run_validate(project: Path, *, include_registry: bool = False) -> int:
    errors = validate_project_schemas(project)
    if include_registry:
        errors.extend(validate_registry())
    if errors:
        for msg in errors:
            print(f"VALIDATE FAIL: {msg}", file=sys.stderr)
        return 1
    print(f"VALIDATE OK: project={project}")
    return 0
