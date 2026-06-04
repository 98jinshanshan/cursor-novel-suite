#!/usr/bin/env python3
"""NEC-11 P7: de-AI audit — lexicon + rhetoric + narrative."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from scripts.audit_common import (  # noqa: E402
    DEAI_CORPUS,
    chapter_display_path,
    default_scan_path,
    load_lexicon_lines,
    load_narrative_patterns,
    load_rhetoric_patterns,
    resolve_chapter,
)
from scripts.audit_result import AuditHit, AuditReport, emit_audit, write_audit_file  # noqa: E402
from scripts import project_registry as reg  # noqa: E402

EYE_RE = re.compile(r"(目光|眼神|视线|眸光)")


def _scan_lexicon(text: str, terms: list[str], report: AuditReport) -> None:
    found: list[tuple[str, int, str]] = []
    for term in terms:
        if len(term) < 2:
            continue
        count = text.count(term)
        if count == 0:
            continue
        sev = "blocker" if term in (
            "值得注意的是",
            "不难发现",
            "综上所述",
            "总而言之",
            "众所周知",
        ) else "warn"
        found.append((term, count, sev))
    found.sort(key=lambda x: -x[1])
    for term, count, sev in found[:40]:
        report.add(
            AuditHit(
                f"deai.lexicon.{term[:20]}",
                sev,  # type: ignore[arg-type]
                f"命中高频词「{term}」×{count}",
            )
        )
    if len(found) > 40:
        report.summary["lexicon_hits_truncated"] = len(found) - 40


def _scan_regex(
    text: str,
    lines: list[str],
    patterns: list[tuple[str, str, str]],
    report: AuditReport,
    *,
    prefix: str,
) -> None:
    for rule_id, pattern, desc in patterns:
        try:
            rx = re.compile(pattern)
        except re.error:
            continue
        for i, line in enumerate(lines, start=1):
            if rx.search(line):
                report.add(
                    AuditHit(
                        rule_id,
                        "warn",
                        desc,
                        line=i,
                        excerpt=line.strip()[:120],
                    )
                )
        if rx.search(text) and not any(h.rule_id == rule_id for h in report.hits):
            report.add(AuditHit(rule_id, "warn", desc))


def run_audit(
    project: Path,
    chapter_path: Path,
    *,
    modes: set[str],
) -> AuditReport:
    report = AuditReport(
        mode="deai",
        project=str(project),
        chapter=chapter_display_path(project, chapter_path),
    )
    text = chapter_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    report.summary["modes"] = sorted(modes)

    if "lexicon" in modes or "all" in modes:
        terms = load_lexicon_lines(DEAI_CORPUS / "lexicon.txt")
        report.summary["lexicon_terms_loaded"] = len(terms)
        _scan_lexicon(text, terms, report)

    if "rhetoric" in modes or "all" in modes:
        _scan_regex(
            text,
            lines,
            load_rhetoric_patterns(DEAI_CORPUS),
            report,
            prefix="rhetoric",
        )

    if "narrative" in modes or "all" in modes:
        _scan_regex(
            text,
            lines,
            load_narrative_patterns(DEAI_CORPUS),
            report,
            prefix="narrative",
        )
        eye_count = len(EYE_RE.findall(text))
        report.summary["eye_word_count"] = eye_count
        if eye_count > 4:
            report.add(
                AuditHit(
                    "narrative.eyes_density",
                    "warn",
                    f"目光/眼神/视线 出现 {eye_count} 次（建议≤4/章）",
                )
            )

    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="De-AI audit (NEC-11)")
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--chapter", default=None)
    ap.add_argument("--modes", default="all", help="lexicon,rhetoric,narrative,all")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--json", action="store_true", dest="json_only")
    args = ap.parse_args()
    project = reg.resolve_project(args.project)
    modes = {m.strip().lower() for m in args.modes.split(",") if m.strip()}
    if "all" in modes:
        modes = {"lexicon", "rhetoric", "narrative"}
    try:
        chapter = resolve_chapter(project, args.chapter)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    report = run_audit(project, chapter, modes=modes)
    out = args.out or default_scan_path(project, chapter, "deai")
    write_audit_file(out, report)
    emit_audit(report, json_only=args.json_only)
    return 0 if report.status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
