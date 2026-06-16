#!/usr/bin/env python3
"""Unified safe-runner entry."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: safe_runner.py rg|read|pytest ...", file=sys.stderr)
        return 1
    cmd = sys.argv[1]
    rest = sys.argv[2:]
    scripts = {
        "rg": HERE / "safe_rg.py",
        "read": HERE / "safe_read.py",
        "pytest": HERE / "safe_pytest.py",
    }
    if cmd not in scripts:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        return 1
    return subprocess.call([sys.executable, str(scripts[cmd]), *rest])


if __name__ == "__main__":
    raise SystemExit(main())
