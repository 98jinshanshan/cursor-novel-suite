#!/usr/bin/env python3
"""Monthly diff for open items in full-reference-gap-matrix.md (§2 tables)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1]
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from scripts import suite_paths as sp  # noqa: E402

MATRIX_REL = Path("docs/audit/2026-06-02-full-reference-gap-matrix.md")
SNAPSHOT_DIR_REL = Path("docs/audit/gap-matrix-snapshots")
ROW_RE = re.compile(r"^\| ([A-Z][A-Z0-9~\-]+) \|")
SKIP_SUGGEST = re.compile(r"不借|➖")
OPEN_STATUS = re.compile(r"⚠️|❌")


def matrix_path() -> Path:
    return sp.suite_root() / MATRIX_REL


def snapshot_dir() -> Path:
    return sp.suite_root() / SNAPSHOT_DIR_REL


def parse_open_items(text: str) -> dict[str, dict[str, str]]:
    """Extract §2 table rows still open (P3后 ⚠️/❌, 建议非不借)."""
    items: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        if not ROW_RE.match(line) or line.strip().startswith("| ---"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 7:
            continue
        item_id = parts[1]
        metric = parts[2]
        status = parts[4]
        suggestion = parts[5]
        if not OPEN_STATUS.search(status):
            continue
        if suggestion in ("—", "-", ""):
            continue
        if SKIP_SUGGEST.search(suggestion):
            continue
        items[item_id] = {
            "metric": metric,
            "status": status,
            "suggestion": suggestion,
        }
    return items


def latest_snapshot_before(month_id: str) -> Path | None:
    snap_dir = snapshot_dir()
    if not snap_dir.is_dir():
        return None
    candidates = sorted(p for p in snap_dir.glob("*.json") if p.stem < month_id)
    return candidates[-1] if candidates else None


def diff_snapshots(
    old: dict[str, dict[str, str]],
    new: dict[str, dict[str, str]],
) -> dict[str, list[str]]:
    old_ids = set(old)
    new_ids = set(new)
    return {
        "closed": sorted(old_ids - new_ids),
        "new_open": sorted(new_ids - old_ids),
        "still_open": sorted(old_ids & new_ids),
        "changed": sorted(
            i
            for i in old_ids & new_ids
            if old[i].get("status") != new[i].get("status")
            or old[i].get("suggestion") != new[i].get("suggestion")
        ),
    }


def render_report(
    *,
    month_id: str,
    items: dict[str, dict[str, str]],
    diff: dict[str, list[str]] | None,
    prev_label: str | None,
) -> str:
    lines = [
        f"# Gap Matrix Diff — {month_id}",
        "",
        f"- 生成（UTC）：{datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"- 源：[2026-06-02-full-reference-gap-matrix.md](./2026-06-02-full-reference-gap-matrix.md)",
        f"- 仍开放指标：**{len(items)}**",
        "",
    ]
    if diff and prev_label:
        lines.extend(
            [
                "## 与上月对比",
                "",
                f"- 基线快照：`{prev_label}`",
                f"- 新开放：{', '.join(diff['new_open']) or '（无）'}",
                f"- 已关闭：{', '.join(diff['closed']) or '（无）'}",
                f"- 仍开放：{len(diff['still_open'])} 项",
                f"- 状态/建议变更：{', '.join(diff['changed']) or '（无）'}",
                "",
            ]
        )
    lines.extend(["## 当前开放项", "", "| ID | 指标 | P3 后 | 建议 |", "| --- | --- | --- | --- |"])
    for item_id in sorted(items):
        row = items[item_id]
        lines.append(
            f"| {item_id} | {row['metric']} | {row['status']} | {row['suggestion']} |"
        )
    lines.append("")
    lines.append(
        "> 每月运行：`py -3 cursor-novel-writer/engine/novel_cli.py suite gap-diff`"
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Snapshot and diff gap-matrix open items")
    ap.add_argument(
        "--month",
        default=datetime.now(timezone.utc).strftime("%Y-%m"),
        help="Snapshot id YYYY-MM (default: current UTC month)",
    )
    ap.add_argument("--write-report", action="store_true", help="Write docs/audit/gap-matrix-diff-YYYY-MM.md")
    ap.add_argument("--json", action="store_true", help="Print JSON summary to stdout")
    args = ap.parse_args()

    matrix = matrix_path()
    if not matrix.is_file():
        print(f"ERROR: missing matrix {matrix}", flush=True)
        return 1

    items = parse_open_items(matrix.read_text(encoding="utf-8"))
    month_id = args.month
    snap_dir = snapshot_dir()
    snap_dir.mkdir(parents=True, exist_ok=True)
    out_json = snap_dir / f"{month_id}.json"
    payload = {
        "month": month_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(MATRIX_REL).replace("\\", "/"),
        "open_count": len(items),
        "items": items,
    }

    prev = latest_snapshot_before(month_id)
    diff = None
    prev_label = None
    if prev and prev.is_file():
        prev_data = json.loads(prev.read_text(encoding="utf-8"))
        prev_items = prev_data.get("items", {})
        diff = diff_snapshots(prev_items, items)
        prev_label = prev.name

    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: snapshot -> {out_json} ({len(items)} open items)")

    if diff:
        print(
            f"DIFF vs {prev_label}: "
            f"+{len(diff['new_open'])} new, -{len(diff['closed'])} closed, "
            f"{len(diff['still_open'])} unchanged"
        )

    if args.write_report:
        report_path = sp.suite_root() / "docs/audit" / f"gap-matrix-diff-{month_id}.md"
        report_path.write_text(
            render_report(month_id=month_id, items=items, diff=diff, prev_label=prev_label),
            encoding="utf-8",
        )
        print(f"OK: report -> {report_path}")

    if args.json:
        summary = {
            "month": month_id,
            "open_count": len(items),
            "snapshot": str(out_json.relative_to(sp.suite_root())).replace("\\", "/"),
            "diff": diff,
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
