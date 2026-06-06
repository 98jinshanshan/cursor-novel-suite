"""Qdrant backend tests (mocked — no Docker required)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from novel_suite.memory.qdrant_backend import QdrantMemoryBackend, collection_name, is_configured
from novel_suite.memory.store import MemoryRecord, MemoryStore


def test_collection_name_sanitized():
    assert collection_name("novel-837dd4f1", 768) == "novel_novel-837dd4f1_d768"


def test_probe_not_configured(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("QDRANT_URL", raising=False)
    qd = QdrantMemoryBackend(Path("/tmp/x"), vector_dim=256)
    info = qd.probe()
    assert info["configured"] is False


def test_sync_raises_without_qdrant(novels_scratch: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("QDRANT_URL", raising=False)
    store = MemoryStore(novels_scratch)
    store.store("test", "L4")
    with pytest.raises(RuntimeError, match="QDRANT_NOT_AVAILABLE"):
        store.sync_to_qdrant()


def test_hybrid_search_uses_qdrant_when_available(novels_scratch: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("QDRANT_URL", "http://127.0.0.1:6333")

    mock_rec = MemoryRecord(
        id="abc123",
        layer="L4",
        text="林骁琥珀色眼睛",
        tags=["林骁"],
        vector=[0.1] * 256,
    )

    with patch("novel_suite.memory.store.QdrantMemoryBackend") as MockQd:
        inst = MockQd.return_value
        inst.search.return_value = [(mock_rec, 0.92)]
        inst.probe.return_value = {"reachable": True}

        store = MemoryStore(novels_scratch)
        hits = store.search("眼睛", layer="L4", backend="hybrid")
        assert hits
        assert hits[0][0].text == "林骁琥珀色眼睛"
        inst.search.assert_called_once()


def test_sync_to_qdrant_mock(novels_scratch: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("QDRANT_URL", "http://127.0.0.1:6333")

    store = MemoryStore(novels_scratch)
    store.store("林墨：琥珀色眼睛", "L4", tags=["林墨"])

    with patch("novel_suite.memory.store.QdrantMemoryBackend") as MockQd:
        inst = MockQd.return_value
        inst.upsert_batch.return_value = 1
        inst.collection = "novel_test_d256"

        stats = store.sync_to_qdrant()
        assert stats["synced"] == 1
        inst.upsert_batch.assert_called_once()
