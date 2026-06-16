#!/usr/bin/env python3
"""DocRouter preflight — thin wrapper; rule entry for long tasks."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: docrouter_preflight.py <task description>", file=sys.stderr)
        return 2
    query = " ".join(sys.argv[1:])
    cmd = [
        sys.executable,
        "-m",
        "novel_suite.cli",
        "doc-router",
        "preflight",
        query,
        "--json",
    ]
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")}
    return subprocess.call(cmd, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
