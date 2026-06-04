#!/usr/bin/env python3
"""NEC-11 P6: hard blocker scan — delegates format lint + review file."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from scripts.audit_common import resolve_chapter  # noqa: E402
from scripts.audit_result import AuditHit, AuditReport, emit_audit, write_audit_file  # noqa: E402
from scripts import project_registry as reg  # noqa: E402


def run_audit(project: Path, chapter_path: Path | None) -> AuditReport:
    report = AuditReport(mode="blocker", project=str(project))
    if chapter_path:
        proc = subprocess.run(
            [
                sys.executable,
                str(ENGINE_ROOT / "scripts" / "chapter_format_lint.py"),
                "--project",
                str(project),
                "--chapter",
                str(chapter_path),
                "--json",
            ],
            capture_output=True,
            text=True,
        )
        for line in proc.stdout.splitlines():
            if line.startswith("AUDIT:"):
                data = json.loads(line[6:].strip())
                for hit in data.get("hits", []):
                    if hit.get("severity") == "blocker":
                        report.add(
                            AuditHit(
                                hit.get("rule_id", "format"),
                                "blocker",
                                hit.get("message", ""),
                                line=hit.get("line"),
                                excerpt=hit.get("excerpt", ""),
                            )
                        )
                report.summary["format_status"] = data.get("status")

    reviews = sorted(project.glob("reviews/ch*-review.md"))
    if reviews:
        text = reviews[-1].read_text(encoding="utf-8")
        if "## blockers" in text.lower():
            for line in text.splitlines():
                if line.strip().startswith("- [ ]"):
                    report.add(
                        AuditHit(
                            "review.open_blocker",
                            "blocker",
                            line.strip(),
                        )
                    )
    else:
        report.add(
            AuditHit(
                "review.missing",
                "warn",
                "尚无 reviews/chNN-review.md",
            )
        )

    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--chapter", default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--json", action="store_true", dest="json_only")
    args = ap.parse_args()
    project = reg.resolve_project(args.project)
    chapter = None
    if args.chapter:
        try:
            chapter = resolve_chapter(project, args.chapter)
        except FileNotFoundError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    report = run_audit(project, chapter)
    out = args.out or (project / "reviews" / "blocker-scan.json")
    write_audit_file(out, report)
    emit_audit(report, json_only=args.json_only)
    return 0 if report.status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
