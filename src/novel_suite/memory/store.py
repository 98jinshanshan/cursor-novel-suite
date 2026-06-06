"""Layered memory store — JSONL canonical + optional Qdrant index."""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from novel_suite.core.sanitizer import detect_injection, sanitize_prompt_input
from novel_suite.memory.embed import Embedder, cosine_similarity, embed_text, get_embedder
from novel_suite.memory.layers import MemoryLayer
from novel_suite.memory.qdrant_backend import QdrantMemoryBackend, is_configured


@dataclass
class MemoryRecord:
    id: str
    layer: MemoryLayer
    text: str
    tags: list[str] = field(default_factory=list)
    vector: list[float] = field(default_factory=list)
    created_at: str = ""
    embed_backend: str = ""
    embed_dim: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> MemoryRecord:
        return cls(
            id=str(data.get("id", "")),
            layer=data.get("layer", "L2"),  # type: ignore[arg-type]
            text=str(data.get("text", "")),
            tags=list(data.get("tags") or []),
            vector=[float(x) for x in (data.get("vector") or [])],
            created_at=str(data.get("created_at", "")),
            embed_backend=str(data.get("embed_backend") or ""),
            embed_dim=int(data.get("embed_dim") or 0),
        )


class MemoryStore:
    """File-backed vector memory; Qdrant as optional search index."""

    def __init__(
        self,
        project: Path,
        *,
        embedder: Embedder | None = None,
    ) -> None:
        self.project = project.resolve()
        self.root = self.project / "canon" / "memory"
        self.root.mkdir(parents=True, exist_ok=True)
        self._embedder = embedder or get_embedder()

    @property
    def embedder(self) -> Embedder:
        return self._embedder

    def _qdrant(self) -> QdrantMemoryBackend | None:
        if not is_configured():
            return None
        try:
            return QdrantMemoryBackend(self.project, vector_dim=self._embedder.dim)
        except ImportError:
            return None

    def _path(self, layer: MemoryLayer) -> Path:
        return self.root / f"{layer.lower()}.jsonl"

    def _load_layer(self, layer: MemoryLayer) -> list[MemoryRecord]:
        path = self._path(layer)
        if not path.is_file():
            return []
        records: list[MemoryRecord] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(MemoryRecord.from_dict(json.loads(line)))
            except json.JSONDecodeError:
                continue
        return records

    def _append(self, record: MemoryRecord) -> None:
        path = self._path(record.layer)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")

    def _vectorize(self, text: str) -> list[float]:
        return embed_text(text, embedder=self._embedder)

    def store(
        self,
        text: str,
        layer: MemoryLayer,
        *,
        tags: list[str] | None = None,
        record_id: str | None = None,
    ) -> MemoryRecord:
        raw = (text or "").strip()
        if not raw:
            raise ValueError("MEMORY_TEXT_EMPTY")
        injections = detect_injection(raw)
        if injections:
            logging.getLogger(__name__).warning(
                "Prompt injection patterns in memory store text",
                extra={"patterns": injections, "preview": raw[:100]},
            )
        body = sanitize_prompt_input(raw)
        if not body.strip():
            raise ValueError("MEMORY_TEXT_EMPTY")
        tag_list = [t.strip() for t in (tags or []) if t and t.strip()]
        vec = self._vectorize(body)
        rec = MemoryRecord(
            id=record_id or uuid.uuid4().hex[:12],
            layer=layer,
            text=body,
            tags=tag_list,
            vector=vec,
            created_at=datetime.now(timezone.utc).isoformat(),
            embed_backend=self._embedder.backend,
            embed_dim=self._embedder.dim,
        )
        self._append(rec)
        self._sync_qdrant_one(rec)
        return rec

    def search(
        self,
        query: str,
        *,
        layer: MemoryLayer | None = None,
        tags: list[str] | None = None,
        limit: int = 5,
        backend: str = "hybrid",
    ) -> list[tuple[MemoryRecord, float]]:
        q = (query or "").strip()
        if not q:
            return []
        qvec = self._vectorize(q)

        if backend in ("hybrid", "qdrant"):
            qd = self._qdrant()
            if qd is not None:
                try:
                    hits = qd.search(qvec, layer=layer, tags=tags, limit=limit)
                    if hits or backend == "qdrant":
                        return hits[: max(1, limit)]
                except Exception:
                    if backend == "qdrant":
                        return []

        return self._search_file(qvec, query=q, layer=layer, tags=tags, limit=limit)

    def _search_file(
        self,
        qvec: list[float],
        *,
        query: str,
        layer: MemoryLayer | None,
        tags: list[str] | None,
        limit: int,
    ) -> list[tuple[MemoryRecord, float]]:
        layers: tuple[MemoryLayer, ...]
        if layer:
            layers = (layer,)
        else:
            layers = ("L1", "L2", "L3", "L4")

        tag_set = {t.strip().lower() for t in (tags or []) if t.strip()}
        scored: list[tuple[MemoryRecord, float]] = []
        for ly in layers:
            for rec in self._load_layer(ly):
                if tag_set and not tag_set.intersection({t.lower() for t in rec.tags}):
                    continue
                if not rec.vector or len(rec.vector) != len(qvec):
                    sim = 0.0
                else:
                    sim = cosine_similarity(qvec, rec.vector)
                if any(tok in rec.text for tok in query.split() if len(tok) >= 2):
                    sim += 0.05
                scored.append((rec, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[: max(1, limit)]

    def list_layers(self) -> dict[str, int]:
        return {ly: len(self._load_layer(ly)) for ly in ("L1", "L2", "L3", "L4")}  # type: ignore[arg-type]

    def list_records(self, layer: MemoryLayer) -> list[MemoryRecord]:
        return self._load_layer(layer)

    def all_records(self) -> list[MemoryRecord]:
        out: list[MemoryRecord] = []
        for ly in ("L1", "L2", "L3", "L4"):
            out.extend(self._load_layer(ly))  # type: ignore[arg-type]
        return out

    def _sync_qdrant_one(self, record: MemoryRecord) -> bool:
        qd = self._qdrant()
        if qd is None:
            return False
        try:
            if not record.vector or len(record.vector) != self._embedder.dim:
                record.vector = self._vectorize(record.text)
                record.embed_backend = self._embedder.backend
                record.embed_dim = self._embedder.dim
            qd.upsert(record)
            return True
        except Exception:
            return False

    def sync_to_qdrant(self, *, reembed: bool = False) -> dict[str, Any]:
        """Bulk upsert all JSONL records into Qdrant (Sprint 1.2)."""
        qd = self._qdrant()
        if qd is None:
            raise RuntimeError("QDRANT_NOT_AVAILABLE")

        records = self.all_records()
        batch: list[MemoryRecord] = []
        skipped = 0
        reembedded = 0

        for rec in records:
            needs_reembed = (
                reembed
                or not rec.vector
                or len(rec.vector) != self._embedder.dim
                or rec.embed_backend != self._embedder.backend
            )
            if needs_reembed:
                rec.vector = self._vectorize(rec.text)
                rec.embed_backend = self._embedder.backend
                rec.embed_dim = self._embedder.dim
                reembedded += 1
            elif not rec.vector:
                skipped += 1
                continue
            batch.append(rec)

        synced = qd.upsert_batch(batch)
        return {
            "synced": synced,
            "total_file_records": len(records),
            "reembedded": reembedded,
            "skipped": skipped,
            "collection": qd.collection,
            "vector_dim": self._embedder.dim,
            "embed_backend": self._embedder.backend,
        }

    def probe(self) -> dict[str, Any]:
        qd = self._qdrant()
        qdrant_info = qd.probe() if qd is not None else {"configured": False, "reachable": False}
        from novel_suite.memory.embed import embed_backend_info

        return {
            "project": str(self.project),
            "file_layers": self.list_layers(),
            "embed": embed_backend_info(),
            "qdrant": qdrant_info,
        }
