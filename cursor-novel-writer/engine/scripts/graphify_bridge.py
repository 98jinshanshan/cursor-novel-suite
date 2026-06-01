#!/usr/bin/env python3
"""Bridge to safishamsi/graphify (graphifyy) + graphify-novel skill workflows."""

from __future__ import annotations

import argparse
import glob
import json
import shutil
import subprocess
import sys
from pathlib import Path


def graphify_base() -> list[str] | None:
    """Resolve graphify CLI: py -m graphify (preferred) or graphify on PATH."""
    try:
        subprocess.run(
            [sys.executable, "-m", "graphify"],
            capture_output=True,
            timeout=5,
        )
        return [sys.executable, "-m", "graphify"]
    except (OSError, subprocess.TimeoutExpired):
        pass
    if shutil.which("graphify"):
        return ["graphify"]
    return None


def run_graphify(args: list[str], project: Path) -> int | None:
    base = graphify_base()
    if not base:
        return None
    cmd = base + args
    print(f"Running: {' '.join(cmd)}")
    try:
        return subprocess.call(cmd, cwd=str(project))
    except OSError as exc:
        print(f"WARN: graphify CLI failed ({exc}); using offline fallback.", file=sys.stderr)
        return None


def scaffold_bible(project: Path, premise: str) -> None:
    bible = project / "bible"
    (bible / "characters").mkdir(parents=True, exist_ok=True)
    (bible / "threads").mkdir(parents=True, exist_ok=True)
    (bible / "world").mkdir(parents=True, exist_ok=True)
    premise_path = bible / "premise.md"
    if not premise_path.exists():
        premise_path.write_text(f"# Premise\n\n{premise}\n", encoding="utf-8")
    for name, content in [
        ("characters/_index.md", "# Characters\n\n| slug | name | status |\n| --- | --- | --- |\n"),
        ("threads/_index.md", "# Threads\n\n| slug | name | status |\n| --- | --- | --- |\n"),
        ("world/_index.md", "# World\n\n"),
        ("timeline.md", "# Timeline\n\n"),
    ]:
        path = bible / name
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    ignore = project / ".graphifyignore"
    if not ignore.exists():
        ignore.write_text(
            "graphify-out/\ndraft/\nstatic/\nbible/characters/\nbible/threads/\nbible/timeline.md\n",
            encoding="utf-8",
        )


def cmd_init(project: Path, premise: str) -> int:
    project.mkdir(parents=True, exist_ok=True)
    (project / "graphify-out").mkdir(exist_ok=True)
    scaffold_bible(project, premise)
    meta = {"premise": premise, "graphify": "bible-scaffold"}
    (project / "graphify-out" / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"OK: bible scaffold at {project / 'bible'} (graphify-novel layout)")
    print("Tip: run `update --from-chapters` to build graphify-out/graph.json")
    return 0


def cmd_review(project: Path, chapter: Path) -> int:
    if not chapter.exists():
        print(f"ERROR: chapter not found: {chapter}", file=sys.stderr)
        return 1
    rel = str(chapter.relative_to(project))
    graph = project / "graphify-out" / "graph.json"
    if graph.exists() and graphify_base():
        q = f"consistency issues and character relationships in {rel}"
        rc = run_graphify(["query", q, "--budget", "1200"], project)
        if rc is not None and rc == 0:
            print("For full review workflow use skill novel-review + graphify-novel review.")
            return 0
    print(f"Offline review stub for {chapter.name}.")
    print("Install: pip install graphifyy — then update --from-chapters, or use novel-review skill.")
    return 2


def cmd_update(project: Path, from_chapters: bool) -> int:
    _ = from_chapters  # graphify update scans project tree
    if graphify_base():
        rc = run_graphify(["update", str(project.resolve())], project)
        if rc is not None and rc == 0:
            return 0
    chapters = sorted(glob.glob(str(project / "chapters" / "*.md")))
    out = project / "graphify-out" / "chapter_index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"chapters": chapters}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Offline: indexed {len(chapters)} chapters -> {out}")
    return 0


def cmd_status(project: Path) -> int:
    report = project / "graphify-out" / "GRAPH_REPORT.md"
    graph = project / "graphify-out" / "graph.json"
    if graph.exists():
        if report.exists():
            text = report.read_text(encoding="utf-8")
            print(text[:2000] + ("..." if len(text) > 2000 else ""))
        else:
            data = json.loads(graph.read_text(encoding="utf-8"))
            nodes = len(data.get("nodes", []))
            edges = len(data.get("edges", []))
            print(f"graphify-out/graph.json: {nodes} nodes, {edges} edges")
        return 0
    meta = project / "graphify-out" / "meta.json"
    if meta.exists():
        print(meta.read_text(encoding="utf-8"))
    else:
        print("No graph yet. Run: graphify_bridge.py init --premise '...' then update --from-chapters")
    return 0


def cmd_query(project: Path, **kwargs) -> int:
    if not graphify_base():
        print("Offline: install graphifyy — pip install graphifyy", file=sys.stderr)
        return 2
    graph = project / "graphify-out" / "graph.json"
    if not graph.exists():
        print("ERROR: no graphify-out/graph.json — run update --from-chapters first", file=sys.stderr)
        return 1
    if kwargs.get("from_char") and kwargs.get("to_char"):
        return run_graphify(["path", kwargs["from_char"], kwargs["to_char"]], project) or 1
    if kwargs.get("character"):
        q = f"{kwargs['character']} relationships and story connections"
        return run_graphify(["query", q, "--budget", "1200"], project) or 1
    print("ERROR: query requires --character or --from/--to", file=sys.stderr)
    return 1


def add_project_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--project",
        type=Path,
        default=None,
        help="Novel project directory (default: current directory)",
    )


def extract_global_project(argv: list[str]) -> tuple[Path | None, list[str]]:
    """Pull --project from anywhere in argv so it works before or after subcommand."""
    project: Path | None = None
    rest: list[str] = []
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok == "--project" and i + 1 < len(argv):
            project = Path(argv[i + 1])
            i += 2
            continue
        if tok.startswith("--project="):
            project = Path(tok.split("=", 1)[1])
            i += 1
            continue
        rest.append(tok)
        i += 1
    return project, rest


def resolve_project(args: argparse.Namespace, global_project: Path | None = None) -> Path:
    proj = getattr(args, "project", None) or global_project
    return (proj or Path(".")).resolve()


def build_parser() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    add_project_arg(parent)

    p = argparse.ArgumentParser(description="Graphify bridge for cursor-novel-writer")
    sub = p.add_subparsers(dest="command", required=True)

    i = sub.add_parser("init", parents=[parent])
    i.add_argument("--premise", required=True)

    r = sub.add_parser("review", parents=[parent])
    r.add_argument("--chapter", type=Path, required=True)

    u = sub.add_parser("update", parents=[parent])
    u.add_argument("--from-chapters", action="store_true")

    sub.add_parser("status", parents=[parent])

    q = sub.add_parser("query", parents=[parent])
    q.add_argument("--character")
    q.add_argument("--from", dest="from_char")
    q.add_argument("--to", dest="to_char")

    return p


def main() -> int:
    global_project, rest = extract_global_project(sys.argv[1:])
    args = build_parser().parse_args(rest)
    project = resolve_project(args, global_project)

    if args.command == "init":
        return cmd_init(project, args.premise)
    if args.command == "review":
        ch = args.chapter
        if not ch.is_absolute():
            ch = project / ch
        return cmd_review(project, ch)
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
