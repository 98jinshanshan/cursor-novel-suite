#!/usr/bin/env python3
"""NEC completion manifest for video jobs (V0–V2)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ENGINE_DIR = Path(__file__).resolve().parents[1]
WRITER_ENGINE = ENGINE_DIR.parent.parent / "cursor-novel-writer" / "engine"
if str(WRITER_ENGINE) not in sys.path:
    sys.path.insert(0, str(WRITER_ENGINE))

from scripts.node_completion import utc_now, write_manifest  # noqa: E402


def job_completion_path(job_dir: Path) -> Path:
    return job_dir / "node.completion.json"


def build_v0_completion(
    *,
    job_dir: Path,
    artifact: Path | None,
    qc_ok: bool,
    mode: str = "summary",
    failed: bool = False,
    failure_note: str = "",
) -> dict[str, Any]:
    ok = not failed and artifact is not None and artifact.is_file() and qc_ok
    if failed:
        top_status = "failed"
    elif ok:
        top_status = "complete"
    else:
        top_status = "partial"
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "phase": 0,
        "skill": "video-chapter-summary",
        "project_slug": job_dir.name,
        "status": top_status,
        "started_at": utc_now(),
        "artifacts": {
            "job_dir": str(job_dir),
            "mp4": str(artifact) if artifact else "",
            "storyboard": str(job_dir / "storyboard.json"),
        },
        "subtasks": [
            {
                "id": "V0-S1",
                "title": "script + storyboard",
                "executor": "agent",
                "status": "done" if (job_dir / "script.md").is_file() else "pending",
                "output_paths": [str(job_dir / "script.md")] if (job_dir / "script.md").is_file() else [],
            },
            {
                "id": "V0-S2",
                "title": "summary pipeline",
                "executor": "cli",
                "command": "video_cli summary",
                "status": "done" if artifact else "pending",
                "output_paths": [str(artifact)] if artifact else [],
            },
            {
                "id": "V0-S3",
                "title": "qc_video",
                "executor": "cli",
                "status": "done" if qc_ok else "pending",
                "output_paths": [],
            },
        ],
        "video_mode": mode,
    }
    if failure_note:
        manifest["failure_note"] = failure_note
    if ok:
        manifest["completed_at"] = utc_now()
    return manifest


def write_job_completion(
    job_dir: Path,
    *,
    artifact: Path | None,
    qc_ok: bool,
    mode: str = "summary",
) -> Path:
    path = job_completion_path(job_dir)
    write_manifest(path, build_v0_completion(job_dir=job_dir, artifact=artifact, qc_ok=qc_ok, mode=mode))
    return path


def write_job_completion_failed(job_dir: Path, *, note: str, mode: str = "summary") -> Path:
    path = job_completion_path(job_dir)
    write_manifest(
        path,
        build_v0_completion(
            job_dir=job_dir,
            artifact=None,
            qc_ok=False,
            mode=mode,
            failed=True,
            failure_note=note,
        ),
    )
    return path
