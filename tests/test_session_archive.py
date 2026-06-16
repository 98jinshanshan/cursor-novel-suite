"""Tests for platforms/session-archive.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "session_archive",
    ROOT / "platforms" / "session-archive.py",
)
assert _spec and _spec.loader
sa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sa)


SAMPLE_TRANSCRIPT = "\n".join(
    [
        json.dumps(
            {
                "role": "user",
                "message": {"content": [{"type": "text", "text": "<user_query>\n测试问题 A\n</user_query>"}]},
            },
            ensure_ascii=False,
        ),
        json.dumps(
            {
                "role": "assistant",
                "message": {"content": [{"type": "text", "text": "ok"}]},
            }
        ),
        json.dumps(
            {
                "role": "user",
                "message": {"content": [{"type": "text", "text": "<user_query>\n测试问题 B\n</user_query>"}]},
            },
            ensure_ascii=False,
        ),
    ]
)


def test_pick_workspace_prefers_novel_suite_root(tmp_path: Path):
    plain = tmp_path / "plain"
    suite = tmp_path / "suite"
    plain.mkdir()
    suite.mkdir()
    (suite / ".novel-suite-root").write_text("{}", encoding="utf-8")
    picked = sa.pick_workspace([str(plain), str(suite)])
    assert picked == suite.resolve()


def test_extract_user_messages(tmp_path: Path):
    p = tmp_path / "t.jsonl"
    p.write_text(SAMPLE_TRANSCRIPT, encoding="utf-8")
    rows = sa.extract_user_messages(p)
    assert len(rows) == 2
    assert rows[0]["u"] == 1
    assert "测试问题 A" in rows[0]["text"]


def test_copy_archive_workspace_local(tmp_path: Path):
    ws = tmp_path / "proj"
    ws.mkdir()
    (ws / "docs" / "audit").mkdir(parents=True)
    tr = tmp_path / "conv.jsonl"
    tr.write_text(SAMPLE_TRANSCRIPT, encoding="utf-8")
    payload = {
        "conversation_id": "test-conv-uuid",
        "workspace_roots": [str(ws)],
        "transcript_path": str(tr),
        "trigger": "auto",
        "messages_to_compact": 5,
    }
    meta = sa.copy_archive(payload, event="preCompact")
    assert "session-archives" in meta["archive_folder"]
    assert (Path(meta["archive_folder"]) / "transcript.jsonl").is_file()
    ledger = ws / "docs" / "audit" / "session-ledger.jsonl"
    assert ledger.is_file()
    line = json.loads(ledger.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert line["conversation_id"] == "test-conv-uuid"
    assert line["ingest"] == "pending"
