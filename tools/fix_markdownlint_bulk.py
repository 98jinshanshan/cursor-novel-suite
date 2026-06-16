#!/usr/bin/env python3
"""One-off bulk fix for MD060 table separators and simple MD013 wraps."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOBS = [
    ".cursor/rules/**/*.mdc",
    "cursor-novel-writer/**/*.md",
    "cursor-novel-video/**/*.md",
    "docs/**/*.md",
    "skills/**/*.md",
    "*.md",
]

SKIP = {"graphify-out", "GRAPH_REPORT.md", "tmp"}


def should_skip(path: Path) -> bool:
    return any(part in SKIP for part in path.parts)


def fix_separator_line(line: str) -> str:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return line
    inner = stripped[1:-1]
    if re.search(r"[A-Za-z\u4e00-\u9fff0-9]", inner.replace("-", "").replace(":", "")):
        return line
    cols = [c.strip() for c in inner.split("|")]
    if len(cols) < 2:
        return line
    return "| " + " | ".join("---" for _ in cols) + " |"


def wrap_md013(line: str, limit: int = 120) -> str:
    if len(line) <= limit or line.startswith("```") or line.startswith("|"):
        return line
    if line.lstrip().startswith(">"):
        return line
    indent = len(line) - len(line.lstrip())
    prefix = " " * indent
    text = line.strip()
    if len(text) <= limit:
        return line
    words = text.split()
    out: list[str] = []
    cur = prefix
    for w in words:
        trial = (cur + w) if cur == prefix else (cur + " " + w)
        if len(trial.strip()) > limit and cur.strip():
            out.append(cur.rstrip())
            cur = prefix + w
        else:
            cur = trial
    if cur.strip():
        out.append(cur.rstrip())
    return "\n".join(out) if len(out) > 1 else line


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()
    new_lines = [fix_separator_line(ln) for ln in lines]
    new_lines = [wrap_md013(ln) for ln in new_lines]
    updated = "\n".join(new_lines) + ("\n" if original.endswith("\n") else "")
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> int:
    changed = 0
    for pattern in GLOBS:
        for path in ROOT.glob(pattern):
            if not path.is_file() or should_skip(path):
                continue
            if process_file(path):
                changed += 1
                print(f"fixed: {path.relative_to(ROOT)}")
    print(f"done: {changed} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
