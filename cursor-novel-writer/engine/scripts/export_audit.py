#!/usr/bin/env python3
"""NEC-11 P9: export readiness — chapters + dist."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from scripts.audit_result import AuditHit, AuditReport, emit_audit, write_audit_file  # noqa: E402
from scripts import project_registry as reg  # noqa: E402


def run_audit(project: Path) -> AuditReport:
    report = AuditReport(mode="export", project=str(project))
    chapters = [
        p
        for p in (project / "chapters").glob("*.md")
        if p.is_file() and not p.name.startswith("_")
    ]
    if not chapters:
        report.add(AuditHit("export.no_chapters", "blocker", "无章节可导出"))

    dist = project / "dist"
    epubs = list(dist.glob("*.epub")) if dist.is_dir() else []
    report.summary["chapter_count"] = len(chapters)
    report.summary["epub_count"] = len(epubs)
    if not epubs:
        report.add(
            AuditHit(
                "export.no_epub",
                "warn",
                "dist/ 下无 .epub（导出前可忽略）",
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
    out = args.out or (project / "reviews" / "export-scan.json")
    write_audit_file(out, report)
    emit_audit(report, json_only=args.json_only)
    return 0 if report.status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
