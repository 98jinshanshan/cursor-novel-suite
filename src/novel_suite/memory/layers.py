"""L1–L4 memory layer definitions (SOLO node 3 / C3-A01)."""

from __future__ import annotations

from typing import Literal

MemoryLayer = Literal["L1", "L2", "L3", "L4"]

LAYERS: tuple[MemoryLayer, ...] = ("L1", "L2", "L3", "L4")

_LAYER_DESC = {
    "L1": "macro summary (book / arc)",
    "L2": "chapter-level events",
    "L3": "scene / beat fragments",
    "L4": "settings — characters, world rules",
}


def parse_layer(value: str) -> MemoryLayer:
    key = (value or "").strip().upper()
    if key not in LAYERS:
        raise ValueError(f"Invalid memory layer {value!r}; use one of {', '.join(LAYERS)}")
    return key  # type: ignore[return-value]


def layer_description(layer: MemoryLayer) -> str:
    return _LAYER_DESC[layer]
