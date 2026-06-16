"""Tests for ui-agent-workbench static assets."""

from __future__ import annotations

from pathlib import Path

from novel_suite.core.contracts import novel_suite_root


def test_workbench_static_files_exist():
    root = novel_suite_root() / "ui-agent-workbench"
    for rel in (
        "README.md",
        "ui-workbench.sample.json",
        "static/index.html",
        "static/app.js",
        "static/styles.css",
        "design/layout.md",
    ):
        path = root / rel
        assert path.is_file(), rel


def test_index_html_references_blocked():
    html = (novel_suite_root() / "ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    assert "BLOCKED" in html
    assert "planned" in html
    assert "planned-but-blocked" in html or "仍被禁用" in html


def test_app_js_uses_api_routes():
    js = (novel_suite_root() / "ui-agent-workbench/static/app.js").read_text(encoding="utf-8")
    assert "/doctor" in js
    assert "/agents/market-scan/run" in js
    assert "/agents/ip-to-short-drama/run" in js
    assert "ARTIFACT_LABELS" in js
    assert "summary-card" in js or "renderSummaryCard" in js
