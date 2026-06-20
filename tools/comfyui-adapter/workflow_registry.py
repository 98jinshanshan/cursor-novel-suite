#!/usr/bin/env python3
"""Discover and score local ComfyUI workflow JSON files."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ADAPTERS = ROOT / "cursor-novel-video" / "adapters"
CH02 = ROOT / "novels" / "novel-837dd4f1" / "video" / "ch02"
WORKFLOW_DIRS = [
    CH02 / "comfyui_workflows",
    ROOT / "novel-suite" / "adapters" / "image-generation",
    ADAPTERS,
]

SCORE_WEIGHTS = {
    "local_runnable": 25,
    "character_consistency": 20,
    "batch_shot_input": 15,
    "aspect_9x16": 10,
    "deps_clear": 10,
    "shot_mapping": 10,
    "license_clear": 5,
    "manifest_qc": 5,
}


def discover_workflow_files() -> list[Path]:
    found: list[Path] = []
    seen: set[str] = set()
    for base in WORKFLOW_DIRS:
        if not base.is_dir():
            continue
        for p in base.rglob("*.json"):
            key = str(p.resolve())
            if key in seen:
                continue
            if "registry" in p.name.lower() or "mapping" in p.name.lower():
                continue
            seen.add(key)
            found.append(p.resolve())
    return sorted(found)


def _score_workflow(path: Path, object_info: dict[str, Any] | None) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")[:50000]
    low = text.lower()
    is_api = '"class_type"' in text
    has_save = "saveimage" in low or "saveanimated" in low
    has_txt2img = any(x in low for x in ("ksampler", "cliptextencode", "checkpointloadersimple"))
    has_i2v = any(x in low for x in ("wan", "animatediff", "svd", "i2v", "video"))
    has_ip = "ipadapter" in low

    scores = {
        "local_runnable": 20 if is_api and has_save else (10 if has_txt2img else 0),
        "character_consistency": 15 if has_ip else 5,
        "batch_shot_input": 10 if "shot" in low or "batch" in low else 5,
        "aspect_9x16": 8 if any(x in low for x in ("768", "1344", "1080", "1920", "9:16")) else 3,
        "deps_clear": 8 if is_api else 4,
        "shot_mapping": 5,
        "license_clear": 2,
        "manifest_qc": 3,
    }
    total = sum(scores.values())
    status = "validated" if total >= 60 and has_txt2img else "candidate"
    if not has_save:
        status = "blocked"
    return {
        "workflow_id": path.stem,
        "path": str(path),
        "source": "local_or_user_provided",
        "license": "unknown/manual_review_required",
        "format": "api" if is_api else "ui",
        "has_txt2img": has_txt2img,
        "has_i2v": has_i2v,
        "has_ipadapter": has_ip,
        "score_breakdown": scores,
        "total_score": total,
        "status": status,
        "allowed_for_commercial": False,
    }


def build_registry(*, object_info: dict[str, Any] | None = None, out_dir: Path | None = None) -> dict[str, Any]:
    out = out_dir or (CH02 / "comfyui_workflows")
    out.mkdir(parents=True, exist_ok=True)
    files = discover_workflow_files()
    entries = [_score_workflow(p, object_info) for p in files]

    minimal = {
        "workflow_id": "minimal_local_txt2img",
        "path": "builtin://minimal_local_txt2img",
        "source": "minimal_local_workflow",
        "license": "internal",
        "format": "api",
        "has_txt2img": True,
        "has_i2v": False,
        "score_breakdown": {k: SCORE_WEIGHTS[k] for k in SCORE_WEIGHTS},
        "total_score": sum(SCORE_WEIGHTS.values()),
        "status": "validated",
        "allowed_for_commercial": False,
    }
    entries.append(minimal)
    entries.sort(key=lambda x: x["total_score"], reverse=True)
    selected = entries[0] if entries else minimal

    registry = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workflow_count": len(entries),
        "workflows": entries,
        "selected_workflow_id": selected["workflow_id"],
        "selected_workflow": selected,
    }
    reg_path = out / "registry.json"
    reg_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
    sel_path = out / "selected_workflow.json"
    sel_path.write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    return registry


if __name__ == "__main__":
    import argparse

    from comfyui_client import object_info, validate_url

    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8188")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    oi = None
    try:
        oi = object_info(validate_url(args.url))
    except Exception:
        oi = None
    reg = build_registry(object_info=oi, out_dir=Path(args.out) if args.out else None)
    print(json.dumps({"status": "ok", "selected": reg["selected_workflow_id"], "count": reg["workflow_count"]}, ensure_ascii=False))
