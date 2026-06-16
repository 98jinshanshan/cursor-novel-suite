"""Tests for gap_matrix_diff.py parser."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ENGINE = Path(__file__).resolve().parents[1] / "cursor-novel-writer" / "engine" / "scripts"
sys.path.insert(0, str(ENGINE))

import gap_matrix_diff as gmd  # noqa: E402


SAMPLE = """
| ID | 指标 | 原状态 | **P3 后** | 建议 |
| --- | --- | --- | --- | --- |
| SS-04 | kebab-case ID 校验 | ⚠️ | ⚠️ | 可选：schema 校验脚本 |
| SS-09 | plot-frameworks.md | ⚠️ | ✅ | — |
| NS-05 | 诗词 epigraph/epilogue | ⚠️ | ⚠️ | 不借（网文专项） |
| GN-08 | thread new/resolve/list | ❌ | ❌ | 建议 P5（长篇连载） |
"""


def test_parse_open_items_excludes_closed_and_skip():
    items = gmd.parse_open_items(SAMPLE)
    assert set(items) == {"SS-04", "GN-08"}
    assert items["GN-08"]["suggestion"].startswith("建议")


def test_diff_snapshots():
    old = {"A": {"status": "⚠️"}, "B": {"status": "❌"}}
    new = {"B": {"status": "⚠️"}, "C": {"status": "❌"}}
    diff = gmd.diff_snapshots(old, new)
    assert diff["closed"] == ["A"]
    assert diff["new_open"] == ["C"]
    assert diff["still_open"] == ["B"]
    assert diff["changed"] == ["B"]


@pytest.mark.skipif(
    not (Path(__file__).resolve().parents[1] / gmd.MATRIX_REL).is_file(),
    reason="gap matrix doc missing",
)
def test_live_matrix_parses_some_open_items():
    text = (Path(__file__).resolve().parents[1] / gmd.MATRIX_REL).read_text(encoding="utf-8")
    items = gmd.parse_open_items(text)
    assert len(items) >= 5
