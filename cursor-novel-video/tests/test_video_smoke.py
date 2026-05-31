"""Smoke tests for cursor-novel-video."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
SCRIPTS = ENGINE / "scripts"
DEMO_CH = ROOT.parent / "cursor-novel-writer" / "examples" / "demo-novel" / "chapters" / "01_试章.md"

# Import pipeline helpers without running FFmpeg
sys.path.insert(0, str(ENGINE))
import video_cli  # noqa: E402


SAMPLE = """# 第1章

## 一
第一句。

## 二
第二句。
"""


def test_split_scenes():
    scenes = video_cli.split_scenes(SAMPLE)
    assert len(scenes) == 2
    assert "第一句" in scenes[0]


def test_summarize_chapter():
    text = video_cli.summarize_chapter(SAMPLE, max_chars=50)
    assert len(text) <= 50


def test_create_job_storyboard(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(video_cli, "DEFAULT_JOBS", tmp_path / "jobs")
    ch = tmp_path / "ch.md"
    ch.write_text(SAMPLE, encoding="utf-8")
    job = video_cli.create_job("drama", ch, "9:16")
    sb = json.loads((job / "storyboard.json").read_text(encoding="utf-8"))
    assert sb["mode"] == "drama"
    assert len(sb["scenes"]) >= 2


def test_beat_lock_split_sentences():
    sys.path.insert(0, str(SCRIPTS))
    import beat_lock  # noqa: E402

    parts = beat_lock.split_sentences("第一句。第二句！")
    assert len(parts) == 2


@pytest.mark.ffmpeg
def test_drama_pipeline_e2e():
    if not shutil.which("ffmpeg"):
        pytest.skip("ffmpeg not available")
    if not DEMO_CH.is_file():
        pytest.skip("demo chapter missing")
    r = subprocess.run(
        [sys.executable, str(ENGINE / "video_cli.py"), "drama", "--chapter", str(DEMO_CH)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        timeout=180,
    )
    assert r.returncode == 0, r.stderr
    assert "OK:" in r.stdout
