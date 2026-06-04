#!/usr/bin/env python3
"""NEC-11 P8: compare prior audit scans + review re-validate markers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from scripts.audit_result import AuditHit, AuditReport, emit_audit, write_audit_file  # noqa: E402
from scripts import project_registry as reg  # noqa: E402


def _load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def run_audit(project: Path) -> AuditReport:
    report = AuditReport(mode="revalidate", project=str(project))
    reviews_dir = project / "reviews"
    if not reviews_dir.is_dir():
        report.add(AuditHit("revalidate.no_reviews", "blocker", "缺少 reviews/"))
        return report

    scans = sorted(reviews_dir.glob("*-scan.json"), key=lambda p: p.stat().st_mtime)
    if len(scans) < 1:
        report.add(AuditHit("revalidate.no_scans", "warn", "无 *-scan.json 可对比"))
    elif len(scans) >= 2:
        prev, curr = scans[-2], scans[-1]
        p_data = _load_json(prev) or {}
        c_data = _load_json(curr) or {}
        report.summary["prev_scan"] = prev.name
        report.summary["curr_scan"] = curr.name
        if p_data.get("status") == "error" and c_data.get("status") == "ok":
            report.summary["improved"] = True
        elif c_data.get("summary", {}).get("blockers", 0) > 0:
            report.add(
                AuditHit(
                    "revalidate.still_blockers",
                    "blocker",
                    f"{curr.name} 仍有 blocker",
                )
            )

    review_files = sorted(reviews_dir.glob("ch*-review.md"))
    if review_files:
        text = review_files[-1].read_text(encoding="utf-8").lower()
        if "re-validate" not in text and "## de-ai" not in text:
            report.add(
                AuditHit(
                    "revalidate.missing_section",
                    "warn",
                    "review 缺 Re-validate 或 De-AI 节",
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
    out = args.out or (project / "reviews" / "revalidate-scan.json")
    write_audit_file(out, report)
    emit_audit(report, json_only=args.json_only)
    return 0 if report.status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
