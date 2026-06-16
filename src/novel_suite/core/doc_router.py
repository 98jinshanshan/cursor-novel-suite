"""DocRouter — SQLite FTS5 document index, query, preflight, and read-budget guard."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import subprocess
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping

from novel_suite.core.paths import suite_root

RiskLevel = Literal["ok", "warning", "high", "critical"]
ScopeName = Literal["cursor_project", "workflow_os_docs", "active_novel"]

DEFAULT_INDEX_PATH = Path(".cache/docrouter/doc_router.sqlite")
LARGE_FILE_BYTES = 1_048_576
HEAD_LINES = 80
SUMMARY_MAX_CHARS = 2000

WORKFLOW_OS_DOCS = Path(
    r"G:/Users/admin/Documents/AI_Workspace_OS/02_Projects_项目区/Project_10_Workflow_OS/docs"
)
CURSOR_HEALTH_SCRIPT = Path(
    r"G:/Users/admin/Documents/AI_Workspace_OS/02_Projects_项目区/Project_10_Workflow_OS/tools/cursor-health/Test-CursorStateHealth.ps1"
)

DEFAULT_EXCLUDE_GLOBS = [
    "**/.git/**",
    "**/.venv/**",
    "**/node_modules/**",
    "**/__pycache__/**",
    "**/.cache/**",
    "**/reports/cursor-health/*.json",
]

BUDGET_BY_RISK: dict[RiskLevel, dict[str, Any]] = {
    "ok": {"top_k": 15, "max_docs": 10, "max_chars_per_doc": 12000, "allow_full_read": True, "summary_only": False, "block_long_task": False},
    "warning": {"top_k": 10, "max_docs": 6, "max_chars_per_doc": 8000, "allow_full_read": True, "summary_only": False, "block_long_task": False},
    "high": {"top_k": 8, "max_docs": 4, "max_chars_per_doc": 4000, "allow_full_read": False, "summary_only": False, "block_long_task": False},
    "critical": {"top_k": 5, "max_docs": 0, "max_chars_per_doc": 0, "allow_full_read": False, "summary_only": True, "block_long_task": True},
}

DOC_CHAIN_RE = re.compile(r"<!-- DOC_CHAIN_START -->(.*?)<!-- DOC_CHAIN_END -->", re.DOTALL)
DOC_META_RE = re.compile(r"<!-- DOC_META_START -->(.*?)<!-- DOC_META_END -->", re.DOTALL)
META_LINE_RE = re.compile(r"^>\s*(.+?):\s*(.+)$", re.MULTILINE)
CHAIN_LINE_RE = re.compile(r"^>\s*(.+?):\s*(.+)$", re.MULTILINE)
HEADING_RE = re.compile(r"^#{1,3}\s+(.+)$", re.MULTILINE)


@dataclass
class DocRecord:
    path: str
    title: str
    category: str
    scope: str
    summary: str
    keywords: str
    header_excerpt: str
    doc_chain: dict[str, str] = field(default_factory=dict)
    doc_meta: dict[str, str] = field(default_factory=dict)
    mtime: float = 0.0
    size: int = 0
    file_hash: str = ""
    is_large: bool = False
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_doc_chain(text: str) -> dict[str, str]:
    match = DOC_CHAIN_RE.search(text)
    if not match:
        return {}
    block = match.group(1)
    return {m.group(1).strip(): m.group(2).strip().strip("`") for m in CHAIN_LINE_RE.finditer(block)}


def parse_doc_meta(text: str) -> dict[str, str]:
    match = DOC_META_RE.search(text)
    if not match:
        return {}
    block = match.group(1)
    return {m.group(1).strip(): m.group(2).strip() for m in META_LINE_RE.finditer(block)}


def _file_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()[:16]


def _extract_title(text: str, path: Path) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    meta = parse_doc_meta(text)
    if meta.get("文档类型"):
        return meta["文档类型"]
    return path.stem


def _extract_category(text: str, path: Path) -> str:
    meta = parse_doc_meta(text)
    if meta.get("所属分类"):
        return meta["所属分类"]
    parts = path.parts
    for name in ("docs", "novel-suite", "skills", "canon", "chapters", "reviews", "video"):
        if name in parts:
            idx = parts.index(name)
            if idx + 1 < len(parts):
                return f"{name}/{parts[idx + 1]}"
            return name
    return path.suffix.lstrip(".") or "unknown"


def _extract_keywords(text: str, doc_chain: dict[str, str], doc_meta: dict[str, str]) -> str:
    tokens: list[str] = []
    for key in ("node_id", "chain_id", "node_type", "文档类型", "当前状态"):
        val = doc_chain.get(key) or doc_meta.get(key)
        if val:
            tokens.append(val)
    headings = HEADING_RE.findall(text[:8000])
    tokens.extend(headings[:12])
    return " ".join(dict.fromkeys(tokens))


def _build_summary(text: str, *, max_chars: int = SUMMARY_MAX_CHARS) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--"):
            continue
        if stripped.startswith(">"):
            continue
        if stripped.startswith("#"):
            lines.append(stripped.lstrip("#").strip())
        elif stripped.startswith("|") or stripped.startswith("```"):
            continue
        else:
            lines.append(stripped)
        if sum(len(x) + 1 for x in lines) >= max_chars:
            break
    summary = " ".join(lines)
    return summary[:max_chars]


def _read_file_excerpt(path: Path) -> tuple[str, str, int, bool]:
    raw = path.read_bytes()
    size = len(raw)
    is_large = size > LARGE_FILE_BYTES
    text = raw[:LARGE_FILE_BYTES if is_large else size].decode("utf-8", errors="replace")
    header = "\n".join(text.splitlines()[:HEAD_LINES])
    return text, header, size, is_large


def _matches_glob(path: Path, pattern: str) -> bool:
    return path.match(pattern.replace("**/", "").replace("/**", "/*")) or path.match(pattern)


def _should_exclude(path: Path, exclude_globs: list[str]) -> bool:
    pstr = str(path).replace("\\", "/")
    for pat in exclude_globs:
        norm = pat.replace("\\", "/")
        if norm.endswith("/**"):
            prefix = norm[:-3]
            if prefix in pstr:
                return True
        elif path.match(norm):
            return True
    return False


def _active_novel_slug(root: Path) -> str | None:
    active_file = root / "novels" / ".active"
    if not active_file.is_file():
        return None
    slug = active_file.read_text(encoding="utf-8").strip()
    return slug or None


def default_scope_paths(root: Path, scope: ScopeName | str) -> list[Path]:
    root = root.resolve()
    paths: list[Path] = []
    if scope == "cursor_project":
        candidates = [
            root / "README.md",
            root / "docs",
            root / "novel-suite",
            root / "src",
            root / "tests",
        ]
        for c in candidates:
            if c.is_file():
                paths.append(c)
            elif c.is_dir():
                paths.append(c)
    elif scope == "workflow_os_docs":
        if WORKFLOW_OS_DOCS.is_dir():
            paths.append(WORKFLOW_OS_DOCS)
    elif scope == "active_novel":
        slug = _active_novel_slug(root)
        if slug:
            novel = root / "novels" / slug
            for sub in ("canon", "chapters", "reviews", "video"):
                p = novel / sub
                if p.is_dir():
                    paths.append(p)
    return paths


def collect_files(
    paths: list[Path | str],
    *,
    include_globs: list[str] | None = None,
    exclude_globs: list[str] | None = None,
) -> list[Path]:
    exclude = exclude_globs or DEFAULT_EXCLUDE_GLOBS
    found: list[Path] = []
    seen: set[str] = set()

    def _add(path: Path) -> None:
        key = str(path.resolve())
        if key in seen:
            return
        if not path.is_file():
            return
        if _should_exclude(path, exclude):
            return
        if path.suffix.lower() not in {".md", ".py"}:
            return
        seen.add(key)
        found.append(path.resolve())

    for raw in paths:
        p = Path(raw).resolve()
        if p.is_file():
            _add(p)
        elif p.is_dir():
            for ext in (".md", ".py"):
                for match in p.rglob(f"*{ext}"):
                    _add(match)
    return sorted(found, key=lambda x: str(x).lower())


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS doc_index USING fts5(
          path UNINDEXED,
          title,
          category UNINDEXED,
          scope UNINDEXED,
          summary,
          keywords,
          header_excerpt,
          doc_chain UNINDEXED,
          doc_meta UNINDEXED,
          mtime UNINDEXED,
          size UNINDEXED,
          file_hash UNINDEXED,
          is_large UNINDEXED,
          tokenize='unicode61'
        );
        """
    )
    conn.commit()


def index_document(path: Path, scope: str) -> DocRecord | None:
    try:
        text, header, size, is_large = _read_file_excerpt(path)
    except OSError:
        return None
    doc_chain = parse_doc_chain(text)
    doc_meta = parse_doc_meta(text)
    title = _extract_title(text, path)
    category = _extract_category(text, path)
    summary = _build_summary(text)
    keywords = _extract_keywords(text, doc_chain, doc_meta)
    stat = path.stat()
    content_for_hash = header.encode("utf-8") if is_large else path.read_bytes()[:65536]
    return DocRecord(
        path=str(path),
        title=title,
        category=category,
        scope=scope,
        summary=summary,
        keywords=keywords,
        header_excerpt=header[:4000],
        doc_chain=doc_chain,
        doc_meta=doc_meta,
        mtime=stat.st_mtime,
        size=size,
        file_hash=_file_hash(content_for_hash),
        is_large=is_large,
    )


def build_index(
    paths: list[Path | str] | None = None,
    out_db: Path | str | None = None,
    *,
    root: Path | str | None = None,
    scopes: list[str] | None = None,
    include_globs: list[str] | None = None,
    exclude_globs: list[str] | None = None,
) -> dict[str, Any]:
    root_path = Path(root).resolve() if root else suite_root()
    db_path = Path(out_db) if out_db else (root_path / DEFAULT_INDEX_PATH)
    scope_list = scopes or ["cursor_project", "workflow_os_docs", "active_novel"]

    all_files: list[tuple[Path, str]] = []
    for scope in scope_list:
        for base in default_scope_paths(root_path, scope):
            for fp in collect_files([base], include_globs=include_globs, exclude_globs=exclude_globs):
                all_files.append((fp, scope))
    if paths:
        for fp in collect_files(list(paths), include_globs=include_globs, exclude_globs=exclude_globs):
            all_files.append((fp, "custom"))

    conn = _connect(db_path)
    _init_schema(conn)
    conn.execute("DELETE FROM doc_index")
    indexed = 0
    skipped = 0
    for fp, scope in all_files:
        rec = index_document(fp, scope)
        if rec is None:
            skipped += 1
            continue
        conn.execute(
            """
            INSERT INTO doc_index (
              path, title, category, scope, summary, keywords, header_excerpt,
              doc_chain, doc_meta, mtime, size, file_hash, is_large
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rec.path,
                rec.title,
                rec.category,
                rec.scope,
                rec.summary,
                rec.keywords,
                rec.header_excerpt,
                json.dumps(rec.doc_chain, ensure_ascii=False),
                json.dumps(rec.doc_meta, ensure_ascii=False),
                rec.mtime,
                rec.size,
                rec.file_hash,
                1 if rec.is_large else 0,
            ),
        )
        indexed += 1

    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        ("built_at", datetime.now(timezone.utc).isoformat()),
    )
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        ("indexed_count", str(indexed)),
    )
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        ("root", str(root_path)),
    )
    conn.commit()
    conn.close()
    return {
        "db_path": str(db_path),
        "indexed": indexed,
        "skipped": skipped,
        "scopes": scope_list,
        "root": str(root_path),
    }


def _default_db(root: Path | None = None) -> Path:
    base = root or suite_root()
    return base / DEFAULT_INDEX_PATH


def query_index(
    query: str,
    *,
    top_k: int = 10,
    scope: str | None = None,
    max_docs: int | None = None,
    max_chars: int | None = None,
    db_path: Path | str | None = None,
    root: Path | str | None = None,
) -> list[DocRecord]:
    root_path = Path(root).resolve() if root else suite_root()
    db = Path(db_path) if db_path else _default_db(root_path)
    if not db.is_file():
        return []

    conn = _connect(db)
    rows: list[sqlite3.Row] = []

    fts_query = " OR ".join(f'"{t}"' for t in query.split() if t.strip())
    if fts_query:
        sql = """
            SELECT path, title, category, scope, summary, keywords, header_excerpt,
                   doc_chain, doc_meta, mtime, size, file_hash, is_large,
                   bm25(doc_index) AS score
            FROM doc_index
            WHERE doc_index MATCH ?
        """
        params: list[Any] = [fts_query]
        if scope:
            sql += " AND scope = ?"
            params.append(scope)
        sql += " ORDER BY score LIMIT ?"
        params.append(top_k)
        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError:
            rows = []

    if len(rows) < top_k:
        like_params: list[Any] = []
        like_clauses = []
        for token in query.split():
            t = token.strip()
            if not t:
                continue
            like_clauses.append(
                "(path LIKE ? OR title LIKE ? OR summary LIKE ? OR keywords LIKE ? OR header_excerpt LIKE ?)"
            )
            pat = f"%{t}%"
            like_params.extend([pat] * 5)
        if like_clauses:
            sql = f"""
                SELECT path, title, category, scope, summary, keywords, header_excerpt,
                       doc_chain, doc_meta, mtime, size, file_hash, is_large,
                       0.0 AS score
                FROM doc_index
                WHERE ({' OR '.join(like_clauses)})
            """
            if scope:
                sql += " AND scope = ?"
                like_params.append(scope)
            sql += " LIMIT ?"
            like_params.append(top_k)
            existing = {r["path"] for r in rows}
            for row in conn.execute(sql, like_params).fetchall():
                if row["path"] not in existing:
                    rows.append(row)
                    existing.add(row["path"])
                if len(rows) >= top_k:
                    break

    conn.close()

    limit = max_docs if max_docs is not None else top_k
    results: list[DocRecord] = []
    for row in rows[:limit]:
        excerpt = row["header_excerpt"] or ""
        if max_chars is not None:
            excerpt = excerpt[:max_chars]
        results.append(
            DocRecord(
                path=row["path"],
                title=row["title"] or "",
                category=row["category"] or "",
                scope=row["scope"] or "",
                summary=(row["summary"] or "")[: (max_chars or SUMMARY_MAX_CHARS)],
                keywords=row["keywords"] or "",
                header_excerpt=excerpt,
                doc_chain=json.loads(row["doc_chain"] or "{}"),
                doc_meta=json.loads(row["doc_meta"] or "{}"),
                mtime=float(row["mtime"] or 0),
                size=int(row["size"] or 0),
                file_hash=row["file_hash"] or "",
                is_large=bool(row["is_large"]),
                score=float(row["score"] or 0),
            )
        )
    return results


def explain_selection(query: str, selected_docs: Iterable[DocRecord | Mapping[str, Any]]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for doc in selected_docs:
        if isinstance(doc, DocRecord):
            d = doc.to_dict()
        else:
            d = dict(doc)
        reasons: list[str] = []
        q_lower = query.lower()
        for field_name in ("title", "summary", "keywords", "path"):
            val = str(d.get(field_name, "")).lower()
            for token in query.split():
                if token.lower() in val:
                    reasons.append(f"matched '{token}' in {field_name}")
        chain = d.get("doc_chain") or {}
        if chain.get("node_id"):
            reasons.append(f"DOC_CHAIN node_id={chain['node_id']}")
        items.append({"path": d.get("path"), "title": d.get("title"), "reasons": reasons[:6], "score": d.get("score", 0)})
    return {"query": query, "count": len(items), "selections": items}


def read_budget_guard(
    risk_level: RiskLevel,
    requested_docs: int,
    requested_chars: int,
    *,
    allow_full_read: bool | None = None,
) -> dict[str, Any]:
    budget = dict(BUDGET_BY_RISK.get(risk_level, BUDGET_BY_RISK["ok"]))
    if allow_full_read is not None:
        budget["allow_full_read"] = allow_full_read and budget.get("allow_full_read", True)

    violations: list[str] = []
    allowed = True
    if requested_docs > budget["max_docs"]:
        violations.append(f"requested_docs {requested_docs} > max_docs {budget['max_docs']}")
        allowed = False
    if requested_chars > budget["max_chars_per_doc"] and budget["max_chars_per_doc"] > 0:
        violations.append(
            f"requested_chars {requested_chars} > max_chars_per_doc {budget['max_chars_per_doc']}"
        )
        allowed = False
    if budget.get("summary_only") and requested_docs > 0:
        violations.append("critical risk: summary_only mode — no full document reads")
        allowed = False
    if not budget.get("allow_full_read", True) and allow_full_read:
        violations.append(f"{risk_level} risk: full read not allowed")
        allowed = False

    return {"risk_level": risk_level, "budget": budget, "allowed": allowed, "violations": violations}


def probe_cursor_health() -> dict[str, Any]:
    if not CURSOR_HEALTH_SCRIPT.is_file():
        return {"available": False, "risk_level": "ok", "source": "unavailable", "detail": "health script not found"}
    try:
        proc = subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(CURSOR_HEALTH_SCRIPT),
                "-Json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        raw = (proc.stdout or "").strip()
        if not raw:
            return {"available": False, "risk_level": "ok", "source": "script_empty", "detail": proc.stderr[:200]}
        data = json.loads(raw)
        return {
            "available": True,
            "risk_level": data.get("risk_level", "ok"),
            "source": "Test-CursorStateHealth.ps1",
            "state_db_mb": data.get("state_db_mb"),
            "detail": data,
        }
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as exc:
        return {"available": False, "risk_level": "ok", "source": "error", "detail": str(exc)}


def probe_qdrant() -> dict[str, Any]:
    url = "http://127.0.0.1:6333/collections"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:  # noqa: S310
            body = json.loads(resp.read().decode("utf-8"))
            return {"available": True, "url": url, "collections": body.get("result", {}).get("collections", [])}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return {"available": False, "url": url, "error": str(exc)}


def probe_embedding_model() -> dict[str, Any]:
    try:
        import sentence_transformers  # type: ignore[import-untyped]  # noqa: F401

        return {"available": True, "package": "sentence-transformers", "note": "installed; no auto-download attempted"}
    except ImportError:
        return {
            "available": False,
            "package": "sentence-transformers",
            "note": "not installed; SQLite FTS remains primary; install manually if needed",
        }


def preflight(
    query: str,
    *,
    db_path: Path | str | None = None,
    root: Path | str | None = None,
    risk_level: RiskLevel | None = None,
) -> dict[str, Any]:
    health = probe_cursor_health()
    risk: RiskLevel = risk_level or health.get("risk_level", "ok")  # type: ignore[assignment]
    if risk not in BUDGET_BY_RISK:
        risk = "ok"

    budget_cfg = BUDGET_BY_RISK[risk]
    hits = query_index(
        query,
        top_k=budget_cfg["top_k"],
        max_docs=budget_cfg["max_docs"] or budget_cfg["top_k"],
        max_chars=budget_cfg["max_chars_per_doc"] or None,
        db_path=db_path,
        root=root,
    )

    selected = [h.to_dict() for h in hits]
    guard = read_budget_guard(risk, len(selected), budget_cfg["max_chars_per_doc"])

    status: Literal["ok", "blocked"] = "ok"
    blocked_reason: str | None = None
    if budget_cfg.get("block_long_task"):
        status = "blocked"
        blocked_reason = "critical Cursor state risk — long tasks blocked; summary-only mode"
    elif not guard["allowed"]:
        status = "blocked"
        blocked_reason = "; ".join(guard["violations"])

    return {
        "status": status,
        "risk_level": risk,
        "query": query,
        "selected_docs": selected,
        "read_budget": {
            "max_docs": budget_cfg["max_docs"],
            "max_chars_per_doc": budget_cfg["max_chars_per_doc"],
            "allow_full_read": budget_cfg["allow_full_read"],
            "summary_only": budget_cfg.get("summary_only", False),
            "top_k": budget_cfg["top_k"],
        },
        "blocked_reason": blocked_reason,
        "cursor_health": health,
        "explanation": explain_selection(query, selected),
    }


def validate_index(*, db_path: Path | str | None = None, root: Path | str | None = None) -> dict[str, Any]:
    root_path = Path(root).resolve() if root else suite_root()
    db = Path(db_path) if db_path else _default_db(root_path)
    issues: list[str] = []
    if not db.is_file():
        issues.append(f"index missing: {db}")
        return {"status": "error", "issues": issues, "db_path": str(db)}

    conn = _connect(db)
    try:
        count = conn.execute("SELECT COUNT(*) AS c FROM doc_index").fetchone()["c"]
        meta = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM meta")}
    except sqlite3.Error as exc:
        issues.append(f"schema error: {exc}")
        return {"status": "error", "issues": issues, "db_path": str(db)}
    finally:
        conn.close()

    if count == 0:
        issues.append("index empty — run doc-router build")
    fts_ok = True
    try:
        conn = _connect(db)
        conn.execute("SELECT path FROM doc_index WHERE doc_index MATCH 'test' LIMIT 1")
        conn.close()
    except sqlite3.Error:
        fts_ok = False
        issues.append("FTS5 query failed")

    return {
        "status": "ok" if not issues else "error",
        "issues": issues,
        "db_path": str(db),
        "document_count": count,
        "built_at": meta.get("built_at"),
        "fts_ok": fts_ok,
        "vector_backend": {"qdrant": probe_qdrant(), "embedding": probe_embedding_model()},
    }
