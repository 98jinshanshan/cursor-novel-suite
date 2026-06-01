#!/usr/bin/env python3
"""Monorepo intel/ path helpers (P-1 market intelligence)."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from scripts import suite_paths as sp

INTEL_DIR = sp.intel_dir()
RADAR_DIR = INTEL_DIR / "radar"
CONCEPTS_DIR = INTEL_DIR / "concepts"


def iso_week_id(when: date | datetime | None = None) -> str:
    d = when or datetime.now()
    if isinstance(d, datetime):
        d = d.date()
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def radar_path_for_week(week_id: str | None = None) -> Path:
    wid = week_id or iso_week_id()
    return RADAR_DIR / f"{wid}.md"


def ensure_intel_dirs() -> None:
    RADAR_DIR.mkdir(parents=True, exist_ok=True)
    CONCEPTS_DIR.mkdir(parents=True, exist_ok=True)
