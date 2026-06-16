"""CLI handler for writer clean."""

from __future__ import annotations

import argparse

from novel_suite.core import errors as E
from novel_suite.core.result import emit, ok_result
from novel_suite.writer.project_clean import clean_empty_projects


def cmd_writer_clean(args: argparse.Namespace) -> int:
    dry_run = bool(getattr(args, "dry_run", False))
    summary = clean_empty_projects(dry_run=dry_run)
    code = E.CLEAN_DRY_RUN_OK if dry_run else E.CLEAN_OK
    verb = "Would remove" if dry_run else "Removed"
    return emit(
        ok_result(
            code,
            f"{verb} {summary['found']} empty project(s)",
            dry_run=dry_run,
            found=summary["found"],
            removed=summary["removed"],
            targets=summary["targets"],
            next_actions=[
                "novel-suite writer init --from-scan intel/radar/<latest>.scan.json --json"
                if summary["found"]
                else "Registry is clean — run writer scan then init --from-scan",
            ],
        ),
        json_out=bool(getattr(args, "json", False)),
    )
