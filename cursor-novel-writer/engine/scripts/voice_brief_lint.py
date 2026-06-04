#!/usr/bin/env python3
"""NEC-11 P4: voice-brief.md field linter."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from scripts.audit_common import parse_voice_brief_fields  # noqa: E402
from scripts.audit_result import AuditHit, AuditReport, emit_audit, write_audit_file  # noqa: E402
from scripts import project_registry as reg  # noqa: E402

VALID_PLATFORMS = {
    "番茄小说",
    "晋江文学城",
    "起点中文网",
    "知乎盐选",
    "通用",
}
VALID_STRUCTURE = {"continuous", "scene-beats"}
VALID_LAYOUT = {"cn-fiction-indent", "cn-fiction-no-indent"}


def run_audit(project: Path) -> AuditReport:
    report = AuditReport(mode="voice", project=str(project))
    path = project / "canon" / "voice-brief.md"
    if not path.is_file():
        report.add(AuditHit("voice.missing", "blocker", "缺少 canon/voice-brief.md"))
        return report

    text = path.read_text(encoding="utf-8")
    if "## 发表平台" not in text:
        report.add(AuditHit("voice.section_platform", "blocker", "缺少 ## 发表平台"))
    if "## 章节结构" not in text:
        report.add(AuditHit("voice.section_structure", "blocker", "缺少 ## 章节结构"))

    fields = parse_voice_brief_fields(path)
    pt = fields.get("platform_target", "")
    if not pt or pt.startswith("（"):
        report.add(AuditHit("voice.platform_target", "blocker", "platform_target 未填写"))
    elif pt not in VALID_PLATFORMS:
        report.add(
            AuditHit(
                "voice.platform_target_unknown",
                "warn",
                f"platform_target 非标准值: {pt}",
            )
        )

    cs = fields.get("chapter_structure", "")
    if cs and cs not in VALID_STRUCTURE and "continuous" not in cs:
        report.add(AuditHit("voice.chapter_structure", "warn", f"chapter_structure: {cs}"))

    pl = fields.get("prose_layout", "")
    if pl and pl not in VALID_LAYOUT and "cn-fiction-indent" not in pl:
        report.add(AuditHit("voice.prose_layout", "warn", f"prose_layout: {pl}"))

    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--json", action="store_true", dest="json_only")
    args = ap.parse_args()
    project = reg.resolve_project(args.project)
    report = run_audit(project)
    out = args.out or (project / "reviews" / "voice-brief-scan.json")
    write_audit_file(out, report)
    emit_audit(report, json_only=args.json_only)
    return 0 if report.status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
