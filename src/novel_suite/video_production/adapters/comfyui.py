"""ComfyUI handoff adapter skeleton — dry-run plan only, no HTTP/socket."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from novel_suite.video_production.adapters.policy import (
    assert_dry_run_only,
    default_adapter_policy,
)

_PROMPT_BATCH = "prompt_batch.sample.jsonl"
_KEYFRAME_MANIFEST = "keyframe_to_video_manifest.sample.json"
_OUTPUT_NAME = "comfyui_plan.json"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def run_comfyui_dry_run(handoff_dir: Path, output_dir: Path) -> dict[str, Any]:
    """Read handoff samples and write a local ComfyUI execution plan (no external calls)."""
    policy = default_adapter_policy("comfyui")
    assert_dry_run_only(policy)

    prompt_path = handoff_dir / _PROMPT_BATCH
    manifest_path = handoff_dir / _KEYFRAME_MANIFEST
    if not prompt_path.is_file():
        raise FileNotFoundError(f"Missing handoff input: {prompt_path}")
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Missing handoff input: {manifest_path}")

    prompts = _read_jsonl(prompt_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    shot_ids = sorted(
        sid
        for sid in (p.get("shot_id") for p in prompts)
        if isinstance(sid, str) and sid
    )
    manifest_shots = [s.get("shot_id") for s in manifest.get("shots", []) if s.get("shot_id")]

    plan: dict[str, Any] = {
        **policy,
        "mode": "dry_run_plan_only",
        "input_files": [
            str(prompt_path.name),
            str(manifest_path.name),
        ],
        "prompt_count": len(prompts),
        "shot_ids": shot_ids,
        "manifest_shot_ids": manifest_shots,
        "planned_nodes": [
            {
                "node_type": "LoadImage",
                "purpose": "keyframe_input",
                "shot_ids": manifest_shots,
            },
            {
                "node_type": "CLIPTextEncode",
                "purpose": "prompt_batch",
                "batch_line_ids": [p.get("batch_line_id") for p in prompts],
            },
            {
                "node_type": "SaveAnimatedWEBP",
                "purpose": "placeholder_output",
                "note": "Manual ComfyUI workflow assembly required",
            },
        ],
        "external_call_performed": False,
        "risk_notes": [
            "Do not enable adapter without commercial_handoff_gate review",
            "ComfyUI server must not be contacted in dry-run mode",
            "All prompts marked adapter_enabled=false in source samples",
        ],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / _OUTPUT_NAME
    out_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    plan["output_path"] = str(out_path)
    return plan
