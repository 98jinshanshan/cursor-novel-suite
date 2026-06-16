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
from novel_suite.video.character.cli import (
    cmd_character_list,
    cmd_character_pack,
    cmd_character_qc,
)
from novel_suite.video.compose.cli import cmd_compose_run, cmd_pipeline_run
from novel_suite.video.gate.cli import cmd_gate
from novel_suite.auth.cli import cmd_auth_login, cmd_auth_logout, cmd_auth_status
from novel_suite.platforms._registry import list_platform_keys
from novel_suite.core.paths import suite_root
from novel_suite.video.publish.cli import cmd_cookie, cmd_publish, cmd_publish_list
from novel_suite.analytics.cli import (
    cmd_analytics_cross_report,
    cmd_analytics_record,
    cmd_analytics_report,
    cmd_analytics_status,
)
from novel_suite.novel.publish.cli import cmd_novel_publish_list, cmd_novel_publish_upload
from novel_suite.video.stills.cli import cmd_stills_generate
from novel_suite.video.storyboard.cli_handlers import run_storyboard
from novel_suite.writer.clean_cli import cmd_writer_clean
from novel_suite.writer.init import run_init
from novel_suite.writer.intel import run_scan
from novel_suite.memory import commands as memory_commands
from novel_suite.core.product_layer import (
    get_product_category_ids,
    run_product_list,
    run_product_read,
    run_product_validate,
)
from novel_suite.video_production.cli import run_adapter_dry_run
from novel_suite.core.commercialization import (
    run_commercial_release_candidate_validate,
    run_commercial_review_validate,
)
from novel_suite.core.workflow_contracts import run_workflow_contract_validate
from novel_suite.core.trace_state import run_multi_ide_trials_validate, run_trace_state_validate
from novel_suite.core.future_backends import (
    run_future_backends_validate,
    run_trial_feedback_review_validate,
)
from novel_suite.core.agent_entry_menu import (
    run_agent_entry_menu_list,
    run_agent_entry_menu_validate,
)
from novel_suite.server import run_server_validate
from novel_suite.core.ip_production_demo import (
    run_ip_production_demo,
    run_ip_production_demo_validate,
)
from novel_suite.core.novel_review_demo import (
    run_novel_review_demo,
    run_novel_review_demo_validate,
)
from novel_suite.core.realgen_demo import run_realgen_demo, run_realgen_demo_validate
from novel_suite.core.realpipeline import run_realpipeline, validate_realpipeline
from novel_suite.core.doc_router_commands import (
    run_doc_router_build,
    run_doc_router_explain,
    run_doc_router_preflight,
    run_doc_router_query,
    run_doc_router_validate,
)
from novel_suite.core.delivery_readiness import (
    run_delivery_hub_validate,
    run_demo_roadmap_validate,
    run_human_trial_runbook_validate,
    run_legal_release_review_validate,
    run_freeze_version_alignment_validate,
    run_legal_review_packet_validate,
    run_legal_review_response_intake_validate,
    run_first_trial_session_kit_validate,
    run_freeze_review_meeting_validate,
    run_legal_review_meeting_validate,
    run_trial_result_review_validate,
    run_freeze_decision_record_validate,
    run_legal_decision_record_validate,
    run_trial_result_import_preflight_validate,
    run_freeze_decision_import_preflight_validate,
    run_legal_decision_import_preflight_validate,
    run_trial_import_decision_record_validate,
    run_freeze_import_decision_record_validate,
    run_legal_import_decision_board_validate,
    run_trial_decision_fill_kit_validate,
    run_freeze_decision_fill_kit_validate,
    run_legal_board_execution_kit_validate,
    run_solo_founder_freeze_self_check_validate,
    run_solo_founder_compliance_self_check_validate,
    run_solo_founder_release_blocked_declaration_validate,
    run_solo_demo_15min_validate,
    run_promptpack_first_run_validate,
    run_multi_ide_dry_run_feedback_validate,
    run_solo_demo_trial_intake_validate,
    run_promptpack_friction_review_validate,
    run_multi_ide_feedback_backlog_validate,
    run_openclaw_feedback_consolidation_validate,
    run_package_freeze_candidate_validate,
    run_trial_results_intake_validate,
)


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
    return doctor.cmd_doctor(
        json_out=args.json,
        core_only=args.core_only,
        core_contracts=args.core_contracts,
        agents=agents,
    )


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
    doc.add_argument(
        "--core-contracts",
        action="store_true",
        dest="core_contracts",
        help="Check novel-suite/ product layer contracts, gates, packs, adapters",
    )
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

    cln = wr_sub.add_parser("clean", help="Remove registry novels with zero chapters")
    cln.add_argument("--dry-run", action="store_true", help="List empty projects without deleting")
    _add_json_flag(cln)
    cln.set_defaults(func=cmd_writer_clean)

    ini = wr_sub.add_parser("init", help="Scaffold new novel under novels/<slug>/")
    ini.add_argument("--title", default="", help="Required unless --from-scan")
    ini.add_argument("--premise", default="", help="Required unless --from-scan")
    ini.add_argument(
        "--from-scan",
        type=Path,
        default=None,
        metavar="SCAN_JSON",
        help="Load title/premise/platform from scan JSON (intel/radar/*.scan.json)",
    )
    ini.add_argument(
        "--scan-theme-index",
        type=int,
        default=0,
        help="Theme index in scan JSON themes[] (default: 0 = TOP1)",
    )
    ini.add_argument("--genre", default="通用")
    ini.add_argument("--slug", default="")
    ini.add_argument(
        "--target-platform",
        "--platform-target",
        default="通用",
        dest="platform_target",
        choices=["fanqie", "qidian", "jinjiang", "douyin", "kuaishou", "bilibili", "通用"],
        help="Target publish platform (affects writing style & video format)",
    )
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

    v_sb = vid_sub.add_parser("storyboard", help="Generate chapter storyboard JSON (Sprint 2.1)")
    v_sb.add_argument(
        "--chapter",
        required=True,
        help="Chapter file, chapters/<file>.md, or ch01 (from progress.json)",
    )
    _add_project_arg(v_sb)
    v_sb.add_argument(
        "--chapter-key",
        default="",
        help="Output subdir under project/video/ (default: derived from chapter filename)",
    )
    v_sb.add_argument("--mode", default="summary", choices=["summary", "drama"])
    v_sb.add_argument("--target-duration", type=int, default=60, dest="target_duration")
    v_sb.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1"])
    v_sb.add_argument("--min-scenes", type=int, default=6, dest="min_scenes")
    v_sb.add_argument("--max-scenes", type=int, default=12, dest="max_scenes")
    v_sb.add_argument(
        "--llm",
        action="store_true",
        help="Use Ollama LLM when available (falls back to rule-based)",
    )
    _add_json_flag(v_sb)
    v_sb.set_defaults(func=cmd_video_storyboard)

    v_char = vid_sub.add_parser("character", help="Character asset management (Sprint 2.2)")
    char_sub = v_char.add_subparsers(dest="character_cmd", required=True)

    v_char_list = char_sub.add_parser("list", help="List characters from CVDP")
    _add_project_arg(v_char_list)
    v_char_list.add_argument("--chapter-key", default="ch01")
    _add_json_flag(v_char_list)
    v_char_list.set_defaults(func=cmd_video_character_list)

    v_char_pack = char_sub.add_parser("pack", help="Build character asset pack")
    _add_project_arg(v_char_pack)
    v_char_pack.add_argument("--chapter-key", default="ch01")
    v_char_pack.add_argument(
        "--render-refs",
        action="store_true",
        help="Render ref images via ComfyUI (requires GPU stack)",
    )
    v_char_pack.add_argument(
        "--characters",
        default="",
        help="Comma-separated character names (default: all)",
    )
    _add_json_flag(v_char_pack)
    v_char_pack.set_defaults(func=cmd_video_character_pack)

    v_char_qc = char_sub.add_parser("qc", help="QC character asset pack")
    _add_project_arg(v_char_qc)
    v_char_qc.add_argument("--chapter-key", default="ch01")
    _add_json_flag(v_char_qc)
    v_char_qc.set_defaults(func=cmd_video_character_qc)

    v_stills = vid_sub.add_parser("stills", help="Generate keyframe stills (Sprint 2.3a)")
    stills_sub = v_stills.add_subparsers(dest="stills_cmd", required=True)
    v_stills_gen = stills_sub.add_parser("generate", help="Generate stills from storyboard")
    _add_project_arg(v_stills_gen)
    v_stills_gen.add_argument("--chapter-key", default="ch01")
    v_stills_gen.add_argument("--mode", choices=["proof", "final"], default="proof")
    v_stills_gen.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1"])
    _add_json_flag(v_stills_gen)
    v_stills_gen.set_defaults(func=cmd_video_stills_generate)

    v_compose = vid_sub.add_parser("compose", help="Compose video from stills (Sprint 2.3b)")
    _add_project_arg(v_compose)
    v_compose.add_argument("--chapter-key", default="ch01")
    v_compose.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    v_compose.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1"])
    v_compose.add_argument("--subtitles", action="store_true")
    _add_json_flag(v_compose)
    v_compose.set_defaults(func=cmd_video_compose)

    v_pipe = vid_sub.add_parser("pipeline", help="Run full video pipeline E2E (Sprint 2.3c)")
    _add_project_arg(v_pipe)
    v_pipe.add_argument("--chapter-key", default="ch01")
    v_pipe.add_argument("--mode", choices=["proof", "final"], default="proof")
    v_pipe.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    v_pipe.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1"])
    v_pipe.add_argument("--subtitles", action="store_true")
    v_pipe.add_argument("--platform", default="douyin")
    _add_json_flag(v_pipe)
    v_pipe.set_defaults(func=cmd_video_pipeline)

    v_gate = vid_sub.add_parser("gate", help="Run publish gate checks (Sprint 3)")
    _add_project_arg(v_gate)
    v_gate.add_argument("--chapter-key", default="ch01")
    v_gate.add_argument("--platform", default="douyin", choices=["douyin", "kuaishou"])
    _add_json_flag(v_gate)
    v_gate.set_defaults(func=cmd_video_gate)

    v_pub = vid_sub.add_parser("publish", help="Publish video to platform (Sprint 3)")
    pub_sub = v_pub.add_subparsers(dest="publish_cmd", required=True)

    pub_upload = pub_sub.add_parser("upload", help="Upload and publish video")
    _add_project_arg(pub_upload)
    pub_upload.add_argument("--chapter-key", default="ch01")
    pub_upload.add_argument(
        "--platform",
        default="douyin",
        choices=list_platform_keys(platform_type="video"),
    )
    pub_upload.add_argument("--title", help="Video title (default: Chapter <key>)")
    pub_upload.add_argument("--no-headless", action="store_true", help="Show browser for QR login")
    pub_upload.add_argument("--skip-gate", action="store_true", help="Skip publish gate check")
    _add_json_flag(pub_upload)
    pub_upload.set_defaults(func=cmd_video_publish)

    pub_list = pub_sub.add_parser("list", help="List publish records")
    _add_project_arg(pub_list)
    pub_list.add_argument("--chapter-key", default="ch01")
    _add_json_flag(pub_list)
    pub_list.set_defaults(func=cmd_video_publish_list)

    v_cookie = vid_sub.add_parser("cookie", help="Check platform cookie status")
    v_cookie.add_argument("--platform", default="douyin")
    _add_json_flag(v_cookie)
    v_cookie.set_defaults(func=cmd_video_cookie)

    auth = sub.add_parser("auth", help="Platform authentication (Sprint 4)")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True)
    platform_choices = list_platform_keys()

    auth_login = auth_sub.add_parser("login", help="Login to a platform")
    auth_login.add_argument("--platform", required=True, choices=platform_choices)
    _add_json_flag(auth_login)
    auth_login.set_defaults(func=cmd_auth_login_cli)

    auth_logout = auth_sub.add_parser("logout", help="Logout from a platform")
    auth_logout.add_argument("--platform", required=True, choices=platform_choices)
    _add_json_flag(auth_logout)
    auth_logout.set_defaults(func=cmd_auth_logout_cli)

    auth_status = auth_sub.add_parser("status", help="Check auth status")
    auth_status.add_argument("--platform", choices=platform_choices)
    _add_json_flag(auth_status)
    auth_status.set_defaults(func=cmd_auth_status_cli)

    nov_parser = sub.add_parser("novel", help="Novel management (publish)")
    nov_sub = nov_parser.add_subparsers(dest="novel_cmd", required=True)

    nov_pub = nov_sub.add_parser("publish", help="Publish novel to platform")
    nov_pub_sub = nov_pub.add_subparsers(dest="publish_cmd", required=True)

    nov_pub_up = nov_pub_sub.add_parser("upload", help="Upload novel to platform")
    _add_project_arg(nov_pub_up)
    nov_pub_up.add_argument(
        "--platform",
        default="fanqie",
        choices=["fanqie", "qidian", "jinjiang"],
    )
    _add_json_flag(nov_pub_up)
    nov_pub_up.set_defaults(func=cmd_novel_publish_upload_cli)

    nov_pub_list = nov_pub_sub.add_parser("list", help="List publish records")
    _add_project_arg(nov_pub_list)
    _add_json_flag(nov_pub_list)
    nov_pub_list.set_defaults(func=cmd_novel_publish_list_cli)

    ana = sub.add_parser("analytics", help="Publish analytics tracking (Sprint 6)")
    ana_sub = ana.add_subparsers(dest="analytics_cmd", required=True)

    ana_record = ana_sub.add_parser("record", help="Record performance metrics")
    _add_project_arg(ana_record)
    ana_record.add_argument(
        "--metrics",
        required=True,
        help='Metrics as key=value pairs, e.g. "播放量=15000 收入=12.5"',
    )
    ana_record.add_argument("--type", choices=["novel", "video"], default="novel")
    ana_record.add_argument("--key", default="ch01", help="Content key (e.g. ch01, full)")
    _add_json_flag(ana_record)
    ana_record.set_defaults(func=cmd_analytics_record_cli)

    ana_status = ana_sub.add_parser("status", help="Show aggregated metrics for a project")
    _add_project_arg(ana_status)
    _add_json_flag(ana_status)
    ana_status.set_defaults(func=cmd_analytics_status_cli)

    ana_report = ana_sub.add_parser("report", help="Generate Markdown analytics report")
    _add_project_arg(ana_report)
    ana_report.add_argument("--period", default="all", help="Report period label")
    _add_json_flag(ana_report)
    ana_report.set_defaults(func=cmd_analytics_report_cli)

    ana_cross = ana_sub.add_parser("cross-report", help="Cross-project analytics summary")
    _add_json_flag(ana_cross)
    ana_cross.set_defaults(func=cmd_analytics_cross_report_cli)

    prod = sub.add_parser("product", help="Novel Suite product layer (read-only docs/contracts)")
    prod_sub = prod.add_subparsers(dest="product_cmd", required=True)

    prod_list = prod_sub.add_parser("list", help="List product-layer categories and assets")
    _add_json_flag(prod_list)
    prod_list.set_defaults(func=cmd_product_list)

    prod_read = prod_sub.add_parser("read", help="Read a product-layer asset")
    prod_read.add_argument(
        "--category",
        required=True,
        choices=get_product_category_ids(),
    )
    prod_read.add_argument("--name", required=True, help="Asset name (e.g. chapter_writing)")
    _add_json_flag(prod_read)
    prod_read.set_defaults(func=cmd_product_read)

    prod_validate = prod_sub.add_parser("validate", help="Validate product-layer completeness")
    _add_json_flag(prod_validate)
    prod_validate.set_defaults(func=cmd_product_validate)

    vp = sub.add_parser(
        "video-production",
        help="Video-production handoff adapters (default-off dry-run only)",
    )
    vp_sub = vp.add_subparsers(dest="vp_cmd", required=True)
    vp_adapter = vp_sub.add_parser("adapter", help="Handoff adapter commands")
    vp_adapter_sub = vp_adapter.add_subparsers(dest="vp_adapter_cmd", required=True)
    vp_dry = vp_adapter_sub.add_parser(
        "dry-run",
        help="Generate local plan/manifest from example handoff (no external calls)",
    )
    vp_dry.add_argument(
        "--adapter",
        required=True,
        choices=["comfyui", "otio", "davinci"],
        help="Adapter skeleton to run",
    )
    vp_dry.add_argument(
        "--example",
        default="cold_case_echo_short_drama",
        help="Example package under video-production/examples/",
    )
    vp_dry.add_argument(
        "--output",
        default=".tmp/novel-suite-c5",
        help="Output directory (relative to suite root)",
    )
    _add_json_flag(vp_dry)
    vp_dry.set_defaults(func=cmd_video_production_adapter_dry_run)

    cr = sub.add_parser(
        "commercial-review",
        help="C6/C7 commercial preflight (read-only validate)",
    )
    cr_sub = cr.add_subparsers(dest="commercial_review_cmd", required=True)
    cr_validate = cr_sub.add_parser("validate", help="Validate commercial review docs and manifest")
    _add_json_flag(cr_validate)
    cr_validate.set_defaults(func=cmd_commercial_review_validate)

    crc = sub.add_parser(
        "commercial-release-candidate",
        help="C9 commercial release candidate gate (read-only validate)",
    )
    crc_sub = crc.add_subparsers(dest="candidate_cmd", required=True)
    crc_validate = crc_sub.add_parser("validate", help="Validate candidate package docs and final gate")
    _add_json_flag(crc_validate)
    crc_validate.set_defaults(func=cmd_commercial_release_candidate_validate)

    wfc = sub.add_parser("workflow-contract", help="F2 workflow contract schema (read-only validate)")
    wfc_sub = wfc.add_subparsers(dest="workflow_contract_cmd", required=True)
    wfc_validate = wfc_sub.add_parser("validate", help="Validate workflow contract schema and samples")
    _add_json_flag(wfc_validate)
    wfc_validate.set_defaults(func=cmd_workflow_contract_validate)

    ts = sub.add_parser("trace-state", help="F3 trace/state specs (read-only validate)")
    ts_sub = ts.add_subparsers(dest="trace_state_cmd", required=True)
    ts_validate = ts_sub.add_parser("validate", help="Validate trace-state schema and JSONL samples")
    _add_json_flag(ts_validate)
    ts_validate.set_defaults(func=cmd_trace_state_validate)

    mit = sub.add_parser("multi-ide-trials", help="C10 multi-IDE trial scripts (read-only validate)")
    mit_sub = mit.add_subparsers(dest="multi_ide_trials_cmd", required=True)
    mit_validate = mit_sub.add_parser("validate", help="Validate trial cards and feedback schema")
    _add_json_flag(mit_validate)
    mit_validate.set_defaults(func=cmd_multi_ide_trials_validate)

    fb = sub.add_parser("future-backends", help="F4/F5 design & research (read-only validate)")
    fb_sub = fb.add_subparsers(dest="future_backends_cmd", required=True)
    fb_validate = fb_sub.add_parser("validate", help="Validate orchestrator PoC design and RAG research")
    _add_json_flag(fb_validate)
    fb_validate.set_defaults(func=cmd_future_backends_validate)

    tfr = sub.add_parser("trial-feedback-review", help="C11 feedback review specs (read-only validate)")
    tfr_sub = tfr.add_subparsers(dest="trial_feedback_review_cmd", required=True)
    tfr_validate = tfr_sub.add_parser("validate", help="Validate feedback classification and revision rules")
    _add_json_flag(tfr_validate)
    tfr_validate.set_defaults(func=cmd_trial_feedback_review_validate)

    dh = sub.add_parser("delivery-hub", help="G1 delivery index (read-only validate)")
    dh_sub = dh.add_subparsers(dest="delivery_hub_cmd", required=True)
    dh_validate = dh_sub.add_parser("validate", help="Validate delivery hub docs and manifest")
    _add_json_flag(dh_validate)
    dh_validate.set_defaults(func=cmd_delivery_hub_validate)

    dr = sub.add_parser("demo-roadmap", help="G2 demo roadmap (read-only validate)")
    dr_sub = dr.add_subparsers(dest="demo_roadmap_cmd", required=True)
    dr_validate = dr_sub.add_parser("validate", help="Validate demo scripts and boundaries")
    _add_json_flag(dr_validate)
    dr_validate.set_defaults(func=cmd_demo_roadmap_validate)

    lrr = sub.add_parser("legal-release-review", help="G3 legal review checklists (read-only validate)")
    lrr_sub = lrr.add_subparsers(dest="legal_release_review_cmd", required=True)
    lrr_validate = lrr_sub.add_parser("validate", help="Validate legal review package")
    _add_json_flag(lrr_validate)
    lrr_validate.set_defaults(func=cmd_legal_release_review_validate)

    htr = sub.add_parser("human-trial-runbook", help="H1 human trial runbook (read-only validate)")
    htr_sub = htr.add_subparsers(dest="human_trial_runbook_cmd", required=True)
    htr_validate = htr_sub.add_parser("validate", help="Validate human trial runbook")
    _add_json_flag(htr_validate)
    htr_validate.set_defaults(func=cmd_human_trial_runbook_validate)

    pfc = sub.add_parser("package-freeze-candidate", help="H2 freeze candidate manifest (read-only validate)")
    pfc_sub = pfc.add_subparsers(dest="package_freeze_candidate_cmd", required=True)
    pfc_validate = pfc_sub.add_parser("validate", help="Validate package freeze candidate")
    _add_json_flag(pfc_validate)
    pfc_validate.set_defaults(func=cmd_package_freeze_candidate_validate)

    lrp = sub.add_parser("legal-review-packet", help="H3 legal review packet (read-only validate)")
    lrp_sub = lrp.add_subparsers(dest="legal_review_packet_cmd", required=True)
    lrp_validate = lrp_sub.add_parser("validate", help="Validate legal review packet materials")
    _add_json_flag(lrp_validate)
    lrp_validate.set_defaults(func=cmd_legal_review_packet_validate)

    tri = sub.add_parser("trial-results-intake", help="I1 trial results intake (read-only validate)")
    tri_sub = tri.add_subparsers(dest="trial_results_intake_cmd", required=True)
    tri_validate = tri_sub.add_parser("validate", help="Validate trial results intake templates")
    _add_json_flag(tri_validate)
    tri_validate.set_defaults(func=cmd_trial_results_intake_validate)

    fva = sub.add_parser("freeze-version-alignment", help="I2 freeze version alignment (read-only validate)")
    fva_sub = fva.add_subparsers(dest="freeze_version_alignment_cmd", required=True)
    fva_validate = fva_sub.add_parser("validate", help="Validate freeze version alignment templates")
    _add_json_flag(fva_validate)
    fva_validate.set_defaults(func=cmd_freeze_version_alignment_validate)

    lri = sub.add_parser("legal-review-response-intake", help="I3 legal response intake (read-only validate)")
    lri_sub = lri.add_subparsers(dest="legal_review_response_intake_cmd", required=True)
    lri_validate = lri_sub.add_parser("validate", help="Validate legal response intake templates")
    _add_json_flag(lri_validate)
    lri_validate.set_defaults(func=cmd_legal_review_response_intake_validate)

    fts = sub.add_parser("first-trial-session-kit", help="J1 first trial session kit (read-only validate)")
    fts_sub = fts.add_subparsers(dest="first_trial_session_kit_cmd", required=True)
    fts_validate = fts_sub.add_parser("validate", help="Validate first trial session kit templates")
    _add_json_flag(fts_validate)
    fts_validate.set_defaults(func=cmd_first_trial_session_kit_validate)

    frm = sub.add_parser("freeze-review-meeting", help="J2 freeze review meeting (read-only validate)")
    frm_sub = frm.add_subparsers(dest="freeze_review_meeting_cmd", required=True)
    frm_validate = frm_sub.add_parser("validate", help="Validate freeze review meeting materials")
    _add_json_flag(frm_validate)
    frm_validate.set_defaults(func=cmd_freeze_review_meeting_validate)

    lrm = sub.add_parser("legal-review-meeting", help="J3 legal review meeting (read-only validate)")
    lrm_sub = lrm.add_subparsers(dest="legal_review_meeting_cmd", required=True)
    lrm_validate = lrm_sub.add_parser("validate", help="Validate legal review meeting materials")
    _add_json_flag(lrm_validate)
    lrm_validate.set_defaults(func=cmd_legal_review_meeting_validate)

    trr = sub.add_parser("trial-result-review", help="K1 trial result review (read-only validate)")
    trr_sub = trr.add_subparsers(dest="trial_result_review_cmd", required=True)
    trr_validate = trr_sub.add_parser("validate", help="Validate trial result review templates")
    _add_json_flag(trr_validate)
    trr_validate.set_defaults(func=cmd_trial_result_review_validate)

    fdr = sub.add_parser("freeze-decision-record", help="K2 freeze decision record (read-only validate)")
    fdr_sub = fdr.add_subparsers(dest="freeze_decision_record_cmd", required=True)
    fdr_validate = fdr_sub.add_parser("validate", help="Validate freeze decision record templates")
    _add_json_flag(fdr_validate)
    fdr_validate.set_defaults(func=cmd_freeze_decision_record_validate)

    ldr = sub.add_parser("legal-decision-record", help="K3 legal decision record (read-only validate)")
    ldr_sub = ldr.add_subparsers(dest="legal_decision_record_cmd", required=True)
    ldr_validate = ldr_sub.add_parser("validate", help="Validate legal decision record templates")
    _add_json_flag(ldr_validate)
    ldr_validate.set_defaults(func=cmd_legal_decision_record_validate)

    trip = sub.add_parser("trial-result-import-preflight", help="L1 trial import preflight (read-only validate)")
    trip_sub = trip.add_subparsers(dest="trial_result_import_preflight_cmd", required=True)
    trip_validate = trip_sub.add_parser("validate", help="Validate trial result import preflight")
    _add_json_flag(trip_validate)
    trip_validate.set_defaults(func=cmd_trial_result_import_preflight_validate)

    fdip = sub.add_parser("freeze-decision-import-preflight", help="L2 freeze import preflight (read-only validate)")
    fdip_sub = fdip.add_subparsers(dest="freeze_decision_import_preflight_cmd", required=True)
    fdip_validate = fdip_sub.add_parser("validate", help="Validate freeze decision import preflight")
    _add_json_flag(fdip_validate)
    fdip_validate.set_defaults(func=cmd_freeze_decision_import_preflight_validate)

    ldip = sub.add_parser("legal-decision-import-preflight", help="L3 legal import preflight (read-only validate)")
    ldip_sub = ldip.add_subparsers(dest="legal_decision_import_preflight_cmd", required=True)
    ldip_validate = ldip_sub.add_parser("validate", help="Validate legal decision import preflight")
    _add_json_flag(ldip_validate)
    ldip_validate.set_defaults(func=cmd_legal_decision_import_preflight_validate)

    tidr = sub.add_parser("trial-import-decision-record", help="M1 trial import decision (read-only validate)")
    tidr_sub = tidr.add_subparsers(dest="trial_import_decision_record_cmd", required=True)
    tidr_validate = tidr_sub.add_parser("validate", help="Validate trial import decision record")
    _add_json_flag(tidr_validate)
    tidr_validate.set_defaults(func=cmd_trial_import_decision_record_validate)

    fidr = sub.add_parser("freeze-import-decision-record", help="M2 freeze import decision (read-only validate)")
    fidr_sub = fidr.add_subparsers(dest="freeze_import_decision_record_cmd", required=True)
    fidr_validate = fidr_sub.add_parser("validate", help="Validate freeze import decision record")
    _add_json_flag(fidr_validate)
    fidr_validate.set_defaults(func=cmd_freeze_import_decision_record_validate)

    lidb = sub.add_parser("legal-import-decision-board", help="M3 legal import decision board (read-only validate)")
    lidb_sub = lidb.add_subparsers(dest="legal_import_decision_board_cmd", required=True)
    lidb_validate = lidb_sub.add_parser("validate", help="Validate legal import decision board")
    _add_json_flag(lidb_validate)
    lidb_validate.set_defaults(func=cmd_legal_import_decision_board_validate)

    tdfk = sub.add_parser("trial-decision-fill-kit", help="N1 trial decision fill kit (read-only validate)")
    tdfk_sub = tdfk.add_subparsers(dest="trial_decision_fill_kit_cmd", required=True)
    tdfk_validate = tdfk_sub.add_parser("validate", help="Validate trial decision fill kit")
    _add_json_flag(tdfk_validate)
    tdfk_validate.set_defaults(func=cmd_trial_decision_fill_kit_validate)

    fdfk = sub.add_parser("freeze-decision-fill-kit", help="N2 freeze decision fill kit (read-only validate)")
    fdfk_sub = fdfk.add_subparsers(dest="freeze_decision_fill_kit_cmd", required=True)
    fdfk_validate = fdfk_sub.add_parser("validate", help="Validate freeze decision fill kit")
    _add_json_flag(fdfk_validate)
    fdfk_validate.set_defaults(func=cmd_freeze_decision_fill_kit_validate)

    lbek = sub.add_parser("legal-board-execution-kit", help="N3 legal board execution kit (read-only validate)")
    lbek_sub = lbek.add_subparsers(dest="legal_board_execution_kit_cmd", required=True)
    lbek_validate = lbek_sub.add_parser("validate", help="Validate legal board execution kit")
    _add_json_flag(lbek_validate)
    lbek_validate.set_defaults(func=cmd_legal_board_execution_kit_validate)

    sffsc = sub.add_parser(
        "solo-founder-freeze-self-check",
        help="O2 solo founder freeze self-check (read-only validate)",
    )
    sffsc_sub = sffsc.add_subparsers(dest="solo_founder_freeze_self_check_cmd", required=True)
    sffsc_validate = sffsc_sub.add_parser("validate", help="Validate solo founder freeze self-check")
    _add_json_flag(sffsc_validate)
    sffsc_validate.set_defaults(func=cmd_solo_founder_freeze_self_check_validate)

    sfcs = sub.add_parser(
        "solo-founder-compliance-self-check",
        help="O3 solo founder compliance self-check (read-only validate)",
    )
    sfcs_sub = sfcs.add_subparsers(dest="solo_founder_compliance_self_check_cmd", required=True)
    sfcs_validate = sfcs_sub.add_parser("validate", help="Validate solo founder compliance self-check")
    _add_json_flag(sfcs_validate)
    sfcs_validate.set_defaults(func=cmd_solo_founder_compliance_self_check_validate)

    sfrbd = sub.add_parser(
        "solo-founder-release-blocked-declaration",
        help="O2+O3 merged blocked declaration (read-only validate)",
    )
    sfrbd_sub = sfrbd.add_subparsers(dest="solo_founder_release_blocked_declaration_cmd", required=True)
    sfrbd_validate = sfrbd_sub.add_parser("validate", help="Validate solo founder release blocked declaration")
    _add_json_flag(sfrbd_validate)
    sfrbd_validate.set_defaults(func=cmd_solo_founder_release_blocked_declaration_validate)

    sd15 = sub.add_parser("solo-demo-15min", help="P1 solo 15min demo route (read-only validate)")
    sd15_sub = sd15.add_subparsers(dest="solo_demo_15min_cmd", required=True)
    sd15_validate = sd15_sub.add_parser("validate", help="Validate solo demo 15min package")
    _add_json_flag(sd15_validate)
    sd15_validate.set_defaults(func=cmd_solo_demo_15min_validate)

    pfr = sub.add_parser("promptpack-first-run", help="P2 PromptPack first-run guides (read-only validate)")
    pfr_sub = pfr.add_subparsers(dest="promptpack_first_run_cmd", required=True)
    pfr_validate = pfr_sub.add_parser("validate", help="Validate promptpack first-run package")
    _add_json_flag(pfr_validate)
    pfr_validate.set_defaults(func=cmd_promptpack_first_run_validate)

    midf = sub.add_parser("multi-ide-dry-run-feedback", help="P3 multi-IDE feedback template (read-only validate)")
    midf_sub = midf.add_subparsers(dest="multi_ide_dry_run_feedback_cmd", required=True)
    midf_validate = midf_sub.add_parser("validate", help="Validate multi-IDE dry-run feedback package")
    _add_json_flag(midf_validate)
    midf_validate.set_defaults(func=cmd_multi_ide_dry_run_feedback_validate)

    sdti = sub.add_parser("solo-demo-trial-intake", help="Q1 solo demo trial intake (read-only validate)")
    sdti_sub = sdti.add_subparsers(dest="solo_demo_trial_intake_cmd", required=True)
    sdti_validate = sdti_sub.add_parser("validate", help="Validate solo demo trial intake")
    _add_json_flag(sdti_validate)
    sdti_validate.set_defaults(func=cmd_solo_demo_trial_intake_validate)

    pfr = sub.add_parser("promptpack-friction-review", help="Q2 promptpack friction review (read-only validate)")
    pfr_sub = pfr.add_subparsers(dest="promptpack_friction_review_cmd", required=True)
    pfr_validate = pfr_sub.add_parser("validate", help="Validate promptpack friction review")
    _add_json_flag(pfr_validate)
    pfr_validate.set_defaults(func=cmd_promptpack_friction_review_validate)

    mifb = sub.add_parser("multi-ide-feedback-backlog", help="Q3 multi-IDE feedback backlog (read-only validate)")
    mifb_sub = mifb.add_subparsers(dest="multi_ide_feedback_backlog_cmd", required=True)
    mifb_validate = mifb_sub.add_parser("validate", help="Validate multi-IDE feedback backlog")
    _add_json_flag(mifb_validate)
    mifb_validate.set_defaults(func=cmd_multi_ide_feedback_backlog_validate)

    ofc = sub.add_parser(
        "openclaw-feedback-consolidation",
        help="OpenClaw feedback merge consolidation (read-only validate)",
    )
    ofc_sub = ofc.add_subparsers(dest="openclaw_feedback_consolidation_cmd", required=True)
    ofc_validate = ofc_sub.add_parser("validate", help="Validate openclaw feedback consolidation")
    _add_json_flag(ofc_validate)
    ofc_validate.set_defaults(func=cmd_openclaw_feedback_consolidation_validate)

    aem = sub.add_parser("agent-entry-menu", help="UI Agent menu manifest (validate/list)")
    aem_sub = aem.add_subparsers(dest="agent_entry_menu_cmd", required=True)
    aem_validate = aem_sub.add_parser("validate", help="Validate agent entry menu package")
    _add_json_flag(aem_validate)
    aem_validate.set_defaults(func=cmd_agent_entry_menu_validate)
    aem_list = aem_sub.add_parser("list", help="List agent menu items from manifest")
    _add_json_flag(aem_list)
    aem_list.set_defaults(func=cmd_agent_entry_menu_list)

    srv = sub.add_parser("server", help="UI Agent Workbench API server")
    srv_sub = srv.add_subparsers(dest="server_cmd", required=True)
    srv_validate = srv_sub.add_parser("validate", help="Validate server contract (no listen)")
    _add_json_flag(srv_validate)
    srv_validate.set_defaults(func=cmd_server_validate)
    srv_run = srv_sub.add_parser("run", help="Run local API server")
    srv_run.add_argument("--host", default="127.0.0.1")
    srv_run.add_argument("--port", type=int, default=8765)
    _add_json_flag(srv_run)
    srv_run.set_defaults(func=cmd_server_run)

    ipd = sub.add_parser("ip-production-demo", help="IP to short drama offline demo package")
    ipd_sub = ipd.add_subparsers(dest="ip_production_demo_cmd", required=True)
    ipd_validate = ipd_sub.add_parser("validate", help="Validate ip-production-demo artifacts")
    _add_json_flag(ipd_validate)
    ipd_validate.set_defaults(func=cmd_ip_production_demo_validate)
    ipd_run = ipd_sub.add_parser("run", help="Assemble demo production package (offline)")
    _add_json_flag(ipd_run)
    ipd_run.set_defaults(func=cmd_ip_production_demo_run)

    nrd = sub.add_parser("novel-review-demo", help="Novel review offline demo (no auto-rewrite)")
    nrd_sub = nrd.add_subparsers(dest="novel_review_demo_cmd", required=True)
    nrd_validate = nrd_sub.add_parser("validate", help="Validate novel-review-demo artifacts")
    _add_json_flag(nrd_validate)
    nrd_validate.set_defaults(func=cmd_novel_review_demo_validate)
    nrd_run = nrd_sub.add_parser("run", help="Run offline review demo package")
    _add_json_flag(nrd_run)
    nrd_run.set_defaults(func=cmd_novel_review_demo_run)

    rgd = sub.add_parser("realgen-demo", help="Real local chapter/review/package/video generation")
    rgd_sub = rgd.add_subparsers(dest="realgen_demo_cmd", required=True)
    rgd_validate = rgd_sub.add_parser("validate", help="Validate realgen-demo package")
    _add_json_flag(rgd_validate)
    rgd_validate.set_defaults(func=cmd_realgen_demo_validate)
    rgd_run = rgd_sub.add_parser("run", help="Run full RealGen pipeline (writes cold_case_echo_realgen_01/)")
    _add_json_flag(rgd_run)
    rgd_run.set_defaults(func=cmd_realgen_demo_run)

    rp = sub.add_parser("realpipeline", help="RealPipeline-2B NVP-gated novel+video evidence validation")
    rp.add_argument("--project", default="novels/novel-837dd4f1", help="Novel project path")
    rp_sub = rp.add_subparsers(dest="realpipeline_cmd", required=True)
    rp_validate = rp_sub.add_parser("validate", help="Validate NVP manifest and Phase 0-9 + video evidence")
    _add_json_flag(rp_validate)
    rp_validate.add_argument("--project", default="novels/novel-837dd4f1")
    rp_validate.set_defaults(func=cmd_realpipeline_validate)
    rp_run = rp_sub.add_parser("run", help="Confirm RealPipeline-2B evidence on disk")
    _add_json_flag(rp_run)
    rp_run.add_argument("--project", default="novels/novel-837dd4f1")
    rp_run.set_defaults(func=cmd_realpipeline_run)

    mcp_parser = sub.add_parser("mcp", help="MCP Server management (Sprint 4)")
    mcp_sub = mcp_parser.add_subparsers(dest="mcp_cmd", required=True)
    mcp_serve = mcp_sub.add_parser("serve", help="Start MCP server (stdio or SSE)")
    mcp_serve.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP transport (stdio=Cursor subprocess, sse=HTTP Streamable)",
    )
    _add_json_flag(mcp_serve)
    mcp_serve.set_defaults(func=cmd_mcp_serve)

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

    dr = sub.add_parser("doc-router", help="Document routing index — preflight before bulk reads")
    dr_sub = dr.add_subparsers(dest="doc_router_cmd", required=True)

    dr_build = dr_sub.add_parser("build", help="Build SQLite FTS document index")
    dr_build.add_argument("--root", default="", help="Suite root (default: auto-detect)")
    dr_build.add_argument("--out", default="", help="Output SQLite path")
    dr_build.add_argument("--scopes", default="", help="Comma-separated scopes")
    dr_build.add_argument("--include", default="", help="Extra include globs")
    dr_build.add_argument("--exclude", default="", help="Extra exclude globs")
    _add_json_flag(dr_build)
    dr_build.set_defaults(func=cmd_doc_router_build)

    dr_query = dr_sub.add_parser("query", help="Query document index")
    dr_query.add_argument("query", help="Search query")
    dr_query.add_argument("--top-k", type=int, default=10)
    dr_query.add_argument("--scope", default="", help="Scope filter")
    dr_query.add_argument("--max-docs", type=int, default=None)
    dr_query.add_argument("--root", default="")
    dr_query.add_argument("--db", default="")
    _add_json_flag(dr_query)
    dr_query.set_defaults(func=cmd_doc_router_query)

    dr_preflight = dr_sub.add_parser("preflight", help="Preflight task with read budget + cursor health")
    dr_preflight.add_argument("query", help="Task description to route")
    dr_preflight.add_argument("--root", default="")
    dr_preflight.add_argument("--db", default="")
    dr_preflight.add_argument(
        "--risk-level",
        default="",
        choices=["", "ok", "warning", "high", "critical"],
        help="Override cursor health risk level",
    )
    _add_json_flag(dr_preflight)
    dr_preflight.set_defaults(func=cmd_doc_router_preflight)

    dr_validate = dr_sub.add_parser("validate", help="Validate index schema and FTS")
    dr_validate.add_argument("--root", default="")
    dr_validate.add_argument("--db", default="")
    _add_json_flag(dr_validate)
    dr_validate.set_defaults(func=cmd_doc_router_validate)

    dr_explain = dr_sub.add_parser("explain", help="Explain document selection")
    dr_explain.add_argument("--query", required=True)
    dr_explain.add_argument("--docs", required=True, help="JSON array of selected docs")
    _add_json_flag(dr_explain)
    dr_explain.set_defaults(func=cmd_doc_router_explain)

    return ap


def cmd_writer_init(args: argparse.Namespace) -> int:
    if args.from_scan is None and (not args.title.strip() or not args.premise.strip()):
        return emit(
            error_result(
                E.INIT_TITLE_REQUIRED if not args.title.strip() else E.INIT_PREMISE_REQUIRED,
                "Provide --title and --premise, or use --from-scan <radar.scan.json>",
            ),
            json_out=args.json,
        )
    return emit(
        run_init(
            title=args.title,
            premise=args.premise,
            genre=args.genre,
            slug=args.slug or "",
            output=args.output,
            concept=args.concept,
            platform_target=args.platform_target,
            from_scan=args.from_scan,
            scan_theme_index=args.scan_theme_index,
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


def cmd_video_storyboard(args: argparse.Namespace) -> int:
    return emit(run_storyboard(args), json_out=args.json)


def cmd_video_character_list(args: argparse.Namespace) -> int:
    return emit(cmd_character_list(args), json_out=args.json)


def cmd_video_character_pack(args: argparse.Namespace) -> int:
    return emit(cmd_character_pack(args), json_out=args.json)


def cmd_video_character_qc(args: argparse.Namespace) -> int:
    return emit(cmd_character_qc(args), json_out=args.json)


def cmd_video_stills_generate(args: argparse.Namespace) -> int:
    return emit(cmd_stills_generate(args), json_out=args.json)


def cmd_video_compose(args: argparse.Namespace) -> int:
    return emit(cmd_compose_run(args), json_out=args.json)


def cmd_video_pipeline(args: argparse.Namespace) -> int:
    return emit(cmd_pipeline_run(args), json_out=args.json)


def cmd_video_gate(args: argparse.Namespace) -> int:
    return emit(cmd_gate(args), json_out=args.json)


def cmd_analytics_record_cli(args: argparse.Namespace) -> int:
    return emit(cmd_analytics_record(args), json_out=args.json)


def cmd_analytics_status_cli(args: argparse.Namespace) -> int:
    return emit(cmd_analytics_status(args), json_out=args.json)


def cmd_analytics_report_cli(args: argparse.Namespace) -> int:
    return emit(cmd_analytics_report(args), json_out=args.json)


def cmd_analytics_cross_report_cli(args: argparse.Namespace) -> int:
    return emit(cmd_analytics_cross_report(args), json_out=args.json)


def cmd_novel_publish_upload_cli(args: argparse.Namespace) -> int:
    return emit(cmd_novel_publish_upload(args), json_out=args.json)


def cmd_novel_publish_list_cli(args: argparse.Namespace) -> int:
    return emit(cmd_novel_publish_list(args), json_out=args.json)


def cmd_video_publish(args: argparse.Namespace) -> int:
    return emit(cmd_publish(args), json_out=args.json)


def cmd_video_publish_list(args: argparse.Namespace) -> int:
    return emit(cmd_publish_list(args), json_out=args.json)


def cmd_video_cookie(args: argparse.Namespace) -> int:
    return emit(cmd_cookie(args), json_out=args.json)


def cmd_auth_login_cli(args: argparse.Namespace) -> int:
    return emit(cmd_auth_login(args), json_out=args.json)


def cmd_auth_logout_cli(args: argparse.Namespace) -> int:
    return emit(cmd_auth_logout(args), json_out=args.json)


def cmd_auth_status_cli(args: argparse.Namespace) -> int:
    return emit(cmd_auth_status(args), json_out=args.json)


def cmd_product_list(args: argparse.Namespace) -> int:
    return emit(run_product_list(), json_out=args.json)


def cmd_product_read(args: argparse.Namespace) -> int:
    return emit(run_product_read(args.category, args.name), json_out=args.json)


def cmd_product_validate(args: argparse.Namespace) -> int:
    return emit(run_product_validate(), json_out=args.json, blocked_summary=True)


def cmd_video_production_adapter_dry_run(args: argparse.Namespace) -> int:
    return emit(
        run_adapter_dry_run(args.adapter, args.example, args.output),
        json_out=args.json,
    )


def cmd_commercial_review_validate(args: argparse.Namespace) -> int:
    return emit(run_commercial_review_validate(), json_out=args.json)


def cmd_commercial_release_candidate_validate(args: argparse.Namespace) -> int:
    return emit(run_commercial_release_candidate_validate(), json_out=args.json, blocked_summary=True)


def cmd_workflow_contract_validate(args: argparse.Namespace) -> int:
    return emit(run_workflow_contract_validate(), json_out=args.json)


def cmd_trace_state_validate(args: argparse.Namespace) -> int:
    return emit(run_trace_state_validate(), json_out=args.json)


def cmd_multi_ide_trials_validate(args: argparse.Namespace) -> int:
    return emit(run_multi_ide_trials_validate(), json_out=args.json)


def cmd_future_backends_validate(args: argparse.Namespace) -> int:
    return emit(run_future_backends_validate(), json_out=args.json)


def cmd_trial_feedback_review_validate(args: argparse.Namespace) -> int:
    return emit(run_trial_feedback_review_validate(), json_out=args.json)


def cmd_delivery_hub_validate(args: argparse.Namespace) -> int:
    return emit(run_delivery_hub_validate(), json_out=args.json)


def cmd_demo_roadmap_validate(args: argparse.Namespace) -> int:
    return emit(run_demo_roadmap_validate(), json_out=args.json)


def cmd_legal_release_review_validate(args: argparse.Namespace) -> int:
    return emit(run_legal_release_review_validate(), json_out=args.json)


def cmd_human_trial_runbook_validate(args: argparse.Namespace) -> int:
    return emit(run_human_trial_runbook_validate(), json_out=args.json)


def cmd_package_freeze_candidate_validate(args: argparse.Namespace) -> int:
    return emit(run_package_freeze_candidate_validate(), json_out=args.json)


def cmd_legal_review_packet_validate(args: argparse.Namespace) -> int:
    return emit(run_legal_review_packet_validate(), json_out=args.json)


def cmd_trial_results_intake_validate(args: argparse.Namespace) -> int:
    return emit(run_trial_results_intake_validate(), json_out=args.json)


def cmd_freeze_version_alignment_validate(args: argparse.Namespace) -> int:
    return emit(run_freeze_version_alignment_validate(), json_out=args.json)


def cmd_legal_review_response_intake_validate(args: argparse.Namespace) -> int:
    return emit(run_legal_review_response_intake_validate(), json_out=args.json)


def cmd_first_trial_session_kit_validate(args: argparse.Namespace) -> int:
    return emit(run_first_trial_session_kit_validate(), json_out=args.json)


def cmd_freeze_review_meeting_validate(args: argparse.Namespace) -> int:
    return emit(run_freeze_review_meeting_validate(), json_out=args.json)


def cmd_legal_review_meeting_validate(args: argparse.Namespace) -> int:
    return emit(run_legal_review_meeting_validate(), json_out=args.json)


def cmd_trial_result_review_validate(args: argparse.Namespace) -> int:
    return emit(run_trial_result_review_validate(), json_out=args.json)


def cmd_freeze_decision_record_validate(args: argparse.Namespace) -> int:
    return emit(run_freeze_decision_record_validate(), json_out=args.json)


def cmd_legal_decision_record_validate(args: argparse.Namespace) -> int:
    return emit(run_legal_decision_record_validate(), json_out=args.json)


def cmd_trial_result_import_preflight_validate(args: argparse.Namespace) -> int:
    return emit(run_trial_result_import_preflight_validate(), json_out=args.json)


def cmd_freeze_decision_import_preflight_validate(args: argparse.Namespace) -> int:
    return emit(run_freeze_decision_import_preflight_validate(), json_out=args.json)


def cmd_legal_decision_import_preflight_validate(args: argparse.Namespace) -> int:
    return emit(run_legal_decision_import_preflight_validate(), json_out=args.json)


def cmd_trial_import_decision_record_validate(args: argparse.Namespace) -> int:
    return emit(run_trial_import_decision_record_validate(), json_out=args.json)


def cmd_freeze_import_decision_record_validate(args: argparse.Namespace) -> int:
    return emit(run_freeze_import_decision_record_validate(), json_out=args.json)


def cmd_legal_import_decision_board_validate(args: argparse.Namespace) -> int:
    return emit(run_legal_import_decision_board_validate(), json_out=args.json)


def cmd_trial_decision_fill_kit_validate(args: argparse.Namespace) -> int:
    return emit(run_trial_decision_fill_kit_validate(), json_out=args.json)


def cmd_freeze_decision_fill_kit_validate(args: argparse.Namespace) -> int:
    return emit(run_freeze_decision_fill_kit_validate(), json_out=args.json)


def cmd_legal_board_execution_kit_validate(args: argparse.Namespace) -> int:
    return emit(run_legal_board_execution_kit_validate(), json_out=args.json)


def cmd_solo_founder_freeze_self_check_validate(args: argparse.Namespace) -> int:
    return emit(run_solo_founder_freeze_self_check_validate(), json_out=args.json)


def cmd_solo_founder_compliance_self_check_validate(args: argparse.Namespace) -> int:
    return emit(run_solo_founder_compliance_self_check_validate(), json_out=args.json)


def cmd_solo_founder_release_blocked_declaration_validate(args: argparse.Namespace) -> int:
    return emit(run_solo_founder_release_blocked_declaration_validate(), json_out=args.json)


def cmd_solo_demo_15min_validate(args: argparse.Namespace) -> int:
    return emit(run_solo_demo_15min_validate(), json_out=args.json)


def cmd_promptpack_first_run_validate(args: argparse.Namespace) -> int:
    return emit(run_promptpack_first_run_validate(), json_out=args.json)


def cmd_multi_ide_dry_run_feedback_validate(args: argparse.Namespace) -> int:
    return emit(run_multi_ide_dry_run_feedback_validate(), json_out=args.json)


def cmd_solo_demo_trial_intake_validate(args: argparse.Namespace) -> int:
    return emit(run_solo_demo_trial_intake_validate(), json_out=args.json)


def cmd_promptpack_friction_review_validate(args: argparse.Namespace) -> int:
    return emit(run_promptpack_friction_review_validate(), json_out=args.json)


def cmd_multi_ide_feedback_backlog_validate(args: argparse.Namespace) -> int:
    return emit(run_multi_ide_feedback_backlog_validate(), json_out=args.json)


def cmd_openclaw_feedback_consolidation_validate(args: argparse.Namespace) -> int:
    return emit(run_openclaw_feedback_consolidation_validate(), json_out=args.json)


def cmd_agent_entry_menu_validate(args: argparse.Namespace) -> int:
    return emit(run_agent_entry_menu_validate(), json_out=args.json, blocked_summary=True)


def cmd_agent_entry_menu_list(args: argparse.Namespace) -> int:
    return emit(run_agent_entry_menu_list(), json_out=args.json)


def cmd_server_validate(args: argparse.Namespace) -> int:
    return emit(run_server_validate(), json_out=args.json, blocked_summary=True)


def cmd_server_run(args: argparse.Namespace) -> int:
    from novel_suite.server.runner import run_server_blocking

    return run_server_blocking(host=args.host, port=args.port, json_out=args.json)


def cmd_ip_production_demo_validate(args: argparse.Namespace) -> int:
    return emit(run_ip_production_demo_validate(), json_out=args.json)


def cmd_ip_production_demo_run(args: argparse.Namespace) -> int:
    return emit(run_ip_production_demo(), json_out=args.json)


def cmd_novel_review_demo_validate(args: argparse.Namespace) -> int:
    return emit(run_novel_review_demo_validate(), json_out=args.json)


def cmd_novel_review_demo_run(args: argparse.Namespace) -> int:
    return emit(run_novel_review_demo(), json_out=args.json)


def cmd_realgen_demo_validate(args: argparse.Namespace) -> int:
    return emit(run_realgen_demo_validate(), json_out=args.json, blocked_summary=True)


def cmd_realgen_demo_run(args: argparse.Namespace) -> int:
    return emit(
        error_result(
            "REALGEN_DEMO_DEPRECATED",
            "RealGen-1旁路已废止；请使用 realpipeline --project novels/novel-837dd4f1",
            commercial_release_allowed=False,
            verdict="blocked",
            next_actions=["novel-suite realpipeline validate --project novels/novel-837dd4f1 --json"],
        ),
        json_out=args.json,
        blocked_summary=True,
    )


def cmd_realpipeline_validate(args: argparse.Namespace) -> int:
    return emit(validate_realpipeline(args.project), json_out=args.json, blocked_summary=True)


def cmd_realpipeline_run(args: argparse.Namespace) -> int:
    return emit(run_realpipeline(args.project), json_out=args.json, blocked_summary=True)


def cmd_mcp_serve(args: argparse.Namespace) -> int:
    config_path = suite_root() / ".cursor" / "mcp.json"
    if not config_path.is_file():
        msg = "MCP config not found. Run: platforms/install-mcp.ps1"
        if args.json:
            return emit(
                error_result(E.MCP_CONFIG_MISSING, msg, next_actions=[msg]),
                json_out=True,
            )
        print(msg, file=sys.stderr)
    try:
        from novel_suite.mcp_server import run_server

        transport = getattr(args, "transport", "stdio") or "stdio"
        run_server(transport=transport)
    except ImportError:
        hint = "pip install mcp"
        if args.json:
            return emit(
                error_result(E.MCP_SDK_MISSING, hint, next_actions=[hint]),
                json_out=True,
            )
        print(f"MCP SDK missing. {hint}", file=sys.stderr)
        return 1
    return 0


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


def cmd_doc_router_build(args: argparse.Namespace) -> int:
    return emit(run_doc_router_build(args), json_out=args.json)


def cmd_doc_router_query(args: argparse.Namespace) -> int:
    return emit(run_doc_router_query(args), json_out=args.json)


def cmd_doc_router_preflight(args: argparse.Namespace) -> int:
    return emit(run_doc_router_preflight(args), json_out=args.json)


def cmd_doc_router_validate(args: argparse.Namespace) -> int:
    return emit(run_doc_router_validate(args), json_out=args.json)


def cmd_doc_router_explain(args: argparse.Namespace) -> int:
    return emit(run_doc_router_explain(args), json_out=args.json)


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
