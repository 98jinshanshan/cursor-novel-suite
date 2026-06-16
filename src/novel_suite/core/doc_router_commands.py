"""CLI handlers for doc-router subcommands."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from novel_suite.core import doc_router
from novel_suite.core.paths import suite_root
from novel_suite.core.result import artifact, error_result, ok_result


def run_doc_router_build(args: argparse.Namespace):
    root = Path(args.root).resolve() if args.root else suite_root()
    out = Path(args.out).resolve() if args.out else root / doc_router.DEFAULT_INDEX_PATH
    scopes = [s.strip() for s in (args.scopes or "").split(",") if s.strip()] or None
    result = doc_router.build_index(
        out_db=out,
        root=root,
        scopes=scopes,
        include_globs=[g.strip() for g in (args.include or "").split(",") if g.strip()] or None,
        exclude_globs=[g.strip() for g in (args.exclude or "").split(",") if g.strip()] or None,
    )
    return ok_result(
        "DOC_ROUTER_BUILD_OK",
        f"Indexed {result['indexed']} documents",
        artifacts=[artifact(result["db_path"], label="doc-router index")],
        **result,
    )


def run_doc_router_query(args: argparse.Namespace):
    query = (args.query or "").strip()
    if not query:
        return error_result("DOC_ROUTER_QUERY_EMPTY", "Provide query text")
    root = Path(args.root).resolve() if getattr(args, "root", None) else suite_root()
    db = Path(args.db).resolve() if getattr(args, "db", None) else None
    hits = doc_router.query_index(
        query,
        top_k=args.top_k,
        scope=args.scope or None,
        max_docs=args.max_docs,
        db_path=db,
        root=root,
    )
    return ok_result(
        "DOC_ROUTER_QUERY_OK",
        f"Found {len(hits)} document(s)",
        hits=[h.to_dict() for h in hits],
        query=query,
    )


def run_doc_router_preflight(args: argparse.Namespace):
    query = (args.query or "").strip()
    if not query:
        return error_result("DOC_ROUTER_QUERY_EMPTY", "Provide task/query text for preflight")
    root = Path(args.root).resolve() if getattr(args, "root", None) else suite_root()
    db = Path(args.db).resolve() if getattr(args, "db", None) else None
    risk = getattr(args, "risk_level", None) or None
    if risk == "":
        risk = None
    payload = doc_router.preflight(query, db_path=db, root=root, risk_level=risk)
    code = "DOC_ROUTER_PREFLIGHT_OK" if payload["status"] == "ok" else "DOC_ROUTER_PREFLIGHT_BLOCKED"
    fn = ok_result if payload["status"] == "ok" else error_result
    return fn(code, payload.get("blocked_reason") or "Preflight complete", **payload)


def run_doc_router_validate(args: argparse.Namespace):
    root = Path(args.root).resolve() if getattr(args, "root", None) else suite_root()
    db = Path(args.db).resolve() if getattr(args, "db", None) else None
    payload = doc_router.validate_index(db_path=db, root=root)
    if payload["status"] == "ok":
        return ok_result("DOC_ROUTER_VALIDATE_OK", "DocRouter index valid", **payload)
    return error_result("DOC_ROUTER_VALIDATE_FAIL", "; ".join(payload.get("issues", [])), **payload)


def run_doc_router_explain(args: argparse.Namespace):
    query = (args.query or "").strip()
    docs_raw = (args.docs or "").strip()
    if not query or not docs_raw:
        return error_result("DOC_ROUTER_EXPLAIN_EMPTY", "Provide --query and --docs JSON array")
    try:
        docs = json.loads(docs_raw)
    except json.JSONDecodeError as exc:
        return error_result("DOC_ROUTER_EXPLAIN_INVALID", str(exc))
    payload = doc_router.explain_selection(query, docs)
    return ok_result("DOC_ROUTER_EXPLAIN_OK", f"Explained {payload['count']} selection(s)", **payload)
