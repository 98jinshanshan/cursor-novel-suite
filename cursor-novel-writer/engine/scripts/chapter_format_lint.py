#!/usr/bin/env python3
"""NEC-11 P5/P6: chapter markdown format + cn-fiction-indent linter."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from scripts.audit_common import (  # noqa: E402
    chapter_display_path,
    count_cjk,
    default_scan_path,
    parse_story_meta,
    parse_voice_brief_fields,
    resolve_chapter,
)
from scripts.audit_result import AuditHit, AuditReport, emit_audit, write_audit_file  # noqa: E402
from scripts import project_registry as reg  # noqa: E402

CHAPTER_TITLE_RE = re.compile(r"^#\s*第\s*(\d+)\s*章")
END_MARK_RE = re.compile(r"（第\s*\d+\s*章完）")
FORBIDDEN_SECTION_RE = re.compile(r"^##\s*[一二三四五六七八九十]")
FORBIDDEN_LINE_RE = re.compile(r"^[一二三四五六七八九十]\s*$")
FULLWIDTH_INDENT = "\u3000\u3000"


def run_audit(project: Path, chapter_path: Path) -> AuditReport:
    report = AuditReport(
        mode="format",
        project=str(project),
        chapter=chapter_display_path(project, chapter_path),
    )
    text = chapter_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    if not CHAPTER_TITLE_RE.search(lines[0] if lines else ""):
        report.add(
            AuditHit(
                "format.missing_title",
                "blocker",
                "首行须为 # 第N章：标题",
                line=1,
                excerpt=(lines[0][:80] if lines else ""),
            )
        )

    if "---" not in text:
        report.add(
            AuditHit("format.missing_hr", "blocker", "缺少首尾 --- 分隔线")
        )

    if not END_MARK_RE.search(text):
        report.add(
            AuditHit("format.missing_end_mark", "warn", "建议文末含（第N章完）")
        )

    for i, line in enumerate(lines, start=1):
        if FORBIDDEN_SECTION_RE.match(line.strip()):
            report.add(
                AuditHit(
                    "format.forbidden_section",
                    "blocker",
                    "禁止章内 ## 一/二/三 小节",
                    line=i,
                    excerpt=line.strip(),
                )
            )
        if FORBIDDEN_LINE_RE.match(line.strip()):
            report.add(
                AuditHit(
                    "format.forbidden_beat_line",
                    "blocker",
                    "禁止单独一行 一/二/三 节拍",
                    line=i,
                    excerpt=line.strip(),
                )
            )

    narrative_lines = []
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#") or s == "---" or s.startswith("（第"):
            continue
        if s.startswith("|"):
            continue
        narrative_lines.append(line)

    if narrative_lines:
        indented = sum(1 for ln in narrative_lines if ln.startswith(FULLWIDTH_INDENT))
        ratio = indented / len(narrative_lines)
        if ratio < 0.85:
            report.add(
                AuditHit(
                    "format.indent_ratio",
                    "blocker",
                    f"叙事段首「　　」比例过低: {ratio:.0%}（要求≥85%）",
                )
            )
        top_plain = sum(
            1
            for ln in narrative_lines
            if ln.strip() and not ln.startswith(FULLWIDTH_INDENT) and not ln.strip().startswith(">")
        )
        if top_plain > max(2, len(narrative_lines) * 0.1):
            report.add(
                AuditHit(
                    "format.top_plain_paragraph",
                    "warn",
                    f"存在 {top_plain} 处顶格叙事段",
                )
            )

    if '"' in text or "'" in text:
        report.add(
            AuditHit(
                "format.ascii_quotes",
                "warn",
                "检测到 ASCII 引号，对话应使用全角 “”",
            )
        )

    vb = parse_voice_brief_fields(project / "canon" / "voice-brief.md")
    structure = vb.get("chapter_structure", "continuous")
    if "scene-beats" not in structure and "continuous" in structure:
        pass  # already checked forbidden sections

    story_meta = parse_story_meta(project / "story.md")
    wpc = int(story_meta.get("words_per_chapter", "4000") or "4000")
    min_w = max(500, int(wpc * 0.7))
    max_w = int(wpc * 1.5)
    cjk = count_cjk(text)
    report.summary["cjk_chars"] = cjk
    if cjk < min_w:
        report.add(
            AuditHit(
                "format.word_count_low",
                "warn",
                f"CJK 字数 {cjk} 低于建议下限 {min_w}",
            )
        )
    elif cjk > max_w:
        report.add(
            AuditHit(
                "format.word_count_high",
                "nit",
                f"CJK 字数 {cjk} 高于建议上限 {max_w}",
            )
        )

    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Chapter format lint (NEC-11)")
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--chapter", default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--json", action="store_true", dest="json_only")
    args = ap.parse_args()
    project = reg.resolve_project(args.project)
    try:
        chapter = resolve_chapter(project, args.chapter)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    report = run_audit(project, chapter)
    out = args.out or default_scan_path(project, chapter, "format")
    write_audit_file(out, report)
    emit_audit(report, json_only=args.json_only)
    return 0 if report.status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
