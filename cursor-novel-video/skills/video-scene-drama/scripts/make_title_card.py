#!/usr/bin/env python3
"""Skill wrapper → engine/scripts/make_title_card.py (Option A)."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_TARGET = _REPO / "engine" / "scripts" / "make_title_card.py"

if __name__ == "__main__":
    if not _TARGET.is_file():
        print(f"ERROR: requires full repo clone; missing {_TARGET}", file=sys.stderr)
        sys.exit(1)
    sys.argv[0] = str(_TARGET)
    runpy.run_path(str(_TARGET), run_name="__main__")
