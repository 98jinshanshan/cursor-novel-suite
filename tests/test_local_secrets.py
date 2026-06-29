"""Tests for local secret storage (no real keys in repo)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cursor-novel-video" / "adapters"))

from local_secrets import assert_local_workstation  # noqa: E402


def test_forbidden_fingerprint_file_has_no_raw_keys():
    fp = ROOT / "platforms" / "secret-fingerprints.json"
    data = json.loads(fp.read_text(encoding="utf-8"))
    blob = json.dumps(data)
    assert "sk-" not in blob
    assert len(data["forbidden_sha256"]) >= 1
    for entry in data["forbidden_sha256"]:
        assert len(entry["sha256"]) == 64


def test_forbidden_fingerprint_is_valid_sha256():
    fp = json.loads((ROOT / "platforms" / "secret-fingerprints.json").read_text(encoding="utf-8"))
    for entry in fp["forbidden_sha256"]:
        assert entry["id"]
        assert len(entry["sha256"]) == 64
        int(entry["sha256"], 16)  # valid hex


def test_assert_local_workstation_blocks_ci(monkeypatch):
    monkeypatch.setenv("CI", "true")
    try:
        assert_local_workstation()
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "CI" in str(exc)
