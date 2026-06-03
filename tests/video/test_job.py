"""Video job state machine unit tests (no FFmpeg)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from novel_suite.core import errors as E
from novel_suite.video import job

REPO = Path(__file__).resolve().parents[2]
DEMO_CH = REPO / "cursor-novel-writer" / "examples" / "demo-novel" / "chapters" / "01_试章.md"
DEMO_PROJECT = REPO / "cursor-novel-writer" / "examples" / "demo-novel"


@pytest.fixture
def jobs_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "video_jobs"
    root.mkdir()
    monkeypatch.setattr(job, "video_jobs_dir", lambda: root)
    cli = job.load_video_cli()
    monkeypatch.setattr(cli, "DEFAULT_JOBS", root)
    return root


def test_create_summary_job_pending(jobs_root: Path):
    if not DEMO_CH.is_file():
        pytest.skip("demo chapter missing")
    result = job.create_summary_job(
        chapter="01_试章.md",
        project=DEMO_PROJECT,
        aspect="9:16",
    )
    assert result.status == "ok"
    assert result.code == E.VIDEO_CREATE_OK
    assert result.details["status"] == "pending" or result.details.get("job_id")
    job_id = result.details["job_id"]
    job_dir = jobs_root / job_id
    state = json.loads((job_dir / "job_state.json").read_text(encoding="utf-8"))
    assert state["status"] == "pending"
    assert state["stage"] == "intake"


def test_job_status_not_found():
    result = job.job_status("nonexistent-job-id-xyz")
    assert result.code == E.VIDEO_JOB_NOT_FOUND


def test_job_status_pending(jobs_root: Path):
    if not DEMO_CH.is_file():
        pytest.skip("demo chapter missing")
    created = job.create_summary_job(chapter=DEMO_CH, aspect="9:16")
    job_id = created.details["job_id"]
    result = job.job_status(job_id)
    assert result.status == "ok"
    assert result.code == E.VIDEO_STATUS_OK
    assert result.details["status"] == "pending"


def test_resume_blocked_when_succeeded(jobs_root: Path, monkeypatch: pytest.MonkeyPatch):
    job_dir = jobs_root / "fake_done"
    job_dir.mkdir()
    (job_dir / "storyboard.json").write_text(
        json.dumps({"mode": "summary", "aspect": "9:16"}), encoding="utf-8"
    )
    (job_dir / "job_state.json").write_text(
        json.dumps({"status": "succeeded", "stage": "export", "job_id": job_dir.name}),
        encoding="utf-8",
    )
    result = job.resume_job(job_dir.name)
    assert result.code == E.VIDEO_RESUME_BLOCKED


def test_chapter_not_found(jobs_root: Path):
    result = job.create_summary_job(
        chapter="missing.md",
        project=DEMO_PROJECT,
    )
    assert result.code == E.VIDEO_CHAPTER_NOT_FOUND
