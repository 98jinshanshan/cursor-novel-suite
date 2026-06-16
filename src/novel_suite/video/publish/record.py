"""Publish record persistence — write + list publish history."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _records_path(project: Path, chapter_key: str) -> Path:
    return project / "video" / chapter_key / "publish" / "publish_records.json"


def load_records(project: Path, chapter_key: str) -> list[dict[str, Any]]:
    """Load publish records, newest first."""
    path = _records_path(project, chapter_key)
    if not path.is_file():
        return []
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            return []
        records.sort(key=lambda r: r.get("published_at", ""), reverse=True)
        return records
    except (json.JSONDecodeError, OSError):
        return []


def add_record(
    project: Path,
    chapter_key: str,
    entry: dict[str, Any],
) -> list[dict[str, Any]]:
    """Append one publish record and persist."""
    records = load_records(project, chapter_key)
    entry["published_at"] = datetime.now(timezone.utc).isoformat()
    entry["chapter_key"] = chapter_key
    records.insert(0, entry)
    path = _records_path(project, chapter_key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return records


def last_record(project: Path, chapter_key: str) -> dict[str, Any] | None:
    records = load_records(project, chapter_key)
    return records[0] if records else None


def records_summary(project: Path, chapter_key: str) -> dict[str, Any]:
    records = load_records(project, chapter_key)
    ok_count = sum(1 for r in records if r.get("ok"))
    fail_count = sum(1 for r in records if not r.get("ok"))
    return {
        "chapter_key": chapter_key,
        "total": len(records),
        "successful": ok_count,
        "failed": fail_count,
        "latest": records[0] if records else None,
        "records": records,
    }
