#!/usr/bin/env python3
"""Node Execution Contract (NEC) — completion manifest helpers."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GATE_CMD_RE = re.compile(r"pipeline\s+gate\s+--phase\s+(\d+)", re.I)
ENGINE_DIR = Path(__file__).resolve().parents[1]
NOVEL_CLI = ENGINE_DIR / "novel_cli.py"
DEMO_PROJECT = ENGINE_DIR.parent / "examples" / "demo-novel"

from scripts import intel_paths as intel
from scripts import suite_paths as sp

SCHEMA_NAME = "node-completion.schema.json"

# Phase 0 required subtasks for gate (fiction section may be hybrid/agent)
PHASE0_REQUIRED_DONE = frozenset({"P0-S0", "P0-S1", "P0-S3", "P0-S4"})
PHASE0_FICTION_MARKERS = ("### 番茄", "### 起点", "## 平台快照")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def completion_path_for_radar(radar_md: Path) -> Path:
    return radar_md.with_suffix(".completion.json")


def completion_path_for_project(project: Path, phase: int) -> Path:
    return project / "canon" / "nodes" / f"phase-{phase}.completion.json"


def phase0_subtask_templates() -> list[dict[str, Any]]:
    return [
        {
            "id": "P0-S0",
            "title": "确认 intel 路径与周期",
            "executor": "cli",
            "command": "novel intel paths",
            "status": "pending",
            "output_paths": [],
        },
        {
            "id": "P0-S1",
            "title": "短视频平台热点 CLI 扫描",
            "executor": "cli",
            "command": "novel intel scan --period week [--platforms ...]",
            "status": "pending",
            "output_paths": [],
        },
        {
            "id": "P0-S2",
            "title": "文字平台快照（番茄/起点/晋江/盐选）",
            "executor": "hybrid",
            "reference": "platform-scan-guide.md",
            "status": "pending",
            "output_paths": [],
        },
        {
            "id": "P0-S3",
            "title": "题材簇 Top10 + 雷达结构对齐模板",
            "executor": "hybrid",
            "reference": "radar-report-template.md",
            "status": "pending",
            "output_paths": [],
        },
        {
            "id": "P0-S4",
            "title": "短视频 rubric 评分 + 候选 concept",
            "executor": "cli",
            "command": "novel intel scan (concepts)",
            "status": "pending",
            "output_paths": [],
        },
        {
            "id": "P0-S7",
            "title": "intel rubric 审计（可选）",
            "executor": "cli",
            "command": "novel audit intel --radar intel/radar/….md",
            "status": "pending",
            "output_paths": [],
        },
        {
            "id": "P0-S5",
            "title": "用户确认 Top1–3 → approved concept-brief",
            "executor": "agent",
            "reference": "templates/concept-brief.md",
            "status": "pending",
            "output_paths": [],
        },
        {
            "id": "P0-S6",
            "title": "立项与 Phase 1 gate",
            "executor": "cli",
            "command": "novel init --concept ... && novel pipeline gate --phase 1",
            "status": "pending",
            "output_paths": [],
        },
    ]


def build_phase0_manifest(
    *,
    period_id: str,
    radar_md: Path,
    concepts_dir: Path | None = None,
) -> dict[str, Any]:
    subtasks = phase0_subtask_templates()
    return {
        "schema_version": "1.0",
        "phase": 0,
        "skill": "novel-market-scan",
        "period_id": period_id,
        "status": "partial",
        "started_at": utc_now(),
        "artifacts": {
            "radar_md": str(radar_md),
            "concepts_dir": str(concepts_dir or intel.CONCEPTS_DIR),
        },
        "subtasks": subtasks,
    }


def _set_subtask(manifest: dict[str, Any], sub_id: str, **updates: Any) -> None:
    for st in manifest.get("subtasks", []):
        if st.get("id") == sub_id:
            st.update(updates)
            return
    raise KeyError(f"subtask not found: {sub_id}")


def radar_has_fiction_sections(radar_md: Path) -> bool:
    if not radar_md.is_file():
        return False
    text = radar_md.read_text(encoding="utf-8")
    return any(marker in text for marker in PHASE0_FICTION_MARKERS)


def radar_has_topic_cluster(radar_md: Path) -> bool:
    if not radar_md.is_file():
        return False
    text = radar_md.read_text(encoding="utf-8")
    return "## 题材簇" in text or "## 题材热度榜" in text


def recompute_phase0_status(manifest: dict[str, Any], radar_md: Path) -> str:
    if radar_md.is_file():
        _set_subtask(manifest, "P0-S1", status="done", output_paths=[str(radar_md)])
    if radar_has_fiction_sections(radar_md):
        _set_subtask(
            manifest,
            "P0-S2",
            status="done",
            notes="fiction platform sections present in radar",
        )
    if radar_has_topic_cluster(radar_md):
        _set_subtask(manifest, "P0-S3", status="done")

    concepts = manifest.get("artifacts", {}).get("concepts_dir", "")
    if concepts:
        cdir = Path(concepts)
        if cdir.is_dir() and any(cdir.glob("*.md")):
            _set_subtask(
                manifest,
                "P0-S4",
                status="done",
                output_paths=[str(p) for p in sorted(cdir.glob("*.md"))[:5]],
            )

    by_id = {st["id"]: st for st in manifest.get("subtasks", [])}
    done_ids = {st["id"] for st in manifest["subtasks"] if st.get("status") == "done"}
    required_met = PHASE0_REQUIRED_DONE.issubset(done_ids)
    p05 = by_id.get("P0-S5", {})
    p06 = by_id.get("P0-S6", {})

    if required_met and p05.get("status") == "done" and p06.get("status") == "done":
        manifest["status"] = "complete"
        manifest["completed_at"] = utc_now()
    else:
        manifest["status"] = "partial"
    return manifest["status"]


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_manifest(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest_semantics(manifest: dict[str, Any]) -> list[str]:
    """NEC §4.3: complete forbids pending subtasks."""
    errors: list[str] = []
    if manifest.get("status") == "complete":
        pending = [st["id"] for st in manifest.get("subtasks", []) if st.get("status") == "pending"]
        if pending:
            errors.append(f"status=complete but pending subtasks: {', '.join(pending)}")
    return errors


def validate_manifest_file(path: Path) -> list[str]:
    from jsonschema import Draft7Validator  # noqa: PLC0415

    from scripts.pipeline_gate import load_schema  # noqa: PLC0415

    if not path.is_file():
        return [f"missing completion manifest: {path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.name}: invalid JSON — {exc.msg}"]
    schema = load_schema(SCHEMA_NAME)
    errors: list[str] = []
    for err in sorted(Draft7Validator(schema).iter_errors(data), key=lambda e: list(e.path)):
        loc = ".".join(str(part) for part in err.path) or "(root)"
        errors.append(f"{path.name}: {loc} — {err.message}")
    return errors


def validate_phase0_intel(*, week_id: str | None = None, for_gate: bool = False) -> list[str]:
    """Validate suite-level Phase 0 completion for current ISO week."""
    if for_gate:
        return validate_phase0_intel_for_gate(week_id=week_id)
    errors: list[str] = []
    wid = week_id or intel.iso_week_id()
    radar = intel.radar_path_for_week(wid)
    completion = completion_path_for_radar(radar)

    if not radar.is_file():
        errors.append(f"Phase 0: missing radar {radar}")
        return errors

    errors.extend(validate_manifest_file(completion))
    if errors:
        return errors

    manifest = load_manifest(completion)
    assert manifest is not None
    errors.extend(validate_phase0_manifest_content(manifest, radar, for_gate=False))
    errors.extend(validate_manifest_semantics(manifest))
    return errors


def validate_phase0_manifest_content(
    manifest: dict[str, Any],
    radar_md: Path,
    *,
    for_gate: bool = False,
) -> list[str]:
    errors: list[str] = []
    if manifest.get("status") not in ("complete", "partial", "pending"):
        errors.append("Phase 0 manifest: invalid status")

    done = {st["id"] for st in manifest.get("subtasks", []) if st.get("status") == "done"}
    missing = PHASE0_REQUIRED_DONE - done
    if missing:
        errors.append(f"Phase 0 manifest: required subtasks not done: {', '.join(sorted(missing))}")

    if not radar_has_topic_cluster(radar_md):
        errors.append(f"{radar_md.name}: missing topic cluster section (题材热度榜/题材簇)")

    return errors


def build_project_phase0_manifest(*, project: Path, concept_path: Path, radar_md: Path | None) -> dict[str, Any]:
    subtasks = phase0_subtask_templates()
    for st in subtasks:
        if st["id"] in ("P0-S5", "P0-S6"):
            st["status"] = "done"
        if st["id"] == "P0-S5":
            st["output_paths"] = [str(concept_path)]
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "phase": 0,
        "skill": "novel-market-scan",
        "project_slug": project.name,
        "status": "complete",
        "started_at": utc_now(),
        "completed_at": utc_now(),
        "artifacts": {
            "concept_brief": str(project / "canon" / "concept-brief.md"),
            "radar_md": str(radar_md) if radar_md else "",
        },
        "subtasks": subtasks,
    }
    return manifest


def _mark_subtasks_done(manifest: dict[str, Any], ids: frozenset[str]) -> None:
    for st in manifest.get("subtasks", []):
        if st.get("id") in ids:
            st["status"] = "done"


def build_project_phase1_manifest(*, project: Path) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "phase": 1,
        "skill": "story-init",
        "project_slug": project.name,
        "status": "complete",
        "started_at": utc_now(),
        "completed_at": utc_now(),
        "artifacts": {
            "story_md": str(project / "story.md"),
            "project_json": str(project / "canon" / "project.json"),
        },
        "subtasks": [
            {
                "id": "P1-S0",
                "title": "确认 active / slug",
                "executor": "cli",
                "command": "novel list",
                "status": "done",
                "output_paths": [],
            },
            {
                "id": "P1-S1",
                "title": "story.md 与 premise",
                "executor": "agent",
                "reference": "story-template.md",
                "status": "done",
                "output_paths": [str(project / "story.md")],
            },
            {
                "id": "P1-S2",
                "title": "novel init 脚手架",
                "executor": "cli",
                "command": "novel init",
                "status": "done",
                "output_paths": [str(project)],
            },
            {
                "id": "P1-S3",
                "title": "pipeline gate phase 2",
                "executor": "cli",
                "command": "novel pipeline gate --phase 2",
                "status": "pending",
                "output_paths": [],
            },
        ],
    }


def write_project_phase1_manifest(project: Path) -> Path:
    path = completion_path_for_project(project, 1)
    (project / "canon" / "nodes").mkdir(parents=True, exist_ok=True)
    write_manifest(path, build_project_phase1_manifest(project=project))
    return path


def write_project_phase0_manifest(project: Path, *, concept_path: Path, radar_md: Path | None) -> Path:
    path = completion_path_for_project(project, 0)
    write_manifest(path, build_project_phase0_manifest(project=project, concept_path=concept_path, radar_md=radar_md))
    return path


def validate_phase0_project_gate(project: Path) -> list[str]:
    """Phase 1 gate: project manifest and/or suite intel manifest."""
    errors: list[str] = []
    proj_manifest_path = completion_path_for_project(project, 0)
    if proj_manifest_path.is_file():
        errors.extend(validate_manifest_file(proj_manifest_path))
        if errors:
            return errors
        manifest = load_manifest(proj_manifest_path)
        assert manifest is not None
        if manifest.get("status") != "complete":
            errors.append(f"{proj_manifest_path.name}: status must be complete")
        p05 = any(
            st.get("id") == "P0-S5" and st.get("status") == "done"
            for st in manifest.get("subtasks", [])
        )
        p06 = any(
            st.get("id") == "P0-S6" and st.get("status") == "done"
            for st in manifest.get("subtasks", [])
        )
        if not (p05 and p06):
            errors.append("Phase 0 project manifest: P0-S5 and P0-S6 must be done")
        errors.extend(validate_manifest_semantics(manifest))
        return errors

    errors.extend(validate_phase0_intel_for_gate())
    return errors


def validate_phase0_intel_for_gate(*, week_id: str | None = None) -> list[str]:
    """Gate phase 1: require radar + completion manifest for current ISO week."""
    wid = week_id or intel.iso_week_id()
    radar = intel.radar_path_for_week(wid)
    completion = completion_path_for_radar(radar)
    errors: list[str] = []
    if not radar.is_file():
        errors.append(f"Phase 0: missing {radar} — run novel intel scan --period week")
        return errors
    errors.extend(validate_manifest_file(completion))
    if errors:
        return errors
    manifest = load_manifest(completion)
    assert manifest is not None
    errors.extend(validate_phase0_manifest_content(manifest, radar, for_gate=True))
    errors.extend(validate_manifest_semantics(manifest))
    return errors


def mark_phase0_cli_done(
    *,
    radar_md: Path,
    period_id: str,
    concepts_dir: Path | None,
    no_concepts: bool,
) -> Path:
    """After intel_scan: write/update completion manifest."""
    completion = completion_path_for_radar(radar_md)
    manifest = load_manifest(completion) or build_phase0_manifest(
        period_id=period_id,
        radar_md=radar_md,
        concepts_dir=concepts_dir,
    )
    _set_subtask(
        manifest,
        "P0-S0",
        status="done",
        output_paths=[str(intel.INTEL_DIR), str(radar_md)],
    )
    recompute_phase0_status(manifest, radar_md)
    if not no_concepts:
        recompute_phase0_status(manifest, radar_md)
    promote_phase0_if_demo_project_linked(radar_md)
    write_manifest(completion, manifest)
    return completion


def promote_phase0_if_demo_project_linked(radar_md: Path) -> None:
    """When demo-novel (or any scaffolded book) exists, close P0-S5/S6 on suite radar manifest."""
    if not DEMO_PROJECT.is_dir():
        return
    concept = DEMO_PROJECT / "canon" / "concept-brief.md"
    project_json = DEMO_PROJECT / "canon" / "project.json"
    if not concept.is_file() or not project_json.is_file():
        return
    completion = completion_path_for_radar(radar_md)
    manifest = load_manifest(completion)
    if manifest is None:
        return
    _set_subtask(manifest, "P0-S5", status="done", output_paths=[str(concept)])
    from scripts.pipeline_gate import run_gate  # noqa: PLC0415

    from scripts.pipeline_gate import gate_entry_ok  # noqa: PLC0415

    ok, _ = gate_entry_ok(DEMO_PROJECT, 1)
    if ok:
        _set_subtask(manifest, "P0-S6", status="done", output_paths=[str(DEMO_PROJECT)])
    recompute_phase0_status(manifest, radar_md)
    write_manifest(completion, manifest)


def _count_md_files(folder: Path) -> int:
    if not folder.is_dir():
        return 0
    return sum(1 for p in folder.glob("*.md") if not p.name.startswith("_"))


def build_project_phase2_manifest(*, project: Path) -> dict[str, Any]:
    chars = sorted(project.glob("characters/*.md"))
    char_paths = [str(p) for p in chars if not p.name.startswith("_")]
    locs = _count_md_files(project / "worldbuilding" / "locations")
    systems = _count_md_files(project / "worldbuilding" / "systems")
    artifacts_ok = len(char_paths) >= 2 and (locs + systems) >= 1
    status = "complete" if artifacts_ok else "partial"
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "phase": 2,
        "skill": "worldbuilding+character-management",
        "project_slug": project.name,
        "status": status,
        "started_at": utc_now(),
        "artifacts": {
            "characters": char_paths[:10],
            "worldbuilding_locations": str(project / "worldbuilding" / "locations"),
            "worldbuilding_systems": str(project / "worldbuilding" / "systems"),
        },
        "subtasks": [
            {
                "id": "P2a-S1",
                "title": "地点/系统",
                "executor": "agent",
                "reference": "worldbuilding/node-dispatch.md",
                "status": "done" if (locs + systems) >= 1 else "pending",
                "output_paths": [],
            },
            {
                "id": "P2b-S1",
                "title": "人物卡 ≥2",
                "executor": "agent",
                "reference": "character-management/node-dispatch.md",
                "status": "done" if len(char_paths) >= 2 else "pending",
                "output_paths": char_paths[:5],
            },
            {
                "id": "P2b-S3",
                "title": "novel relations check",
                "executor": "cli",
                "command": "novel relations check",
                "status": "pending",
                "output_paths": [],
            },
            {
                "id": "P2-S4",
                "title": "pipeline gate phase 3",
                "executor": "cli",
                "command": "novel pipeline gate --phase 3",
                "status": "pending",
                "output_paths": [],
            },
        ],
    }
    if artifacts_ok:
        manifest["completed_at"] = utc_now()
    return manifest


def build_project_phase3_manifest(*, project: Path) -> dict[str, Any]:
    arcs = sorted((project / "plot" / "arcs").glob("*.md")) if (project / "plot" / "arcs").is_dir() else []
    foreshadow = project / "plot" / "foreshadowing.md"
    ok = len(arcs) >= 1 and foreshadow.is_file()
    status = "complete" if ok else "partial"
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "phase": 3,
        "skill": "plot-structure",
        "project_slug": project.name,
        "status": status,
        "started_at": utc_now(),
        "artifacts": {
            "arcs": [str(p) for p in arcs],
            "foreshadowing": str(foreshadow) if foreshadow.is_file() else "",
        },
        "subtasks": [
            {
                "id": "P3-S1",
                "title": "plot arcs ≥1",
                "executor": "agent",
                "reference": "plot-structure/node-dispatch.md",
                "status": "done" if arcs else "pending",
                "output_paths": [str(p) for p in arcs[:3]],
            },
            {
                "id": "P3-S2",
                "title": "foreshadowing.md",
                "executor": "agent",
                "status": "done" if foreshadow.is_file() else "pending",
                "output_paths": [str(foreshadow)] if foreshadow.is_file() else [],
            },
            {
                "id": "P3-S3",
                "title": "pipeline gate phase 4",
                "executor": "cli",
                "command": "novel pipeline gate --phase 4",
                "status": "pending",
                "output_paths": [],
            },
        ],
    }
    if ok:
        manifest["completed_at"] = utc_now()
    return manifest


def _chapter_files(project: Path) -> list[Path]:
    chapters = project / "chapters"
    if not chapters.is_dir():
        return []
    return sorted(p for p in chapters.glob("*.md") if not p.name.startswith("_"))


def _latest_chapter_scan_json(project: Path, suffix: str) -> Path | None:
    chapters = _chapter_files(project)
    if not chapters:
        return None
    from scripts.audit_common import default_scan_path  # noqa: PLC0415

    path = default_scan_path(project, chapters[-1], suffix)
    return path if path.is_file() else None


def _audit_scan_status(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "error"
    return str(data.get("status", ""))


def _latest_review(project: Path) -> Path | None:
    reviews_dir = project / "reviews"
    if not reviews_dir.is_dir():
        return None
    reviews = sorted(reviews_dir.glob("ch*-review.md"), key=lambda p: p.stat().st_mtime)
    return reviews[-1] if reviews else None


def _review_has_section(report: Path, heading_prefix: str) -> bool:
    if not report.is_file():
        return False
    prefix = heading_prefix.lower()
    for line in report.read_text(encoding="utf-8").splitlines():
        if line.strip().lower().startswith(prefix):
            return True
    return False


def voice_brief_ready(path: Path) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    return "## 发表平台" in text and "platform_target" in text


def build_project_phase4_manifest(*, project: Path) -> dict[str, Any]:
    vb = project / "canon" / "voice-brief.md"
    ok = voice_brief_ready(vb)
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "phase": 4,
        "skill": "voice-brief",
        "project_slug": project.name,
        "status": "complete" if ok else "partial",
        "started_at": utc_now(),
        "artifacts": {"voice_brief": str(vb) if vb.is_file() else ""},
        "subtasks": [
            {
                "id": "P4-S1",
                "title": "填写 voice-brief",
                "executor": "agent",
                "reference": "templates/voice-brief.md",
                "status": "done" if ok else "pending",
                "output_paths": [str(vb)] if ok else [],
            },
            {
                "id": "P4-S2",
                "title": "pipeline gate phase 5",
                "executor": "cli",
                "command": "novel pipeline gate --phase 5",
                "status": "pending",
                "output_paths": [],
            },
        ],
    }
    if ok:
        manifest["completed_at"] = utc_now()
    return manifest


def build_project_phase5_manifest(*, project: Path) -> dict[str, Any]:
    chapters = _chapter_files(project)
    snaps = list((project / "canon" / "snapshots").glob("*.md")) if (project / "canon" / "snapshots").is_dir() else []
    format_scan = _latest_chapter_scan_json(project, "format")
    fmt_ok = _audit_scan_status(format_scan) in (None, "ok", "warn")
    ok = len(chapters) >= 1 and fmt_ok
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "phase": 5,
        "skill": "chapter-writing",
        "project_slug": project.name,
        "status": "complete" if ok else "partial",
        "started_at": utc_now(),
        "artifacts": {
            "chapters": [str(p) for p in chapters[:10]],
            "snapshots": [str(p) for p in snaps[:5]],
            "format_scan_json": str(format_scan) if format_scan else "",
        },
        "subtasks": [
            {
                "id": "P5-S3",
                "title": "章节正文",
                "executor": "agent",
                "reference": "chapter-writing/node-dispatch.md",
                "status": "done" if ok else "pending",
                "output_paths": [str(chapters[-1])] if chapters else [],
            },
            {
                "id": "P5-S8",
                "title": "chapter format lint",
                "executor": "cli",
                "command": "novel audit format --json",
                "status": "done" if (format_scan and fmt_ok) or (len(chapters) >= 1 and fmt_ok) else "pending",
                "output_paths": [str(format_scan)] if format_scan else [],
            },
            {
                "id": "P5-S4",
                "title": "章后 snapshot",
                "executor": "agent",
                "reference": "templates/snapshot-chapter.md",
                "status": "done" if snaps else "pending",
                "output_paths": [str(snaps[-1])] if snaps else [],
            },
            {
                "id": "P5-S6",
                "title": "pipeline gate phase 6",
                "executor": "cli",
                "command": "novel pipeline gate --phase 6",
                "status": "pending",
                "output_paths": [],
            },
        ],
    }
    if ok:
        manifest["completed_at"] = utc_now()
    return manifest


def build_project_phase6_manifest(*, project: Path) -> dict[str, Any]:
    review = _latest_review(project)
    blockers_section = review is not None and _review_has_section(review, "## blockers")
    blockers_closed = review is not None and not _review_has_open_blockers(review)
    format_scan = _latest_chapter_scan_json(project, "format")
    blocker_scan = _latest_chapter_scan_json(project, "blocker")
    ok = review is not None and blockers_section and blockers_closed
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "phase": 6,
        "skill": "novel-review",
        "project_slug": project.name,
        "status": "complete" if ok else "partial",
        "started_at": utc_now(),
        "artifacts": {
            "review": str(review) if review else "",
            "format_scan_json": str(format_scan) if format_scan else "",
            "blocker_scan_json": str(blocker_scan) if blocker_scan else "",
        },
        "subtasks": [
            {
                "id": "P6-S1",
                "title": "forge 1-3 + review 报告",
                "executor": "agent",
                "reference": "novel-review/node-dispatch.md",
                "status": "done" if ok else "pending",
                "output_paths": [str(review)] if review else [],
            },
            {
                "id": "P6-S4",
                "title": "format + blocker audit",
                "executor": "cli",
                "command": "novel audit format && novel audit blocker",
                "status": "done"
                if ok and (format_scan is not None or blocker_scan is not None)
                else "pending",
                "output_paths": [str(p) for p in (format_scan, blocker_scan) if p],
            },
            {
                "id": "P6-S3",
                "title": "pipeline gate phase 7",
                "executor": "cli",
                "command": "novel pipeline gate --phase 7",
                "status": "pending",
                "output_paths": [],
            },
        ],
    }
    if ok:
        manifest["completed_at"] = utc_now()
    return manifest


def build_project_phase7_manifest(*, project: Path) -> dict[str, Any]:
    review = _latest_review(project)
    has_deai = review is not None and _review_has_section(review, "## de-ai")
    deai_scan = _latest_chapter_scan_json(project, "deai")
    scan_ok = _audit_scan_status(deai_scan) != "error"
    ok = has_deai and scan_ok
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "phase": 7,
        "skill": "novel-review",
        "project_slug": project.name,
        "status": "complete" if ok else "partial",
        "started_at": utc_now(),
        "artifacts": {
            "review": str(review) if review else "",
            "deai_scan_json": str(deai_scan) if deai_scan else "",
        },
        "subtasks": [
            {
                "id": "P7-S0",
                "title": "deai audit dispatch",
                "executor": "cli",
                "reference": "deai-audit-dispatch.md",
                "status": "done" if deai_scan else "pending",
                "output_paths": [],
            },
            {
                "id": "P7-S1",
                "title": "novel audit deai",
                "executor": "cli",
                "command": "novel audit deai --json",
                "status": "done" if deai_scan and scan_ok else "pending",
                "output_paths": [str(deai_scan)] if deai_scan else [],
            },
            {
                "id": "P7-S2",
                "title": "deai-checklist + Sable",
                "executor": "agent",
                "reference": "deai-checklist.md",
                "status": "done" if has_deai else "pending",
                "output_paths": [],
            },
            {
                "id": "P7-S3",
                "title": "review De-AI 节",
                "executor": "agent",
                "status": "done" if ok else "pending",
                "output_paths": [str(review)] if review and ok else [],
            },
        ],
    }
    if ok:
        manifest["completed_at"] = utc_now()
    return manifest


def build_project_phase8_manifest(*, project: Path) -> dict[str, Any]:
    review = _latest_review(project)
    has_reval = review is not None and (
        _review_has_section(review, "## re-validate") or "re-validate" in review.read_text(encoding="utf-8").lower()
    )
    ok = has_reval
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "phase": 8,
        "skill": "novel-review",
        "project_slug": project.name,
        "status": "complete" if ok else "partial",
        "started_at": utc_now(),
        "artifacts": {"review": str(review) if review else ""},
        "subtasks": [
            {
                "id": "P8-S1",
                "title": "re-review round",
                "executor": "agent",
                "reference": "review-repair-spec.md",
                "status": "done" if ok else "pending",
                "output_paths": [str(review)] if review and ok else [],
            },
        ],
    }
    if ok:
        manifest["completed_at"] = utc_now()
    return manifest


def _review_has_open_blockers(report: Path) -> bool:
    from scripts.pipeline_gate import has_open_blockers  # noqa: PLC0415

    return has_open_blockers(report)


def build_project_phase9_manifest(*, project: Path) -> dict[str, Any]:
    epubs = list((project / "dist").glob("*.epub")) if (project / "dist").is_dir() else []
    review = _latest_review(project)
    blockers_ok = review is None or not _review_has_open_blockers(review)
    ok = len(epubs) >= 1 and blockers_ok
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "phase": 9,
        "skill": "novel-export",
        "project_slug": project.name,
        "status": "complete" if ok else "partial",
        "started_at": utc_now(),
        "artifacts": {"epub": [str(p) for p in epubs[:3]]},
        "subtasks": [
            {
                "id": "P9-S0",
                "title": "pipeline gate phase 9",
                "executor": "cli",
                "command": "novel pipeline gate --phase 9",
                "status": "done" if blockers_ok else "pending",
                "output_paths": [],
            },
            {
                "id": "P9-S1",
                "title": "Quill export audit",
                "executor": "agent",
                "reference": "quill-export-audit.md",
                "status": "pending",
                "output_paths": [],
            },
            {
                "id": "P9-S2",
                "title": "create_epub",
                "executor": "cli",
                "command": "novel export",
                "status": "done" if epubs else "pending",
                "output_paths": [str(epubs[0])] if epubs else [],
            },
        ],
    }
    if ok:
        manifest["completed_at"] = utc_now()
    return manifest


def _sync_phase1(project: Path) -> dict[str, Any]:
    manifest = build_project_phase1_manifest(project=project)
    if (project / "story.md").is_file() and (project / "canon" / "project.json").is_file():
        _mark_subtasks_done(manifest, frozenset({"P1-S0", "P1-S1", "P1-S2"}))
        manifest["status"] = "complete"
        manifest["completed_at"] = utc_now()
    return manifest


SYNC_PHASE_BUILDERS: dict[int, Any] = {}


def _register_sync_builders() -> None:
    SYNC_PHASE_BUILDERS.update(
        {
            1: lambda p: _sync_phase1(p),
            2: lambda p: build_project_phase2_manifest(project=p),
            3: lambda p: build_project_phase3_manifest(project=p),
            4: lambda p: build_project_phase4_manifest(project=p),
            5: lambda p: build_project_phase5_manifest(project=p),
            6: lambda p: build_project_phase6_manifest(project=p),
            7: lambda p: build_project_phase7_manifest(project=p),
            8: lambda p: build_project_phase8_manifest(project=p),
            9: lambda p: build_project_phase9_manifest(project=p),
        }
    )


_register_sync_builders()

SYNC_PHASE_MAX = 9


def _gate_phase_from_subtask(st: dict[str, Any]) -> int | None:
    cmd = st.get("command") or ""
    match = GATE_CMD_RE.search(cmd)
    return int(match.group(1)) if match else None


def _relations_check_ok(project: Path) -> bool:
    r = subprocess.run(
        [sys.executable, str(NOVEL_CLI), "relations", "check", "--project", str(project)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return r.returncode == 0


def probe_agent_subtask(project: Path, st: dict[str, Any]) -> bool:
    sub_id = st.get("id", "")
    if sub_id == "P9-S1":
        dist = project / "dist"
        return dist.is_dir() and any(dist.glob("*.epub"))
    ref = st.get("reference") or ""
    if sub_id == "P4-S1" or "voice-brief" in ref:
        return voice_brief_ready(project / "canon" / "voice-brief.md")
    return False


def finalize_project_manifest(project: Path, manifest: dict[str, Any]) -> None:
    """Mark gate/cli/agent subtasks from disk + gate runs; recompute status (NEC P1–P3)."""
    from scripts.pipeline_gate import gate_entry_ok  # noqa: PLC0415

    for st in manifest.get("subtasks", []):
        if st.get("status") == "done":
            continue
        executor = st.get("executor")
        if executor == "cli":
            gate_phase = _gate_phase_from_subtask(st)
            if gate_phase is not None:
                ok, _ = gate_entry_ok(project, gate_phase)
                if ok:
                    st["status"] = "done"
                continue
            if st.get("id") == "P2b-S3" and _relations_check_ok(project):
                st["status"] = "done"
        elif executor in ("agent", "hybrid") and probe_agent_subtask(project, st):
            st["status"] = "done"

    recompute_project_manifest_status(manifest)


def recompute_project_manifest_status(manifest: dict[str, Any]) -> None:
    subs = manifest.get("subtasks", [])
    pending = [s for s in subs if s.get("status") == "pending"]
    if not pending:
        manifest["status"] = "complete"
        manifest["completed_at"] = utc_now()
    else:
        if any(s.get("status") == "done" for s in subs):
            manifest["status"] = "partial"
        else:
            manifest["status"] = "pending"
        manifest.pop("completed_at", None)


def sync_project_phase_manifest(project: Path, phase: int) -> Path:
    """Rebuild phase-N.completion.json from on-disk artifacts."""
    (project / "canon" / "nodes").mkdir(parents=True, exist_ok=True)
    builder = SYNC_PHASE_BUILDERS.get(phase)
    if builder is None:
        raise ValueError(f"sync not implemented for phase {phase} (max {SYNC_PHASE_MAX})")
    manifest = builder(project)
    finalize_project_manifest(project, manifest)
    path = completion_path_for_project(project, phase)
    write_manifest(path, manifest)
    return path


def validate_project_phase_gate(project: Path, phase: int) -> list[str]:
    """Require phase-N completion manifest when entering gate phase N+1."""
    path = completion_path_for_project(project, phase)
    errors: list[str] = []
    if not path.is_file():
        errors.append(
            f"Phase {phase}: missing {path.relative_to(project)} — run: "
            f"novel node sync --phase {phase} --project {project}"
        )
        return errors
    errors.extend(validate_manifest_file(path))
    if errors:
        return errors
    manifest = load_manifest(path)
    assert manifest is not None
    if manifest.get("status") != "complete":
        errors.append(
            f"{path.name}: status={manifest.get('status')} — run novel node sync --phase {phase}"
        )
    errors.extend(validate_manifest_semantics(manifest))
    return errors
