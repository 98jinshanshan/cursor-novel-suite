"""Text embeddings — hash (CI) or M3E (production)."""

from __future__ import annotations

import hashlib
import math
import re
from typing import Any, Protocol

from novel_suite.core.env_config import get_memory_embed_backend, get_memory_embed_model

_DIM_HASH = 256
_M3E_DEFAULT = "moka-ai/m3e-base"
_TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)


class Embedder(Protocol):
    @property
    def backend(self) -> str: ...

    @property
    def dim(self) -> int: ...

    def embed(self, text: str) -> list[float]: ...


class HashEmbedder:
    """Deterministic local embedder — no extra deps."""

    backend = "hash"

    def __init__(self, *, dim: int = _DIM_HASH) -> None:
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self._dim
        tokens = _TOKEN_RE.findall((text or "").lower())
        if not tokens:
            tokens = ["_empty_"]
        for tok in tokens:
            digest = hashlib.sha256(tok.encode("utf-8")).digest()
            for i in range(0, min(len(digest), self._dim)):
                vec[i % self._dim] += (digest[i] / 255.0) - 0.5
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


class M3EEmbedder:
    """M3E via sentence-transformers (lazy singleton per model name)."""

    _cache: dict[str, M3EEmbedder] = {}

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model: Any = None
        self._dim: int | None = None

    @property
    def backend(self) -> str:
        return "m3e"

    @classmethod
    def get(cls, model_name: str) -> M3EEmbedder:
        if model_name not in cls._cache:
            cls._cache[model_name] = cls(model_name)
        return cls._cache[model_name]

    def _load(self) -> None:
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers required for M3E: pip install sentence-transformers"
            ) from exc
        self._model = SentenceTransformer(self.model_name)

    @property
    def dim(self) -> int:
        if self._dim is None:
            self._dim = len(self.embed("dimension probe"))
        return self._dim

    def embed(self, text: str) -> list[float]:
        self._load()
        vec = self._model.encode(text or "", normalize_embeddings=True)
        return [float(x) for x in vec]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (na * nb)


_default_hash: HashEmbedder | None = None


def _resolve_backend_pref() -> str:
    raw = get_memory_embed_backend()
    if raw in ("hash", "m3e"):
        return raw
    if get_memory_embed_model():
        return "m3e"
    return "hash"


def get_embedder(*, prefer: str | None = None) -> Embedder:
    """Factory: M3E when configured + deps available; else hash."""
    pref = (prefer or _resolve_backend_pref()).lower()
    if pref == "m3e":
        model = get_memory_embed_model() or _M3E_DEFAULT
        try:
            return M3EEmbedder.get(model)
        except ImportError:
            pass
    global _default_hash
    if _default_hash is None:
        _default_hash = HashEmbedder()
    return _default_hash


def embed_text(text: str, *, embedder: Embedder | None = None) -> list[float]:
    emb = embedder or get_embedder()
    return emb.embed(text)


def embed_backend_info() -> dict[str, Any]:
    pref = _resolve_backend_pref()
    emb = get_embedder(prefer=pref)
    info: dict[str, Any] = {
        "preferred": pref,
        "backend": emb.backend,
        "dim": emb.dim,
        "model": getattr(emb, "model_name", None),
    }
    if pref == "m3e" and emb.backend != "m3e":
        info["fallback"] = "hash"
        info["note"] = "pip install sentence-transformers for M3E"
    return info
