#!/usr/bin/env python3
"""Novel writer CLI — equal capability to IDE Skills."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_MONOREPO = Path(__file__).resolve().parents[2]
_SRC = _MONOREPO / "src"
if (_SRC / "novel_suite").is_dir():
    _src_s = str(_SRC)
    if _src_s not in sys.path:
        sys.path.insert(0, _src_s)

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT.parent / "templates"
SCRIPTS = ROOT / "scripts"

from scripts import pipeline_gate as gate
from scripts import project_registry as reg


def resolve_project(args: argparse.Namespace) -> Path:
    explicit = getattr(args, "project", None)
    return reg.resolve_project(explicit)


def add_project_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--project",
        type=Path,
        default=None,
        help="Novel project directory (default: novels/.active)",
    )


def scaffold_project(
    output: Path,
    title: str,
    premise: str,
    *,
    genre: str = "通用",
    slug: str = "",
    platform_target: str = "通用",
    register: bool = True,
    concept_path: Path | None = None,
) -> Path:
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    dirs = [
        "canon/snapshots",
        "characters",
        "worldbuilding/locations",
        "worldbuilding/systems",
        "plot/arcs",
        "chapters/.drafts",
        "reviews",
        "dist",
        "graphify-out",
        "bible",
    ]
    for d in dirs:
        (output / d).mkdir(parents=True, exist_ok=True)

    if not slug:
        slug = reg.slug_from_title(title)

    story = TEMPLATES / "story.md"
    if story.exists():
        content = story.read_text(encoding="utf-8")
        content = content.replace("example-novel", slug)
        content = content.replace("雾港来信", title)
        content = content.replace("一封没有寄件人的信，把档案员拉回十年前的失踪案。", premise)
        content = content.replace("悬疑", genre)
        (output / "story.md").write_text(content, encoding="utf-8")
    else:
        (output / "story.md").write_text(f"# {title}\n\n{premise}\n", encoding="utf-8")

    for name, dest in [
        ("task_plan.md", "task_plan.md"),
        ("voice-brief.md", "canon/voice-brief.md"),
        ("characters_index.md", "characters/_index.md"),
        ("chapters_index.md", "chapters/_index.md"),
    ]:
        src = TEMPLATES / name
        if src.exists():
            shutil.copy(src, output / dest)

    task_plan_path = output / "task_plan.md"
    if concept_path and concept_path.is_file():
        shutil.copy(concept_path, output / "canon" / "concept-brief.md")
        from scripts import intel_paths as intel  # noqa: PLC0415
        from scripts import node_completion as nec  # noqa: PLC0415

        radar = intel.radar_path_for_week()
        nec.write_project_phase0_manifest(
            output,
            concept_path=concept_path,
            radar_md=radar if radar.is_file() else None,
        )
        if task_plan_path.is_file():
            tp = task_plan_path.read_text(encoding="utf-8")
            tp = tp.replace(
                "- [ ] Phase 0: 选品（novel-market-scan → canon/concept-brief.md）",
                "- [x] Phase 0: 选品（novel-market-scan → canon/concept-brief.md）",
            )
            task_plan_path.write_text(tp, encoding="utf-8")
    elif (TEMPLATES / "concept-brief.md").is_file() and not (output / "canon" / "concept-brief.md").exists():
        cb = (TEMPLATES / "concept-brief.md").read_text(encoding="utf-8")
        cb = cb.replace("{{TITLE}}", title).replace("{{YYYY-Www}}", "pending")
        (output / "canon" / "concept-brief.md").write_text(cb, encoding="utf-8")

    voice_path = output / "canon" / "voice-brief.md"
    if voice_path.is_file():
        vb = voice_path.read_text(encoding="utf-8")
        if "platform_target" in vb and "（番茄" in vb:
            vb = vb.replace(
                "（番茄小说 / 晋江文学城 / 起点中文网 / 通用）",
                platform_target,
            )
            voice_path.write_text(vb, encoding="utf-8")

    (output / "worldbuilding/_index.md").write_text("# 世界观索引\n\n", encoding="utf-8")
    (output / "plot/_index.md").write_text("# 情节索引\n\n", encoding="utf-8")
    (output / "plot/timeline.md").write_text("# 时间线\n\n", encoding="utf-8")
    (output / "plot/foreshadowing.md").write_text(
        "# 伏笔矩阵\n\n| 元素 | 埋设章 | 发展 | 回收 | 状态 |\n|------|--------|------|------|------|\n",
        encoding="utf-8",
    )

    now = datetime.now(timezone.utc).isoformat()
    progress = {
        "title": title,
        "author": "",
        "slug": slug,
        "updated_at": now,
        "chapters": [],
        "total_words": 0,
    }
    (output / "canon/progress.json").write_text(
        json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    proj_meta = json.loads((TEMPLATES / "project.json").read_text(encoding="utf-8"))
    proj_meta.update(
        {
            "novel_id": slug,
            "slug": slug,
            "title": title,
            "platform_target": platform_target,
            "created_at": now,
        }
    )
    (output / "canon/project.json").write_text(
        json.dumps(proj_meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    from scripts import node_completion as nec  # noqa: PLC0415

    nec.write_project_phase1_manifest(output)

    subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "graphify_bridge.py"),
            "--project",
            str(output),
            "init",
            "--premise",
            premise,
        ],
        check=False,
    )

    if register:
        under_novels = False
        try:
            output.resolve().relative_to(reg.novels_root().resolve())
            under_novels = True
        except ValueError:
            pass
        if under_novels:
            reg.register_novel(output, title, slug, platform_target=platform_target)

    print(f"Initialized: {output}")
    print(f"Slug: {slug} (active novel)")
    return output


def cmd_init(args: argparse.Namespace) -> int:
    platform = getattr(args, "platform_target", "通用")
    out_arg = None if args.output is None else str(args.output).replace("\\", "/")
    if out_arg is None or out_arg in (".", "./my-novel", "my-novel"):
        path, slug = reg.default_novel_path(args.title)
        if args.slug:
            slug = reg.allocate_slug(args.slug) if args.slug in reg.list_slugs() else args.slug
            path = reg.novels_root() / slug
    else:
        assert args.output is not None
        path = args.output.resolve()
        slug = args.slug or reg.allocate_slug(reg.slug_from_title(args.title))
    under_novels = False
    try:
        path.resolve().relative_to(reg.novels_root().resolve())
        under_novels = True
    except ValueError:
        pass
    scaffold_project(
        path,
        args.title,
        args.premise,
        genre=args.genre,
        slug=slug,
        platform_target=platform,
        register=under_novels,
        concept_path=getattr(args, "concept", None),
    )
    return 0


def cmd_use(args: argparse.Namespace) -> int:
    path = reg.set_active(args.slug)
    print(f"Active novel: {args.slug} -> {path}")
    return 0


def cmd_list(_args: argparse.Namespace) -> int:
    data = reg.load_registry()
    active = reg.get_active_slug()
    for n in data.get("novels", []):
        mark = "*" if n.get("slug") == active else " "
        jobs = n.get("video_jobs") or []
        job_note = f"\tvideo_jobs={len(jobs)}" if jobs else ""
        print(f"{mark} {n.get('slug')}\t{n.get('title')}\t{n.get('path')}{job_note}")
    if not data.get("novels"):
        print("(no novels in registry — run: novel init --title '...')")
    return 0


def cmd_active(_args: argparse.Namespace) -> int:
    slug = reg.get_active_slug()
    if not slug:
        print("No active novel")
        return 1
    path = reg.find_by_slug(slug)
    print(f"{slug}\t{path}")
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    project = resolve_project(args)
    try:
        from novel_suite.writer.chapter import run_chapter_promote
        from novel_suite.core.result import emit

        return emit(run_chapter_promote(project, chapter_file=args.chapter), json_out=False)
    except ImportError:
        pass
    draft = project / "chapters" / ".drafts" / args.chapter
    if not draft.is_file():
        print(f"Draft not found: {draft}", file=sys.stderr)
        return 1
    target = project / "chapters" / args.chapter
    shutil.copy2(draft, target)
    print(f"Promoted: {draft.name} -> {target}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    project = resolve_project(args)
    gate_args = argparse.Namespace(project=project, phase=9)
    if cmd_pipeline_gate(gate_args) != 0:
        return 1
    if args.format == "epub":
        out = args.output
        cmd = [sys.executable, str(SCRIPTS / "create_epub.py"), "--project", str(project)]
        if out:
            cmd.extend(["--output", str(out)])
        return subprocess.call(cmd)
    print("Supported: epub", file=sys.stderr)
    return 1


def cmd_review(args: argparse.Namespace) -> int:
    project = resolve_project(args)
    if args.chapter:
        ch = Path(args.chapter)
        if not ch.is_absolute():
            ch = project / ch
    else:
        chapters = sorted((project / "chapters").glob("*.md"))
        if not chapters:
            print("No chapters found", file=sys.stderr)
            return 1
        ch = chapters[-1]
    return subprocess.call(
        [
            sys.executable,
            str(SCRIPTS / "graphify_bridge.py"),
            "--project",
            str(project),
            "review",
            "--chapter",
            str(ch),
        ]
    )


def cmd_status(args: argparse.Namespace) -> int:
    project = resolve_project(args)
    progress = project / "canon/progress.json"
    if progress.exists():
        print(progress.read_text(encoding="utf-8"))
    return subprocess.call(
        [
            sys.executable,
            str(SCRIPTS / "graphify_bridge.py"),
            "--project",
            str(project),
            "status",
        ]
    )


def cmd_pipeline_gate(args: argparse.Namespace) -> int:
    project = resolve_project(args)
    phase = int(getattr(args, "phase", 1) or 1)
    return gate.run_gate(project, phase)


def cmd_pipeline_validate(args: argparse.Namespace) -> int:
    project = resolve_project(args)
    include_registry = bool(getattr(args, "registry", False))
    return gate.run_validate(project, include_registry=include_registry)


def cmd_intel_paths(_args: argparse.Namespace) -> int:
    from scripts import intel_paths as intel  # noqa: PLC0415

    intel.ensure_intel_dirs()
    week = intel.iso_week_id()
    print(f"intel_dir\t{intel.INTEL_DIR}")
    print(f"radar_dir\t{intel.RADAR_DIR}")
    print(f"concepts_dir\t{intel.CONCEPTS_DIR}")
    print(f"radar_this_week\t{intel.radar_path_for_week()}")
    print(f"iso_week\t{week}")
    return 0


def cmd_suite_doctor(args: argparse.Namespace) -> int:
    cmd = [sys.executable, str(SCRIPTS / "suite_doctor.py")]
    if getattr(args, "json_out", False):
        cmd.append("--json")
    if getattr(args, "core_only", False):
        cmd.append("--core-only")
    if getattr(args, "agents", ""):
        cmd.extend(["--agents", args.agents])
    return subprocess.call(cmd)


def cmd_suite_gap_diff(args: argparse.Namespace) -> int:
    cmd = [sys.executable, str(SCRIPTS / "gap_matrix_diff.py"), "--write-report"]
    if getattr(args, "month", ""):
        cmd.extend(["--month", args.month])
    if getattr(args, "json_out", False):
        cmd.append("--json")
    return subprocess.call(cmd)


def cmd_intel_scan(args: argparse.Namespace) -> int:
    cmd = [
        sys.executable,
        str(SCRIPTS / "intel_scan.py"),
        "--period",
        args.period,
        "--platforms",
        args.platforms,
        "--max-results",
        str(args.max_results),
        "--timeout",
        str(args.timeout),
        "--concept-top",
        str(args.concept_top),
    ]
    if getattr(args, "input", None):
        cmd.extend(["--input", str(args.input)])
    if getattr(args, "radar", None):
        cmd.extend(["--radar", str(args.radar)])
    if getattr(args, "concepts_dir", None):
        cmd.extend(["--concepts-dir", str(args.concepts_dir)])
    if getattr(args, "no_concepts", False):
        cmd.append("--no-concepts")
    if getattr(args, "demo", False):
        cmd.append("--demo")
    if getattr(args, "fallback_demo", False):
        cmd.append("--fallback-demo")
    return subprocess.call(cmd)


def cmd_node_sync(args: argparse.Namespace) -> int:
    from scripts import node_completion as nec  # noqa: PLC0415

    project = resolve_project(args)
    phase = int(args.phase)
    if phase < 1 or phase > nec.SYNC_PHASE_MAX:
        print(
            f"ERROR: node sync supports phase 1-{nec.SYNC_PHASE_MAX} only (got {phase})",
            file=sys.stderr,
        )
        return 1
    path = nec.sync_project_phase_manifest(project, phase)
    print(f"OK: synced -> {path}")
    return 0


def cmd_node_validate(args: argparse.Namespace) -> int:
    from scripts import intel_paths as intel  # noqa: PLC0415
    from scripts import node_completion as nec  # noqa: PLC0415

    phase = int(args.phase)
    errors: list[str] = []
    if phase == 0 and args.project is None:
        errors.extend(nec.validate_phase0_intel())
    elif phase == 0:
        project = resolve_project(args)
        errors.extend(nec.validate_phase0_project_gate(project))
    else:
        project = resolve_project(args)
        path = nec.completion_path_for_project(project, phase)
        errors.extend(nec.validate_manifest_file(path))
        if path.is_file():
            manifest = nec.load_manifest(path)
            if manifest:
                if manifest.get("status") != "complete":
                    errors.append(f"{path.name}: status must be complete")
                errors.extend(nec.validate_manifest_semantics(manifest))
    if errors:
        for msg in errors:
            print(f"NODE VALIDATE FAIL: {msg}", file=sys.stderr)
        return 1
    if phase == 0 and not getattr(args, "project", None):
        print(f"NODE VALIDATE OK: intel week={intel.iso_week_id()}")
    else:
        print(f"NODE VALIDATE OK: phase={phase} project={resolve_project(args)}")
    return 0


def cmd_pipeline_status(args: argparse.Namespace) -> int:
    project = resolve_project(args)
    task_plan = project / "task_plan.md"
    voice = project / "canon" / "voice-brief.md"
    concept = project / "canon" / "concept-brief.md"
    phases = gate.parse_pipeline_phases(task_plan)
    if not phases:
        print(f"No pipeline phases in {task_plan}", file=sys.stderr)
        return 1
    print(f"Project: {project}")
    print(f"Slug: {project.name}")
    print(f"Concept brief: {'OK' if concept.is_file() else 'MISSING (Phase 0)'}")
    print(f"Voice brief: {'OK' if voice.is_file() else 'MISSING'}")
    current = None
    for label, done in phases:
        mark = "x" if done else " "
        print(f"  [{mark}] {label}")
        if not done and current is None:
            current = label
    if current:
        print(f"\nNext: {current}")
    else:
        print("\nPipeline phases complete.")
    return 0


def cmd_graphify(args: argparse.Namespace) -> int:
    project = resolve_project(args)
    cmd = [
        sys.executable,
        str(SCRIPTS / "graphify_bridge.py"),
        "--project",
        str(project),
        args.graphify_cmd,
    ]
    if args.graphify_cmd == "init" and args.premise:
        cmd.extend(["--premise", args.premise])
    if args.graphify_cmd == "update" and args.from_chapters:
        cmd.append("--from-chapters")
    if args.graphify_cmd == "query":
        if args.character:
            cmd.extend(["--character", args.character])
        if args.from_char:
            cmd.extend(["--from", args.from_char])
        if args.to_char:
            cmd.extend(["--to", args.to_char])
    return subprocess.call(cmd)


def cmd_bible_summary(args: argparse.Namespace) -> int:
    project = resolve_project(args)
    lines: list[str] = [f"# Story Bible — {project.name}", ""]

    proj_json = project / "canon" / "project.json"
    if proj_json.is_file():
        meta = json.loads(proj_json.read_text(encoding="utf-8"))
        lines.append("## Project")
        for k in ("title", "slug", "platform_target", "author", "novel_id"):
            if meta.get(k):
                lines.append(f"- **{k}**: {meta[k]}")
        lines.append("")

    story = project / "story.md"
    if story.is_file():
        text = story.read_text(encoding="utf-8")
        preview = "\n".join(text.splitlines()[:12])
        lines.extend(["## Story (excerpt)", preview, ""])

    idx = project / "characters" / "_index.md"
    if idx.is_file():
        lines.extend(["## Characters", idx.read_text(encoding="utf-8").strip(), ""])

    snaps = sorted((project / "canon" / "snapshots").glob("ch*-after.md"))
    if snaps:
        latest = snaps[-1]
        lines.extend([f"## Latest snapshot ({latest.name})", latest.read_text(encoding="utf-8").strip(), ""])

    foreshadow = project / "plot" / "foreshadowing.md"
    if foreshadow.is_file():
        lines.extend(["## Foreshadowing", foreshadow.read_text(encoding="utf-8").strip(), ""])

    bible_idx = project / "bible" / "characters" / "_index.md"
    if bible_idx.is_file():
        lines.extend(["## Graphify bible", bible_idx.read_text(encoding="utf-8").strip(), ""])

    graph = project / "graphify-out" / "graph.json"
    if graph.is_file():
        data = json.loads(graph.read_text(encoding="utf-8"))
        lines.append(f"## Graph: {len(data.get('nodes', []))} nodes, {len(data.get('edges', []))} edges")

    out = "\n".join(lines).strip() + "\n"
    if getattr(args, "output", None):
        args.output.write_text(out, encoding="utf-8")
        print(f"Wrote: {args.output}")
    else:
        print(out)
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    from scripts import audit_registry as ar  # noqa: PLC0415

    mode = args.audit_mode.strip().lower()
    script = ar.AUDIT_MODES.get(mode) or ar.VIDEO_AUDIT_MODES.get(mode)
    if not script or not script.is_file():
        print(
            f"Unknown audit mode: {mode}. Choose from: {', '.join(ar.ALL_MODES)}",
            file=sys.stderr,
        )
        return 2

    if mode == "video-script":
        if not getattr(args, "script", None):
            print("video-script mode requires --script path", file=sys.stderr)
            return 2
        cmd = [sys.executable, str(script), "--script", str(args.script)]
        return subprocess.call(cmd)

    cmd = [sys.executable, str(script)]
    if mode == "intel":
        if getattr(args, "radar", None):
            cmd.extend(["--radar", str(args.radar)])
    else:
        project = resolve_project(args)
        cmd.extend(["--project", str(project)])
        if getattr(args, "chapter", None):
            cmd.extend(["--chapter", str(args.chapter)])
        if getattr(args, "modes", None) and mode == "deai":
            cmd.extend(["--modes", args.modes])
    if getattr(args, "out", None):
        cmd.extend(["--out", str(args.out)])
    if getattr(args, "json_out", False):
        cmd.append("--json")
    return subprocess.call(cmd)


def cmd_relations_check(args: argparse.Namespace) -> int:
    project = resolve_project(args)
    return subprocess.call(
        [sys.executable, str(SCRIPTS / "validate_relations.py"), "--project", str(project)]
    )


def main() -> int:
    p = argparse.ArgumentParser(prog="novel", description="cursor-novel-writer CLI")
    add_project_arg(p)
    sub = p.add_subparsers(dest="command", required=True)

    i = sub.add_parser("init", help="Scaffold new novel under novels/<slug>/")
    i.add_argument("--title", required=True)
    i.add_argument("--premise", required=True)
    i.add_argument("--genre", default="通用")
    i.add_argument("--slug", default="", help="Optional slug; auto from title if omitted")
    i.add_argument("--platform-target", default="通用", dest="platform_target")
    i.add_argument("--output", type=Path, default=None, help="Override path (default: novels/<slug>/)")
    i.add_argument(
        "--concept",
        type=Path,
        default=None,
        help="Path to concept-brief.md (intel/concepts/...) — copies to canon/ and marks Phase 0",
    )
    i.set_defaults(func=cmd_init)

    sub.add_parser("list", help="List registered novels").set_defaults(func=cmd_list)
    sub.add_parser("active", help="Show active novel slug and path").set_defaults(func=cmd_active)

    u = sub.add_parser("use", help="Set active novel by slug")
    u.add_argument("slug")
    u.set_defaults(func=cmd_use)

    pr = sub.add_parser("promote", help="Promote chapter draft to chapters/")
    add_project_arg(pr)
    pr.add_argument("chapter", help="Filename e.g. 01_试章.md")
    pr.set_defaults(func=cmd_promote)

    e = sub.add_parser("export", help="Export manuscript")
    add_project_arg(e)
    e.add_argument("--format", default="epub", choices=["epub"])
    e.add_argument("--output", type=Path, default=None)
    e.set_defaults(func=cmd_export)

    r = sub.add_parser("review", help="Review chapter consistency")
    add_project_arg(r)
    r.add_argument("--chapter", default=None)
    r.set_defaults(func=cmd_review)

    s = sub.add_parser("status", help="Project + graphify status")
    add_project_arg(s)
    s.set_defaults(func=cmd_status)

    pl = sub.add_parser("pipeline", help="Pipeline progress (novel-pipeline phases)")
    add_project_arg(pl)
    pl_sub = pl.add_subparsers(dest="pipeline_cmd", required=True)
    pl_st = pl_sub.add_parser("status", help="Show task_plan pipeline phase progress")
    add_project_arg(pl_st)
    pl_st.set_defaults(func=cmd_pipeline_status)
    pl_gate = pl_sub.add_parser("gate", help="Schema-backed phase gate (X-07)")
    add_project_arg(pl_gate)
    pl_gate.add_argument("--phase", type=int, default=1, help="Minimum phase to enter (default 1)")
    pl_gate.set_defaults(func=cmd_pipeline_gate)
    pl_val = pl_sub.add_parser("validate", help="Validate canon JSON against schema/")
    add_project_arg(pl_val)
    pl_val.add_argument("--registry", action="store_true", help="Also validate novels/_registry.json")
    pl_val.set_defaults(func=cmd_pipeline_validate)

    intel_p = sub.add_parser("intel", help="Market intelligence paths (P-1)")
    intel_sub = intel_p.add_subparsers(dest="intel_cmd", required=True)
    intel_sub.add_parser("paths", help="Print intel/ and current week radar path").set_defaults(
        func=cmd_intel_paths
    )
    intel_scan = intel_sub.add_parser("scan", help="Run cross-platform short-video trend scan")
    intel_scan.add_argument("--period", choices=["week", "month"], default="week")
    intel_scan.add_argument(
        "--platforms",
        default="douyin,bilibili,kuaishou,xiaohongshu,weibo",
        help="Comma-separated ids: douyin,bilibili,kuaishou,xiaohongshu,weibo",
    )
    intel_scan.add_argument("--max-results", type=int, default=6, dest="max_results")
    intel_scan.add_argument("--timeout", type=float, default=12.0)
    intel_scan.add_argument("--input", type=Path, default=None, help="Optional JSON/NDJSON hit input")
    intel_scan.add_argument(
        "--demo",
        action="store_true",
        help="Offline smoke using intel/fixtures/smoke-hits.json",
    )
    intel_scan.add_argument(
        "--fallback-demo",
        action="store_true",
        dest="fallback_demo",
        help="On zero live hits, load intel/fixtures/smoke-hits.json (network/SSL fallback)",
    )
    intel_scan.add_argument("--radar", type=Path, default=None, help="Custom radar markdown output path")
    intel_scan.add_argument("--concepts-dir", type=Path, default=None, dest="concepts_dir")
    intel_scan.add_argument("--concept-top", type=int, default=3, dest="concept_top")
    intel_scan.add_argument("--no-concepts", action="store_true", dest="no_concepts")
    intel_scan.set_defaults(func=cmd_intel_scan)

    node_p = sub.add_parser("node", help="NEC completion manifest validation")
    node_val = node_p.add_subparsers(dest="node_cmd", required=True)
    node_sync = node_val.add_parser("sync", help="Rebuild phase completion manifest from artifacts")
    add_project_arg(node_sync)
    node_sync.add_argument("--phase", type=int, required=True, help="Pipeline phase 1-9")
    node_sync.set_defaults(func=cmd_node_sync)
    node_v = node_val.add_parser("validate", help="Validate phase completion manifest")
    add_project_arg(node_v)
    node_v.add_argument("--phase", type=int, required=True, help="Pipeline phase 0-9")
    node_v.set_defaults(func=cmd_node_validate)

    g = sub.add_parser("graphify", help="Direct graphify bridge")
    add_project_arg(g)
    g.add_argument("graphify_cmd", choices=["init", "update", "status", "query"])
    g.add_argument("--premise", default="")
    g.add_argument("--from-chapters", action="store_true")
    g.add_argument("--character", default="", help="query: character name or slug")
    g.add_argument("--from-char", default="", dest="from_char", help="query: path from")
    g.add_argument("--to-char", default="", dest="to_char", help="query: path to")
    g.set_defaults(func=cmd_graphify)

    bib = sub.add_parser("bible", help="Story Bible utilities (NM-05)")
    add_project_arg(bib)
    bib_sub = bib.add_subparsers(dest="bible_cmd", required=True)
    bib_sum = bib_sub.add_parser("summary", help="Print aggregated Story Bible markdown")
    add_project_arg(bib_sum)
    bib_sum.add_argument("--output", type=Path, default=None, help="Write to file instead of stdout")
    bib_sum.set_defaults(func=cmd_bible_summary)

    rel = sub.add_parser("relations", help="Character relationship utilities (SS-05)")
    add_project_arg(rel)
    rel_sub = rel.add_subparsers(dest="relations_cmd", required=True)
    rel_chk = rel_sub.add_parser("check", help="Validate bidirectional relationship links")
    add_project_arg(rel_chk)
    rel_chk.set_defaults(func=cmd_relations_check)

    suite_p = sub.add_parser("suite", help="Novel Suite workspace utilities")
    suite_sub = suite_p.add_subparsers(dest="suite_cmd", required=True)
    suite_doc = suite_sub.add_parser("doctor", help="Check suite root, engine, and installed skills")
    suite_doc.add_argument("--json", action="store_true", dest="json_out")
    suite_doc.add_argument(
        "--core-only",
        action="store_true",
        help="Skip IDE skill install dirs (CI)",
    )
    suite_doc.add_argument(
        "--agents",
        default="",
        help="Check skills only for these agents (comma-separated, e.g. trae-cn)",
    )
    suite_doc.set_defaults(func=cmd_suite_doctor)
    suite_gap = suite_sub.add_parser(
        "gap-diff",
        help="Snapshot open items in full-reference-gap-matrix and write monthly diff report",
    )
    suite_gap.add_argument("--month", default="", help="YYYY-MM (default: current UTC month)")
    suite_gap.add_argument("--json", action="store_true", dest="json_out")
    suite_gap.set_defaults(func=cmd_suite_gap_diff)

    w = sub.add_parser("write", help="Print guidance for chapter writing (use IDE skill for generation)")
    add_project_arg(w)
    w.add_argument("--chapter", type=int, required=True)

    def cmd_write(a: argparse.Namespace) -> int:
        print(f"Use skill chapter-writing or Agent to draft chapter {a.chapter}.")
        print(f"Project: {resolve_project(a)}")
        print("Context files: story.md, task_plan.md, plot/foreshadowing.md")
        return 0

    w.set_defaults(func=cmd_write)

    aud = sub.add_parser("audit", help="NEC-11 phase audit/lint scripts")
    aud.add_argument(
        "audit_mode",
        choices=[
            "format",
            "deai",
            "voice",
            "plot",
            "story",
            "canon",
            "blocker",
            "revalidate",
            "export",
            "intel",
            "video-script",
        ],
        help="Audit mode (see skills/novel-review/references/audit-dispatch-index.md)",
    )
    add_project_arg(aud)
    aud.add_argument("--chapter", default=None, help="Chapter path (modes: format, deai, blocker)")
    aud.add_argument("--modes", default="all", help="deai: lexicon,rhetoric,narrative,all")
    aud.add_argument("--out", type=Path, default=None, help="Write JSON scan path")
    aud.add_argument("--json", action="store_true", dest="json_out")
    aud.add_argument("--radar", type=Path, default=None, help="intel mode: radar md path")
    aud.add_argument("--script", type=Path, default=None, help="video-script mode: script.md path")
    aud.set_defaults(func=cmd_audit)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
