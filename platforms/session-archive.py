#!/usr/bin/env python3
"""Workspace-local session archive on preCompact/sessionEnd + JSONL ingest helpers."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

USER_QUERY_RE = re.compile(r"<user_query>\s*(.*?)\s*</user_query>", re.DOTALL | re.IGNORECASE)
LEDGER_NAME = "session-ledger.jsonl"
ARCHIVES_DIR = Path("docs/audit/session-archives")
FALLBACK_ROOT = Path.home() / ".cursor" / "fallback-session-archives"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_stdin_json() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def pick_workspace(roots: list[str]) -> Path | None:
    if not roots:
        return None
    paths = [Path(r).resolve() for r in roots if r]
    if not paths:
        return None

    def score(p: Path) -> tuple[int, int]:
        s = 0
        if (p / ".novel-suite-root").is_file():
            s += 100
        if (p / ".git").exists():
            s += 50
        if (p / "docs" / "audit").is_dir():
            s += 40
        if (p / "docs").is_dir():
            s += 10
        return (s, -len(str(p)))

    return max(paths, key=score)


def audit_base(workspace: Path | None) -> Path:
    if workspace is None:
        base = FALLBACK_ROOT
        base.mkdir(parents=True, exist_ok=True)
        return base
    if (workspace / "docs" / "audit").is_dir():
        return workspace / "docs" / "audit"
    audit = workspace / "docs" / "audit"
    audit.mkdir(parents=True, exist_ok=True)
    return audit


def archive_folder_name(payload: dict) -> str:
    trigger = payload.get("trigger", "compact")
    msgs = payload.get("messages_to_compact", payload.get("message_count", 0))
    return f"{utc_stamp()}_{trigger}_msgs{msgs}"


def resolve_transcript(payload: dict) -> Path | None:
    tp = payload.get("transcript_path") or ""
    if tp:
        p = Path(tp)
        if p.is_file():
            return p
    env_tp = __import__("os").environ.get("CURSOR_TRANSCRIPT_PATH", "")
    if env_tp:
        p = Path(env_tp)
        if p.is_file():
            return p
    return None


def copy_archive(payload: dict, *, event: str) -> dict:
    workspace = pick_workspace(payload.get("workspace_roots") or [])
    conv = payload.get("conversation_id") or "unknown-conversation"
    transcript = resolve_transcript(payload)

    audit = audit_base(workspace)
    folder_name = archive_folder_name(payload)
    dest_dir = audit / "session-archives" / conv / folder_name
    dest_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "archived_at": iso_now(),
        "hook_event": event,
        "conversation_id": conv,
        "archive_folder": str(dest_dir),
        "archive_folder_name": folder_name,
        "workspace_root": str(workspace) if workspace else None,
        "transcript_path_source": str(transcript) if transcript else None,
        "trigger": payload.get("trigger"),
        "context_usage_percent": payload.get("context_usage_percent"),
        "context_tokens": payload.get("context_tokens"),
        "context_window_size": payload.get("context_window_size"),
        "message_count": payload.get("message_count"),
        "messages_to_compact": payload.get("messages_to_compact"),
        "is_first_compaction": payload.get("is_first_compaction"),
        "cursor_version": payload.get("cursor_version"),
        "ingest_status": "pending",
    }
    (dest_dir / "compact-meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if transcript:
        shutil.copy2(transcript, dest_dir / "transcript.jsonl")
        meta["transcript_copied"] = True
    else:
        meta["transcript_copied"] = False
        (dest_dir / "transcript-missing.txt").write_text(
            "transcript_path was null or file missing\n",
            encoding="utf-8",
        )

    ledger_path = audit / LEDGER_NAME
    ledger_row = {
        "ts": meta["archived_at"],
        "event": event,
        "conversation_id": conv,
        "archive_rel": str(dest_dir.relative_to(audit)).replace("\\", "/")
        if workspace
        else str(dest_dir),
        "archive_folder_name": folder_name,
        "workspace_root": meta["workspace_root"],
        "messages_to_compact": meta.get("messages_to_compact"),
        "trigger": meta.get("trigger"),
        "ingest": "pending",
        "transcript_copied": meta["transcript_copied"],
    }
    with ledger_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ledger_row, ensure_ascii=False) + "\n")

    return meta


def extract_user_messages(transcript_path: Path) -> list[dict]:
    rows: list[dict] = []
    u_idx = 0
    for line in transcript_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("role") != "user":
            continue
        u_idx += 1
        text = ""
        msg = obj.get("message") or {}
        for block in msg.get("content") or []:
            if block.get("type") == "text":
                text += block.get("text") or ""
        m = USER_QUERY_RE.search(text)
        body = (m.group(1) if m else text).strip()
        if not body:
            continue
        rows.append({"u": u_idx, "text": body[:2000]})
    return rows


def cmd_ingest_archive(archive_dir: Path) -> int:
    meta_path = archive_dir / "compact-meta.json"
    if not meta_path.is_file():
        print(f"ERROR: missing {meta_path}", file=sys.stderr)
        return 1
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    transcript = archive_dir / "transcript.jsonl"
    if not transcript.is_file():
        print(f"WARN: no transcript in {archive_dir}", file=sys.stderr)
        meta["ingest_status"] = "no_transcript"
    else:
        queries = extract_user_messages(transcript)
        out = archive_dir / "user-queries.json"
        out.write_text(json.dumps(queries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        meta["ingest_status"] = "extracted"
        meta["user_message_count"] = len(queries)
        print(f"OK: extracted {len(queries)} user messages -> {out}")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


def cmd_ingest_pending(audit_dir: Path) -> int:
    archives_root = audit_dir / "session-archives"
    if not archives_root.is_dir():
        print("OK: no session-archives yet")
        return 0
    n = 0
    for meta_file in sorted(archives_root.glob("*/*/compact-meta.json")):
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        if meta.get("ingest_status") in ("extracted", "ingested"):
            continue
        if cmd_ingest_archive(meta_file.parent) == 0:
            n += 1
    print(f"OK: ingested {n} archive(s)")
    return 0


def scan_agent_transcripts(projects_root: Path, *, ingest: bool) -> int:
    if not projects_root.is_dir():
        print(f"ERROR: missing {projects_root}", file=sys.stderr)
        return 1
    count = 0
    for jsonl in projects_root.glob("*/agent-transcripts/*/*.jsonl"):
        if "subagents" in jsonl.parts:
            continue
        count += 1
        print(f"FOUND: {jsonl}")
    print(f"OK: scanned {count} parent transcript(s) (use hook-archive on active chats for workspace-local copies)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Session archive + ingest for Cursor preCompact")
    sub = ap.add_subparsers(dest="cmd", required=True)

    hook = sub.add_parser("hook", help="Read hook JSON from stdin and archive to workspace docs/audit")
    hook.add_argument("--event", default="preCompact")

    ing = sub.add_parser("ingest", help="Extract user-queries.json from one archive folder")
    ing.add_argument("archive_dir", type=Path)

    pend = sub.add_parser("ingest-pending", help="Ingest all pending archives under docs/audit")
    pend.add_argument("--workspace", type=Path, default=None)

    scan = sub.add_parser("scan-transcripts", help="List IDE agent-transcripts (discovery)")
    scan.add_argument(
        "--projects-root",
        type=Path,
        default=Path.home() / ".cursor" / "projects",
    )
    scan.add_argument("--ingest", action="store_true")

    args = ap.parse_args()

    if args.cmd == "hook":
        payload = read_stdin_json()
        if not payload:
            print("WARN: empty stdin", file=sys.stderr)
            return 0
        meta = copy_archive(payload, event=args.event)
        print(json.dumps({"ok": True, "archive_folder": meta["archive_folder"]}, ensure_ascii=False))
        return 0

    if args.cmd == "ingest":
        return cmd_ingest_archive(args.archive_dir.resolve())

    if args.cmd == "ingest-pending":
        ws = args.workspace or Path.cwd()
        audit = audit_base(ws.resolve() if ws else None)
        return cmd_ingest_pending(audit)

    if args.cmd == "scan-transcripts":
        return scan_agent_transcripts(args.projects_root, ingest=args.ingest)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
