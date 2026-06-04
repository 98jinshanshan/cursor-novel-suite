#!/usr/bin/env python3
"""NEC-11 P1: story.md + project.json + concept-brief cross-check."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from scripts.audit_result import AuditHit, AuditReport, emit_audit, write_audit_file  # noqa: E402
from scripts import pipeline_gate as gate  # noqa: E402
from scripts import project_registry as reg  # noqa: E402


def run_audit(project: Path) -> AuditReport:
    report = AuditReport(mode="story", project=str(project))
    story = project / "story.md"
    pj = project / "canon" / "project.json"
    cb = project / "canon" / "concept-brief.md"

    if not story.is_file():
        report.add(AuditHit("story.missing_story", "blocker", "缺少 story.md"))
    if not pj.is_file():
        report.add(AuditHit("story.missing_project_json", "blocker", "缺少 canon/project.json"))
    else:
        errs = gate.validate_json_file(pj, "project.schema.json")
        for e in errs[:5]:
            report.add(AuditHit("story.schema", "blocker", e))
    if not cb.is_file():
        report.add(AuditHit("story.missing_concept", "warn", "缺少 canon/concept-brief.md"))
    else:
        for h in gate.CONCEPT_HEADINGS:
            if h not in cb.read_text(encoding="utf-8"):
                report.add(AuditHit("story.concept_heading", "warn", f"concept-brief 缺 {h}"))

    if pj.is_file() and story.is_file():
        data = json.loads(pj.read_text(encoding="utf-8"))
        slug = data.get("slug", "")
        if slug and slug != project.name:
            report.add(
                AuditHit(
                    "story.slug_mismatch",
                    "warn",
                    f"project.json slug={slug} vs folder {project.name}",
                )
            )

    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--json", action="store_true", dest="json_only")
    args = ap.parse_args()
    project = reg.resolve_project(args.project)
    report = run_audit(project)
    out = args.out or (project / "reviews" / "story-init-scan.json")
    write_audit_file(out, report)
    emit_audit(report, json_only=args.json_only)
    return 0 if report.status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
