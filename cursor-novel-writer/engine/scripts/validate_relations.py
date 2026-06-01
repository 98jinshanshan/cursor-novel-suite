#!/usr/bin/env python3
"""Check bidirectional character relationship links (SS-05)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def parse_relationships(text: str) -> list[str]:
    """Extract target ids from relationships block in frontmatter."""
    if not text.startswith("---"):
        return []
    end = text.find("---", 3)
    if end < 0:
        return []
    fm = text[3:end]
    targets: list[str] = []
    in_rel = False
    for line in fm.splitlines():
        if re.match(r"^relationships\s*:", line):
            in_rel = True
            continue
        if in_rel:
            m = re.match(r"\s*-\s*target:\s*(\S+)", line)
            if m:
                targets.append(m.group(1).strip())
                continue
            if line.strip() and not line.startswith(" ") and not line.startswith("-"):
                in_rel = False
    return targets


def check_project(project: Path) -> list[str]:
    chars_dir = project / "characters"
    if not chars_dir.is_dir():
        return []
    files = {p.stem: p for p in chars_dir.glob("*.md") if p.name != "_index.md"}
    warnings: list[str] = []
    for cid, path in files.items():
        targets = parse_relationships(path.read_text(encoding="utf-8"))
        for tid in targets:
            if tid not in files:
                warnings.append(f"{cid} → {tid}: target file missing")
                continue
            reverse = parse_relationships(files[tid].read_text(encoding="utf-8"))
            if cid not in reverse:
                warnings.append(f"{cid} → {tid}: missing reverse link in {tid}.md")
    return warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate bidirectional character relations")
    ap.add_argument("--project", type=Path, default=Path("."))
    args = ap.parse_args()
    project = args.project.resolve()
    warnings = check_project(project)
    if warnings:
        for w in warnings:
            print(w)
        return 1
    print("OK: all relationship links are bidirectional")
    return 0


if __name__ == "__main__":
    sys.exit(main())
