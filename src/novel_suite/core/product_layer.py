"""Novel Suite product layer — read-only index of novel-suite/ assets."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from novel_suite.core.contracts import novel_suite_root, run_core_contract_checks
from novel_suite.core.paths import suite_root
from novel_suite.core.result import Result, artifact, error_result, ok_result
from novel_suite.core import errors as E

_SAFE_NAME = re.compile(r"^[\w\u4e00-\u9fff\-]+$", re.UNICODE)

_READABLE_SUFFIXES = frozenset({".md", ".json", ".jsonl", ".csv", ".xml", ".edl"})

_ASSET_TYPE_BY_SUFFIX: dict[str, str] = {
    ".md": "markdown",
    ".json": "json",
    ".jsonl": "jsonl",
    ".csv": "csv",
    ".xml": "xml",
    ".edl": "edl",
}


def video_production_root() -> Path:
    return novel_suite_root() / "video-production"


def product_layer_root() -> Path:
    return novel_suite_root()


def _vp() -> Path:
    return video_production_root()


# category -> (base_path, kind)
_CATEGORY_DIRS: dict[str, tuple[Path, str]] = {
    "contracts": (novel_suite_root() / "core" / "contracts", "schema"),
    "gates": (novel_suite_root() / "core" / "gates", "md"),
    "workflows": (novel_suite_root() / "core" / "workflows", "md"),
    "prompt_packs": (novel_suite_root() / "prompt-packs", "md"),
    "rules_packs": (novel_suite_root() / "rules-packs", "rules"),
    "adapters": (novel_suite_root() / "adapters", "adapter"),
    "examples": (novel_suite_root() / "examples", "example"),
    "video_production_contracts": (_vp() / "contracts", "md"),
    "video_production_workflows": (_vp() / "workflows", "md"),
    "video_production_gates": (_vp() / "gates", "md"),
    "video_production_adapters": (_vp() / "adapters", "adapter"),
    "video_quality_definitions": (_vp() / "quality" / "definitions", "md"),
    "video_quality_gates": (_vp() / "quality" / "gates", "md"),
    "video_quality_taxonomies": (_vp() / "quality" / "taxonomies", "md"),
    "video_quality_repair": (_vp() / "quality" / "repair", "md"),
    "video_quality_reports": (_vp() / "quality" / "reports", "md"),
    "video_handoff_common": (_vp() / "handoff" / "common", "md"),
    "video_handoff_ai_generation": (_vp() / "handoff" / "ai-video-generation", "md"),
    "video_handoff_timeline": (_vp() / "handoff" / "editing-timeline", "md"),
    "video_handoff_vfx": (_vp() / "handoff" / "compositing-vfx", "md"),
    "video_handoff_local_processing": (_vp() / "handoff" / "local-processing", "md"),
    "video_handoff_rights_risk": (_vp() / "handoff" / "rights-and-risk", "md"),
    "video_production_examples": (_vp() / "examples", "vp_example"),
    "workflow_contracts": (novel_suite_root() / "workflow-contracts" / "examples", "wf_contract"),
}


def get_product_category_ids() -> list[str]:
    return list(_CATEGORY_DIRS.keys())


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _asset_entry(root: Path, path: Path, *, name: str, asset_type: str) -> dict[str, str]:
    return {
        "name": name,
        "path": _rel(root, path),
        "type": asset_type,
    }


def _list_md_files(root: Path, base: Path, *, skip_readme: bool = True) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    if not base.is_dir():
        return items
    for path in sorted(base.glob("*.md")):
        if skip_readme and path.name.upper() == "README.MD":
            continue
        items.append(_asset_entry(root, path, name=path.stem, asset_type="markdown"))
    return items


def _list_rules_packs(root: Path, base: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    if not base.is_dir():
        return items
    for agent_dir in sorted(base.iterdir()):
        if not agent_dir.is_dir() or agent_dir.name == "README.md":
            continue
        entry = "AGENTS.md" if agent_dir.name == "codex" else "rules.md"
        path = agent_dir / entry
        if path.is_file():
            items.append(_asset_entry(root, path, name=agent_dir.name, asset_type="markdown"))
    return items


def _list_adapters(root: Path, base: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    if not base.is_dir():
        return items
    for adapter_dir in sorted(base.iterdir()):
        if not adapter_dir.is_dir():
            continue
        path = adapter_dir / "ADAPTER_DISABLED_BY_DEFAULT.md"
        if path.is_file():
            items.append(_asset_entry(root, path, name=adapter_dir.name, asset_type="markdown"))
    return items


def _list_examples(root: Path, base: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    if not base.is_dir():
        return items
    for child in sorted(base.iterdir()):
        if child.is_dir():
            readme = child / "README.md"
            if readme.is_file():
                items.append(_asset_entry(root, readme, name=child.name, asset_type="markdown"))
    return items


def _list_vp_examples(root: Path, base: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    if not base.is_dir():
        return items
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        readme = child / "README.md"
        if readme.is_file():
            items.append(_asset_entry(root, readme, name=child.name, asset_type="markdown"))
        handoff_readme = child / "handoff" / "README.md"
        if handoff_readme.is_file():
            items.append(
                _asset_entry(
                    root,
                    handoff_readme,
                    name=f"{child.name}_handoff",
                    asset_type="markdown",
                )
            )
    return items


def _list_wf_contracts(root: Path, base: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    if not base.is_dir():
        return items
    for path in sorted(base.glob("*.contract.json")):
        items.append(
            _asset_entry(root, path, name=path.name.replace(".contract.json", ""), asset_type="json")
        )
    return items


def _list_category_assets(category: str) -> list[dict[str, str]]:
    root = suite_root()
    if category not in _CATEGORY_DIRS:
        return []
    base, kind = _CATEGORY_DIRS[category]
    if kind == "wf_contract":
        return _list_wf_contracts(root, base)
    if kind == "rules":
        return _list_rules_packs(root, base)
    if kind == "adapter":
        return _list_adapters(root, base)
    if kind == "example":
        return _list_examples(root, base)
    if kind == "vp_example":
        return _list_vp_examples(root, base)
    if not base.is_dir():
        return []
    if category == "contracts":
        items: list[dict[str, str]] = []
        for stem in ("story_bible", "chapter_context", "scene_to_video", "asset_registry"):
            for ext in (".schema.md", ".schema.json"):
                path = base / f"{stem}{ext}"
                if path.is_file():
                    items.append(
                        _asset_entry(
                            root,
                            path,
                            name=f"{stem}{ext.replace('.schema', '')}",
                            asset_type="json" if ext.endswith(".json") else "markdown",
                        )
                    )
        return items
    return _list_md_files(root, base, skip_readme=category != "prompt_packs")


def list_product_assets() -> dict[str, Any]:
    """Return all product-layer categories and asset entries (read-only metadata)."""
    root = suite_root()
    ns = product_layer_root()
    categories: dict[str, list[dict[str, str]]] = {}
    for cat in _CATEGORY_DIRS:
        categories[cat] = _list_category_assets(cat)
    return {
        "root": _rel(root, ns),
        "video_production_root": _rel(root, _vp()) if _vp().is_dir() else None,
        "categories": categories,
        "category_count": len(categories),
        "asset_count": sum(len(v) for v in categories.values()),
    }


def _resolve_asset_path(category: str, name: str) -> Path:
    if category not in _CATEGORY_DIRS:
        raise ValueError(f"{E.PRODUCT_INVALID_CATEGORY}: unknown category {category!r}")
    safe = (name or "").strip()
    if not safe or not _SAFE_NAME.match(safe):
        raise ValueError(f"{E.PRODUCT_INVALID_NAME}: invalid asset name {name!r}")
    if ".." in safe or "/" in safe or "\\" in safe:
        raise ValueError(f"{E.PRODUCT_PATH_TRAVERSAL}: rejected path in name")

    ns = product_layer_root()
    base, kind = _CATEGORY_DIRS[category]

    if kind == "rules":
        entry = "AGENTS.md" if safe == "codex" else "rules.md"
        candidate = (base / safe / entry).resolve()
    elif kind == "adapter":
        candidate = (base / safe / "ADAPTER_DISABLED_BY_DEFAULT.md").resolve()
    elif kind == "example":
        candidate = (base / safe / "README.md").resolve()
    elif kind == "vp_example":
        if safe.endswith("_handoff"):
            project = safe[: -len("_handoff")]
            candidate = (base / project / "handoff" / "README.md").resolve()
        else:
            candidate = (base / safe / "README.md").resolve()
    elif kind == "wf_contract":
        candidate = (base / f"{safe}.contract.json").resolve()
    elif category == "contracts":
        if safe.endswith(".json") or safe.endswith("_json"):
            stem = safe.replace("_json", "").replace(".json", "")
            candidate = (base / f"{stem}.schema.json").resolve()
        else:
            stem = safe.replace(".md", "")
            candidate = (base / f"{stem}.schema.md").resolve()
    else:
        candidate = (base / f"{safe}.md").resolve()

    try:
        candidate.relative_to(ns.resolve())
    except ValueError as exc:
        raise ValueError(f"{E.PRODUCT_PATH_TRAVERSAL}: {candidate}") from exc

    if candidate.suffix not in _READABLE_SUFFIXES:
        raise ValueError(f"{E.PRODUCT_NOT_FOUND}: unsupported asset type")
    return candidate


def read_product_asset(category: str, name: str) -> dict[str, Any]:
    """Read a single product-layer asset; never reads novels/**."""
    path = _resolve_asset_path(category, name)
    if not path.is_file():
        raise ValueError(f"{E.PRODUCT_NOT_FOUND}: {category}/{name}")
    root = suite_root()
    text = path.read_text(encoding="utf-8")
    asset_type = _ASSET_TYPE_BY_SUFFIX.get(path.suffix, "text")
    payload: dict[str, Any] = {
        "category": category,
        "name": name,
        "path": _rel(root, path),
        "type": asset_type,
        "size_bytes": path.stat().st_size,
        "content_text": text,
    }
    if path.suffix == ".json":
        payload["content"] = json.loads(text)
    else:
        payload["content"] = text
    return payload


def _append_check(
    checks: list[dict[str, Any]],
    root: Path,
    ns: Path,
    rel: str,
) -> None:
    path = ns / Path(rel)
    checks.append(
        {
            "name": f"product.{rel.replace('/', '.')}",
            "ok": path.is_file(),
            "path": _rel(root, path) if path.is_file() else str(path),
            **({} if path.is_file() else {"error": "missing"}),
        }
    )


def validate_product_layer() -> list[dict[str, Any]]:
    """Validate product-layer completeness (contracts + video-production + handoff)."""
    checks, _ = run_core_contract_checks()
    root = suite_root()
    ns = product_layer_root()
    vp = _vp()

    for rel in (
        "README.md",
        "PRODUCT_BOUNDARY.md",
        "prompt-packs/PP-001_novel_project_init.md",
        "examples/cold_case_echo/README.md",
    ):
        _append_check(checks, root, ns, rel)

    if not vp.is_dir():
        checks.append(
            {
                "name": "product.video-production",
                "ok": False,
                "path": str(vp),
                "error": "missing video-production dir",
            }
        )
        return checks

    _append_check(checks, root, vp, "README.md")

    for stem in (
        "scene_package",
        "shot_package",
        "keyframe_package",
        "generation_package",
        "timeline_package",
    ):
        _append_check(checks, root, vp, f"contracts/{stem}.schema.md")

    for stem in (
        "novel_to_short_drama",
        "scene_breakdown",
        "shot_planning",
        "keyframe_planning",
        "external_generation_handoff",
        "timeline_assembly",
        "delivery_qc",
    ):
        _append_check(checks, root, vp, f"workflows/{stem}.md")

    for stem in (
        "visual_consistency_gate",
        "motion_continuity_gate",
        "timeline_qc_gate",
        "generation_rights_gate",
        "external_handoff_gate",
        "transition_effects_gate",
        "story_drama_gate",
    ):
        _append_check(checks, root, vp, f"gates/{stem}.md")

    for adapter in (
        "comfyui",
        "runway",
        "kling",
        "pika",
        "luma",
        "davinci-resolve",
        "premiere",
        "after-effects",
        "blender",
        "opentimelineio",
        "ffmpeg",
    ):
        _append_check(
            checks,
            root,
            vp,
            f"adapters/{adapter}/ADAPTER_DISABLED_BY_DEFAULT.md",
        )

    _append_check(checks, root, vp, "quality/README.md")
    for stem in (
        "high_quality_video_definition",
        "quality_scorecard",
        "quality_verdicts",
    ):
        _append_check(checks, root, vp, f"quality/definitions/{stem}.md")
    for stem in (
        "technical_quality_gate",
        "audio_quality_gate",
        "visual_consistency_gate",
        "motion_continuity_gate",
        "editing_rhythm_gate",
        "transition_effects_gate",
        "story_drama_gate",
        "commercial_delivery_gate",
    ):
        _append_check(checks, root, vp, f"quality/gates/{stem}.md")
    for stem in ("defect_taxonomy", "transition_taxonomy", "effects_taxonomy"):
        _append_check(checks, root, vp, f"quality/taxonomies/{stem}.md")
    for stem in ("repair_playbook", "shot_level_repair_plan"):
        _append_check(checks, root, vp, f"quality/repair/{stem}.md")
    for stem in ("quality_report.schema", "repair_plan.schema"):
        _append_check(checks, root, vp, f"quality/reports/{stem}.md")

    _append_check(checks, root, vp, "handoff/README.md")
    for stem in (
        "handoff_package_structure",
        "asset_manifest.schema",
        "shot_handoff.schema",
        "timeline_handoff.schema",
        "handoff_status_report.schema",
        "manual_execution_checklist",
    ):
        _append_check(checks, root, vp, f"handoff/common/{stem}.md")

    _append_check(checks, root, vp, "handoff/ai-video-generation/README.md")
    _append_check(checks, root, vp, "handoff/ai-video-generation/comfyui_handoff.md")
    _append_check(checks, root, vp, "handoff/editing-timeline/README.md")
    _append_check(checks, root, vp, "handoff/editing-timeline/timeline_mapping_table.md")
    _append_check(checks, root, vp, "handoff/compositing-vfx/README.md")
    _append_check(checks, root, vp, "handoff/local-processing/ffmpeg_handoff.md")
    _append_check(checks, root, vp, "handoff/rights-and-risk/commercial_handoff_gate.md")

    _append_check(checks, root, vp, "examples/cold_case_echo_short_drama/README.md")
    _append_check(checks, root, vp, "examples/cold_case_echo_short_drama/handoff/README.md")

    _append_check(checks, root, vp, "commercial-review/README.md")
    _append_check(checks, root, vp, "commercial-review/release-blockers.md")
    _append_check(checks, root, vp, "commercial-review/sample-package-manifest.sample.json")
    _append_check(checks, root, ns, "commercialization/README.md")
    _append_check(checks, root, ns, "commercialization/prelaunch-gate.md")
    _append_check(checks, root, ns, "commercialization/claims-forbidden.md")
    _append_check(checks, root, vp, "adapter-security-review/README.md")
    _append_check(checks, root, vp, "adapter-security-review/adapter-readiness-matrix.md")
    _append_check(checks, root, ns, "commercial-release-candidate/README.md")
    _append_check(checks, root, ns, "commercial-release-candidate/final-release-gate.md")
    _append_check(checks, root, ns, "workflow-contracts/README.md")
    _append_check(checks, root, ns, "workflow-contracts/workflow_contract.schema.json")
    _append_check(checks, root, ns, "workflow-contracts/examples/commercial_release_candidate.contract.json")
    _append_check(checks, root, ns, "trace-state/README.md")
    _append_check(checks, root, ns, "trace-state/trace_state.schema.json")
    _append_check(checks, root, ns, "trace-state/examples/workflow_contract_validate.trace.jsonl")
    _append_check(checks, root, ns, "multi-ide-trials/README.md")
    _append_check(checks, root, ns, "multi-ide-trials/trial_feedback_form.schema.json")
    _append_check(checks, root, ns, "multi-ide-trials/trial_cards/cursor_trial_card.md")
    _append_check(checks, root, ns, "orchestrator-poc-design/README.md")
    _append_check(checks, root, ns, "orchestrator-poc-design/examples/product_validate_graph.design.json")
    _append_check(checks, root, ns, "knowledge-backend-research/README.md")
    _append_check(checks, root, ns, "knowledge-backend-research/candidate_backends_matrix.md")
    _append_check(checks, root, ns, "knowledge-backend-research/rag_no_go_decision.md")
    _append_check(checks, root, ns, "trial-feedback-review/README.md")
    _append_check(checks, root, ns, "trial-feedback-review/feedback_classification.schema.json")
    _append_check(checks, root, ns, "trial-feedback-review/product_revision_backlog.md")
    _append_check(checks, root, ns, "delivery-hub/README.md")
    _append_check(checks, root, ns, "delivery-hub/start-here.md")
    _append_check(checks, root, ns, "delivery-hub/known-blockers-summary.md")
    _append_check(checks, root, ns, "demo-roadmap/README.md")
    _append_check(checks, root, ns, "demo-roadmap/demo_script_15min.md")
    _append_check(checks, root, ns, "demo-roadmap/demo_no_external_call_checklist.md")
    _append_check(checks, root, ns, "legal-release-review/README.md")
    _append_check(checks, root, ns, "legal-release-review/blocker_closure_policy.md")
    _append_check(checks, root, ns, "legal-release-review/release_approval_required_signatures.md")
    _append_check(checks, root, ns, "human-trial-runbook/README.md")
    _append_check(checks, root, ns, "human-trial-runbook/human-trial-runbook.sample.json")
    _append_check(checks, root, ns, "package-freeze-candidate/README.md")
    _append_check(checks, root, ns, "package-freeze-candidate/freeze_candidate_manifest.sample.json")
    _append_check(checks, root, ns, "legal-review-packet/README.md")
    _append_check(checks, root, ns, "legal-review-packet/legal-review-packet.sample.json")
    _append_check(checks, root, ns, "trial-results-intake/README.md")
    _append_check(checks, root, ns, "trial-results-intake/trial-results-intake.sample.json")
    _append_check(checks, root, ns, "freeze-version-alignment/README.md")
    _append_check(checks, root, ns, "freeze-version-alignment/freeze-version-alignment.sample.json")
    _append_check(checks, root, ns, "legal-review-response-intake/README.md")
    _append_check(checks, root, ns, "legal-review-response-intake/legal-review-response-intake.sample.json")
    _append_check(checks, root, ns, "first-trial-session-kit/README.md")
    _append_check(checks, root, ns, "first-trial-session-kit/first-trial-session-kit.sample.json")
    _append_check(checks, root, ns, "freeze-review-meeting/README.md")
    _append_check(checks, root, ns, "freeze-review-meeting/freeze-review-meeting.sample.json")
    _append_check(checks, root, ns, "legal-review-meeting/README.md")
    _append_check(checks, root, ns, "legal-review-meeting/legal-review-meeting.sample.json")
    _append_check(checks, root, ns, "trial-result-review/README.md")
    _append_check(checks, root, ns, "trial-result-review/trial-result-review.sample.json")
    _append_check(checks, root, ns, "freeze-decision-record/README.md")
    _append_check(checks, root, ns, "freeze-decision-record/freeze-decision-record.sample.json")
    _append_check(checks, root, ns, "legal-decision-record/README.md")
    _append_check(checks, root, ns, "legal-decision-record/legal-decision-record.sample.json")
    _append_check(checks, root, ns, "trial-result-import-preflight/README.md")
    _append_check(checks, root, ns, "trial-result-import-preflight/trial-result-import-preflight.sample.json")
    _append_check(checks, root, ns, "freeze-decision-import-preflight/README.md")
    _append_check(checks, root, ns, "freeze-decision-import-preflight/freeze-decision-import-preflight.sample.json")
    _append_check(checks, root, ns, "legal-decision-import-preflight/README.md")
    _append_check(checks, root, ns, "legal-decision-import-preflight/legal-decision-import-preflight.sample.json")
    _append_check(checks, root, ns, "trial-import-decision-record/README.md")
    _append_check(checks, root, ns, "trial-import-decision-record/trial-import-decision-record.sample.json")
    _append_check(checks, root, ns, "freeze-import-decision-record/README.md")
    _append_check(checks, root, ns, "freeze-import-decision-record/freeze-import-decision-record.sample.json")
    _append_check(checks, root, ns, "legal-import-decision-board/README.md")
    _append_check(checks, root, ns, "legal-import-decision-board/legal-import-decision-board.sample.json")
    _append_check(checks, root, ns, "trial-decision-fill-kit/README.md")
    _append_check(checks, root, ns, "trial-decision-fill-kit/trial-decision-fill-kit.sample.json")
    _append_check(checks, root, ns, "freeze-decision-fill-kit/README.md")
    _append_check(checks, root, ns, "freeze-decision-fill-kit/freeze-decision-fill-kit.sample.json")
    _append_check(checks, root, ns, "legal-board-execution-kit/README.md")
    _append_check(checks, root, ns, "legal-board-execution-kit/legal-board-execution-kit.sample.json")
    _append_check(checks, root, ns, "solo-founder-freeze-self-check/README.md")
    _append_check(checks, root, ns, "solo-founder-freeze-self-check/solo-founder-freeze-self-check.sample.json")
    _append_check(checks, root, ns, "solo-founder-compliance-self-check/README.md")
    _append_check(checks, root, ns, "solo-founder-compliance-self-check/solo-founder-compliance-self-check.sample.json")
    _append_check(checks, root, ns, "solo-founder-release-blocked-declaration/README.md")
    _append_check(checks, root, ns, "solo-founder-release-blocked-declaration/solo-founder-release-blocked-declaration.sample.json")
    _append_check(checks, root, ns, "solo-demo-15min/README.md")
    _append_check(checks, root, ns, "solo-demo-15min/solo-demo-15min.sample.json")
    _append_check(checks, root, ns, "promptpack-first-run/README.md")
    _append_check(checks, root, ns, "promptpack-first-run/promptpack-first-run.sample.json")
    _append_check(checks, root, ns, "multi-ide-dry-run-feedback/README.md")
    _append_check(checks, root, ns, "multi-ide-dry-run-feedback/multi-ide-dry-run-feedback.sample.json")
    _append_check(checks, root, ns, "solo-demo-trial-intake/README.md")
    _append_check(checks, root, ns, "solo-demo-trial-intake/solo-demo-trial-intake.sample.json")
    _append_check(checks, root, ns, "promptpack-friction-review/README.md")
    _append_check(checks, root, ns, "promptpack-friction-review/promptpack-friction-review.sample.json")
    _append_check(checks, root, ns, "multi-ide-feedback-backlog/README.md")
    _append_check(checks, root, ns, "multi-ide-feedback-backlog/multi-ide-feedback-backlog.sample.json")
    _append_check(checks, root, ns, "openclaw-feedback-consolidation/README.md")
    _append_check(checks, root, ns, "openclaw-feedback-consolidation/openclaw-feedback-consolidation.sample.json")
    _append_check(checks, root, ns, "agent-entry-menu/README.md")
    _append_check(checks, root, ns, "agent-entry-menu/agent-ui-manifest.sample.json")
    _append_check(checks, root, ns, "ui-agent-workbench/README.md")
    _append_check(checks, root, ns, "ui-agent-workbench/static/index.html")
    _append_check(checks, root, ns, "server/api-contract.json")
    _append_check(checks, root, ns, "ip-production-demo/README.md")
    _append_check(checks, root, ns, "ip-production-demo/ip-production-demo.sample.json")
    _append_check(checks, root, ns, "ui-agent-workbench/runbook.md")
    _append_check(checks, root, ns, "ui-agent-workbench/openclaw_retest_prompt.md")
    _append_check(checks, root, ns, "ui-agent-workbench/ux_notes.md")
    _append_check(checks, root, ns, "ui-agent-workbench/demo_success_gate.md")
    _append_check(checks, root, ns, "ui-agent-workbench/mobile_app_readiness_plan.md")
    _append_check(checks, root, ns, "ui-agent-workbench/mobile_input_schemas.md")
    _append_check(checks, root, ns, "ui-agent-workbench/mobile_artifact_preview.md")
    _append_check(checks, root, ns, "user-trial-1/README.md")
    _append_check(checks, root, ns, "user-trial-1/scenario_brief.md")
    _append_check(checks, root, ns, "user-trial-1/sample_chapter.md")
    _append_check(checks, root, ns, "user-trial-1/trial_runbook.md")
    _append_check(checks, root, ns, "user-trial-1/observer_checklist.md")
    _append_check(checks, root, ns, "user-trial-1/user_feedback_form.md")
    _append_check(checks, root, ns, "user-trial-1/success_metrics.md")
    _append_check(checks, root, ns, "user-trial-1/boundary_notice.md")
    _append_check(checks, root, ns, "realgen-demo/DEPRECATED.md")
    _append_check(checks, root, ns, "novel-review-demo/README.md")
    _append_check(checks, root, ns, "novel-review-demo/novel-review-demo.sample.json")

    return checks


def run_product_list() -> Result:
    data = list_product_assets()
    return ok_result(
        "PRODUCT_LIST_OK",
        f"Listed {data['asset_count']} product-layer asset(s)",
        artifacts=[artifact(data["root"], kind="directory", label="product_layer")],
        **data,
    )


def run_product_read(category: str, name: str) -> Result:
    try:
        data = read_product_asset(category, name)
    except ValueError as exc:
        msg = str(exc)
        if E.PRODUCT_INVALID_CATEGORY in msg:
            return error_result(E.PRODUCT_INVALID_CATEGORY, msg)
        if E.PRODUCT_INVALID_NAME in msg or E.PRODUCT_PATH_TRAVERSAL in msg:
            return error_result(E.PRODUCT_INVALID_NAME, msg)
        return error_result(E.PRODUCT_NOT_FOUND, msg)
    return ok_result(
        "PRODUCT_READ_OK",
        f"Read {category}/{name}",
        artifacts=[artifact(data["path"], kind="file", label="product_asset")],
        asset=data,
    )


def run_product_validate() -> Result:
    checks = validate_product_layer()
    failed = [c for c in checks if not c.get("ok")]
    if failed:
        return error_result(
            E.PRODUCT_VALIDATE_FAIL,
            f"Product layer: {len(failed)} check(s) failed",
            required=[c["name"] for c in failed],
            checks=checks,
        )
    return ok_result(
        "PRODUCT_VALIDATE_OK",
        "Product layer validation passed",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        next_actions=["novel-suite product list --json"],
    )


def tool_product_list() -> dict[str, Any]:
    return run_product_list().to_dict()


def tool_product_read(category: str, name: str) -> dict[str, Any]:
    return run_product_read(category, name).to_dict()


def tool_product_validate() -> dict[str, Any]:
    return run_product_validate().to_dict()
