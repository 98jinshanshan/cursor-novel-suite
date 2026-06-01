"""Smoke tests for cursor-novel-writer."""

from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
SCRIPTS = ENGINE / "scripts"
DEMO = ROOT / "examples" / "demo-novel"


def _load_module(module_name: str, module_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_demo_novel_structure():
    assert (DEMO / "story.md").is_file()
    assert (DEMO / "characters" / "chen-wei.md").is_file()
    assert (DEMO / "worldbuilding" / "systems" / "archive-seal-system.md").is_file()
    assert (DEMO / "plot" / "arcs" / "arc-main-letter.md").is_file()
    assert len(list((DEMO / "characters").glob("*.md"))) >= 3


def test_novel_cli_project_after_subcommand():
    r = subprocess.run(
        [sys.executable, str(ENGINE / "novel_cli.py"), "status", "--project", str(DEMO)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0
    assert "雾港来信" in r.stdout


def test_graphify_bridge_offline_status():
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "graphify_bridge.py"),
            "status",
            "--project",
            str(DEMO),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0


def test_graphify_bridge_offline_review_requires_graphify():
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "graphify_bridge.py"),
            "review",
            "--project",
            str(DEMO),
            "--chapter",
            str(DEMO / "chapters" / "01_试章.md"),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode in (0, 2)


def test_skill_wrapper_create_epub(tmp_path: Path):
    out = tmp_path / "out.epub"
    r = subprocess.run(
        [
            sys.executable,
            str(ROOT / "skills" / "novel-export" / "scripts" / "create_epub.py"),
            "--project",
            str(DEMO),
            "--output",
            str(out),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr
    assert out.is_file()
    assert out.stat().st_size > 500


def test_progress_json_valid():
    data = json.loads((DEMO / "canon" / "progress.json").read_text(encoding="utf-8"))
    assert data["title"] == "雾港来信"
    assert len(data["chapters"]) >= 1


def test_novel_pipeline_skill_exists():
    assert (ROOT / "skills" / "novel-pipeline" / "SKILL.md").is_file()


def test_demo_voice_brief():
    assert (DEMO / "canon" / "voice-brief.md").is_file()


def test_novel_cli_pipeline_status():
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "pipeline",
            "status",
            "--project",
            str(DEMO),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0
    assert "Phase" in r.stdout
    assert "Next:" in r.stdout


def test_project_registry_slug():
    sys.path.insert(0, str(ENGINE))
    reg = _load_module("project_registry", SCRIPTS / "project_registry.py")

    assert reg.slug_from_title("My Novel Title") == "my-novel-title"
    s = reg.slug_from_title("雾港来信")
    assert s.startswith("novel-")


def test_novel_cli_bible_summary():
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "bible",
            "summary",
            "--project",
            str(DEMO),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0
    assert "Story Bible" in r.stdout
    assert "雾港来信" in r.stdout or "Characters" in r.stdout


def test_relations_check_demo():
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "relations",
            "check",
            "--project",
            str(DEMO),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode in (0, 1)


def test_novel_cli_intel_paths():
    r = subprocess.run(
        [sys.executable, str(ENGINE / "novel_cli.py"), "intel", "paths"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0
    assert "radar_this_week" in r.stdout
    assert "intel" in r.stdout.lower()


def test_novel_cli_intel_scan_from_input(tmp_path: Path):
    sample = tmp_path / "hits.json"
    sample.write_text(
        json.dumps(
            [
                {
                    "platform": "douyin",
                    "title": "离婚后她逆袭打脸，豪门反转短视频爆火",
                    "url": "https://example.com/a",
                    "snippet": "都市情感+反转，完播率提升",
                },
                {
                    "platform": "bilibili",
                    "title": "重生复仇题材本周热度上升",
                    "url": "https://example.com/b",
                    "snippet": "爽文节奏，适配剧情切条",
                },
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    radar = tmp_path / "radar.md"
    concepts = tmp_path / "concepts"
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "intel",
            "scan",
            "--input",
            str(sample),
            "--platforms",
            "douyin,bilibili",
            "--radar",
            str(radar),
            "--concepts-dir",
            str(concepts),
            "--concept-top",
            "1",
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr
    assert radar.is_file()
    assert "题材热度榜" in radar.read_text(encoding="utf-8")
    assert len(list(concepts.glob("*.md"))) == 1


def test_novel_cli_intel_scan_demo(tmp_path: Path):
    radar = tmp_path / "radar-demo.md"
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "intel",
            "scan",
            "--demo",
            "--period",
            "week",
            "--radar",
            str(radar),
            "--no-concepts",
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "WARN: --demo" in r.stderr
    assert radar.is_file()
    assert "题材热度榜" in radar.read_text(encoding="utf-8")


def test_pipeline_gate_demo_phase7_blocked():
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "pipeline",
            "gate",
            "--phase",
            "7",
            "--project",
            str(DEMO),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode != 0
    assert "GATE FAIL" in r.stderr
    assert "Phase 6" in r.stderr


def test_pipeline_validate_demo():
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "pipeline",
            "validate",
            "--project",
            str(DEMO),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr
    assert "VALIDATE OK" in r.stdout


def test_pipeline_gate_rejects_bad_project_json(tmp_path: Path):
    project = tmp_path / "bad-novel"
    project.mkdir()
    (project / "canon").mkdir()
    (project / "task_plan.md").write_text(
        "- [x] Phase 0: 选品\n- [x] Phase 1: 立项\n",
        encoding="utf-8",
    )
    (project / "canon" / "concept-brief.md").write_text(
        "## 元信息\n\n## 题材摘要\n\n## 故事内核\n",
        encoding="utf-8",
    )
    (project / "story.md").write_text("# Title\n", encoding="utf-8")
    (project / "canon" / "project.json").write_text('{"slug": "BAD SLUG"}', encoding="utf-8")
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "pipeline",
            "gate",
            "--phase",
            "2",
            "--project",
            str(project),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode != 0
    assert "GATE FAIL" in r.stderr
    assert "project.json" in r.stderr


def test_pipeline_gate_demo():
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "pipeline",
            "gate",
            "--phase",
            "1",
            "--project",
            str(DEMO),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0
    assert "GATE OK" in r.stdout


def test_export_is_blocked_before_phase9():
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "export",
            "--project",
            str(DEMO),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode != 0
    assert "GATE FAIL" in r.stderr


def test_init_under_novels(tmp_path: Path, monkeypatch):
    sys.path.insert(0, str(ENGINE))
    cli = _load_module("novel_cli", ENGINE / "novel_cli.py")
    reg = cli.reg
    scaffold_project = cli.scaffold_project

    novels = tmp_path / "novels"
    monkeypatch.setattr(reg, "NOVELS_DIR", novels)
    monkeypatch.setattr(reg, "REGISTRY_PATH", novels / "_registry.json")
    monkeypatch.setattr(reg, "ACTIVE_PATH", novels / ".active")
    monkeypatch.setattr(reg, "MONOREPO_ROOT", tmp_path)
    novels.mkdir(parents=True, exist_ok=True)

    out = novels / "test-book"
    scaffold_project(out, "Test Book", "premise", slug="test-book", register=True)
    assert (out / "canon" / "project.json").is_file()
    assert (out / "chapters" / ".drafts").is_dir()
    assert (out / "canon" / "snapshots").is_dir()
    data = reg.load_registry()
    assert any(n["slug"] == "test-book" for n in data["novels"])


MONOREPO = Path(__file__).resolve().parents[2]


def test_suite_paths_discovers_monorepo():
    sys.path.insert(0, str(ENGINE))
    sp = _load_module("suite_paths", SCRIPTS / "suite_paths.py")
    root = sp.suite_root(start=ENGINE)
    assert (root / sp.MARKER).is_file()
    assert (root / sp.WRITER_DIR / "engine" / "novel_cli.py").is_file()


def test_suite_paths_env_override(tmp_path: Path, monkeypatch):
    sys.path.insert(0, str(ENGINE))
    sp = _load_module("suite_paths_env", SCRIPTS / "suite_paths.py")

    fake = tmp_path / "suite"
    fake.mkdir()
    (fake / sp.MARKER).write_text("novel-suite-root=1\n", encoding="utf-8")
    writer = fake / sp.WRITER_DIR
    (writer / "engine").mkdir(parents=True)
    (writer / "engine" / "novel_cli.py").write_text("# stub\n", encoding="utf-8")

    monkeypatch.setenv(sp.ENV_ROOT, str(fake))
    assert sp.suite_root() == fake.resolve()


def test_suite_doctor_core_only():
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "suite",
            "doctor",
            "--core-only",
            "--json",
        ],
        capture_output=True,
        text=True,
        cwd=str(MONOREPO),
    )
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    assert payload["ok"] is True
    names = {c["name"] for c in payload["checks"]}
    assert "suite_root" in names
    assert "writer_engine" in names
    assert not any(n.startswith("skills_cursor") for n in names)
