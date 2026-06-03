"""Ensure `src/novel_suite` is importable when running legacy engine scripts without pip install."""

from __future__ import annotations

import sys
from pathlib import Path

_INSERTED = False


def ensure_src_path(*, start: Path | None = None) -> None:
    global _INSERTED
    if _INSERTED:
        return
    anchors = [start, Path(__file__).resolve()]
    for anchor in anchors:
        if anchor is None:
            continue
        for parent in [anchor, *anchor.parents]:
            candidate = parent / "src"
            if (candidate / "novel_suite").is_dir():
                src = str(candidate.resolve())
                if src not in sys.path:
                    sys.path.insert(0, src)
                _INSERTED = True
                return
