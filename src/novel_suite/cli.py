#!/usr/bin/env python3
"""Novel Suite 2.0 unified CLI (writer/video). Legacy novel_cli.py remains compatible."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from novel_suite import __version__
from novel_suite.core import errors as E
from novel_suite.core.result import emit, error_result, ok_result
from novel_suite.writer import doctor, gate, registry
from novel_suite.writer.chapter import run_chapter_draft, run_chapter_promote
from novel_suite.writer.export import run_export
from novel_suite.video.job import create_summary_job, job_status, resume_job, run_job
from novel_suite.writer.init import run_init
from novel_suite.writer.intel import run_scan
from novel_suite.memory import commands as memory_commands


def _add_json_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="Emit JSON Result Contract")


def _add_project_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--project",
        type=Path,
        default=None,
        help="Novel project directory (default: active novel)",
    )


def cmd_version(args: argparse.Namespace) -> int:
    if args.json:
        return emit(
            ok_result("VERSION_OK", f"Novel Suite {__version__}", version=__version__),
            json_out=True,
        )
    print(f"novel-suite {__version__}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    agents = [a.strip() for a in args.agents.split(",") if a.strip()] or None
    return doctor.cmd_doctor(json_out=args.json, core_only=args.core_only, agents=agents)


def cmd_writer_list(args: argparse.Namespace) -> int:
    reg = registry.load_registry()
    novels = reg.get("novels", [])
    if args.json:
        return emit(
            ok_result(
                "LIST_OK",
                f"{len(novels)} novel(s) registered",
                artifacts=[{"type": "registry", "path": str(registry._registry_path())}],
                novels=novels,
                active_slug=registry.get_active_slug(),
            ),
            json_out=True,
        )
    for n in novels:
        mark = "*" if n.get("slug") == registry.get_active_slug() else " "
        print(f"{mark} {n.get('slug')}\t{n.get('title')}\t{n.get('path')}")
    return 0


def cmd_writer_active(args: argparse.Namespace) -> int:
    slug = registry.get_active_slug()
    path = registry.find_by_slug(slug) if slug else None
    if args.json:
        if not slug:
            return emit(
                error_result(
                    "NO_ACTIVE_NOVEL",
                    "No active novel",
                    next_actions=["novel-suite writer init ...", "novel-suite writer use <slug>"],
                ),
                json_out=True,
            )
        return emit(
            ok_result(
                "ACTIVE_OK",
                f"Active novel: {slug}",
                artifacts=[{"type": "directory", "path": str(path)}] if path else [],
                slug=slug,
            ),
            json_out=True,
        )
    if slug:
        print(f"active\t{slug}\t{path}")
        return 0
    print("active\t(none)")
    return 0


def cmd_writer_use(args: argparse.Namespace) -> int:
    try:
        path = registry.set_active(args.slug)
    except ValueError as exc:
        return emit(error_result("UNKNOWN_NOVEL_SLUG", str(exc)), json_out=args.json)
    return emit(
        ok_result(
            "USE_OK",
            f"Active novel set to {args.slug}",
            artifacts=[{"type": "directory", "path": str(path)}],
            slug=args.slug,
        ),
        json_out=args.json,
    )


def cmd_writer_gate(args: argparse.Namespace) -> int:
    return gate.cmd_gate(project=args.project, phase=args.phase, json_out=args.json)


def cmd_writer_validate(args: argparse.Namespace) -> int:
    try:
        project = registry.resolve_project(args.project)
    except ValueError as exc:
        return emit(error_result("NO_ACTIVE_NOVEL", str(exc)), json_out=args.json)
    return emit(
        gate.run_validate(project, include_registry=args.registry),
        json_out=args.json,
    )


def cmd_writer_status(args: argparse.Namespace) -> int:
    """Delegate to legacy novel_cli status (text); JSON summarizes paths."""
    try:
        project = registry.resolve_project(args.project)
    except ValueError as exc:
        return emit(error_result("NO_ACTIVE_NOVEL", str(exc)), json_out=args.json)
    story = project / "story.md"
    title = ""
    if story.is_file():
        for line in story.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
    if args.json:
        return emit(
            ok_result(
                "STATUS_OK",
                title or str(project.name),
                artifacts=[{"type": "directory", "path": str(project)}],
                title=title,
            ),
            json_out=True,
        )
    print(f"project\t{project}")
    print(f"title\t{title or '(unknown)'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="novel-suite", description="Novel Suite 2.0 CLI")
    sub = ap.add_subparsers(dest="command", required=True)

    ver = sub.add_parser("version", help="Print package version")
    _add_json_flag(ver)
    ver.set_defaults(func=cmd_version)

    doc = sub.add_parser("doctor", help="Workspace health check")
    doc.add_argument("--core-only", action="store_true")
    doc.add_argument("--agents", default="")
    _add_json_flag(doc)
    doc.set_defaults(func=cmd_doctor)

    wr = sub.add_parser("writer", help="Writer commands")
    wr_sub = wr.add_subparsers(dest="writer_cmd", required=True)

    lst = wr_sub.add_parser("list", help="List registered novels")
    _add_json_flag(lst)
    lst.set_defaults(func=cmd_writer_list)

    act = wr_sub.add_parser("active", help="Show active novel slug")
    _add_json_flag(act)
    act.set_defaults(func=cmd_writer_active)

    use = wr_sub.add_parser("use", help="Set active novel")
    use.add_argument("slug")
    _add_json_flag(use)
    use.set_defaults(func=cmd_writer_use)

    st = wr_sub.add_parser("status", help="Project status summary")
    _add_project_arg(st)
    _add_json_flag(st)
    st.set_defaults(func=cmd_writer_status)

    gt = wr_sub.add_parser("gate", help="Pipeline phase gate")
    _add_project_arg(gt)
    gt.add_argument("--phase", type=int, default=1)
    _add_json_flag(gt)
    gt.set_defaults(func=cmd_writer_gate)

    val = wr_sub.add_parser("validate", help="Validate project JSON schemas")
    _add_project_arg(val)
    val.add_argument("--registry", action="store_true")
    _add_json_flag(val)
    val.set_defaults(func=cmd_writer_validate)

    ini = wr_sub.add_parser("init", help="Scaffold new novel under novels/<slug>/")
    ini.add_argument("--title", required=True)
    ini.add_argument("--premise", required=True)
    ini.add_argument("--genre", default="通用")
    ini.add_argument("--slug", default="")
    ini.add_argument("--platform-target", default="通用", dest="platform_target")
    ini.add_argument("--output", type=Path, default=None)
    ini.add_argument("--concept", type=Path, default=None)
    _add_json_flag(ini)
    ini.set_defaults(func=cmd_writer_init)

    sc = wr_sub.add_parser("scan", help="Phase 0 market scan (intel radar + concepts)")
    sc.add_argument("--period", choices=("week", "month"), default="week")
    sc.add_argument("--platforms", default="douyin,bilibili,kuaishou,xiaohongshu,weibo")
    sc.add_argument("--demo", action="store_true", help="Offline fixture smoke-hits.json")
    sc.add_argument("--input", type=Path, default=None, help="JSON/NDJSON hits file")
    sc.add_argument("--radar", type=Path, default=None)
    sc.add_argument("--concepts-dir", type=Path, default=None)
    sc.add_argument("--no-concepts", action="store_true")
    sc.add_argument("--concept-top", type=int, default=3)
    sc.add_argument("--max-results", type=int, default=6)
    sc.add_argument("--timeout", type=float, default=12.0)
    _add_json_flag(sc)
    sc.set_defaults(func=cmd_writer_scan)

    ch = wr_sub.add_parser("chapter", help="Chapter draft/promote")
    ch_sub = ch.add_subparsers(dest="chapter_cmd", required=True)

    ch_draft = ch_sub.add_parser("draft", help="Write chapter from input file + update progress")
    _add_project_arg(ch_draft)
    ch_draft.add_argument("--chapter", type=int, required=True)
    ch_draft.add_argument("--title", required=True)
    ch_draft.add_argument("--input", type=Path, required=True)
    ch_draft.add_argument("--snapshot-input", type=Path, default=argparse.SUPPRESS)
    ch_draft.add_argument(
        "--skip-gate",
        action="store_true",
        help=f"Skip phase 5 gate (requires env {E.ENV_ALLOW_SKIP_GATE}=1)",
    )
    ch_draft.add_argument("--force", action="store_true", help="Overwrite existing chapter file")
    _add_json_flag(ch_draft)
    ch_draft.set_defaults(func=cmd_writer_chapter_draft)

    ch_prom = ch_sub.add_parser("promote", help="Promote chapters/.drafts file to chapters/")
    _add_project_arg(ch_prom)
    ch_prom.add_argument("chapter_file", help="Filename under chapters/.drafts/")
    _add_json_flag(ch_prom)
    ch_prom.set_defaults(func=cmd_writer_chapter_promote)

    exp = wr_sub.add_parser("export", help="Export manuscript (markdown, txt, epub)")
    _add_project_arg(exp)
    exp.add_argument(
        "--format",
        default="markdown",
        choices=["markdown", "txt", "epub"],
        help="Export format",
    )
    exp.add_argument("--output", type=Path, default=None, help="Output file path")
    exp.add_argument(
        "--skip-gate",
        action="store_true",
        help=f"Skip phase 9 gate (requires env {E.ENV_ALLOW_SKIP_GATE}=1)",
    )
    _add_json_flag(exp)
    exp.set_defaults(func=cmd_writer_export)

    vid = sub.add_parser("video", help="Video job commands (Phase G)")
    vid_sub = vid.add_subparsers(dest="video_cmd", required=True)

    v_create = vid_sub.add_parser("create-summary", help="Create summary video job (pending)")
    v_create.add_argument("--chapter", required=True, help="Chapter path or filename with --project")
    _add_project_arg(v_create)
    v_create.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1"])
    v_create.add_argument(
        "--run",
        action="store_true",
        help="Immediately run pipeline after create (legacy one-shot)",
    )
    v_create.add_argument("--subtitles", action="store_true")
    _add_json_flag(v_create)
    v_create.set_defaults(func=cmd_video_create_summary)

    v_run = vid_sub.add_parser("run", help="Run pipeline for an existing job")
    v_run.add_argument("--job", required=True, dest="job_id")
    v_run.add_argument("--aspect", default=None, choices=["9:16", "16:9", "1:1"])
    v_run.add_argument("--subtitles", action="store_true")
    _add_json_flag(v_run)
    v_run.set_defaults(func=cmd_video_run)

    v_st = vid_sub.add_parser("status", help="Read job_state.json")
    v_st.add_argument("--job", required=True, dest="job_id")
    _add_json_flag(v_st)
    v_st.set_defaults(func=cmd_video_status)

    v_res = vid_sub.add_parser("resume", help="Resume pending/failed job")
    v_res.add_argument("--job", required=True, dest="job_id")
    v_res.add_argument("--subtitles", action="store_true")
    _add_json_flag(v_res)
    v_res.set_defaults(func=cmd_video_resume)

    mem = sub.add_parser("memory", help="Vector memory (L1–L4 layered store)")
    mem_sub = mem.add_subparsers(dest="memory_cmd", required=True)

    mem_st = mem_sub.add_parser("status", help="Count records per layer")
    _add_project_arg(mem_st)
    _add_json_flag(mem_st)
    mem_st.set_defaults(func=cmd_memory_status)

    mem_probe = mem_sub.add_parser("probe", help="Probe embed backend + Qdrant connectivity")
    _add_project_arg(mem_probe)
    _add_json_flag(mem_probe)
    mem_probe.set_defaults(func=cmd_memory_probe)

    mem_sync = mem_sub.add_parser("sync", help="Bulk sync JSONL memory to Qdrant")
    _add_project_arg(mem_sync)
    mem_sync.add_argument("--reembed", action="store_true", help="Re-embed all records with current backend")
    _add_json_flag(mem_sync)
    mem_sync.set_defaults(func=cmd_memory_sync)

    mem_store = mem_sub.add_parser("store", help="Store text in a memory layer")
    _add_project_arg(mem_store)
    mem_store.add_argument("--text", required=True, help="Text to store")
    mem_store.add_argument("--layer", required=True, choices=["L1", "L2", "L3", "L4"])
    mem_store.add_argument("--tags", default="", help="Comma-separated tags")
    mem_store.add_argument("--auto-split", action="store_true", help="Split text by layer granularity")
    _add_json_flag(mem_store)
    mem_store.set_defaults(func=cmd_memory_store)

    mem_search = mem_sub.add_parser("search", help="Semantic search memory")
    _add_project_arg(mem_search)
    mem_search.add_argument("--query", required=True)
    mem_search.add_argument("--layer", default="", choices=["", "L1", "L2", "L3", "L4"])
    mem_search.add_argument("--tags", default="")
    mem_search.add_argument("--track", default="", choices=["", "writing", "video"])
    mem_search.add_argument("--limit", type=int, default=5)
    _add_json_flag(mem_search)
    mem_search.set_defaults(func=cmd_memory_search)

    mem_check = mem_sub.add_parser("check", help="Check new text vs L4 settings")
    _add_project_arg(mem_check)
    mem_check.add_argument("--text", required=True)
    _add_json_flag(mem_check)
    mem_check.set_defaults(func=cmd_memory_check)

    return ap


def cmd_writer_init(args: argparse.Namespace) -> int:
    return emit(
        run_init(
            title=args.title,
            premise=args.premise,
            genre=args.genre,
            slug=args.slug or "",
            output=args.output,
            concept=args.concept,
            platform_target=args.platform_target,
            json_mode=args.json,
        ),
        json_out=args.json,
    )


def cmd_writer_scan(args: argparse.Namespace) -> int:
    return emit(
        run_scan(
            period=args.period,
            platforms=args.platforms,
            demo=args.demo,
            input_path=args.input,
            radar_path=args.radar,
            concepts_dir=args.concepts_dir,
            no_concepts=args.no_concepts,
            concept_top=args.concept_top,
            max_results=args.max_results,
            timeout=args.timeout,
        ),
        json_out=args.json,
    )


def cmd_writer_chapter_draft(args: argparse.Namespace) -> int:
    try:
        project = registry.resolve_project(args.project)
    except ValueError as exc:
        return emit(error_result("NO_ACTIVE_NOVEL", str(exc)), json_out=args.json)
    return emit(
        run_chapter_draft(
            project,
            chapter=args.chapter,
            title=args.title,
            input_path=args.input,
            snapshot_input=getattr(args, "snapshot_input", None),
            snapshot_input_given=hasattr(args, "snapshot_input"),
            skip_gate=args.skip_gate,
            force=args.force,
        ),
        json_out=args.json,
    )


def cmd_video_create_summary(args: argparse.Namespace) -> int:
    result = create_summary_job(
        chapter=args.chapter,
        project=args.project,
        aspect=args.aspect,
    )
    if result.status != "ok":
        return emit(result, json_out=args.json)
    if args.run:
        job_id = result.details.get("job_id") or ""
        if not job_id:
            return emit(
                error_result("VIDEO_RUN_FAILED", "Missing job_id after create"),
                json_out=args.json,
            )
        result = run_job(job_id, aspect=args.aspect, subtitles=args.subtitles)
    return emit(result, json_out=args.json)


def cmd_video_run(args: argparse.Namespace) -> int:
    return emit(
        run_job(args.job_id, aspect=args.aspect, subtitles=args.subtitles),
        json_out=args.json,
    )


def cmd_video_status(args: argparse.Namespace) -> int:
    return emit(job_status(args.job_id), json_out=args.json)


def cmd_video_resume(args: argparse.Namespace) -> int:
    return emit(resume_job(args.job_id, subtitles=args.subtitles), json_out=args.json)


def cmd_writer_export(args: argparse.Namespace) -> int:
    try:
        project = registry.resolve_project(args.project)
    except ValueError as exc:
        code = (
            E.PROJECT_NOT_FOUND
            if E.PROJECT_NOT_FOUND in str(exc) or "not found" in str(exc).lower()
            else "NO_ACTIVE_NOVEL"
        )
        return emit(error_result(code, str(exc)), json_out=args.json)
    return emit(
        run_export(
            project,
            fmt=args.format,
            output=args.output,
            skip_gate=args.skip_gate,
        ),
        json_out=args.json,
    )


def cmd_memory_status(args: argparse.Namespace) -> int:
    return emit(memory_commands.run_memory_status(args), json_out=args.json)


def cmd_memory_store(args: argparse.Namespace) -> int:
    return emit(memory_commands.run_memory_store(args), json_out=args.json)


def cmd_memory_search(args: argparse.Namespace) -> int:
    return emit(memory_commands.run_memory_search(args), json_out=args.json)


def cmd_memory_check(args: argparse.Namespace) -> int:
    return emit(memory_commands.run_memory_check(args), json_out=args.json)


def cmd_memory_probe(args: argparse.Namespace) -> int:
    return emit(memory_commands.run_memory_probe(args), json_out=args.json)


def cmd_memory_sync(args: argparse.Namespace) -> int:
    return emit(memory_commands.run_memory_sync(args), json_out=args.json)


def cmd_writer_chapter_promote(args: argparse.Namespace) -> int:
    try:
        project = registry.resolve_project(args.project)
    except ValueError as exc:
        return emit(error_result("NO_ACTIVE_NOVEL", str(exc)), json_out=args.json)
    return emit(
        run_chapter_promote(project, chapter_file=args.chapter_file),
        json_out=args.json,
    )


def main(argv: list[str] | None = None) -> int:
    from novel_suite.bootstrap import ensure_src_path

    ensure_src_path()
    ap = build_parser()
    args = ap.parse_args(argv)
    if not hasattr(args, "func"):
        ap.print_help()
        return 2
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
