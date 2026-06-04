"""MCP path validation — mirrors novel_suite.core.path_safety when available."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_VIDEO_ROOT = Path(__file__).resolve().parents[1]
_MARKER = ".novel-suite-root"


def _find_suite_root() -> Path | None:
    env = os.environ.get("NOVEL_SUITE_ROOT", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if (p / _MARKER).is_file():
            return p
    current = _VIDEO_ROOT.parent.resolve()
    for _ in range(8):
        if (current / _MARKER).is_file():
            return current
        if current.parent == current:
            break
        current = current.parent
    return None


def _allowed_roots() -> list[Path]:
    try:
        src = _find_suite_root()
        if src is not None:
            sys.path.insert(0, str(src / "src"))
            from novel_suite.core.path_safety import mcp_allowed_roots

            return mcp_allowed_roots()
    except Exception:
        pass
    root = _find_suite_root() or _VIDEO_ROOT.parent
    roots = [
        root.resolve(),
        (root / "novels").resolve(),
        _VIDEO_ROOT.resolve(),
        (_VIDEO_ROOT / "tmp").resolve(),
        (_VIDEO_ROOT / "demos").resolve(),
        (root / "cursor-novel-writer" / "examples").resolve(),
    ]
    deduped: list[Path] = []
    seen: set[str] = set()
    for r in roots:
        s = str(r)
        if s not in seen:
            seen.add(s)
            deduped.append(r)
    return deduped


def _within(path: Path, roots: list[Path]) -> bool:
    resolved = path.resolve()
    for base in roots:
        try:
            resolved.relative_to(base)
            return True
        except ValueError:
            continue
    return False


def resolve_mcp_path(path_str: str, *, label: str = "path") -> Path:
    if not path_str or not str(path_str).strip():
        raise ValueError(f"MCP {label}: empty path")
    raw = Path(path_str).expanduser()
    if raw.is_file() or raw.is_dir():
        resolved = raw.resolve()
    else:
        parent = raw.parent.expanduser()
        if not parent.exists():
            raise ValueError(f"MCP {label}: parent directory does not exist: {parent}")
        resolved = parent.resolve() / raw.name
    if not _within(resolved, _allowed_roots()):
        raise ValueError(
            f"MCP {label} out of bounds: {resolved} "
            "(must be under Novel Suite root, novels/, or cursor-novel-video/)"
        )
    return resolved
