#!/usr/bin/env python3
"""NEC-11 V0: video job script.md lint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from result_contract import emit_result  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", type=Path, required=True)
    ap.add_argument("--min-chars", type=int, default=80)
    ap.add_argument("--max-chars", type=int, default=1200)
    args = ap.parse_args()
    path = args.script.resolve()
    if not path.is_file():
        emit_result("error", message=f"not found: {path}")
        return 1
    text = path.read_text(encoding="utf-8").strip()
    n = len(text)
    issues: list[str] = []
    if n < args.min_chars:
        issues.append(f"script too short: {n} < {args.min_chars}")
    if n > args.max_chars:
        issues.append(f"script too long: {n} > {args.max_chars}")
    if not issues:
        emit_result("ok", script=str(path), chars=n)
        return 0
    emit_result("error", script=str(path), chars=n, issues=issues)
    return 1


if __name__ == "__main__":
    sys.exit(main())
