"""CLI handlers for analytics tracking and reports."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from novel_suite.analytics.schema import (
    create_analytics_record,
    parse_metrics_json,
    parse_metrics_text,
    validate_metrics,
)
from novel_suite.analytics.store import add_record, get_latest_metrics, load_records
from novel_suite.core import errors as E
from novel_suite.core.paths import assert_project_in_allowed_roots
from novel_suite.core.result import Result, artifact, error_result, ok_result
from novel_suite.video.publish.record import load_records as load_publish_records
from novel_suite.writer import registry

PUBLISH_KEYS = ("full", "ch01")


def _resolve_project(args: argparse.Namespace) -> Result | Path:
    try:
        project = registry.resolve_project(args.project)
        return assert_project_in_allowed_roots(project)
    except ValueError as exc:
        code = (
            E.PROJECT_PATH_OUT_OF_BOUNDS
            if E.PROJECT_PATH_OUT_OF_BOUNDS in str(exc)
            else E.NO_ACTIVE_NOVEL
        )
        return error_result(code, str(exc))


def _collect_publish_summaries(project: Path) -> dict[str, Any]:
    summaries: dict[str, Any] = {}
    total = 0
    successful = 0
    failed = 0
    for key in PUBLISH_KEYS:
        records = load_publish_records(project, key)
        ok_count = sum(1 for r in records if r.get("ok"))
        fail_count = sum(1 for r in records if not r.get("ok"))
        summaries[key] = {
            "chapter_key": key,
            "total": len(records),
            "successful": ok_count,
            "failed": fail_count,
            "latest": records[0] if records else None,
        }
        total += len(records)
        successful += ok_count
        failed += fail_count
    return {
        "by_key": summaries,
        "total": total,
        "successful": successful,
        "failed": failed,
    }


def _render_report_markdown(
    project: Path,
    *,
    metrics_summary: dict[str, Any],
    publish_summary: dict[str, Any],
    period: str,
) -> str:
    title = project.name
    project_json = project / "canon" / "project.json"
    if project_json.is_file():
        try:
            data = json.loads(project_json.read_text(encoding="utf-8"))
            title = data.get("title") or title
        except (json.JSONDecodeError, OSError):
            pass

    metrics = metrics_summary.get("metrics") or {}
    lines = [
        f"# Analytics Report — {title}",
        "",
        f"- **Project**: `{project}`",
        f"- **Period**: {period}",
        f"- **Generated**: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Metrics Summary",
        "",
        f"- play_count: {metrics.get('play_count', 0):.0f}",
        f"- like_count: {metrics.get('like_count', 0):.0f}",
        f"- comment_count: {metrics.get('comment_count', 0):.0f}",
        f"- share_count: {metrics.get('share_count', 0):.0f}",
        f"- revenue_yuan: {metrics.get('revenue_yuan', 0):.2f}",
        f"- completion_rate: {metrics.get('completion_rate', 0):.2f}",
        f"- follower_gain: {metrics.get('follower_gain', 0):.0f}",
        f"- analytics_records: {metrics_summary.get('record_count', 0)}",
        "",
        "## Publish History",
        "",
        f"- total publishes: {publish_summary.get('total', 0)}",
        f"- successful: {publish_summary.get('successful', 0)}",
        f"- failed: {publish_summary.get('failed', 0)}",
        "",
    ]
    for key, summary in (publish_summary.get("by_key") or {}).items():
        lines.append(f"### {key}")
        lines.append(f"- total: {summary.get('total', 0)}")
        lines.append(f"- successful: {summary.get('successful', 0)}")
        lines.append(f"- failed: {summary.get('failed', 0)}")
        latest = summary.get("latest")
        if latest:
            lines.append(f"- latest_platform: {latest.get('platform', '—')}")
            lines.append(f"- latest_ok: {latest.get('ok', False)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def cmd_analytics_record(args: argparse.Namespace) -> Result:
    resolved = _resolve_project(args)
    if isinstance(resolved, Result):
        return resolved

    project = resolved
    metrics_text = (getattr(args, "metrics", "") or "").strip()
    if not metrics_text:
        return error_result(E.ANALYTICS_NO_METRICS, "No metrics provided (--metrics)")

    metrics, parse_errors = parse_metrics_text(metrics_text)
    if parse_errors:
        return error_result(
            E.ANALYTICS_INVALID_METRIC,
            "; ".join(parse_errors),
            parse_errors=parse_errors,
        )

    ok, val_errors = validate_metrics(metrics)
    if not ok:
        return error_result(
            E.ANALYTICS_INVALID_METRIC,
            "; ".join(val_errors),
            validation_errors=val_errors,
        )

    content_type = (getattr(args, "type", "novel") or "novel").strip().lower()
    content_key = (getattr(args, "key", "ch01") or "ch01").strip()
    record = create_analytics_record(
        content_type=content_type,
        content_key=content_key,
        metrics=metrics,
    )
    add_record(project, record)

    return ok_result(
        E.ANALYTICS_RECORD_OK,
        f"Recorded {len(metrics)} metric(s)",
        record=record,
        metrics=metrics,
        project=str(project),
    )


def cmd_analytics_status(args: argparse.Namespace) -> Result:
    resolved = _resolve_project(args)
    if isinstance(resolved, Result):
        return resolved

    project = resolved
    summary = get_latest_metrics(project)
    return ok_result(
        E.ANALYTICS_STATUS_OK,
        f"{summary['record_count']} analytics record(s)",
        metrics=summary["metrics"],
        record_count=summary["record_count"],
        latest_record=summary.get("latest_record"),
        project=str(project),
    )


def cmd_analytics_report(args: argparse.Namespace) -> Result:
    resolved = _resolve_project(args)
    if isinstance(resolved, Result):
        return resolved

    project = resolved
    period = (getattr(args, "period", "all") or "all").strip()
    metrics_summary = get_latest_metrics(project)
    publish_summary = _collect_publish_summaries(project)

    report_dir = project / "analytics"
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    report_path = report_dir / f"report_{stamp}.md"
    report_text = _render_report_markdown(
        project,
        metrics_summary=metrics_summary,
        publish_summary=publish_summary,
        period=period,
    )
    report_path.write_text(report_text, encoding="utf-8")

    return ok_result(
        E.ANALYTICS_REPORT_OK,
        f"Report written: {report_path.name}",
        artifacts=[artifact(str(report_path), kind="markdown", label="analytics_report")],
        report_path=str(report_path),
        metrics=metrics_summary["metrics"],
        publish_summary=publish_summary,
        period=period,
        project=str(project),
    )


def cmd_analytics_cross_report(args: argparse.Namespace) -> Result:
    reg = registry.load_registry()
    novels = reg.get("novels", [])
    if not novels:
        return error_result(
            E.ANALYTICS_NO_PROJECTS,
            "No registered novel projects",
            next_actions=["novel-suite writer init --title ... --premise ... --json"],
        )

    projects_summary: list[dict[str, Any]] = []
    totals = {
        "play_count": 0.0,
        "revenue_yuan": 0.0,
        "like_count": 0.0,
        "comment_count": 0.0,
        "share_count": 0.0,
        "follower_gain": 0.0,
    }

    for entry in novels:
        path = registry.resolve_project_path(entry)
        if not path.is_dir():
            continue
        metrics_summary = get_latest_metrics(path)
        metrics = metrics_summary.get("metrics") or {}
        row = {
            "slug": entry.get("slug"),
            "title": entry.get("title"),
            "path": str(path),
            "record_count": metrics_summary.get("record_count", 0),
            "metrics": metrics,
        }
        projects_summary.append(row)
        for key in totals:
            totals[key] += float(metrics.get(key, 0) or 0)

    projects_summary.sort(
        key=lambda r: float((r.get("metrics") or {}).get("revenue_yuan", 0) or 0),
        reverse=True,
    )

    return ok_result(
        E.ANALYTICS_CROSS_OK,
        f"Cross-project report for {len(projects_summary)} project(s)",
        project_count=len(projects_summary),
        totals=totals,
        projects=projects_summary,
    )


def cmd_analytics_record_from_json(
    project: Path,
    metrics_json: dict[str, Any],
    *,
    content_type: str = "novel",
    content_key: str = "ch01",
) -> Result:
    """MCP helper — record metrics from a JSON object."""
    try:
        project = assert_project_in_allowed_roots(project.resolve())
    except ValueError as exc:
        return error_result(E.PROJECT_PATH_OUT_OF_BOUNDS, str(exc))

    metrics, parse_errors = parse_metrics_json(metrics_json)
    if parse_errors:
        return error_result(E.ANALYTICS_INVALID_METRIC, "; ".join(parse_errors))

    ok, val_errors = validate_metrics(metrics)
    if not ok:
        return error_result(E.ANALYTICS_INVALID_METRIC, "; ".join(val_errors))

    record = create_analytics_record(
        content_type=content_type,
        content_key=content_key,
        metrics=metrics,
    )
    add_record(project, record)
    return ok_result(
        E.ANALYTICS_RECORD_OK,
        f"Recorded {len(metrics)} metric(s)",
        record=record,
        metrics=metrics,
        project=str(project),
    )
