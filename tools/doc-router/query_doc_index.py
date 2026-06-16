#!/usr/bin/env python3
"""Query DocRouter index — thin wrapper around novel_suite.cli doc-router query."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: query_doc_index.py <query> [--top-k N]", file=sys.stderr)
        return 2
    query = sys.argv[1]
    extra = sys.argv[2:]
    cmd = [
        sys.executable,
        "-m",
        "novel_suite.cli",
        "doc-router",
        "query",
        query,
        "--top-k",
        "10",
        "--json",
        *extra,
    ]
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")}
    return subprocess.call(cmd, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
