"""Vector memory hub — L1–L4 layered store (file-backed; optional Qdrant)."""

from novel_suite.memory.embed import HashEmbedder, M3EEmbedder, embed_backend_info, embed_text, get_embedder
from novel_suite.memory.qdrant_backend import QdrantMemoryBackend, is_configured, qdrant_url
from novel_suite.memory.layers import LAYERS, MemoryLayer, parse_layer
from novel_suite.memory.recall import check_consistency, recall_for_video, recall_for_writing
from novel_suite.memory.splitter import split_for_layer
from novel_suite.memory.store import MemoryRecord, MemoryStore

__all__ = [
    "LAYERS",
    "HashEmbedder",
    "M3EEmbedder",
    "QdrantMemoryBackend",
    "qdrant_url",
    "embed_backend_info",
    "get_embedder",
    "is_configured",
    "MemoryLayer",
    "MemoryRecord",
    "MemoryStore",
    "check_consistency",
    "embed_text",
    "parse_layer",
    "recall_for_video",
    "recall_for_writing",
    "split_for_layer",
]
