"""Qdrant vector backend for memory (Sprint 1.2 / C3-A01)."""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

from novel_suite.core.env_config import get_qdrant_url, get_qdrant_url_or_default
from novel_suite.memory.layers import MemoryLayer

if TYPE_CHECKING:
    from novel_suite.memory.store import MemoryRecord

QDRANT_URL_ENV = "QDRANT_URL"
DEFAULT_QDRANT_URL = "http://127.0.0.1:6333"
_TIMEOUT_SEC = 8.0


def qdrant_url() -> str:
    return get_qdrant_url_or_default()


def is_configured() -> bool:
    return bool(get_qdrant_url())


def collection_name(project_name: str, vector_dim: int) -> str:
    safe = re.sub(r"[^\w\-]", "_", project_name)[:48]
    return f"novel_{safe}_d{vector_dim}"


def _point_id(record_id: str) -> str:
    """Qdrant accepts UUID strings; normalize short hex ids."""
    rid = (record_id or "").strip()
    if len(rid) == 32:
        return rid
    if len(rid) == 12:
        return str(uuid.UUID(hex=rid.ljust(32, "0")))
    try:
        uuid.UUID(rid)
        return rid
    except ValueError:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, rid))


def _import_client():
    from qdrant_client import QdrantClient  # type: ignore[import-untyped]
    from qdrant_client.models import (  # type: ignore[import-untyped]
        Distance,
        FieldCondition,
        Filter,
        MatchAny,
        MatchValue,
        PointStruct,
        VectorParams,
    )

    return QdrantClient, Distance, FieldCondition, Filter, MatchAny, MatchValue, PointStruct, VectorParams


class QdrantMemoryBackend:
    """Per-project Qdrant collection; optional when QDRANT_URL unset."""

    def __init__(self, project: Path, *, vector_dim: int) -> None:
        self.project = project.resolve()
        self.vector_dim = vector_dim
        self.collection = collection_name(self.project.name, vector_dim)
        self._client: Any | None = None

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        if not is_configured():
            raise RuntimeError("QDRANT_NOT_CONFIGURED")
        QdrantClient, *_ = _import_client()
        client = QdrantClient(url=qdrant_url(), timeout=_TIMEOUT_SEC)
        self._client = client
        return client

    def ensure_collection(self) -> None:
        client = self._get_client()
        _, Distance, _, _, _, _, _, VectorParams = _import_client()
        names = {c.name for c in client.get_collections().collections}
        if self.collection in names:
            return
        client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(size=self.vector_dim, distance=Distance.COSINE),
        )

    def upsert(self, record: MemoryRecord) -> None:
        if not record.vector or len(record.vector) != self.vector_dim:
            raise ValueError("MEMORY_VECTOR_DIM_MISMATCH")
        client = self._get_client()
        *_, PointStruct, _ = _import_client()
        self.ensure_collection()
        client.upsert(
            collection_name=self.collection,
            points=[
                PointStruct(
                    id=_point_id(record.id),
                    vector=record.vector,
                    payload={
                        "record_id": record.id,
                        "layer": record.layer,
                        "text": record.text,
                        "tags": record.tags,
                        "project": str(self.project),
                        "created_at": record.created_at,
                    },
                )
            ],
        )

    def upsert_batch(self, records: list[MemoryRecord]) -> int:
        if not records:
            return 0
        client = self._get_client()
        *_, PointStruct, _ = _import_client()
        self.ensure_collection()
        points = []
        for rec in records:
            if not rec.vector or len(rec.vector) != self.vector_dim:
                continue
            points.append(
                PointStruct(
                    id=_point_id(rec.id),
                    vector=rec.vector,
                    payload={
                        "record_id": rec.id,
                        "layer": rec.layer,
                        "text": rec.text,
                        "tags": rec.tags,
                        "project": str(self.project),
                        "created_at": rec.created_at,
                    },
                )
            )
        if not points:
            return 0
        client.upsert(collection_name=self.collection, points=points)
        return len(points)

    def search(
        self,
        query_vector: list[float],
        *,
        layer: MemoryLayer | None = None,
        tags: list[str] | None = None,
        limit: int = 5,
    ) -> list[tuple[MemoryRecord, float]]:
        from novel_suite.memory.store import MemoryRecord

        if len(query_vector) != self.vector_dim:
            return []

        client = self._get_client()
        _, _, FieldCondition, Filter, MatchAny, MatchValue, _, _ = _import_client()
        names = {c.name for c in client.get_collections().collections}
        if self.collection not in names:
            return []

        must: list[Any] = [
            FieldCondition(key="project", match=MatchValue(value=str(self.project))),
        ]
        if layer:
            must.append(FieldCondition(key="layer", match=MatchValue(value=layer)))
        tag_list = [t.strip() for t in (tags or []) if t.strip()]
        if tag_list:
            must.append(FieldCondition(key="tags", match=MatchAny(any=tag_list)))

        qfilter = Filter(must=must) if must else None
        hits = client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            query_filter=qfilter,
            limit=max(1, limit),
            with_payload=True,
        )
        out: list[tuple[MemoryRecord, float]] = []
        for hit in hits:
            payload = hit.payload or {}
            rec = MemoryRecord(
                id=str(payload.get("record_id") or hit.id),
                layer=payload.get("layer", "L2"),  # type: ignore[arg-type]
                text=str(payload.get("text", "")),
                tags=list(payload.get("tags") or []),
                vector=[],
                created_at=str(payload.get("created_at", "")),
            )
            out.append((rec, float(hit.score)))
        return out

    def count_points(self) -> int:
        try:
            client = self._get_client()
            names = {c.name for c in client.get_collections().collections}
            if self.collection not in names:
                return 0
            info = client.get_collection(self.collection)
            return int(getattr(info, "points_count", 0) or 0)
        except Exception:
            return 0

    def probe(self) -> dict[str, Any]:
        if not is_configured():
            return {
                "configured": False,
                "reachable": False,
                "url": "",
                "collection": self.collection,
                "points": 0,
                "note": f"Set {QDRANT_URL_ENV} (e.g. {DEFAULT_QDRANT_URL})",
            }
        url = qdrant_url()
        try:
            _import_client()
        except ImportError:
            return {
                "configured": True,
                "reachable": False,
                "url": url,
                "collection": self.collection,
                "points": 0,
                "error": "pip install qdrant-client",
            }
        try:
            client = self._get_client()
            client.get_collections()
            pts = self.count_points()
            return {
                "configured": True,
                "reachable": True,
                "url": url,
                "collection": self.collection,
                "points": pts,
                "vector_dim": self.vector_dim,
            }
        except Exception as exc:
            return {
                "configured": True,
                "reachable": False,
                "url": url,
                "collection": self.collection,
                "points": 0,
                "error": str(exc),
            }
