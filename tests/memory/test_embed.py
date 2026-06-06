"""Tests for memory embedder."""

from __future__ import annotations

from novel_suite.memory.embed import HashEmbedder, cosine_similarity, embed_backend_info, embed_text, get_embedder


def test_hash_embedder_deterministic():
    e = HashEmbedder()
    a = e.embed("林墨琥珀色眼睛")
    b = e.embed("林墨琥珀色眼睛")
    assert a == b
    assert len(a) == 256


def test_cosine_similarity_identical():
    e = HashEmbedder()
    v = e.embed("test phrase")
    assert cosine_similarity(v, v) > 0.99


def test_embed_text_module():
    v = embed_text("hello world")
    assert len(v) >= 64
