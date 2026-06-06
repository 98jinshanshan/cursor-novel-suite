"""CLI handlers for novel-suite memory subcommands."""

from __future__ import annotations

import argparse
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.paths import assert_project_in_allowed_roots
from novel_suite.core.result import artifact, error_result, ok_result
from novel_suite.memory.layers import LAYERS, parse_layer
from novel_suite.memory.recall import check_consistency, recall_for_video, recall_for_writing
from novel_suite.memory.splitter import split_for_layer
from novel_suite.memory.store import MemoryStore
from novel_suite.writer import registry


def _resolve_project(project: Path | None) -> Path:
    try:
        return registry.resolve_project(project)
    except ValueError as exc:
        raise ValueError(str(exc)) from exc


def _parse_tags(raw: str) -> list[str]:
    if not raw:
        return []
    return [t.strip() for t in raw.replace(";", ",").split(",") if t.strip()]


def run_memory_store(args: argparse.Namespace):
    try:
        project = _resolve_project(args.project)
        project = assert_project_in_allowed_roots(project)
    except ValueError as exc:
        return error_result(E.NO_ACTIVE_NOVEL if "active" in str(exc).lower() else E.PROJECT_PATH_OUT_OF_BOUNDS, str(exc))

    try:
        layer = parse_layer(args.layer)
    except ValueError as exc:
        return error_result(E.MEMORY_INVALID_LAYER, str(exc))

    text = (args.text or "").strip()
    if not text:
        return error_result(E.MEMORY_TEXT_EMPTY, "Provide --text")

    store = MemoryStore(project)
    tags = _parse_tags(args.tags)
    ids: list[str] = []

    if args.auto_split:
        chunks = split_for_layer(text, layer)
        for chunk in chunks:
            rec = store.store(chunk, layer, tags=tags)
            ids.append(rec.id)
    else:
        rec = store.store(text, layer, tags=tags)
        ids.append(rec.id)

    mem_root = project / "canon" / "memory"
    return ok_result(
        E.MEMORY_STORE_OK,
        f"Stored {len(ids)} record(s) in {layer}",
        artifacts=[artifact(str(mem_root / f"{layer.lower()}.jsonl"), kind="file", label="memory")],
        layer=layer,
        record_ids=ids,
        tags=tags,
    )


def run_memory_search(args: argparse.Namespace):
    try:
        project = _resolve_project(args.project)
        project = assert_project_in_allowed_roots(project)
    except ValueError as exc:
        return error_result(E.NO_ACTIVE_NOVEL if "active" in str(exc).lower() else E.PROJECT_PATH_OUT_OF_BOUNDS, str(exc))

    layer = None
    if args.layer:
        try:
            layer = parse_layer(args.layer)
        except ValueError as exc:
            return error_result(E.MEMORY_INVALID_LAYER, str(exc))

    query = (args.query or "").strip()
    if not query:
        return error_result(E.MEMORY_QUERY_EMPTY, "Provide --query")

    store = MemoryStore(project)
    track = (args.track or "").strip().lower()
    tags = _parse_tags(args.tags)

    if track == "writing":
        hits = recall_for_writing(store, query, limit=args.limit)
    elif track == "video":
        hits = recall_for_video(store, query, tags=tags, limit=args.limit)
    else:
        raw = store.search(query, layer=layer, tags=tags or None, limit=args.limit)
        hits = [
            {"id": r.id, "layer": r.layer, "text": r.text, "tags": r.tags, "score": round(s, 4)}
            for r, s in raw
        ]

    return ok_result(
        E.MEMORY_SEARCH_OK,
        f"{len(hits)} hit(s) for query",
        hits=hits,
        query=query,
        layer=layer,
        track=track or "default",
    )


def run_memory_check(args: argparse.Namespace):
    try:
        project = _resolve_project(args.project)
        project = assert_project_in_allowed_roots(project)
    except ValueError as exc:
        return error_result(E.NO_ACTIVE_NOVEL if "active" in str(exc).lower() else E.PROJECT_PATH_OUT_OF_BOUNDS, str(exc))

    text = (args.text or "").strip()
    if not text:
        return error_result(E.MEMORY_TEXT_EMPTY, "Provide --text")

    store = MemoryStore(project)
    report = check_consistency(store, text)
    code = E.MEMORY_CHECK_OK if report.get("pass") else E.MEMORY_CHECK_CONFLICT
    return ok_result(
        code,
        "Consistency check passed" if report.get("pass") else "Possible setting conflicts",
        **report,
    )


def run_memory_probe(args: argparse.Namespace):
    try:
        project = _resolve_project(args.project)
        project = assert_project_in_allowed_roots(project)
    except ValueError as exc:
        return error_result(E.NO_ACTIVE_NOVEL if "active" in str(exc).lower() else E.PROJECT_PATH_OUT_OF_BOUNDS, str(exc))

    store = MemoryStore(project)
    report = store.probe()
    return ok_result(E.MEMORY_PROBE_OK, "Memory stack probe", **report)


def run_memory_sync(args: argparse.Namespace):
    try:
        project = _resolve_project(args.project)
        project = assert_project_in_allowed_roots(project)
    except ValueError as exc:
        return error_result(E.NO_ACTIVE_NOVEL if "active" in str(exc).lower() else E.PROJECT_PATH_OUT_OF_BOUNDS, str(exc))

    store = MemoryStore(project)
    try:
        stats = store.sync_to_qdrant(reembed=args.reembed)
    except RuntimeError as exc:
        return error_result(
            E.MEMORY_QDRANT_UNAVAILABLE,
            str(exc),
            next_actions=[
                "Set QDRANT_URL=http://127.0.0.1:6333",
                "pip install qdrant-client",
                "powershell -File platforms/install-memory-stack.ps1 -ProbeOnly",
            ],
        )
    except ImportError:
        return error_result(
            E.MEMORY_QDRANT_UNAVAILABLE,
            "qdrant-client not installed",
            next_actions=["pip install qdrant-client"],
        )
    except Exception as exc:
        return error_result(E.MEMORY_QDRANT_UNAVAILABLE, str(exc))

    return ok_result(
        E.MEMORY_SYNC_OK,
        f"Synced {stats.get('synced', 0)} point(s) to Qdrant",
        artifacts=[artifact(str(project / "canon" / "memory"), kind="directory", label="memory")],
        **stats,
    )


def run_memory_status(args: argparse.Namespace):
    try:
        project = _resolve_project(args.project)
        project = assert_project_in_allowed_roots(project)
    except ValueError as exc:
        return error_result(E.NO_ACTIVE_NOVEL if "active" in str(exc).lower() else E.PROJECT_PATH_OUT_OF_BOUNDS, str(exc))

    store = MemoryStore(project)
    counts = store.list_layers()
    qd = store.probe().get("qdrant") or {}
    return ok_result(
        E.MEMORY_STATUS_OK,
        "Memory layer counts",
        artifacts=[artifact(str(project / "canon" / "memory"), kind="directory", label="memory")],
        layers=counts,
        supported_layers=list(LAYERS),
        embed_backend=store.embedder.backend,
        qdrant_configured=bool(qd.get("configured")),
        qdrant_reachable=bool(qd.get("reachable")),
    )
