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

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT.parent / "templates"
SCRIPTS = ROOT / "scripts"


def resolve_project(args: argparse.Namespace) -> Path:
    return (getattr(args, "project", None) or Path(".")).resolve()


def add_project_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--project",
        type=Path,
        default=None,
        help="Novel project directory (default: current directory)",
    )


def scaffold_project(output: Path, title: str, premise: str, genre: str = "通用") -> None:
    output.mkdir(parents=True, exist_ok=True)
    dirs = [
        "canon",
        "characters",
        "worldbuilding/locations",
        "worldbuilding/systems",
        "plot/arcs",
        "chapters",
        "reviews",
        "dist",
        "graphify-out",
        "bible",
    ]
    for d in dirs:
        (output / d).mkdir(parents=True, exist_ok=True)

    story = TEMPLATES / "story.md"
    if story.exists():
        content = story.read_text(encoding="utf-8")
        content = content.replace("example-novel", output.name.replace(" ", "-").lower())
        content = content.replace("雾港来信", title)
        content = content.replace("一封没有寄件人的信，把档案员拉回十年前的失踪案。", premise)
        content = content.replace("悬疑", genre)
        (output / "story.md").write_text(content, encoding="utf-8")
    else:
        (output / "story.md").write_text(f"# {title}\n\n{premise}\n", encoding="utf-8")

    for name, dest in [
        ("task_plan.md", "task_plan.md"),
        ("characters_index.md", "characters/_index.md"),
        ("chapters_index.md", "chapters/_index.md"),
    ]:
        src = TEMPLATES / name
        if src.exists():
            shutil.copy(src, output / dest)

    (output / "worldbuilding/_index.md").write_text("# 世界观索引\n\n", encoding="utf-8")
    (output / "plot/_index.md").write_text("# 情节索引\n\n", encoding="utf-8")
    (output / "plot/timeline.md").write_text("# 时间线\n\n", encoding="utf-8")
    (output / "plot/foreshadowing.md").write_text(
        "# 伏笔矩阵\n\n| 元素 | 埋设章 | 发展 | 回收 | 状态 |\n|------|--------|------|------|------|\n",
        encoding="utf-8",
    )

    progress = {
        "title": title,
        "author": "",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "chapters": [],
        "total_words": 0,
    }
    (output / "canon/progress.json").write_text(
        json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8"
    )

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
    print(f"Initialized: {output}")


def cmd_init(args: argparse.Namespace) -> int:
    scaffold_project(args.output.resolve(), args.title, args.premise, args.genre)
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    project = resolve_project(args)
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
    return subprocess.call(cmd)


def main() -> int:
    p = argparse.ArgumentParser(prog="novel", description="cursor-novel-writer CLI")
    add_project_arg(p)
    sub = p.add_subparsers(dest="command", required=True)

    i = sub.add_parser("init", help="Scaffold new novel project")
    i.add_argument("--title", required=True)
    i.add_argument("--premise", required=True)
    i.add_argument("--genre", default="通用")
    i.add_argument("--output", type=Path, default=Path("./my-novel"))
    i.set_defaults(func=cmd_init)

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

    g = sub.add_parser("graphify", help="Direct graphify bridge")
    add_project_arg(g)
    g.add_argument("graphify_cmd", choices=["init", "update", "status"])
    g.add_argument("--premise", default="")
    g.add_argument("--from-chapters", action="store_true")
    g.set_defaults(func=cmd_graphify)

    w = sub.add_parser("write", help="Print guidance for chapter writing (use IDE skill for generation)")
    add_project_arg(w)
    w.add_argument("--chapter", type=int, required=True)

    def cmd_write(a: argparse.Namespace) -> int:
        print(f"Use skill chapter-writing or Agent to draft chapter {a.chapter}.")
        print(f"Project: {resolve_project(a)}")
        print("Context files: story.md, task_plan.md, plot/foreshadowing.md")
        return 0

    w.set_defaults(func=cmd_write)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
