"""OTIO timeline handoff adapter skeleton — OTIO-like outline only, no opentimelineio import."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from novel_suite.video_production.adapters.policy import (
    assert_dry_run_only,
    default_adapter_policy,
)

_TIMELINE_HANDOFF = "timeline_handoff.sample.json"
_TIMELINE_PACKAGE = "timeline_package.sample.json"
_OUTPUT_NAME = "otio_outline.generated.json"


def _load_timeline_source(handoff_dir: Path) -> tuple[dict[str, Any], str]:
    handoff_path = handoff_dir / _TIMELINE_HANDOFF
    if handoff_path.is_file():
        return json.loads(handoff_path.read_text(encoding="utf-8")), handoff_path.name

    package_path = handoff_dir.parent / _TIMELINE_PACKAGE
    if package_path.is_file():
        return json.loads(package_path.read_text(encoding="utf-8")), package_path.name

    raise FileNotFoundError(
        f"Missing timeline input: {handoff_path} or {package_path}"
    )


def run_otio_dry_run(handoff_dir: Path, output_dir: Path) -> dict[str, Any]:
    """Generate OTIO-like outline JSON from handoff samples (no OpenTimelineIO dependency)."""
    policy = default_adapter_policy("opentimelineio")
    assert_dry_run_only(policy)

    source, source_name = _load_timeline_source(handoff_dir)
    clips = source.get("clips", [])
    transitions = source.get("transitions", [])
    subtitles = source.get("subtitles", [])

    tracks = source.get("tracks")
    if not tracks:
        track_ids = sorted({c.get("track", "V1") for c in clips if c.get("track")})
        tracks = [{"id": tid, "type": "video" if tid.startswith("V") else "other"} for tid in track_ids]

    outline: dict[str, Any] = {
        **policy,
        "mode": "dry_run_outline_only",
        "source_file": source_name,
        "timeline_id": source.get("timeline_id", source.get("schema_version", "unknown")),
        "tracks": tracks,
        "clips": clips,
        "transitions": transitions,
        "subtitles": subtitles,
        "otio_schema_hint": {
            "kind": "Timeline",
            "children_kind": "Stack",
            "note": "Outline only — not valid OTIO binary/JSON without opentimelineio library",
        },
        "external_dependency_required": "opentimelineio",
        "external_call_performed": False,
        "manual_execution_required": source.get("manual_execution_required", True),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / _OUTPUT_NAME
    out_path.write_text(json.dumps(outline, ensure_ascii=False, indent=2), encoding="utf-8")
    outline["output_path"] = str(out_path)
    return outline
