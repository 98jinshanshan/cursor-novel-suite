"""Tests for platform publish gate and storyboard."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "engine" / "scripts"
VIDEO_ROOT = ROOT


def test_storyboard_min_scenes(tmp_path: Path):
    sys.path.insert(0, str(SCRIPTS))
    from storyboard_from_chapter import build_scenes  # noqa: E402
    from visual_brief import build_visual_brief  # noqa: E402

    project = tmp_path / "novel"
    (project / "canon").mkdir(parents=True)
    (project / "chapters").mkdir()
    (project / "story.md").write_text("---\ngenre: 悬疑\n---\n", encoding="utf-8")
    (project / "canon" / "voice-brief.md").write_text("冷峻写实\n", encoding="utf-8")
    (project / "chapters" / "01.md").write_text(
        "\n\n".join(f"　　第{i}段叙事内容足够长以触发分镜分组逻辑。" for i in range(12)),
        encoding="utf-8",
    )
    text = (project / "chapters" / "01.md").read_text(encoding="utf-8")
    brief = build_visual_brief(project)
    scenes = build_scenes(text, brief, min_scenes=6, max_scenes=10)
    assert len(scenes) >= 6
    assert all("visual_positive" in s for s in scenes)
    assert "anime" not in scenes[0]["visual_positive"].lower()


def test_gate_intake_passes_demo_project():
    spec = json.loads((VIDEO_ROOT / "references" / "platform-publish-spec.json").read_text(encoding="utf-8"))
    sys.path.insert(0, str(SCRIPTS))
    from platform_publish_gate import gate_intake  # noqa: E402

    ch = ROOT.parent / "cursor-novel-writer" / "examples" / "demo-novel" / "chapters" / "01_试章.md"
    if not ch.is_file():
        pytest.skip("demo chapter missing")
    r = gate_intake(project_root=None, chapter_path=ch, mode="summary")
    assert r["ok"] is True


def test_platform_gate_cli_intake():
    ch = ROOT.parent / "cursor-novel-writer" / "examples" / "demo-novel" / "chapters" / "01_试章.md"
    if not ch.is_file():
        pytest.skip("demo chapter missing")
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "platform_publish_gate.py"),
            "--phase",
            "intake",
            "--chapter",
            str(ch),
            "--mode",
            "motion-comic",
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr
