#!/usr/bin/env python3
"""NEC-11 P0: score latest radar/concept markdown structure."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from scripts.audit_result import AuditHit, AuditReport, emit_audit, write_audit_file  # noqa: E402
from scripts import intel_paths as intel  # noqa: E402


def run_audit(radar_path: Path | None) -> AuditReport:
    report = AuditReport(mode="intel-rubric", project="intel")
    path = radar_path or intel.radar_path_for_week()
    if not path.is_file():
        report.add(AuditHit("intel.no_radar", "blocker", f"缺少雷达: {path}"))
        return report

    text = path.read_text(encoding="utf-8")
    required = ("## 平台快照", "## 题材", "立项候选")
    for sec in required:
        if sec not in text:
            report.add(
                AuditHit(
                    "intel.radar_section",
                    "warn",
                    f"radar 建议含: {sec}",
                )
            )
    if "(待补全)" in text:
        report.add(
            AuditHit(
                "intel.radar_incomplete",
                "warn",
                "平台快照仍有 (待补全) — 需 P0-S2 Agent 补表",
            )
        )

    report.summary["radar_path"] = str(path)
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--radar", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--json", action="store_true", dest="json_only")
    args = ap.parse_args()
    report = run_audit(args.radar)
    intel.ensure_intel_dirs()
    out = args.out or (intel.RADAR_DIR / "intel-rubric-scan.json")
    write_audit_file(out, report)
    emit_audit(report, json_only=args.json_only)
    return 0 if report.status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
