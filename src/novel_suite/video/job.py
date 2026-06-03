"""Video job lifecycle: create → run/status → resume (wraps legacy video_cli)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from novel_suite.core import errors as E
from novel_suite.core.json_stdout import capture_legacy_output
from novel_suite.core.paths import assert_project_in_allowed_roots, suite_root, video_root
from novel_suite.core.result import Result, artifact, error_result, ok_result
from novel_suite.video._legacy import load_video_cli, load_video_script


def video_jobs_dir() -> Path:
    d = video_root() / "tmp" / "video_jobs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def resolve_job_dir(job_id: str) -> Path | None:
    direct = video_jobs_dir() / job_id
    if direct.is_dir():
        return direct
    for p in video_jobs_dir().iterdir():
        if p.is_dir() and p.name == job_id:
            return p
    return None


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def read_job_state(job_dir: Path) -> dict[str, Any]:
    path = job_dir / "job_state.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_job_state(job_dir: Path, payload: dict[str, Any]) -> None:
    payload.setdefault("job_id", job_dir.name)
    (job_dir / "job_state.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _storyboard_mode(job_dir: Path) -> str:
    sb_path = job_dir / "storyboard.json"
    if not sb_path.is_file():
        return "summary"
    sb = json.loads(sb_path.read_text(encoding="utf-8"))
    return str(sb.get("mode", "summary"))


def _job_artifacts(job_dir: Path, root: Path) -> list[dict[str, Any]]:
    arts: list[dict[str, Any]] = [
        artifact(_rel(root, job_dir), kind="directory", label="job_dir"),
        artifact(_rel(root, job_dir / "job_state.json"), label="job_state"),
        artifact(_rel(root, job_dir / "storyboard.json"), label="storyboard"),
    ]
    state = read_job_state(job_dir)
    for item in state.get("artifacts") or []:
        if isinstance(item, dict) and item.get("path"):
            p = Path(str(item["path"]))
            if p.is_file():
                arts.append(artifact(_rel(root, p), kind=item.get("type", "file"), label="output"))
    out_dir = job_dir / "output"
    if out_dir.is_dir():
        for mp4 in sorted(out_dir.glob("*.mp4")):
            rel = _rel(root, mp4)
            if not any(a.get("path") == rel for a in arts):
                arts.append(artifact(rel, kind="video", label="output"))
    return arts


def resolve_chapter_path(chapter: str, project: Path | None) -> Path:
    cli = load_video_cli()
    return cli.resolve_chapter(chapter, project)


def create_summary_job(
    *,
    chapter: Path | str,
    project: Path | None = None,
    aspect: str = "9:16",
) -> Result:
    root = suite_root()
    cli = load_video_cli()
    project_path: Path | None = None
    if project is not None:
        try:
            project_path = assert_project_in_allowed_roots(project)
        except ValueError as exc:
            return error_result(E.PROJECT_NOT_FOUND, str(exc))

    ch = resolve_chapter_path(str(chapter), project_path)
    if not ch.is_file():
        return error_result(
            E.VIDEO_CHAPTER_NOT_FOUND,
            f"Chapter not found: {ch}",
            next_actions=["Pass --chapter path or filename with --project novels/<slug>"],
        )

    bind_mod = load_video_script("novel_bind")
    binding = bind_mod.infer_novel_binding(ch, project=project_path)

    jobs_dir = video_jobs_dir()
    prev_default = getattr(cli, "DEFAULT_JOBS", None)
    try:
        setattr(cli, "DEFAULT_JOBS", jobs_dir)
        job_dir = cli.create_job("summary", ch, aspect, binding=binding)
    finally:
        if prev_default is not None:
            setattr(cli, "DEFAULT_JOBS", prev_default)

    state = read_job_state(job_dir)
    state.update(
        {
            "status": "pending",
            "stage": "intake",
            "job_id": job_dir.name,
            "mode": "summary",
            "aspect": aspect,
        }
    )
    write_job_state(job_dir, state)

    rel_job = _rel(root, job_dir)
    return ok_result(
        E.VIDEO_CREATE_OK,
        f"Video job created (pending): {job_dir.name}",
        artifacts=_job_artifacts(job_dir, root),
        next_actions=[
            f"novel-suite video run --job {job_dir.name} --json",
            f"novel-suite video status --job {job_dir.name} --json",
        ],
        job_id=job_dir.name,
        job_dir=rel_job,
        mode="summary",
        aspect=aspect,
        status="pending",
        stage="intake",
    )


def job_status(job_id: str) -> Result:
    root = suite_root()
    job_dir = resolve_job_dir(job_id)
    if job_dir is None:
        return error_result(
            E.VIDEO_JOB_NOT_FOUND,
            f"Job not found: {job_id}",
            next_actions=[f"List jobs under {video_jobs_dir()}"],
        )

    state = read_job_state(job_dir)
    status = state.get("status", "unknown")
    stage = state.get("stage", "unknown")
    if status == "failed":
        return error_result(
            E.VIDEO_STATUS_FAILED,
            state.get("reason") or f"Job {job_id} failed at stage {stage}",
            artifacts=_job_artifacts(job_dir, root),
            next_actions=[f"novel-suite video resume --job {job_id} --json"],
            job_id=job_id,
            job_dir=_rel(root, job_dir),
            stage=stage,
            status=status,
        )

    return ok_result(
        E.VIDEO_STATUS_OK,
        f"Job {job_id}: {status} ({stage})",
        artifacts=_job_artifacts(job_dir, root),
        next_actions=(
            [f"novel-suite video run --job {job_id} --json"]
            if status == "pending"
            else []
        ),
        job_id=job_id,
        job_dir=_rel(root, job_dir),
        stage=stage,
        status=status,
        mode=_storyboard_mode(job_dir),
    )


def run_job(
    job_id: str,
    *,
    aspect: str | None = None,
    subtitles: bool = False,
) -> Result:
    root = suite_root()
    job_dir = resolve_job_dir(job_id)
    if job_dir is None:
        return error_result(E.VIDEO_JOB_NOT_FOUND, f"Job not found: {job_id}")

    state = read_job_state(job_dir)
    if state.get("status") == "succeeded":
        return ok_result(
            E.VIDEO_RUN_OK,
            f"Job {job_id} already succeeded",
            artifacts=_job_artifacts(job_dir, root),
            job_id=job_id,
            skipped=True,
        )

    mode = _storyboard_mode(job_dir)
    sb_path = job_dir / "storyboard.json"
    use_aspect = aspect
    if use_aspect is None and sb_path.is_file():
        sb = json.loads(sb_path.read_text(encoding="utf-8"))
        use_aspect = sb.get("aspect", "9:16")
    use_aspect = use_aspect or "9:16"

    write_job_state(
        job_dir,
        {
            **state,
            "status": "running",
            "stage": "render",
            "job_id": job_id,
        },
    )

    cli = load_video_cli()
    legacy_output: list[str] = []
    with capture_legacy_output() as captured:
        rc = cli.run_pipeline(job_dir, mode, use_aspect, subtitles=subtitles)
        legacy_output = captured

    final = read_job_state(job_dir)
    arts = _job_artifacts(job_dir, root)

    if rc != 0 or final.get("status") == "failed":
        return error_result(
            E.VIDEO_RUN_FAILED,
            final.get("reason") or f"Pipeline exited {rc}",
            artifacts=arts,
            next_actions=[f"novel-suite video resume --job {job_id} --json"],
            job_id=job_id,
            job_dir=_rel(root, job_dir),
            stage=final.get("stage"),
            status=final.get("status", "failed"),
            legacy_output=legacy_output or None,
        )

    return ok_result(
        E.VIDEO_RUN_OK,
        f"Job {job_id} completed",
        artifacts=arts,
        next_actions=["novel-suite video status --job {0} --json".format(job_id)],
        job_id=job_id,
        job_dir=_rel(root, job_dir),
        stage=final.get("stage", "export"),
        status=final.get("status", "succeeded"),
        legacy_output=legacy_output or None,
    )


def resume_job(
    job_id: str,
    *,
    subtitles: bool = False,
) -> Result:
    job_dir = resolve_job_dir(job_id)
    if job_dir is None:
        return error_result(E.VIDEO_JOB_NOT_FOUND, f"Job not found: {job_id}")

    state = read_job_state(job_dir)
    st = state.get("status")
    if st == "succeeded":
        return error_result(
            E.VIDEO_RESUME_BLOCKED,
            f"Job {job_id} already succeeded; nothing to resume",
            artifacts=_job_artifacts(job_dir, suite_root()),
            job_id=job_id,
        )
    if st == "running":
        return error_result(
            E.VIDEO_RESUME_BLOCKED,
            f"Job {job_id} is still running",
            job_id=job_id,
        )

    # pending or failed → re-run pipeline
    if st == "failed":
        write_job_state(job_dir, {**state, "status": "pending", "stage": "intake"})
    return run_job(job_id, subtitles=subtitles)
