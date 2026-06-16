"""Tests for auth token store (Sprint 4 Phase A)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from novel_suite.auth.token_store import (
    delete_token,
    load_token,
    save_token,
    token_status,
    tokens_dir,
)


@pytest.fixture
def token_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("NOVEL_SUITE_TOKEN_DIR", str(tmp_path))
    monkeypatch.setenv("NOVEL_SUITE_TOKEN_KEY", "pytest-secret-key")
    return tmp_path


def test_save_and_load_token(token_dir: Path):
    path = save_token("douyin", {"access_token": "abc", "expires_at": "2099-01-01T00:00:00Z"})
    assert path.is_file()
    loaded = load_token("douyin")
    assert loaded is not None
    assert loaded["access_token"] == "abc"


def test_token_encrypted_on_disk(token_dir: Path):
    save_token("douyin", {"access_token": "secret"})
    raw = json.loads((token_dir / "douyin.json").read_text(encoding="utf-8"))
    assert "ciphertext" in raw
    assert "secret" not in json.dumps(raw)


def test_delete_token(token_dir: Path):
    save_token("douyin", {"access_token": "x"})
    delete_token("douyin")
    assert load_token("douyin") is None


def test_token_expired_by_saved_at(token_dir: Path):
    save_token("douyin", {"access_token": "old"})
    path = token_dir / "douyin.json"
    envelope = json.loads(path.read_text(encoding="utf-8"))
    from novel_suite.auth import token_store as ts

    payload = ts._decrypt_payload(envelope)
    assert payload is not None
    old = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    payload["saved_at"] = old
    path.write_text(json.dumps(ts._encrypt_payload(payload), ensure_ascii=False), encoding="utf-8")
    assert load_token("douyin") is None


def test_token_status_missing(token_dir: Path):
    status = token_status("kuaishou")
    assert status["valid"] is False
    assert status["reason"] == "not_found_or_expired"


def test_token_file_permissions(token_dir: Path):
    save_token("douyin", {"access_token": "x"})
    if sys.platform == "win32":
        pytest.skip("Unix file mode 600 not enforced on Windows")
    import stat

    mode = (token_dir / "douyin.json").stat().st_mode
    assert stat.S_IMODE(mode) == 0o600
