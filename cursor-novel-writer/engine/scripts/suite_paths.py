#!/usr/bin/env python3
"""Discover Novel Suite monorepo root — path-agnostic, structure-based."""

from __future__ import annotations

import os
from pathlib import Path

MARKER = ".novel-suite-root"
ENV_ROOT = "NOVEL_SUITE_ROOT"
WRITER_DIR = "cursor-novel-writer"
VIDEO_DIR = "cursor-novel-video"
WRITER_CLI = Path(WRITER_DIR) / "engine" / "novel_cli.py"
VIDEO_CLI = Path(VIDEO_DIR) / "engine" / "video_cli.py"

_ENGINE_SCRIPTS = Path(__file__).resolve().parent
_WRITER_FROM_FILE = _ENGINE_SCRIPTS.parents[1]


def is_suite_root(path: Path) -> bool:
    p = path.resolve()
    return (p / MARKER).is_file() and (p / WRITER_CLI).is_file()


def _walk_up(start: Path) -> Path | None:
    current = start.resolve()
    for _ in range(12):
        if is_suite_root(current):
            return current
        if current.parent == current:
            break
        current = current.parent
    return None


def suite_root(*, start: Path | None = None) -> Path:
    """Resolve monorepo root: env → walk from start/cwd → walk from engine file."""
    env = os.environ.get(ENV_ROOT, "").strip()
    if env:
        candidate = Path(env).expanduser().resolve()
        if is_suite_root(candidate):
            return candidate
        raise SystemExit(f"ERROR: {ENV_ROOT}={env} is not a valid suite root (need {MARKER} + {WRITER_CLI})")

    for anchor in (start, Path.cwd(), _WRITER_FROM_FILE.parent):
        if anchor is None:
            continue
        found = _walk_up(anchor)
        if found is not None:
            return found

    legacy = _WRITER_FROM_FILE.parent
    if (legacy / WRITER_CLI).is_file():
        return legacy.resolve()
    raise SystemExit(
        "ERROR: Cannot find Novel Suite root. Open the monorepo root in your IDE "
        f"(must contain {MARKER} and {WRITER_DIR}/), or set {ENV_ROOT}."
    )


def writer_root() -> Path:
    return suite_root() / WRITER_DIR


def video_root() -> Path:
    return suite_root() / VIDEO_DIR


def novels_dir() -> Path:
    p = suite_root() / "novels"
    p.mkdir(parents=True, exist_ok=True)
    return p


def intel_dir() -> Path:
    p = suite_root() / "intel"
    p.mkdir(parents=True, exist_ok=True)
    return p
