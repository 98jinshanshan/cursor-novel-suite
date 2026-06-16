"""Smoke tests for cursor-novel-video."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MONOREPO = ROOT.parent
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


def test_resolve_chapter_bare_filename(tmp_path: Path):
    project = tmp_path / "novel"
    chapters = project / "chapters"
    chapters.mkdir(parents=True)
    ch_file = chapters / "01_试章.md"
    ch_file.write_text(SAMPLE, encoding="utf-8")

    resolved = video_cli.resolve_chapter("01_试章.md", project)
    assert resolved == ch_file.resolve()

    resolved_prefixed = video_cli.resolve_chapter("chapters/01_试章.md", project)
    assert resolved_prefixed == ch_file.resolve()
    assert "chapters" not in resolved_prefixed.parts[-2:][0] or resolved_prefixed.parent.name == "chapters"


def test_resolve_chapter_no_double_chapters_prefix(tmp_path: Path):
    project = tmp_path / "novel"
    chapters = project / "chapters"
    chapters.mkdir(parents=True)
    missing = "chapters/missing.md"

    resolved = video_cli.resolve_chapter(missing, project)
    assert resolved == (project / missing).resolve()
    assert resolved.parts[-2:] != ("chapters", "chapters")


def test_split_scenes():
    scenes = video_cli.split_scenes(SAMPLE)
    assert len(scenes) == 2
    assert "第一句" in scenes[0]


def test_summarize_chapter():
    text = video_cli.summarize_chapter(SAMPLE, max_chars=50)
    assert len(text) <= 50


def test_resolve_chapter_bare_filename(tmp_path: Path):
    project = tmp_path / "proj"
    ch_dir = project / "chapters"
    ch_dir.mkdir(parents=True)
    chapter = ch_dir / "01_试章.md"
    chapter.write_text(SAMPLE, encoding="utf-8")
    assert video_cli.resolve_chapter("01_试章.md", project) == chapter.resolve()


def test_resolve_chapter_prefixed_path_no_double_chapters(tmp_path: Path):
    project = tmp_path / "proj"
    ch_dir = project / "chapters"
    ch_dir.mkdir(parents=True)
    chapter = ch_dir / "01_试章.md"
    chapter.write_text(SAMPLE, encoding="utf-8")
    assert video_cli.resolve_chapter("chapters/01_试章.md", project) == chapter.resolve()
    missing = video_cli.resolve_chapter("chapters/missing.md", project)
    assert missing == (project / "chapters" / "missing.md").resolve()
    assert "chapters/chapters" not in missing.as_posix()


def test_create_job_storyboard(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(video_cli, "DEFAULT_JOBS", tmp_path / "jobs")
    ch = tmp_path / "ch.md"
    ch.write_text(SAMPLE, encoding="utf-8")
    job = video_cli.create_job("drama", ch, "9:16")
    sb = json.loads((job / "storyboard.json").read_text(encoding="utf-8"))
    assert sb["mode"] == "drama"
    assert len(sb["scenes"]) >= 2


def test_video_job_node_completion_manifest(tmp_path: Path):
    sys.path.insert(0, str(SCRIPTS))
    import video_node_completion  # noqa: E402

    job = tmp_path / "job_test"
    job.mkdir()
    (job / "script.md").write_text("# script\n", encoding="utf-8")
    (job / "storyboard.json").write_text("{}", encoding="utf-8")
    out = job / "output"
    out.mkdir()
    mp4 = out / "clip.mp4"
    mp4.write_bytes(b"\x00\x00\x00\x18ftypmp42")
    path = video_node_completion.write_job_completion(job, artifact=mp4, qc_ok=True, mode="summary")
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["status"] == "complete"
    assert data["skill"] == "video-chapter-summary"


def test_infer_novel_binding_demo_chapter():
    if not DEMO_CH.is_file():
        pytest.skip("demo chapter missing")
    sys.path.insert(0, str(SCRIPTS))
    import novel_bind  # noqa: E402

    binding = novel_bind.infer_novel_binding(DEMO_CH)
    assert binding is not None
    assert binding["novel_slug"] == "demo-novel"
    assert binding["in_registry"] is False
    assert binding["source_chapter"].replace("\\", "/").endswith("chapters/01_试章.md")


def test_create_job_binds_novel_metadata(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(video_cli, "DEFAULT_JOBS", tmp_path / "jobs")
    project = tmp_path / "my-novel"
    (project / "canon").mkdir(parents=True)
    (project / "canon" / "project.json").write_text(
        json.dumps({"slug": "my-novel", "title": "My Novel"}, ensure_ascii=False),
        encoding="utf-8",
    )
    ch = project / "chapters" / "01_open.md"
    ch.parent.mkdir(parents=True)
    ch.write_text(SAMPLE, encoding="utf-8")
    sys.path.insert(0, str(SCRIPTS))
    import novel_bind  # noqa: E402

    binding = novel_bind.infer_novel_binding(ch)
    job = video_cli.create_job("summary", ch, "9:16", binding=binding)
    sb = json.loads((job / "storyboard.json").read_text(encoding="utf-8"))
    assert sb["novel"]["slug"] == "my-novel"
    state = json.loads((job / "job_state.json").read_text(encoding="utf-8"))
    assert state["novel_slug"] == "my-novel"


def test_record_video_job_in_registry(tmp_path: Path, monkeypatch):
    sys.path.insert(0, str(SCRIPTS))
    import novel_bind  # noqa: E402

    novels = tmp_path / "novels"
    slug = "vid-test"
    project = novels / slug
    (project / "canon").mkdir(parents=True)
    (project / "canon" / "project.json").write_text(
        json.dumps({"slug": slug, "title": "Video Test"}, ensure_ascii=False),
        encoding="utf-8",
    )
    ch = project / "chapters" / "01_a.md"
    ch.parent.mkdir(parents=True)
    ch.write_text(SAMPLE, encoding="utf-8")
    reg_path = novels / "_registry.json"
    reg_path.write_text(
        json.dumps(
            {
                "version": 1,
                "novels": [{"slug": slug, "path": f"novels/{slug}", "title": "Video Test"}],
                "active_slug": slug,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    sp = novel_bind._suite_paths_module()
    monkeypatch.setattr(sp, "suite_root", lambda: tmp_path)

    binding = novel_bind.infer_novel_binding(ch)
    assert binding is not None
    assert binding["in_registry"] is True
    job_dir = tmp_path / "cursor-novel-video" / "tmp" / "video_jobs" / "job1"
    job_dir.mkdir(parents=True)
    novel_bind._REG = None
    reg = novel_bind._registry_module()
    try:
        import novel_suite.writer.registry as ns_reg
    except ImportError:
        ns_reg = reg
    monkeypatch.setattr(ns_reg, "REGISTRY_PATH", reg_path)
    monkeypatch.setattr(ns_reg, "MONOREPO_ROOT", tmp_path)
    monkeypatch.setattr(ns_reg, "NOVELS_DIR", novels)
    if reg is not ns_reg:
        monkeypatch.setattr(reg, "REGISTRY_PATH", reg_path)
        monkeypatch.setattr(reg, "MONOREPO_ROOT", tmp_path)
        monkeypatch.setattr(reg, "NOVELS_DIR", novels)
    monkeypatch.setattr(novel_bind, "_REG", reg)

    assert novel_bind.record_video_job(
        binding, job_id="job1", job_dir=job_dir, mode="summary", status="running"
    )
    data = json.loads(reg_path.read_text(encoding="utf-8"))
    jobs = data["novels"][0]["video_jobs"]
    assert jobs[0]["job_id"] == "job1"
    assert jobs[0]["chapter"] == "chapters/01_a.md"


def test_beat_lock_split_sentences():
    sys.path.insert(0, str(SCRIPTS))
    import beat_lock  # noqa: E402

    parts = beat_lock.split_sentences("第一句。第二句！")
    assert len(parts) == 2


def test_summary_missing_chapter_emits_error_result(tmp_path: Path):
    missing = tmp_path / "missing.md"
    r = subprocess.run(
        [sys.executable, str(ENGINE / "video_cli.py"), "summary", "--chapter", str(missing)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 1
    assert "RESULT:" in r.stdout


def test_screenplay_to_shots_ch01_node2():
    sys.path.insert(0, str(SCRIPTS))
    import screenplay_to_shots  # noqa: E402

    project = MONOREPO / "novels" / "novel-837dd4f1"
    if not (project / "video" / "ch01" / "screenplay.md").is_file():
        pytest.skip("ch01 screenplay missing")
    out_dir = project / "video" / "ch01"
    payload = screenplay_to_shots.build_shots(project=project, chapter_dir=out_dir)
    assert payload["shot_count"] >= 40
    assert payload["total_duration_sec"] >= 120
    assert payload.get("version") >= 3
    assert "cvdp_ref" in payload
    sh = payload["shots"][0]
    assert sh.get("ambient_bed")
    assert sh.get("mixer_prompt")
    assert sh.get("camera_cuts")
    assert sh.get("character_refs")
    assert sh.get("character_tokens")
    assert "LINXIAO26_CN_LEAN" in sh["character_tokens"]
    assert sh["beat_id"] == "S01-01"
    dlg_beat = next(s for s in payload["shots"] if s["beat_id"] == "S07-02")
    assert len(dlg_beat.get("dialogue", [])) >= 5


def test_script_to_shots_ch01_has_15_shots():
    sys.path.insert(0, str(SCRIPTS))
    import script_to_shots  # noqa: E402

    ch = MONOREPO / "novels" / "novel-837dd4f1" / "chapters" / "01_卷宗亮了.md"
    if not ch.is_file():
        pytest.skip("冷案回声 ch01 missing")
    shots = script_to_shots.shots_from_chapter(ch)
    assert len(shots) == 15
    scenes = script_to_shots.shots_to_storyboard_scenes(shots)
    assert scenes[0]["id"] == "s01"
    assert all(sc.get("motion_prompt") for sc in scenes)
    assert all(sc.get("visual_positive") for sc in scenes)


def test_drama_quality_gate_rejects_few_shots(tmp_path: Path):
    sys.path.insert(0, str(SCRIPTS))
    import drama_quality_gate  # noqa: E402

    job = tmp_path / "job"
    job.mkdir()
    (job / "storyboard.json").write_text(
        json.dumps({"scenes": [{"id": "s01", "narration": "x", "visual_positive": "cinematic photorealistic"}]}),
        encoding="utf-8",
    )
    result = drama_quality_gate.gate_job(job)
    assert not result["ok"]
    assert any("shot count" in e for e in result["errors"])


def test_motion_drama_cli_help():
    r = subprocess.run(
        [sys.executable, str(ENGINE / "video_cli.py"), "motion-drama", "--help"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0
    assert "--project" in r.stdout


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
