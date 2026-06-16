"""CLI handlers for novel publish."""

from __future__ import annotations

import argparse
from pathlib import Path

from novel_suite.core import errors as E
from novel_suite.core.paths import assert_project_in_allowed_roots
from novel_suite.core.result import Result, error_result, ok_result
from novel_suite.novel.publish.fanqie import fanqie_publish_all, publish_to_jinjiang, publish_to_qidian
from novel_suite.video.publish.record import add_record, records_summary
from novel_suite.writer import registry

NOVEL_PUBLISH_RECORD_KEY = "full"


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


def cmd_novel_publish_upload(args: argparse.Namespace) -> Result:
    """发布小说到指定平台。"""
    resolved = _resolve_project(args)
    if isinstance(resolved, Result):
        return resolved

    project = resolved
    platform: str = (getattr(args, "platform", "fanqie") or "fanqie").strip().lower()

    if not project.is_dir():
        return error_result(E.PUBLISH_PROJECT_NOT_FOUND, f"Project not found: {project}")

    if platform == "fanqie":
        result = fanqie_publish_all(project)
    elif platform == "qidian":
        result = publish_to_qidian(project)
    elif platform == "jinjiang":
        result = publish_to_jinjiang(project)
    else:
        return error_result(
            E.PUBLISH_PLATFORM_UNSUPPORTED,
            f"Platform not supported: {platform}",
            platform=platform,
        )

    entry = {
        "type": "novel",
        "platform": platform,
        "project": str(project),
        "ok": result.get("ok", False),
        "total": result.get("total", 0),
        "published_count": result.get("published_count", 0),
        "failed_count": result.get("failed_count", 0),
        "note": result.get("note"),
    }
    add_record(project, NOVEL_PUBLISH_RECORD_KEY, entry)

    if result.get("ok"):
        return ok_result(
            E.PUBLISH_OK,
            f"Published {result['published_count']}/{result['total']} chapters to {platform}",
            publish_result=result,
            platform=platform,
            record=entry,
        )

    return error_result(
        E.PUBLISH_FAILED,
        result.get("error", "Publish failed"),
        publish_result=result,
        platform=platform,
        record=entry,
    )


def cmd_novel_publish_list(args: argparse.Namespace) -> Result:
    """列出小说发布记录。"""
    resolved = _resolve_project(args)
    if isinstance(resolved, Result):
        return resolved

    project = resolved
    summary = records_summary(project, NOVEL_PUBLISH_RECORD_KEY)
    return ok_result(
        E.PUBLISH_LIST_OK,
        f"{summary['total']} publish record(s)",
        records=summary["records"],
        summary={k: v for k, v in summary.items() if k != "records"},
    )
