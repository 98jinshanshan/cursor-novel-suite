#!/usr/bin/env python3
"""Bridge to graphify / graphify-novel CLI for canon consistency."""

from __future__ import annotations

import argparse
import glob
import json
import shutil
import subprocess
import sys
from pathlib import Path


def find_graphify() -> list[str] | None:
    for cmd in (["graphify-novel"], ["graphify"], ["npx", "graphify-novel"]):
        if shutil.which(cmd[0]):
            return cmd
    return None


def run_graphify(args: list[str], project: Path) -> int | None:
    base = find_graphify()
    if not base:
        return None
    cmd = base + args
    print(f"Running: {' '.join(cmd)}")
    try:
        return subprocess.call(cmd, cwd=str(project))
    except OSError as exc:
        print(f"WARN: graphify CLI failed ({exc}); using offline fallback.", file=sys.stderr)
        return None


def cmd_init(project: Path, premise: str) -> int:
    project.mkdir(parents=True, exist_ok=True)
    (project / "graphify-out").mkdir(exist_ok=True)
    rc = run_graphify(["init", premise], project)
    if rc is not None and rc == 0:
        return 0
    # Fallback: write minimal bible scaffold
    bible = project / "bible"
    bible.mkdir(exist_ok=True)
    (bible / "premise.md").write_text(f"# Premise\n\n{premise}\n", encoding="utf-8")
    meta = {"premise": premise, "graphify": "offline-fallback"}
    (project / "graphify-out" / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("WARN: graphify not installed; created offline fallback in bible/ and graphify-out/")
    return 0


def cmd_review(project: Path, chapter: Path) -> int:
    if not chapter.exists():
        print(f"ERROR: chapter not found: {chapter}", file=sys.stderr)
        return 1
    rc = run_graphify(["review", str(chapter.relative_to(project))], project)
    if rc is not None and rc == 0:
        return 0
    print(f"Offline review stub for {chapter.name} — install graphify for full graph review.")
    return 0


def cmd_update(project: Path, from_chapters: bool) -> int:
    args = ["update", "--from-chapters"] if from_chapters else ["update"]
    rc = run_graphify(args, project)
    if rc is not None and rc == 0:
        return 0
    chapters = sorted(glob.glob(str(project / "chapters" / "*.md")))
    out = project / "graphify-out" / "chapter_index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"chapters": chapters}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Offline: indexed {len(chapters)} chapters -> {out}")
    return 0


def cmd_status(project: Path) -> int:
    rc = run_graphify(["status"], project)
    if rc is not None and rc == 0:
        return 0
    meta = project / "graphify-out" / "meta.json"
    if meta.exists():
        print(meta.read_text(encoding="utf-8"))
    else:
        print("No graphify-out metadata. Run init first.")
    return 0


def cmd_query(project: Path, **kwargs) -> int:
    args = ["query"]
    if kwargs.get("character"):
        args.extend(["--character", kwargs["character"]])
    if kwargs.get("from_char") and kwargs.get("to_char"):
        args.extend(["--from", kwargs["from_char"], "--to", kwargs["to_char"]])
    rc = run_graphify(args, project)
    if rc is not None:
        return rc
    print("Offline: graphify query unavailable.", file=sys.stderr)
    return 2


def add_project_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--project",
        type=Path,
        default=None,
        help="Novel project directory (default: current directory)",
    )


def resolve_project(args: argparse.Namespace) -> Path:
    return (getattr(args, "project", None) or Path(".")).resolve()


def main() -> int:
    p = argparse.ArgumentParser(description="Graphify bridge for cursor-novel-writer")
    add_project_arg(p)
    sub = p.add_subparsers(dest="command", required=True)

    i = sub.add_parser("init")
    add_project_arg(i)
    i.add_argument("--premise", required=True)

    r = sub.add_parser("review")
    add_project_arg(r)
    r.add_argument("--chapter", type=Path, required=True)

    u = sub.add_parser("update")
    add_project_arg(u)
    u.add_argument("--from-chapters", action="store_true")

    st = sub.add_parser("status")
    add_project_arg(st)

    q = sub.add_parser("query")
    add_project_arg(q)
    q.add_argument("--character")
    q.add_argument("--from", dest="from_char")
    q.add_argument("--to", dest="to_char")

    args = p.parse_args()
    project = resolve_project(args)

    if args.command == "init":
        return cmd_init(project, args.premise)
    if args.command == "review":
        return cmd_review(project, args.chapter)
    if args.command == "update":
        return cmd_update(project, args.from_chapters)
    if args.command == "status":
        return cmd_status(project)
    if args.command == "query":
        return cmd_query(
            project,
            character=args.character,
            from_char=args.from_char,
            to_char=args.to_char,
        )
    return 1


if __name__ == "__main__":
    sys.exit(main())
