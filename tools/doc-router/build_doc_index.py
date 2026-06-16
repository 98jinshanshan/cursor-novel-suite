#!/usr/bin/env python3
"""Build DocRouter SQLite index — thin wrapper around novel_suite.cli doc-router build."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / ".cache" / "docrouter" / "doc_router.sqlite"


def main() -> int:
    out = DEFAULT_OUT
    extra = sys.argv[1:]
    cmd = [
        sys.executable,
        "-m",
        "novel_suite.cli",
        "doc-router",
        "build",
        "--root",
        str(ROOT),
        "--out",
        str(out),
        "--json",
        *extra,
    ]
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")}
    return subprocess.call(cmd, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
