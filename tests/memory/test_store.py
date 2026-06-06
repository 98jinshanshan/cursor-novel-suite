"""Tests for layered memory store and recall."""

from __future__ import annotations

from pathlib import Path

from novel_suite.memory.layers import parse_layer
from novel_suite.memory.recall import check_consistency, recall_for_video, recall_for_writing
from novel_suite.memory.splitter import split_for_layer
from novel_suite.memory.store import MemoryStore


def test_parse_layer():
    assert parse_layer("l4") == "L4"
    try:
        parse_layer("L9")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_store_and_search(novels_scratch: Path):
    store = MemoryStore(novels_scratch)
    store.store("林墨：黑色短发，琥珀色眼睛，身高178cm", "L4", tags=["character", "林墨"])
    store.store("第1章：林墨在废弃工厂觉醒", "L2", tags=["chapter", "1"])

    hits = store.search("琥珀色眼睛", layer="L4", limit=3)
    assert hits
    assert "琥珀" in hits[0][0].text

    writing = recall_for_writing(store, "林墨觉醒", limit=3)
    assert writing
    video = recall_for_video(store, "林墨", tags=["character"], limit=3)
    assert video


def test_check_consistency_pass(novels_scratch: Path):
    store = MemoryStore(novels_scratch)
    store.store("林墨：琥珀色眼睛", "L4", tags=["林墨"])
    report = check_consistency(store, "林墨的琥珀色眼睛在灯光下发亮")
    assert report["pass"] is True


def test_check_consistency_conflict(novels_scratch: Path):
    store = MemoryStore(novels_scratch)
    store.store("林墨：琥珀色眼睛", "L4", tags=["林墨"])
    report = check_consistency(store, "林墨的蓝色眼睛在灯光下发亮")
    assert report["pass"] is False
    assert report["conflicts"]


def test_split_for_layer_l3():
    text = "第一句。第二句！第三句？"
    chunks = split_for_layer(text, "L3")
    assert len(chunks) >= 2
