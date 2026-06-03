"""Discover Novel Suite monorepo root — path-agnostic, structure-based."""

from __future__ import annotations

import os
from pathlib import Path

from novel_suite.core import errors as E

MARKER = ".novel-suite-root"
ENV_ROOT = "NOVEL_SUITE_ROOT"
WRITER_DIR = "cursor-novel-writer"
VIDEO_DIR = "cursor-novel-video"
WRITER_CLI = Path(WRITER_DIR) / "engine" / "novel_cli.py"
VIDEO_CLI = Path(VIDEO_DIR) / "engine" / "video_cli.py"

_REPO_ANCHOR = Path(__file__).resolve().parents[3]
_ENGINE_SCRIPTS = _REPO_ANCHOR / WRITER_DIR / "engine" / "scripts"


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
    """Resolve monorepo root: env → walk from start/cwd → walk from package anchor."""
    env = os.environ.get(ENV_ROOT, "").strip()
    if env:
        candidate = Path(env).expanduser().resolve()
        if is_suite_root(candidate):
            return candidate
        raise RuntimeError(
            f"{ENV_ROOT}={env} is not a valid suite root (need {MARKER} + {WRITER_CLI})"
        )

    anchors: list[Path | None] = [start, Path.cwd()]
    pkg_anchor = Path(__file__).resolve().parents[3]
    if (pkg_anchor / MARKER).is_file():
        anchors.append(pkg_anchor)

    legacy = _ENGINE_SCRIPTS.parents[2] if _ENGINE_SCRIPTS.is_dir() else None
    if legacy is not None:
        anchors.append(legacy.parent)

    for anchor in anchors:
        if anchor is None:
            continue
        found = _walk_up(anchor)
        if found is not None:
            return found

    raise RuntimeError(
        f"Cannot find Novel Suite root. Open the monorepo (must contain {MARKER} and {WRITER_DIR}/), "
        f"or set {ENV_ROOT}."
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


def schema_dir() -> Path:
    return writer_root() / "schema"


def allowed_project_roots() -> list[Path]:
    """Directories where --project paths may resolve."""
    root = suite_root()
    roots = [novels_dir()]
    examples = writer_root() / "examples"
    if examples.is_dir():
        roots.append(examples)
    return [r.resolve() for r in roots]


def assert_project_in_allowed_roots(project: Path) -> Path:
    """Normalize project path and ensure it stays under novels/ or writer/examples/."""
    resolved = project.resolve()
    for base in allowed_project_roots():
        try:
            resolved.relative_to(base)
            return resolved
        except ValueError:
            continue
    raise ValueError(
        f"{E.PROJECT_PATH_OUT_OF_BOUNDS}: project must be under novels/ or "
        f"{WRITER_DIR}/examples/, got {resolved}"
    )
