"""Semantic split granularity by layer (C3-A03)."""

from __future__ import annotations

import re

from novel_suite.memory.layers import MemoryLayer

_PARA_SPLIT = re.compile(r"\n\s*\n+")
_SENT_SPLIT = re.compile(r"(?<=[。！？.!?])\s*")


def split_for_layer(text: str, layer: MemoryLayer, *, max_chunks: int = 32) -> list[str]:
    """Split text into store-sized chunks appropriate for the layer."""
    raw = (text or "").strip()
    if not raw:
        return []

    if layer == "L1":
        # Whole macro block — one or few large paragraphs
        parts = [p.strip() for p in _PARA_SPLIT.split(raw) if p.strip()]
        if not parts:
            return [raw[:8000]]
        merged: list[str] = []
        buf = ""
        for p in parts:
            if len(buf) + len(p) < 4000:
                buf = f"{buf}\n\n{p}".strip()
            else:
                if buf:
                    merged.append(buf)
                buf = p
        if buf:
            merged.append(buf)
        return merged[:max_chunks]

    if layer == "L2":
        parts = [p.strip() for p in _PARA_SPLIT.split(raw) if p.strip()]
        return parts[:max_chunks] if parts else [raw[:4000]]

    if layer == "L3":
        sents = [s.strip() for s in _SENT_SPLIT.split(raw) if s.strip()]
        if len(sents) <= 1 and len(raw) > 400:
            sents = [raw[i : i + 400].strip() for i in range(0, len(raw), 400)]
        return sents[:max_chunks] if sents else [raw[:800]]

    # L4 — setting atoms: lines or short paragraphs
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if len(lines) >= 2:
        return lines[:max_chunks]
    parts = [p.strip() for p in _PARA_SPLIT.split(raw) if p.strip()]
    return parts[:max_chunks] if parts else [raw[:2000]]
