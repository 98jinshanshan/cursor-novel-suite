"""Bridge scan JSON output into writer init parameters."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from novel_suite.core.paths import suite_root

VALID_PLATFORMS = frozenset(
    {"fanqie", "qidian", "jinjiang", "douyin", "kuaishou", "bilibili", "通用"}
)


def resolve_scan_json_path(scan_file: Path) -> Path:
    """Resolve .scan.json from explicit path or sibling of radar .md."""
    p = scan_file.expanduser()
    if not p.is_absolute():
        p = (suite_root() / p).resolve()
    else:
        p = p.resolve()
    if p.suffix == ".json" and p.is_file():
        return p
    if p.suffix == ".md":
        candidate = p.with_name(f"{p.stem}.scan.json")
        if candidate.is_file():
            return candidate
    if p.is_dir():
        jsons = sorted(p.glob("*.scan.json"), reverse=True)
        if jsons:
            return jsons[0]
    raise FileNotFoundError(f"Scan JSON not found for: {scan_file}")


def load_scan_json(scan_file: Path) -> dict[str, Any]:
    path = resolve_scan_json_path(scan_file)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Scan JSON must be an object")
    return data


def extract_premise_from_concept(concept_path: Path) -> str:
    """Pull a short premise from concept-brief markdown."""
    if not concept_path.is_file():
        return ""
    text = concept_path.read_text(encoding="utf-8")
    for header in ("## 立项梗概", "## 题材摘要", "## 一句话梗概", "## 核心梗概"):
        if header not in text:
            continue
        block = text.split(header, 1)[1].split("##", 1)[0]
        lines: list[str] = []
        for line in block.splitlines():
            s = line.strip()
            if not s or s.startswith("|") or s.startswith(">"):
                continue
            s = re.sub(r"^[-*•]\s*", "", s)
            s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
            if s:
                lines.append(s)
        if lines:
            return " ".join(lines[:4])[:600]
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip() and not p.startswith("#")]
    if paragraphs:
        return paragraphs[0][:600]
    return ""


def pick_theme(scan_data: dict[str, Any], *, index: int = 0) -> dict[str, Any]:
    themes = scan_data.get("themes") or []
    if not themes:
        raise ValueError("Scan JSON has no themes")
    if index < 0 or index >= len(themes):
        raise IndexError(f"Theme index {index} out of range (0..{len(themes) - 1})")
    theme = themes[index]
    if not isinstance(theme, dict):
        raise ValueError("Theme entry must be an object")
    return theme


def init_params_from_scan(
    scan_file: Path,
    *,
    theme_index: int = 0,
    title_override: str = "",
    premise_override: str = "",
    platform_override: str = "",
) -> dict[str, Any]:
    """Build init kwargs from scan JSON (TOP theme by default)."""
    scan_data = load_scan_json(scan_file)
    theme = pick_theme(scan_data, index=theme_index)
    root = suite_root()

    title = (title_override or theme.get("theme") or "").strip()
    if not title:
        raise ValueError("Scan theme has no title")

    platform = (platform_override or theme.get("suggested_platform") or "通用").strip()
    if platform not in VALID_PLATFORMS:
        platform = "通用"

    concept_path: Path | None = None
    rel_concept = theme.get("concept_path")
    if rel_concept:
        concept_path = (root / str(rel_concept)).resolve()
        if not concept_path.is_file():
            concept_path = Path(str(rel_concept)).resolve()

    premise = (premise_override or "").strip()
    if not premise and concept_path and concept_path.is_file():
        premise = extract_premise_from_concept(concept_path)
    if not premise:
        comp = theme.get("competition_analysis") or {}
        gap = comp.get("gap_opportunity", "")
        premise = f"基于扫榜选题「{title}」立项。{gap}".strip()

    return {
        "title": title,
        "premise": premise,
        "platform_target": platform,
        "concept": concept_path,
        "scan_source": str(resolve_scan_json_path(scan_file)),
        "scan_theme": theme,
        "scan_radar_path": scan_data.get("radar_path"),
    }
