#!/usr/bin/env python3
"""NEC-11 P2: characters + worldbuilding presence."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from scripts.audit_result import AuditHit, AuditReport, emit_audit, write_audit_file  # noqa: E402
from scripts import project_registry as reg  # noqa: E402


def run_audit(project: Path) -> AuditReport:
    report = AuditReport(mode="canon", project=str(project))
    chars = [
        p
        for p in project.glob("characters/*.md")
        if p.is_file() and not p.name.startswith("_")
    ]
    locs = list((project / "worldbuilding" / "locations").glob("*.md"))
    systems = list((project / "worldbuilding" / "systems").glob("*.md"))
    locs = [p for p in locs if not p.name.startswith("_")]
    systems = [p for p in systems if not p.name.startswith("_")]

    if len(chars) < 2:
        report.add(
            AuditHit(
                "canon.characters",
                "blocker",
                f"人物卡不足: {len(chars)}（需要≥2）",
            )
        )
    if len(locs) + len(systems) < 1:
        report.add(
            AuditHit(
                "canon.worldbuilding",
                "blocker",
                "缺少 worldbuilding/locations 或 systems",
            )
        )

    proc = subprocess.run(
        [
            sys.executable,
            str(ENGINE_ROOT / "scripts" / "validate_relations.py"),
            "--project",
            str(project),
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        report.add(
            AuditHit(
                "canon.relations",
                "blocker",
                "relations check 失败",
                excerpt=(proc.stderr or proc.stdout)[:200],
            )
        )

    report.summary["characters"] = len(chars)
    report.summary["locations"] = len(locs)
    report.summary["systems"] = len(systems)
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--json", action="store_true", dest="json_only")
    args = ap.parse_args()
    project = reg.resolve_project(args.project)
    report = run_audit(project)
    out = args.out or (project / "reviews" / "canon-scan.json")
    write_audit_file(out, report)
    emit_audit(report, json_only=args.json_only)
    return 0 if report.status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
