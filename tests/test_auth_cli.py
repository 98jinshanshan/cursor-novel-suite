"""Tests for auth CLI handlers (Sprint 4 Phase A)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import pytest

from novel_suite.core import errors as E
from novel_suite.auth.cli import cmd_auth_login, cmd_auth_logout, cmd_auth_status

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture
def token_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("NOVEL_SUITE_TOKEN_DIR", str(tmp_path))
    monkeypatch.setenv("NOVEL_SUITE_TOKEN_KEY", "pytest-secret-key")
    return tmp_path


def test_auth_login_fanqie(token_dir: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("FANQIE_API_KEY", "fanqie-test-key")
    result = cmd_auth_login(argparse.Namespace(platform="fanqie", json=True))
    assert result.status == "ok"
    assert result.code == E.AUTH_LOGIN_OK


def test_auth_login_kuaishou_missing_client(token_dir: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("KUAISHOU_CLIENT_ID", raising=False)
    result = cmd_auth_login(argparse.Namespace(platform="kuaishou", json=True))
    assert result.status == "error"
    assert result.code == E.AUTH_LOGIN_FAILED


def test_auth_login_bilibili_missing_client(token_dir: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("BILIBILI_CLIENT_ID", raising=False)
    result = cmd_auth_login(argparse.Namespace(platform="bilibili", json=True))
    assert result.status == "error"
    assert result.code == E.AUTH_LOGIN_FAILED


def test_auth_login_unknown_platform():
    result = cmd_auth_login(argparse.Namespace(platform="notaplatform", json=True))
    assert result.status == "error"
    assert result.code == E.PLATFORM_UNKNOWN


def test_auth_logout(token_dir: Path):
    from novel_suite.auth.token_store import save_token

    save_token("douyin", {"access_token": "x"})
    result = cmd_auth_logout(argparse.Namespace(platform="douyin", json=True))
    assert result.status == "ok"
    assert result.code == E.AUTH_LOGOUT_OK


def test_auth_status_all(token_dir: Path):
    result = cmd_auth_status(argparse.Namespace(platform=None, json=True))
    assert result.status == "ok"
    assert result.code == E.AUTH_STATUS_OK
    assert len(result.details["statuses"]) == 6


def test_auth_help():
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(REPO)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "auth", "--help"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr
    assert "login" in r.stdout
    assert "logout" in r.stdout
    assert "status" in r.stdout
