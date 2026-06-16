"""DocRouter — index, query, preflight, read-budget tests."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from novel_suite.core import doc_router


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "doc_router"


def _write_fixture(name: str, body: str, tmp: Path) -> Path:
    p = tmp / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


@pytest.fixture
def fixture_docs(tmp_path: Path) -> Path:
    _write_fixture(
        "realpipeline.md",
        """<!-- DOC_CHAIN_START -->
> chain_id: `realpipeline-2b`
> node_id: `realpipeline-2b-report`
> node_type: `report`
<!-- DOC_CHAIN_END -->

<!-- DOC_META_START -->
> 文档类型：阶段报告/RealPipeline-2B
> 所属分类：docs
<!-- DOC_META_END -->

# RealPipeline-2B 执行报告

视频短板与 NVP 强制完整任务链验证。
""",
        tmp_path,
    )
    _write_fixture(
        "videorender_comfyui.md",
        """# VideoRender ComfyUI 工作流选择

ComfyUI workflow adapter 真出图路径与 smoke 测试说明。
""",
        tmp_path,
    )
    _write_fixture(
        "cursor_freeze.md",
        """<!-- DOC_CHAIN_START -->
> node_id: `cursor-freeze-root-cause-audit-20260617`
<!-- DOC_CHAIN_END -->

# Cursor 卡顿根因审计：state.vscdb 膨胀

bubbleId checkpointId agentKv 堆积导致 Cursor 卡顿。
""",
        tmp_path,
    )
    _write_fixture(
        "large_doc.md",
        "# Large Doc\n\n" + ("x" * 2_000_000),
        tmp_path,
    )
    return tmp_path


def test_build_index_generates_sqlite(fixture_docs: Path, tmp_path: Path):
    db = tmp_path / "index.sqlite"
    result = doc_router.build_index(paths=[fixture_docs], out_db=db, root=fixture_docs)
    assert db.is_file()
    assert result["indexed"] >= 3
    conn = sqlite3.connect(str(db))
    count = conn.execute("SELECT COUNT(*) FROM doc_index").fetchone()[0]
    conn.close()
    assert count >= 3


def test_query_realpipeline(fixture_docs: Path, tmp_path: Path):
    db = tmp_path / "index.sqlite"
    doc_router.build_index(paths=[fixture_docs], out_db=db, root=fixture_docs)
    hits = doc_router.query_index("RealPipeline-2B 视频短板", top_k=10, db_path=db)
    paths = [h.path for h in hits]
    assert any("realpipeline" in p.lower() for p in paths)


def test_query_comfyui(fixture_docs: Path, tmp_path: Path):
    db = tmp_path / "index.sqlite"
    doc_router.build_index(paths=[fixture_docs], out_db=db, root=fixture_docs)
    hits = doc_router.query_index("ComfyUI workflow", top_k=10, db_path=db)
    paths = [h.path for h in hits]
    assert any("comfyui" in p.lower() or "videorender" in p.lower() for p in paths)


def test_query_cursor_freeze(fixture_docs: Path, tmp_path: Path):
    db = tmp_path / "index.sqlite"
    doc_router.build_index(paths=[fixture_docs], out_db=db, root=fixture_docs)
    hits = doc_router.query_index("Cursor 卡顿 state.vscdb", top_k=10, db_path=db)
    paths = [h.path for h in hits]
    assert any("cursor" in p.lower() or "freeze" in p.lower() for p in paths)


def test_high_critical_blocks_full_read():
    high = doc_router.read_budget_guard("high", requested_docs=4, requested_chars=4000)
    assert high["budget"]["allow_full_read"] is False

    over = doc_router.read_budget_guard("high", requested_docs=10, requested_chars=12000, allow_full_read=True)
    assert over["allowed"] is False

    critical = doc_router.read_budget_guard("critical", requested_docs=1, requested_chars=1000)
    assert critical["allowed"] is False
    assert critical["budget"]["summary_only"] is True


def test_large_file_not_fully_indexed(fixture_docs: Path, tmp_path: Path):
    db = tmp_path / "index.sqlite"
    doc_router.build_index(paths=[fixture_docs], out_db=db, root=fixture_docs)
    conn = sqlite3.connect(str(db))
    row = conn.execute(
        "SELECT summary, is_large, size FROM doc_index WHERE path LIKE '%large_doc%'"
    ).fetchone()
    conn.close()
    assert row is not None
    assert row[1] == 1
    assert len(row[0]) < 5000


def test_doc_chain_parseable(fixture_docs: Path):
    text = (fixture_docs / "realpipeline.md").read_text(encoding="utf-8")
    chain = doc_router.parse_doc_chain(text)
    assert chain.get("node_id") == "realpipeline-2b-report"
    assert chain.get("chain_id") == "realpipeline-2b"


def test_validate_ok(fixture_docs: Path, tmp_path: Path):
    db = tmp_path / "index.sqlite"
    doc_router.build_index(paths=[fixture_docs], out_db=db, root=fixture_docs)
    payload = doc_router.validate_index(db_path=db, root=fixture_docs)
    assert payload["status"] == "ok"
    assert payload["document_count"] >= 3
    assert payload["fts_ok"] is True


def test_preflight_critical_blocks():
    payload = doc_router.preflight("test task", risk_level="critical")
    assert payload["status"] == "blocked"
    assert payload["read_budget"]["summary_only"] is True


def test_explain_selection(fixture_docs: Path, tmp_path: Path):
    db = tmp_path / "index.sqlite"
    doc_router.build_index(paths=[fixture_docs], out_db=db, root=fixture_docs)
    hits = doc_router.query_index("RealPipeline", db_path=db)
    expl = doc_router.explain_selection("RealPipeline", hits)
    assert expl["count"] >= 1
    assert expl["selections"][0]["reasons"]
