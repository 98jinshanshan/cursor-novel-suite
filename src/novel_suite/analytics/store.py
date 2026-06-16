"""Analytics record persistence per project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from novel_suite.analytics.schema import AVG_METRICS, SUM_METRICS


def _records_path(project: Path) -> Path:
    return project / "analytics" / "records.json"


def load_records(project: Path) -> list[dict[str, Any]]:
    path = _records_path(project)
    if not path.is_file():
        return []
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            return []
        records.sort(key=lambda r: r.get("recorded_at", ""), reverse=True)
        return records
    except (json.JSONDecodeError, OSError):
        return []


def add_record(project: Path, record: dict[str, Any]) -> list[dict[str, Any]]:
    records = load_records(project)
    records.insert(0, record)
    path = _records_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return records


def get_latest_metrics(project: Path) -> dict[str, Any]:
    """Aggregate all analytics records for a project."""
    records = load_records(project)
    totals: dict[str, float] = {k: 0.0 for k in SUM_METRICS}
    completion_values: list[float] = []
    record_count = 0

    for rec in records:
        metrics = rec.get("metrics") or {}
        if not isinstance(metrics, dict):
            continue
        record_count += 1
        for key in SUM_METRICS:
            if key in metrics:
                try:
                    totals[key] += float(metrics[key])
                except (TypeError, ValueError):
                    pass
        if "completion_rate" in metrics:
            try:
                completion_values.append(float(metrics["completion_rate"]))
            except (TypeError, ValueError):
                pass

    aggregated: dict[str, float] = dict(totals)
    if completion_values:
        aggregated["completion_rate"] = sum(completion_values) / len(completion_values)
    else:
        aggregated["completion_rate"] = 0.0

    return {
        "record_count": record_count,
        "metrics": aggregated,
        "latest_record": records[0] if records else None,
    }
