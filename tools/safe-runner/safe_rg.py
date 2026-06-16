#!/usr/bin/env python3
"""Restricted ripgrep-style search — avoids IDE freeze from huge output."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_EXCLUDES = (
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tmp",
    "platforms",
    "node_modules",
    "dist",
    "build",
)

BINARY_GLOBS = ("*.mp4", "*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif")


def _log_dir() -> Path:
    d = Path.cwd() / ".tmp" / "safe-runner"
    d.mkdir(parents=True, exist_ok=True)
    return d


def main() -> int:
    ap = argparse.ArgumentParser(description="Safe restricted search")
    ap.add_argument("pattern", help="Fixed string pattern")
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--max", type=int, default=100)
    args = ap.parse_args()
    max_lines = min(max(args.max, 1), 500)
    root = args.root.resolve()

    cmd = ["rg", "--fixed-strings", args.pattern, str(root)]
    for ex in DEFAULT_EXCLUDES:
        cmd.extend(["--glob", f"!{ex}/**"])
    for g in BINARY_GLOBS:
        cmd.extend(["--glob", f"!{g}"])

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        print("ERROR: ripgrep (rg) not found on PATH", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired:
        print("ERROR: search timed out (60s)", file=sys.stderr)
        return 3

    lines = (proc.stdout or "").splitlines()
    truncated = len(lines) > max_lines
    if truncated:
        log = _log_dir() / f"safe_rg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log.write_text("\n".join(lines), encoding="utf-8")
        shown = lines[:max_lines]
        print("\n".join(shown))
        print(f"\n[safe_rg] truncated {len(lines)} → {max_lines} lines; full log: {log}")
    else:
        print(proc.stdout or "", end="")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
