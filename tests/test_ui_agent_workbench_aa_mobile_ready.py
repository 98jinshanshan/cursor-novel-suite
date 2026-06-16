"""Tests for AA Mobile-Ready PWA input schemas and mobile preview."""

from __future__ import annotations

import json
from pathlib import Path

from novel_suite.core.product_layer import run_product_validate
from novel_suite.cli import cmd_product_validate
from novel_suite.core.commercialization import run_commercial_release_candidate_validate
import argparse


def test_mobile_input_schemas_doc(repo_root: Path):
    path = repo_root / "novel-suite/ui-agent-workbench/mobile_input_schemas.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    for agent in ("市场调研", "ip.to_short_drama", "novel.review"):
        assert agent in text or "IP 转短剧" in text
    assert "demo-only" in text
    assert "auto_rewrite" in text


def test_mobile_artifact_preview_doc(repo_root: Path):
    path = repo_root / "novel-suite/ui-agent-workbench/mobile_artifact_preview.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "Markdown" in text or ".md" in text
    assert "JSON" in text or ".json" in text
    assert "CSV" in text or ".csv" in text


def test_input_panel_in_html(repo_root: Path):
    html = (repo_root / "novel-suite/ui-agent-workbench/static/index.html").read_text(encoding="utf-8")
    assert "agent-input-panel" in html
    assert "menu-legend-tip" in html


def test_input_schemas_and_preview_in_app_js(repo_root: Path):
    js = (repo_root / "novel-suite/ui-agent-workbench/static/app.js").read_text(encoding="utf-8")
    assert "INPUT_SCHEMAS" in js
    assert "PREVIEW_SAMPLES" in js
    assert "renderInputPanel" in js
    assert "renderArtifactPreview" in js
    assert "market-scan" in js
    assert "ip-to-short-drama" in js
    assert "novel-review" in js
    assert "shot_list.csv" in js


def test_mobile_styles(repo_root: Path):
    css = (repo_root / "novel-suite/ui-agent-workbench/static/styles.css").read_text(encoding="utf-8")
    assert "agent-input-panel" in css
    assert "preview-csv-wrap" in css
    assert "max-width: 600px" in css
    assert "min-height: 44px" in css


def test_product_validate_top_level_blocked(monkeypatch, capsys):
    args = argparse.Namespace(json=True)
    code = cmd_product_validate(args)
    assert code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data.get("commercial_release_allowed") is False
    assert data.get("verdict") == "blocked"
    assert data.get("status") == "ok"


def test_product_validate_result_details(repo_root: Path):
    result = run_product_validate()
    assert result.status == "ok"
    assert result.details.get("commercial_release_allowed") is False
    assert result.details.get("verdict") == "blocked"


def test_commercial_still_blocked():
    result = run_commercial_release_candidate_validate()
    assert result.details.get("verdict") == "blocked"
