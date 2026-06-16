"""Storyboard JSON Schema — load, validate, and repair against video job contract."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft7Validator

from novel_suite.core import errors as E
from novel_suite.core.paths import video_root

_SCHEMA_CACHE: dict[str, Any] | None = None

# Optional Sprint 2.1 extensions (do not break existing storyboard.schema.json consumers).
EXTENSION_PROPERTIES: dict[str, Any] = {
    "hook_shot": {
        "type": "object",
        "properties": {
            "description": {"type": "string", "minLength": 1},
            "duration": {"type": "number", "minimum": 2, "maximum": 5},
            "scene_id": {"type": "string"},
        },
    },
    "emotion_arc": {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 1,
    },
}

SCENE_EXTENSION_PROPERTIES: dict[str, Any] = {
    "shot_size": {"type": "string"},
    "angle": {"type": "string"},
    "movement": {"type": "string"},
    "emotion": {"type": "string"},
    "bgm_mood": {"type": "string"},
    "importance_score": {"type": "number", "minimum": 0, "maximum": 1},
}


def storyboard_schema_path() -> Path:
    return video_root() / "schema" / "storyboard.schema.json"


def load_storyboard_schema(*, with_extensions: bool = True) -> dict[str, Any]:
    """Load authoritative storyboard schema; merge optional Sprint 2.1 fields."""
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is not None and with_extensions:
        return _SCHEMA_CACHE

    raw = json.loads(storyboard_schema_path().read_text(encoding="utf-8"))
    if not with_extensions:
        return raw

    schema = copy.deepcopy(raw)
    props = schema.setdefault("properties", {})
    for key, spec in EXTENSION_PROPERTIES.items():
        props.setdefault(key, spec)

    scene_items = (
        schema.get("properties", {})
        .get("scenes", {})
        .get("items", {})
        .setdefault("properties", {})
    )
    for key, spec in SCENE_EXTENSION_PROPERTIES.items():
        scene_items.setdefault(key, spec)

    _SCHEMA_CACHE = schema
    return schema


def validate_storyboard(data: dict[str, Any], *, with_extensions: bool = True) -> list[str]:
    """Return validation error messages; empty list means valid."""
    schema = load_storyboard_schema(with_extensions=with_extensions)
    validator = Draft7Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(data), key=lambda x: x.path)]


def repair_storyboard(data: dict[str, Any], *, default_mode: str = "summary") -> dict[str, Any]:
    """Fill missing required fields with safe defaults before validation."""
    out = copy.deepcopy(data)

    out.setdefault("job_id", "storyboard-draft")
    out.setdefault("source_chapter", "")
    out.setdefault("mode", default_mode)
    out.setdefault("aspect", "9:16")
    out.setdefault("target_duration_sec", 60)
    out.setdefault("voice", "zh-CN-XiaoxiaoNeural")

    scenes = out.get("scenes")
    if not isinstance(scenes, list):
        scenes = []
    repaired_scenes: list[dict[str, Any]] = []
    for i, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            continue
        sc = dict(scene)
        sc.setdefault("id", f"s{i + 1:02d}")
        sc.setdefault("narration", "")
        sc.setdefault("duration_target", 8.0)
        sc.setdefault("visual_job", "transition")
        repaired_scenes.append(sc)
    out["scenes"] = repaired_scenes

    if "hook_shot" in out and isinstance(out["hook_shot"], dict):
        hook = out["hook_shot"]
        hook.setdefault("description", "")
        hook.setdefault("duration", 3)
    if "emotion_arc" in out and not isinstance(out.get("emotion_arc"), list):
        out.pop("emotion_arc", None)

    return out


def validation_result_code(errors: list[str]) -> str:
    return E.STORYBOARD_SCHEMA_INVALID if errors else E.STORYBOARD_OK
