"""DaVinci Resolve handoff adapter skeleton — import plan only, no Resolve API."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from novel_suite.video_production.adapters.policy import (
    assert_dry_run_only,
    default_adapter_policy,
)

_TIMELINE_MAPPING = "timeline_mapping.sample.csv"
_ASSET_MANIFEST = "asset_manifest.sample.json"
_OUTPUT_NAME = "davinci_import_plan.json"


def _read_csv_mapping(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def run_davinci_dry_run(handoff_dir: Path, output_dir: Path) -> dict[str, Any]:
    """Build DaVinci import plan from handoff CSV/JSON (no Resolve scripting)."""
    policy = default_adapter_policy("davinci-resolve")
    assert_dry_run_only(policy)

    mapping_path = handoff_dir / _TIMELINE_MAPPING
    manifest_path = handoff_dir / _ASSET_MANIFEST
    if not mapping_path.is_file():
        raise FileNotFoundError(f"Missing handoff input: {mapping_path}")
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Missing handoff input: {manifest_path}")

    rows = _read_csv_mapping(mapping_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    timeline_clips = [
        {
            "clip_id": r.get("clip_id"),
            "shot_id": r.get("shot_id"),
            "track": r.get("track"),
            "start_sec": float(r["start_sec"]) if r.get("start_sec") else 0,
            "duration_sec": float(r["duration_sec"]) if r.get("duration_sec") else 0,
            "render_path": r.get("render_path"),
            "transition_type": r.get("transition_type"),
        }
        for r in rows
    ]
    subtitles = [
        {"shot_id": r.get("shot_id"), "cue": r.get("subtitle_cue")}
        for r in rows
        if r.get("subtitle_cue")
    ]
    audio_layers = [
        {"shot_id": r.get("shot_id"), "audio_cue": r.get("audio_cue")}
        for r in rows
        if r.get("audio_cue")
    ]

    plan: dict[str, Any] = {
        **policy,
        "mode": "dry_run_import_plan_only",
        "input_files": [mapping_path.name, manifest_path.name],
        "project_id": manifest.get("project_id"),
        "episode_id": manifest.get("episode_id"),
        "media_pool_candidates": manifest.get("assets", []),
        "timeline_clips": timeline_clips,
        "subtitles": subtitles,
        "audio_layers": audio_layers,
        "resolve_api_required": False,
        "external_call_performed": False,
        "manual_execution_required": manifest.get("manual_execution_required", True),
        "commercial_blocked": manifest.get("commercial_blocked", True),
        "risk_notes": [
            "Resolve must be launched manually; no scripting API invoked",
            "Import paths are relative to handoff package root",
        ],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / _OUTPUT_NAME
    out_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    plan["output_path"] = str(out_path)
    return plan
