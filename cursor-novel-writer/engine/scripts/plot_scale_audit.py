#!/usr/bin/env python3
"""NEC-11 P3: plot scale vs platform norms."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from scripts.audit_common import parse_story_meta  # noqa: E402
from scripts.audit_result import AuditHit, AuditReport, emit_audit, write_audit_file  # noqa: E402
from scripts import project_registry as reg  # noqa: E402

PLATFORM_DEFAULTS = {
    "晋江文学城": {"chapters_min": 200, "chapters_max": 500, "wpc": 3500},
    "番茄小说": {"chapters_min": 100, "chapters_max": 800, "wpc": 2200},
    "起点中文网": {"chapters_min": 300, "chapters_max": 1500, "wpc": 3500},
    "通用": {"chapters_min": 12, "chapters_max": 999, "wpc": 4000},
}


def run_audit(project: Path) -> AuditReport:
    report = AuditReport(mode="plot", project=str(project))
    story = project / "story.md"
    meta = parse_story_meta(story)
    if not story.is_file():
        report.add(AuditHit("plot.no_story", "blocker", "缺少 story.md"))
        return report

    try:
        tc = int(meta.get("target_chapters", "0") or "0")
    except ValueError:
        tc = 0
    try:
        wpc = int(meta.get("words_per_chapter", "0") or "0")
    except ValueError:
        wpc = 0

    vb_path = project / "canon" / "voice-brief.md"
    platform = "通用"
    if vb_path.is_file():
        for line in vb_path.read_text(encoding="utf-8").splitlines():
            if "platform_target" in line and "|" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3 and parts[2] and not parts[2].startswith("（"):
                    platform = parts[2]

    norms = PLATFORM_DEFAULTS.get(platform, PLATFORM_DEFAULTS["通用"])
    report.summary["platform_target"] = platform
    report.summary["target_chapters"] = tc
    report.summary["words_per_chapter"] = wpc

    if tc < 1:
        report.add(AuditHit("plot.target_chapters", "blocker", "story.md 缺少 target_chapters"))
    elif tc < 12 and platform == "晋江文学城":
        report.add(
            AuditHit(
                "plot.chapters_too_few_jj",
                "warn",
                f"晋江长篇通常≥200章，当前 target_chapters={tc}（12 应为节拍数非正文章数）",
            )
        )
    elif tc < norms["chapters_min"]:
        report.add(
            AuditHit(
                "plot.chapters_below_norm",
                "warn",
                f"target_chapters={tc} 低于 {platform} 常见下限 {norms['chapters_min']}",
            )
        )

    if wpc < 1500:
        report.add(AuditHit("plot.wpc_low", "warn", f"words_per_chapter={wpc} 偏低"))
    elif platform == "番茄小说" and wpc > 3500:
        report.add(
            AuditHit(
                "plot.wpc_high_fanqie",
                "nit",
                f"番茄建议章均 2000–2300，当前 {wpc}",
            )
        )

    arcs = list((project / "plot" / "arcs").glob("*.md")) if (project / "plot" / "arcs").is_dir() else []
    if not arcs:
        report.add(AuditHit("plot.no_arcs", "blocker", "缺少 plot/arcs/*.md"))
    master = project / "plot" / "arcs" / "master-12.md"
    plan = project / "plot" / "chapter-plan.md"
    if not master.is_file() and not plan.is_file():
        report.add(
            AuditHit(
                "plot.no_chapter_plan",
                "warn",
                "建议 plot/arcs/master-12.md 或 plot/chapter-plan.md",
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
    out = args.out or (project / "reviews" / "plot-scale-scan.json")
    write_audit_file(out, report)
    emit_audit(report, json_only=args.json_only)
    return 0 if report.status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
