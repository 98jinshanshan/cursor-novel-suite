#!/usr/bin/env python3
"""Map shot_list / asset_pack to ComfyUI workflow inputs."""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ADAPTERS = ROOT / "cursor-novel-video" / "adapters"
if str(ADAPTERS) not in sys.path:
    sys.path.insert(0, str(ADAPTERS))

from comfyui_workflow import minimal_image_workflow, portrait_still_workflow  # noqa: E402

CH02 = ROOT / "novels" / "novel-837dd4f1" / "video" / "ch02"
STYLE_PREFIX = "cinematic crime investigation drama, cold tone, realistic, 9:16 vertical, "
NEGATIVE = (
    "nsfw, worst quality, low quality, blurry, bad anatomy, text, watermark, deformed face, "
    "cartoon, anime, gore, logo"
)


def load_shots() -> list[dict[str, str]]:
    path = CH02 / "shot_list.csv"
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_prompt_for_shot(row: dict[str, str]) -> str:
    static = row.get("static_prompt", "").strip()
    motion = row.get("motion_prompt", "").strip()
    emotion = row.get("emotion", "").strip()
    parts = [STYLE_PREFIX]
    if static:
        parts.append(static)
    if motion:
        parts.append(motion)
    if emotion:
        parts.append(f"mood: {emotion}")
    chars = row.get("characters", "")
    if chars:
        parts.append(f"characters: {chars.replace('|', ', ')}")
    return ", ".join(parts)


def build_input_mapping(*, ckpt: str, width: int = 768, height: int = 1344) -> dict[str, Any]:
    shots = load_shots()
    mapping: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workflow_id": "minimal_local_txt2img",
        "checkpoint": ckpt,
        "width": width,
        "height": height,
        "negative_prompt": NEGATIVE,
        "input_slots": {
            "positive_prompt": "CLIPTextEncode.node_2.text",
            "negative_prompt": "CLIPTextEncode.node_3.text",
            "seed": "KSampler.node_5.seed",
            "width": "EmptyLatentImage.node_4.width",
            "height": "EmptyLatentImage.node_4.height",
        },
        "output_slots": {"image": "SaveImage.node_7"},
        "shots": [],
    }
    for i, row in enumerate(shots):
        sid = row["shot_id"]
        positive = build_prompt_for_shot(row)
        seed = 42000 + i
        close = row.get("shot_size", "") in ("close_up", "close-up")
        mapping["shots"].append(
            {
                "shot_id": sid,
                "positive_prompt": positive,
                "seed": seed,
                "portrait": close,
                "duration_sec": float(row.get("duration_sec", 5)),
            }
        )
    out = CH02 / "comfyui_workflows" / "input_mapping.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    return mapping


def build_workflow_for_shot(shot: dict[str, Any], *, ckpt: str, width: int, height: int) -> dict[str, dict[str, Any]]:
    positive = shot["positive_prompt"]
    seed = int(shot["seed"])
    if shot.get("portrait"):
        wf = portrait_still_workflow(positive, negative=NEGATIVE, ckpt=ckpt, width=width, height=height, seed=seed)
    else:
        wf = minimal_image_workflow(positive, negative=NEGATIVE, ckpt=ckpt, width=width, height=height, seed=seed)
    wf["7"]["inputs"]["filename_prefix"] = f"shot_{shot['shot_id']}"
    return wf


def resolve_checkpoint(available: list[str]) -> str:
    for name in available:
        low = name.lower()
        if "realistic" in low or "vision" in low:
            return name
    for name in available:
        if "wan" not in name.lower():
            return name
    return available[0] if available else "Realistic_Vision_V5.1_fp16-no-ema.safetensors"


def list_checkpoints_from_object_info(object_info: dict[str, Any]) -> list[str]:
    cfg = (
        object_info.get("CheckpointLoaderSimple", {})
        .get("input", {})
        .get("required", {})
        .get("ckpt_name")
    )
    if isinstance(cfg, list) and cfg and isinstance(cfg[0], list):
        return [str(x) for x in cfg[0]]
    return []
