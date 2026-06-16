"""Tests for analytics module (Sprint 6)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from novel_suite import mcp_server
from novel_suite.analytics.cli import (
    cmd_analytics_cross_report,
    cmd_analytics_record,
    cmd_analytics_report,
    cmd_analytics_status,
)
from novel_suite.analytics.schema import (
    create_analytics_record,
    parse_metrics_text,
    validate_metrics,
)
from novel_suite.analytics.store import add_record, get_latest_metrics, load_records
from novel_suite.core import errors as E
from novel_suite.video.publish.guide import get_publish_guide


def test_validate_metrics_valid():
    ok, errors = validate_metrics({"play_count": 100, "revenue_yuan": 12.5})
    assert ok is True
    assert errors == []


def test_validate_metrics_invalid():
    ok, errors = validate_metrics({"not_a_metric": 1})
    assert ok is False
    assert any("unknown metric" in e for e in errors)


def test_create_record():
    rec = create_analytics_record(
        content_type="video",
        content_key="ch01",
        metrics={"play_count": 1000.0},
    )
    assert rec["content_type"] == "video"
    assert rec["metrics"]["play_count"] == 1000.0
    assert "recorded_at" in rec


def test_store_and_load(novels_scratch: Path):
    rec = create_analytics_record(
        content_type="novel",
        content_key="full",
        metrics={"play_count": 500.0},
    )
    add_record(novels_scratch, rec)
    loaded = load_records(novels_scratch)
    assert len(loaded) == 1
    assert loaded[0]["metrics"]["play_count"] == 500.0


def test_get_latest_metrics_aggregation(novels_scratch: Path):
    add_record(
        novels_scratch,
        create_analytics_record(
            content_type="novel",
            content_key="full",
            metrics={"play_count": 15000, "revenue_yuan": 12.5, "completion_rate": 0.4},
        ),
    )
    add_record(
        novels_scratch,
        create_analytics_record(
            content_type="novel",
            content_key="full",
            metrics={"play_count": 20000, "revenue_yuan": 8.0, "completion_rate": 0.6},
        ),
    )
    summary = get_latest_metrics(novels_scratch)
    assert summary["record_count"] == 2
    assert summary["metrics"]["play_count"] == 35000
    assert summary["metrics"]["revenue_yuan"] == pytest.approx(20.5)
    assert summary["metrics"]["completion_rate"] == pytest.approx(0.5)


def test_report_generates_markdown(novels_scratch: Path):
    add_record(
        novels_scratch,
        create_analytics_record(
            content_type="video",
            content_key="ch01",
            metrics={"play_count": 100, "revenue_yuan": 1.0},
        ),
    )
    args = argparse.Namespace(project=novels_scratch, period="all", json=True)
    result = cmd_analytics_report(args)
    assert result.status == "ok"
    assert result.code == E.ANALYTICS_REPORT_OK
    report_path = Path(result.details["report_path"])
    assert report_path.is_file()
    text = report_path.read_text(encoding="utf-8")
    assert "Analytics Report" in text
    assert "play_count" in text


def test_cross_report_no_projects(repo_root: Path, monkeypatch: pytest.MonkeyPatch):
    import novel_suite.writer.registry as ns_reg

    novels = repo_root / "novels_empty_test"
    novels.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(ns_reg, "NOVELS_DIR", novels)
    monkeypatch.setattr(ns_reg, "REGISTRY_PATH", novels / "_registry.json")
    monkeypatch.setattr(ns_reg, "ACTIVE_PATH", novels / ".active")
    (novels / "_registry.json").write_text(
        json.dumps({"version": 1, "novels": [], "active_slug": None}),
        encoding="utf-8",
    )
    result = cmd_analytics_cross_report(argparse.Namespace(json=True))
    assert result.status == "error"
    assert result.code == E.ANALYTICS_NO_PROJECTS


def test_mcp_record_parse(novels_scratch: Path):
    payload = json.dumps({"play_count": 15000, "revenue_yuan": 12.5})
    data = mcp_server.tool_analytics_record(str(novels_scratch), payload)
    assert data["status"] == "ok"
    assert data["code"] == E.ANALYTICS_RECORD_OK
    summary = get_latest_metrics(novels_scratch)
    assert summary["metrics"]["play_count"] == 15000


def test_parse_metrics_text_chinese():
    metrics, errors = parse_metrics_text("播放量=15000 收入=12.5")
    assert errors == []
    assert metrics["play_count"] == 15000
    assert metrics["revenue_yuan"] == 12.5


def test_analytics_record_cli(novels_scratch: Path):
    args = argparse.Namespace(
        project=novels_scratch,
        metrics="播放量=15000 收入=12.5",
        type="novel",
        key="ch01",
        json=True,
    )
    result = cmd_analytics_record(args)
    assert result.code == E.ANALYTICS_RECORD_OK
    status = cmd_analytics_status(argparse.Namespace(project=novels_scratch, json=True))
    assert status.details["metrics"]["play_count"] == 15000


def test_analytics_guide():
    guide = get_publish_guide("analytics")
    assert guide["platform_type"] == "analytics"
    assert guide["step_count"] == 3
    assert guide["steps"][0]["action"] == "record_data"


def test_mcp_analytics_report_cross(monkeypatch: pytest.MonkeyPatch):
    with patch(
        "novel_suite.analytics.cli.registry.load_registry",
        return_value={"novels": [], "active_slug": None},
    ):
        data = mcp_server.tool_analytics_report("")
    assert data["status"] == "error"
    assert data["code"] == E.ANALYTICS_NO_PROJECTS
