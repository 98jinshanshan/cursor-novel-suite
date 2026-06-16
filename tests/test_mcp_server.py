"""Tests for novel-suite MCP tool handlers (no mcp package required)."""

from __future__ import annotations

import json

from novel_suite import mcp_server


def test_tool_publish_platforms():
    data = mcp_server.tool_publish_platforms()
    assert data["count"] == 6


def test_tool_publish_platforms_video_filter():
    data = mcp_server.tool_publish_platforms("video")
    assert data["count"] == 3
    assert all(p["type"] == "video" for p in data["platforms"])


def test_tool_publish_guide():
    data = mcp_server.tool_publish_guide("douyin")
    assert data["step_count"] == 4


def test_tool_auth_status():
    data = mcp_server.tool_auth_status()
    assert data["status"] == "ok"
    assert len(data["details"]["statuses"]) == 6


def test_tool_publish_readiness_json_serializable(novels_scratch):  # noqa: ANN001
    data = mcp_server.tool_publish_readiness("douyin", str(novels_scratch), "ch01")
    text = json.dumps(data, ensure_ascii=False)
    assert "missing" in text


def test_tool_novel_publish_upload_no_api_key(novels_scratch):  # noqa: ANN001
    from unittest.mock import patch

    with patch("novel_suite.novel.publish.fanqie._get_api_key", return_value=None):
        data = mcp_server.tool_novel_publish_upload("fanqie", str(novels_scratch))
    assert data["status"] == "error"
    assert data["code"] == "PUBLISH_FAILED"


def test_tool_novel_publish_upload_demo(demo_project, monkeypatch):  # noqa: ANN001
    from novel_suite.auth.token_store import save_token

    monkeypatch.setenv("FANQIE_API_KEY", "test_mcp_key")
    save_token(
        "fanqie",
        {
            "auth_type": "api_key",
            "api_key": "test_mcp_key",
            "expires_at": "2099-01-01T00:00:00+00:00",
        },
    )
    data = mcp_server.tool_novel_publish_upload("fanqie", str(demo_project))
    assert data["status"] == "ok"
    assert data["code"] == "PUBLISH_OK"


def test_mcp_server_transport_help():
    import subprocess
    import sys
    from pathlib import Path

    repo = Path(__file__).resolve().parents[1]
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.mcp_server", "--help"],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    assert "--transport" in r.stdout
