#!/usr/bin/env python3
"""Restricted pytest runner — caps terminal output, logs full result."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MAX_TERMINAL_LINES = 120


def _log_dir() -> Path:
    d = Path.cwd() / ".tmp" / "safe-runner"
    d.mkdir(parents=True, exist_ok=True)
    return d


def main() -> int:
    ap = argparse.ArgumentParser(description="Safe pytest wrapper")
    ap.add_argument("targets", nargs="+", help="pytest targets")
    ap.add_argument("--python", default=sys.executable)
    args = ap.parse_args()

    cmd = [args.python, "-m", "pytest", "-q", *args.targets]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    combined = (proc.stdout or "") + (proc.stderr or "")
    lines = combined.splitlines()
    log = _log_dir() / f"pytest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log.write_text(combined, encoding="utf-8")
    shown = lines[:MAX_TERMINAL_LINES]
    print("\n".join(shown))
    if len(lines) > MAX_TERMINAL_LINES:
        print(f"\n[safe_pytest] truncated; full log: {log}")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
