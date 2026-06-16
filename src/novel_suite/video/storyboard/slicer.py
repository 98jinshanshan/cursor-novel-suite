"""Chapter → visualizable scene slices (C4-A01)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from novel_suite.core.sanitizer import sanitize_prompt_input

_MIN_PARAGRAPH_CHARS = 15
_DEFAULT_MAX_NARRATION = 120


@dataclass(frozen=True)
class SceneSlice:
    index: int
    text: str
    narration: str


def split_paragraphs(text: str) -> list[str]:
    """Extract prose blocks from chapter markdown (aligned with storyboard_from_chapter)."""
    cleaned = sanitize_prompt_input(text)
    cleaned = re.sub(r"^#.*$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^---\s*$", "", cleaned, flags=re.MULTILINE)
    blocks = re.split(r"\n\s*\n", cleaned.strip())
    out: list[str] = []
    for block in blocks:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        paragraph = re.sub(r"\s+", " ", " ".join(lines))
        if len(paragraph) >= _MIN_PARAGRAPH_CHARS:
            out.append(paragraph)
    return out


def condense_narration(paragraph: str, *, max_chars: int = _DEFAULT_MAX_NARRATION) -> str:
    p = re.sub(r"\s+", " ", paragraph.strip())
    if len(p) <= max_chars:
        return p
    parts = re.split(r"(?<=[。！？])", p)
    acc = ""
    for part in parts:
        if not part.strip():
            continue
        if len(acc) + len(part) <= max_chars:
            acc += part
        else:
            break
    return acc.strip() or p[: max_chars - 1] + "…"


def group_paragraphs(
    paragraphs: list[str],
    *,
    min_scenes: int = 6,
    max_scenes: int = 12,
) -> list[str]:
    """Merge/split paragraphs to hit target scene count for summary mode."""
    if not paragraphs:
        return []
    n = len(paragraphs)
    if n <= max_scenes:
        return paragraphs

    target = max(min_scenes, min(max_scenes, max(min_scenes, n // 3)))
    per = max(1, n // target)
    grouped: list[str] = []
    buf: list[str] = []
    for p in paragraphs:
        buf.append(p)
        if len(buf) >= per and len(grouped) < target - 1:
            grouped.append(" ".join(buf))
            buf = []
    if buf:
        grouped.append(" ".join(buf))

    while len(grouped) > max_scenes and len(grouped) > 1:
        grouped[-2] = grouped[-2] + " " + grouped[-1]
        grouped.pop()

    while len(grouped) < min_scenes and len(grouped) < len(paragraphs):
        longest_i = max(range(len(grouped)), key=lambda i: len(grouped[i]))
        chunk = grouped[longest_i]
        mid = len(chunk) // 2
        split_at = chunk.find("。", mid)
        if split_at == -1:
            split_at = mid
        grouped[longest_i : longest_i + 1] = [
            chunk[: split_at + 1],
            chunk[split_at + 1 :].strip(),
        ]

    return grouped[:max_scenes]


def slice_chapter(
    chapter_text: str,
    *,
    min_scenes: int = 6,
    max_scenes: int = 12,
) -> list[SceneSlice]:
    """Split chapter into scored-ready scene slices with condensed narration."""
    paragraphs = split_paragraphs(chapter_text)
    beats = group_paragraphs(paragraphs, min_scenes=min_scenes, max_scenes=max_scenes)
    if len(beats) < min_scenes and paragraphs:
        beats = paragraphs[:max_scenes]

    return [
        SceneSlice(
            index=i,
            text=beat,
            narration=condense_narration(beat),
        )
        for i, beat in enumerate(beats)
    ]
