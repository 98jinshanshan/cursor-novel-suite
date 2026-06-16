"""Tests for novel publish module (Sprint 5 Day 1)."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from novel_suite.auth.token_store import save_token
from novel_suite.core import errors as E
from novel_suite.novel.publish.cli import cmd_novel_publish_list, cmd_novel_publish_upload
from novel_suite.novel.publish.fanqie import (
    _load_chapters,
    fanqie_publish_all,
    fanqie_publish_chapter,
)

REPO = Path(__file__).resolve().parents[2]


def test_get_target_platform_default(tmp_path: Path):
    from novel_suite.novel.publish.project_config import get_target_platform

    assert get_target_platform(tmp_path) == "通用"


def test_get_target_platform_reads_json(tmp_path: Path):
    from novel_suite.novel.publish.project_config import get_platform_config, get_target_platform

    canon = tmp_path / "canon"
    canon.mkdir(parents=True)
    (canon / "project.json").write_text('{"platform_target": "fanqie"}', encoding="utf-8")
    assert get_target_platform(tmp_path) == "fanqie"
    cfg = get_platform_config(tmp_path)
    assert cfg["found"] is True
    assert cfg["config"]["key"] == "fanqie"


def test_load_chapters_empty_dir(tmp_path: Path):
    assert _load_chapters(tmp_path) == []


def test_fanqie_publish_all_no_api_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("novel_suite.novel.publish.fanqie._get_api_key", lambda: None)
    result = fanqie_publish_all(tmp_path)
    assert not result["ok"]
    assert "api key" in result["error"].lower()


def test_fanqie_publish_chapter_stub(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("FANQIE_API_KEY", "test_key_stub")
    save_token(
        "fanqie",
        {
            "auth_type": "api_key",
            "api_key": "test_key_stub",
            "expires_at": "2099-01-01T00:00:00+00:00",
        },
    )
    result = fanqie_publish_chapter("novel_001", 1, "第一章", "测试内容")
    assert result["ok"]
    assert result["chapter_number"] == 1
    assert "Stub" in result["note"]


def test_fanqie_publish_all_with_chapters(demo_project: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("FANQIE_API_KEY", "test_key_all")
    save_token(
        "fanqie",
        {
            "auth_type": "api_key",
            "api_key": "test_key_all",
            "expires_at": "2099-01-01T00:00:00+00:00",
        },
    )
    result = fanqie_publish_all(demo_project)
    assert result["ok"]
    assert result["published_count"] >= 1
    assert result["total"] >= 1


def test_cmd_novel_publish_upload_no_api_key(novels_scratch: Path):
    args = argparse.Namespace(project=novels_scratch, platform="fanqie", json=True)
    result = cmd_novel_publish_upload(args)
    assert result.status == "error"
    assert result.code == E.PUBLISH_FAILED


def test_cmd_novel_publish_list_empty(novels_scratch: Path):
    args = argparse.Namespace(project=novels_scratch, json=True)
    result = cmd_novel_publish_list(args)
    assert result.status == "ok"
    assert result.code == E.PUBLISH_LIST_OK
    assert result.details.get("summary", {}).get("total") == 0


def test_publish_qidian_stub(demo_project: Path):
    args = argparse.Namespace(project=demo_project, platform="qidian", json=True)
    result = cmd_novel_publish_upload(args)
    assert result.status == "ok"
    assert result.details["publish_result"]["platform"] == "qidian"


def test_publish_jinjiang_stub(demo_project: Path):
    args = argparse.Namespace(project=demo_project, platform="jinjiang", json=True)
    result = cmd_novel_publish_upload(args)
    assert result.status == "ok"
    assert result.details["publish_result"]["platform"] == "jinjiang"


def test_novel_publish_upload_help():
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(REPO)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "novel", "publish", "upload", "--help"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr
    assert "--platform" in r.stdout
    assert "fanqie" in r.stdout
    assert "qidian" in r.stdout


def test_novel_publish_list_help():
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(REPO)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "novel", "publish", "list", "--help"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr
    assert "--project" in r.stdout


def test_novel_publish_upload_json(demo_project: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("FANQIE_API_KEY", "test_key_json")
    save_token(
        "fanqie",
        {
            "auth_type": "api_key",
            "api_key": "test_key_json",
            "expires_at": "2099-01-01T00:00:00+00:00",
        },
    )
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(REPO)}
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "novel_suite.cli",
            "novel",
            "publish",
            "upload",
            "--project",
            str(demo_project),
            "--platform",
            "fanqie",
            "--json",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    assert payload["status"] == "ok"
    assert payload["code"] == E.PUBLISH_OK
