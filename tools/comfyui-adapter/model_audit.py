#!/usr/bin/env python3
"""Audit ComfyUI models/nodes vs workflow requirements — no auto-download."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CH02 = ROOT / "novels" / "novel-837dd4f1" / "video" / "ch02"


def _i2v_nodes(object_info: dict[str, Any]) -> list[str]:
    keys = list(object_info.keys())
    return sorted(
        n
        for n in keys
        if any(x in n.lower() for x in ("wan", "animatediff", "svd", "i2v", "videocombine"))
    )


def _checkpoints(object_info: dict[str, Any]) -> list[str]:
    cfg = (
        object_info.get("CheckpointLoaderSimple", {})
        .get("input", {})
        .get("required", {})
        .get("ckpt_name")
    )
    if isinstance(cfg, list) and cfg and isinstance(cfg[0], list):
        return [str(x) for x in cfg[0]]
    return []


def run_audit(object_info: dict[str, Any], *, ckpt_required: str) -> dict[str, Any]:
    CH02.mkdir(parents=True, exist_ok=True)
    checkpoints = _checkpoints(object_info)
    i2v_nodes = _i2v_nodes(object_info)
    missing_models: list[str] = []
    if ckpt_required and ckpt_required not in checkpoints:
        missing_models.append(ckpt_required)

    required_nodes = ["CheckpointLoaderSimple", "KSampler", "CLIPTextEncode", "SaveImage", "EmptyLatentImage", "VAEDecode"]
    missing_nodes = [n for n in required_nodes if n not in object_info]

    i2v_available = any("wan" in n.lower() or "animatediff" in n.lower() or "svd" in n.lower() for n in i2v_nodes)

    audit = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checkpoint_count": len(checkpoints),
        "checkpoints_available": checkpoints,
        "checkpoint_selected": ckpt_required,
        "missing_models": missing_models,
        "missing_custom_nodes": missing_nodes,
        "i2v_node_sample": i2v_nodes[:25],
        "i2v_available": i2v_available,
        "node_count": len(object_info),
        "auto_download": False,
    }

    (CH02 / "missing_models.md").write_text(
        "\n".join(
            [
                "# Missing Models",
                "",
                f"Generated: {audit['generated_at']}",
                "",
                "## Required",
                f"- `{ckpt_required}`: {'OK' if ckpt_required in checkpoints else 'MISSING'}",
                "",
                "## Available checkpoints",
                *[f"- {c}" for c in checkpoints],
                "",
                "**No auto-download performed.**",
            ]
        ),
        encoding="utf-8",
    )

    node_lines = [f"- {n}" for n in missing_nodes] if missing_nodes else ["- (none for minimal txt2img)"]
    (CH02 / "missing_custom_nodes.md").write_text(
        "\n".join(
            [
                "# Missing Custom Nodes",
                "",
                *node_lines,
                "",
                f"I2V-related nodes detected: {len(i2v_nodes)}",
            ]
        ),
        encoding="utf-8",
    )

    (CH02 / "manual_install_instructions.md").write_text(
        "\n".join(
            [
                "# Manual Install Instructions",
                "",
                "DocRouter / VideoRender-2R **does not auto-download** models or custom nodes.",
                "",
                "## If checkpoint missing",
                "1. Place `.safetensors` in ComfyUI `models/checkpoints/`.",
                "2. Restart ComfyUI.",
                "3. Re-run `comfyui_client.py object-info`.",
                "",
                "## If I2V desired",
                f"- i2v_available probe: **{i2v_available}**",
                "- Install Wan/AnimateDiff nodes manually via ComfyUI Manager.",
                "- Confirm license before commercial use.",
            ]
        ),
        encoding="utf-8",
    )

    cap = f"""# ComfyUI Capability Report — Ch.02 VideoRender-2R

Generated: {audit['generated_at']}

## Summary

| Item | Value |
| --- | --- |
| ComfyUI nodes | {audit['node_count']} |
| Checkpoints | {audit['checkpoint_count']} |
| Selected ckpt | `{ckpt_required}` |
| Missing models | {missing_models or 'none'} |
| Missing nodes (minimal) | {missing_nodes or 'none'} |
| i2v_available | **{i2v_available}** |
| auto_download | false |

## Checkpoints

{chr(10).join(f'- `{c}`' for c in checkpoints)}

## I2V node sample

{chr(10).join(f'- `{n}`' for n in i2v_nodes[:15])}

## Policy

- Localhost only (`127.0.0.1:8188`)
- No external API
- No auto model download
"""
    (CH02 / "comfyui_capability_report.md").write_text(cap, encoding="utf-8")
    return audit
