"""
Novel Suite MCP Server — auth + publish tools for agents.

Run (local stdio only):
  py -3 -m novel_suite.mcp_server

Requires: pip install mcp
Security: do not expose to public network without authentication.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from novel_suite.auth.cli import cmd_auth_login, cmd_auth_logout, cmd_auth_status
from novel_suite.core.paths import assert_project_in_allowed_roots
from novel_suite.platforms._registry import list_platforms
from novel_suite.analytics.cli import (
    cmd_analytics_cross_report,
    cmd_analytics_record_from_json,
    cmd_analytics_report,
)
from novel_suite.novel.publish.cli import cmd_novel_publish_upload
from novel_suite.video.publish.cli import cmd_publish
from novel_suite.video.publish.guide import get_publish_guide
from novel_suite.video.publish.status import publish_readiness
from novel_suite.writer import registry
from novel_suite.core.product_layer import (
    tool_product_list,
    tool_product_read,
    tool_product_validate,
)


def _result_json(result: Any) -> str:
    return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)


def _resolve_project_path(project: str) -> Path:
    resolved = registry.resolve_project(Path(project))
    return assert_project_in_allowed_roots(resolved)


def tool_publish_platforms(platform_type: str | None = None) -> dict[str, Any]:
    ptype = platform_type.strip() if platform_type else None
    platforms = list_platforms(platform_type=ptype) if ptype in ("video", "novel") else list_platforms()
    return {"platforms": platforms, "count": len(platforms)}


def tool_publish_readiness(
    platform: str,
    project: str,
    chapter_key: str = "ch01",
    skip_gate: bool = False,
) -> dict[str, Any]:
    project_path = _resolve_project_path(project)
    return publish_readiness(
        platform,
        project_path,
        chapter_key=chapter_key,
        skip_gate=skip_gate,
    )


def tool_publish_guide(platform: str) -> dict[str, Any]:
    return get_publish_guide(platform)


def tool_publish_upload(
    platform: str,
    project: str,
    chapter_key: str = "ch01",
    title: str = "",
    skip_gate: bool = False,
    no_headless: bool = False,
) -> dict[str, Any]:
    args = argparse.Namespace(
        project=Path(project),
        chapter_key=chapter_key,
        platform=platform,
        title=title or None,
        skip_gate=skip_gate,
        no_headless=no_headless,
        json=True,
    )
    return cmd_publish(args).to_dict()


def tool_auth_login(platform: str) -> dict[str, Any]:
    return cmd_auth_login(argparse.Namespace(platform=platform, json=True)).to_dict()


def tool_auth_status(platform: str = "") -> dict[str, Any]:
    return cmd_auth_status(
        argparse.Namespace(platform=platform or None, json=True)
    ).to_dict()


def tool_auth_logout(platform: str) -> dict[str, Any]:
    return cmd_auth_logout(argparse.Namespace(platform=platform, json=True)).to_dict()


def tool_analytics_record(project: str, metrics_json: str) -> dict[str, Any]:
    try:
        payload = json.loads(metrics_json) if metrics_json.strip() else {}
    except json.JSONDecodeError as exc:
        return {"status": "error", "code": "ANALYTICS_INVALID_METRIC", "message": str(exc)}
    if not isinstance(payload, dict):
        return {"status": "error", "code": "ANALYTICS_INVALID_METRIC", "message": "metrics_json must be object"}
    project_path = _resolve_project_path(project)
    return cmd_analytics_record_from_json(project_path, payload).to_dict()


def tool_analytics_report(project: str = "") -> dict[str, Any]:
    if not (project or "").strip():
        return cmd_analytics_cross_report(argparse.Namespace(json=True)).to_dict()
    project_path = _resolve_project_path(project)
    return cmd_analytics_report(
        argparse.Namespace(project=project_path, period="all", json=True)
    ).to_dict()


def tool_novel_publish_upload(platform: str, project: str) -> dict[str, Any]:
    args = argparse.Namespace(
        project=Path(project),
        platform=platform,
        json=True,
    )
    return cmd_novel_publish_upload(args).to_dict()


def run_server(*, transport: str = "stdio") -> None:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print("Install: pip install mcp", file=sys.stderr)
        sys.exit(1)

    mcp = FastMCP("novel-suite")

    @mcp.tool()
    def publish_platforms(platform_type: str = "") -> str:
        """List supported publish platforms (optional filter: video or novel)."""
        return json.dumps(
            tool_publish_platforms(platform_type or None),
            ensure_ascii=False,
            indent=2,
        )

    @mcp.tool()
    def publish_readiness_tool(
        platform: str,
        project: str,
        chapter_key: str = "ch01",
        skip_gate: bool = False,
    ) -> str:
        """Check if a platform is ready to publish (auth, video, gate)."""
        try:
            data = tool_publish_readiness(platform, project, chapter_key, skip_gate)
        except ValueError as exc:
            data = {"ready": False, "error": str(exc)}
        return json.dumps(data, ensure_ascii=False, indent=2)

    @mcp.tool()
    def publish_guide(platform: str) -> str:
        """Get ordered publish steps for agents (login → pipeline → gate → upload)."""
        return json.dumps(tool_publish_guide(platform), ensure_ascii=False, indent=2)

    @mcp.tool()
    def publish_upload(
        platform: str,
        project: str,
        chapter_key: str = "ch01",
        title: str = "",
        skip_gate: bool = False,
        no_headless: bool = False,
    ) -> str:
        """Upload and publish chapter video to a platform."""
        try:
            data = tool_publish_upload(
                platform, project, chapter_key, title, skip_gate, no_headless
            )
        except ValueError as exc:
            data = {"status": "error", "message": str(exc)}
        return json.dumps(data, ensure_ascii=False, indent=2)

    @mcp.tool()
    def auth_login(platform: str) -> str:
        """Login to a platform (OAuth or API key)."""
        return _result_json(cmd_auth_login(argparse.Namespace(platform=platform, json=True)))

    @mcp.tool()
    def auth_status(platform: str = "") -> str:
        """Check login status for one or all platforms."""
        return _result_json(
            cmd_auth_status(argparse.Namespace(platform=platform or None, json=True))
        )

    @mcp.tool()
    def auth_logout(platform: str) -> str:
        """Logout and delete stored credentials for a platform."""
        return _result_json(cmd_auth_logout(argparse.Namespace(platform=platform, json=True)))

    @mcp.tool()
    def analytics_record(project: str, metrics_json: str) -> str:
        """Record publish performance metrics (JSON object with play_count, revenue_yuan, etc.)."""
        try:
            data = tool_analytics_record(project, metrics_json)
        except ValueError as exc:
            data = {"status": "error", "message": str(exc)}
        return json.dumps(data, ensure_ascii=False, indent=2)

    @mcp.tool()
    def analytics_report(project: str = "") -> str:
        """Generate analytics report for one project, or cross-project summary when project is empty."""
        try:
            data = tool_analytics_report(project)
        except ValueError as exc:
            data = {"status": "error", "message": str(exc)}
        return json.dumps(data, ensure_ascii=False, indent=2)

    @mcp.tool()
    def novel_publish_upload(platform: str, project: str) -> str:
        """Publish novel chapters to a web fiction platform (e.g. fanqie)."""
        try:
            data = tool_novel_publish_upload(platform, project)
        except ValueError as exc:
            data = {"status": "error", "message": str(exc)}
        return json.dumps(data, ensure_ascii=False, indent=2)

    @mcp.tool()
    def product_list() -> str:
        """List Novel Suite product-layer docs/contracts (read-only; no TTS/image/publish/API)."""
        return json.dumps(tool_product_list(), ensure_ascii=False, indent=2)

    @mcp.tool()
    def product_read(category: str, name: str) -> str:
        """Read a product-layer asset by category and name (read-only; path traversal blocked)."""
        return json.dumps(tool_product_read(category, name), ensure_ascii=False, indent=2)

    @mcp.tool()
    def product_validate() -> str:
        """Validate product-layer completeness (contracts + required paths; read-only)."""
        return json.dumps(tool_product_validate(), ensure_ascii=False, indent=2)

    if transport == "sse":
        mcp.run(transport="sse")
    else:
        mcp.run()


def main() -> None:
    ap = argparse.ArgumentParser(description="Novel Suite MCP Server")
    ap.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP transport mode (stdio=by IDE, sse=independent HTTP)",
    )
    args = ap.parse_args()
    run_server(transport=args.transport)


if __name__ == "__main__":
    main()
