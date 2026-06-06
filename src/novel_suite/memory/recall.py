"""Dual-track recall — writing vs video (C3-E10)."""

from __future__ import annotations

from pathlib import Path

from novel_suite.memory.layers import MemoryLayer
from novel_suite.memory.store import MemoryRecord, MemoryStore

_WRITING_LAYERS: tuple[MemoryLayer, ...] = ("L2", "L4")
_VIDEO_LAYERS: tuple[MemoryLayer, ...] = ("L3", "L4")


def recall_for_writing(
    store: MemoryStore,
    query: str,
    *,
    limit: int = 5,
) -> list[dict]:
    """Recall chapter summaries + character/world settings for drafting."""
    hits: list[tuple[MemoryRecord, float]] = []
    for layer in _WRITING_LAYERS:
        hits.extend(store.search(query, layer=layer, limit=limit))
    hits.sort(key=lambda x: x[1], reverse=True)
    return [_hit_dict(rec, score) for rec, score in hits[:limit]]


def recall_for_video(
    store: MemoryStore,
    query: str,
    *,
    tags: list[str] | None = None,
    limit: int = 5,
) -> list[dict]:
    """Recall scene beats + visual settings for storyboard/render."""
    hits: list[tuple[MemoryRecord, float]] = []
    for layer in _VIDEO_LAYERS:
        hits.extend(store.search(query, layer=layer, tags=tags, limit=limit))
    hits.sort(key=lambda x: x[1], reverse=True)
    return [_hit_dict(rec, score) for rec, score in hits[:limit]]


def check_consistency(
    store: MemoryStore,
    new_text: str,
    *,
    layer: MemoryLayer = "L4",
    limit: int = 8,
) -> dict:
    """
    Compare new prose against stored L4 settings.
    Returns pass flag + conflicting snippets (heuristic keyword overlap).
    """
    text = (new_text or "").strip()
    if not text:
        return {"pass": True, "conflicts": [], "references": []}

    refs = store.search(text, layer=layer, limit=limit)
    # Also scan all layer records so consistency does not depend on embed score alone
    all_records = store.list_records(layer)
    seen: set[str] = set()
    merged: list[tuple[MemoryRecord, float]] = []
    for rec, score in refs:
        if rec.id not in seen:
            seen.add(rec.id)
            merged.append((rec, score))
    for rec in all_records:
        if rec.id not in seen:
            seen.add(rec.id)
            merged.append((rec, 0.0))

    if not merged:
        return {
            "pass": True,
            "conflicts": [],
            "references": [],
            "note": "no L4 settings to compare",
        }

    conflicts: list[dict] = []
    for rec, score in merged:
        clash = _attribute_value_clash(text, rec.text)
        if clash:
            conflicts.append(
                {
                    "attribute": clash["attribute"],
                    "new_value": clash["new_value"],
                    "stored_value": clash["stored_value"],
                    "new_excerpt": clash["new_excerpt"],
                    "stored_excerpt": clash["stored_excerpt"],
                    "record_id": rec.id,
                    "score": round(score, 3),
                }
            )
    return {
        "pass": len(conflicts) == 0,
        "conflicts": conflicts,
        "references": [_hit_dict(rec, score) for rec, score in refs[:3]],
    }


def _hit_dict(rec: MemoryRecord, score: float) -> dict:
    return {
        "id": rec.id,
        "layer": rec.layer,
        "text": rec.text,
        "tags": rec.tags,
        "score": round(score, 4),
    }


def _excerpt_around(text: str, needle: str, *, radius: int = 40) -> str:
    idx = text.find(needle)
    if idx < 0:
        return text[:80]
    start = max(0, idx - radius)
    end = min(len(text), idx + len(needle) + radius)
    return text[start:end]


_EYE_COLORS = ("琥珀色", "黑色", "棕色", "蓝色", "绿色", "灰色", "金色", "紫色", "红色")


def _attribute_value_clash(new_text: str, stored: str) -> dict | None:
    """Flag only when eye-color (etc.) values explicitly disagree."""
    if "眼睛" not in new_text and "瞳" not in new_text:
        return None
    if "眼睛" not in stored and "瞳" not in stored:
        return None
    new_colors = [c for c in _EYE_COLORS if c in new_text]
    old_colors = [c for c in _EYE_COLORS if c in stored]
    if not new_colors or not old_colors:
        return None
    if set(new_colors) & set(old_colors):
        return None
    return {
        "attribute": "眼睛",
        "new_value": new_colors[0],
        "stored_value": old_colors[0],
        "new_excerpt": _excerpt_around(new_text, new_colors[0]),
        "stored_excerpt": _excerpt_around(stored, old_colors[0]),
    }


def open_store(project: Path) -> MemoryStore:
    return MemoryStore(project)
