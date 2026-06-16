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
    assert "Next:" in r.stdout or "Pipeline phases complete." in r.stdout


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


def test_intel_scan_fallback_demo_on_empty_live(monkeypatch, tmp_path: Path):
    sys.path.insert(0, str(ENGINE / "scripts"))
    import intel_scan as mod  # noqa: PLC0415

    monkeypatch.setattr(mod, "ddg_search", lambda *a, **k: [])

    radar = tmp_path / "radar-fallback.md"
    argv = [
        "intel_scan.py",
        "--period",
        "week",
        "--platforms",
        "douyin",
        "--fallback-demo",
        "--radar",
        str(radar),
        "--no-concepts",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    assert mod.main() == 0
    assert radar.is_file()
    assert "题材热度榜" in radar.read_text(encoding="utf-8")


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
    completion = radar.with_suffix(".completion.json")
    assert completion.is_file(), "intel scan must write NEC completion manifest"
    data = json.loads(completion.read_text(encoding="utf-8"))
    assert data.get("phase") == 0
    assert data.get("skill") == "novel-market-scan"
    done_ids = {st["id"] for st in data["subtasks"] if st.get("status") == "done"}
    assert "P0-S1" in done_ids


def test_batch_b_node_sync_phase2_3_demo():
    for phase in (1, 2, 3):
        r = subprocess.run(
            [
                sys.executable,
                str(ENGINE / "novel_cli.py"),
                "node",
                "sync",
                "--phase",
                str(phase),
                "--project",
                str(DEMO),
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        assert r.returncode == 0, r.stderr + r.stdout
    for phase in (1, 2, 3):
        path = DEMO / "canon" / "nodes" / f"phase-{phase}.completion.json"
        assert path.is_file(), f"missing {path}"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["status"] == "complete", phase
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "pipeline",
            "gate",
            "--phase",
            "4",
            "--project",
            str(DEMO),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "GATE OK" in r.stdout


def test_batch_c_node_sync_phase4_8_demo():
    for phase in (4, 5, 6, 7, 8):
        r = subprocess.run(
            [
                sys.executable,
                str(ENGINE / "novel_cli.py"),
                "node",
                "sync",
                "--phase",
                str(phase),
                "--project",
                str(DEMO),
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        assert r.returncode == 0, r.stderr + r.stdout
        path = DEMO / "canon" / "nodes" / f"phase-{phase}.completion.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["status"] == "complete", f"phase {phase}"
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "pipeline",
            "gate",
            "--phase",
            "6",
            "--project",
            str(DEMO),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "GATE OK" in r.stdout


def test_batch_d_export_sync_phase9_demo():
    (DEMO / "dist").mkdir(parents=True, exist_ok=True)
    for phase in range(1, 9):
        subprocess.run(
            [
                sys.executable,
                str(ENGINE / "novel_cli.py"),
                "node",
                "sync",
                "--phase",
                str(phase),
                "--project",
                str(DEMO),
            ],
            check=True,
            cwd=str(ROOT),
        )
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "export",
            "--format",
            "epub",
            "--project",
            str(DEMO),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert list((DEMO / "dist").glob("*.epub")), "epub should be created"
    for phase in range(1, 10):
        r = subprocess.run(
            [
                sys.executable,
                str(ENGINE / "novel_cli.py"),
                "node",
                "sync",
                "--phase",
                str(phase),
                "--project",
                str(DEMO),
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        assert r.returncode == 0, r.stderr + r.stdout
    p9 = DEMO / "canon" / "nodes" / "phase-9.completion.json"
    assert json.loads(p9.read_text(encoding="utf-8"))["status"] == "complete"


def test_batch_d_gate_phase9_demo():
    tp = DEMO / "task_plan.md"
    text = tp.read_text(encoding="utf-8")
    if "- [ ] Phase 9:" in text:
        tp.write_text(
            text.replace("- [ ] Phase 9:", "- [x] Phase 9:", 1),
            encoding="utf-8",
        )
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "pipeline",
            "gate",
            "--phase",
            "9",
            "--project",
            str(DEMO),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr + r.stdout


def test_node_validate_demo_phase0_project():
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "node",
            "validate",
            "--phase",
            "0",
            "--project",
            str(DEMO),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "NODE VALIDATE OK" in r.stdout


def test_pipeline_gate_phase7_blocked_without_review(tmp_path: Path):
    project = tmp_path / "gate7-block"
    project.mkdir()
    (project / "canon" / "nodes").mkdir(parents=True)
    (project / "task_plan.md").write_text(
        "\n".join(f"- [x] Phase {i}: done" for i in range(0, 7)),
        encoding="utf-8",
    )
    (project / "canon" / "concept-brief.md").write_text(
        "## 元信息\n\n## 题材摘要\n\n## 故事内核\n",
        encoding="utf-8",
    )
    stub_task = {
        "id": "P1-S0",
        "title": "stub",
        "executor": "cli",
        "status": "done",
    }
    for phase in range(0, 7):
        (project / "canon" / "nodes" / f"phase-{phase}.completion.json").write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "phase": phase,
                    "skill": "x",
                    "status": "complete",
                    "subtasks": [stub_task],
                }
            ),
            encoding="utf-8",
        )
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "pipeline",
            "gate",
            "--phase",
            "7",
            "--project",
            str(project),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode != 0
    assert "GATE FAIL" in r.stderr


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


def test_export_blocked_when_gate9_fails(tmp_path: Path):
    project = tmp_path / "no-export"
    project.mkdir()
    (project / "canon").mkdir()
    (project / "task_plan.md").write_text("- [x] Phase 0: x\n- [ ] Phase 8: x\n", encoding="utf-8")
    (project / "canon" / "concept-brief.md").write_text(
        "## 元信息\n\n## 题材摘要\n\n## 故事内核\n",
        encoding="utf-8",
    )
    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "export",
            "--project",
            str(project),
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
    novels.mkdir(parents=True, exist_ok=True)
    try:
        import novel_suite.writer.registry as ns_reg
    except ImportError:
        ns_reg = reg
    monkeypatch.setattr(ns_reg, "NOVELS_DIR", novels)
    monkeypatch.setattr(ns_reg, "REGISTRY_PATH", novels / "_registry.json")
    monkeypatch.setattr(ns_reg, "ACTIVE_PATH", novels / ".active")
    monkeypatch.setattr(ns_reg, "MONOREPO_ROOT", tmp_path)
    if reg is not ns_reg:
        monkeypatch.setattr(reg, "NOVELS_DIR", novels)
        monkeypatch.setattr(reg, "REGISTRY_PATH", novels / "_registry.json")
        monkeypatch.setattr(reg, "ACTIVE_PATH", novels / ".active")
        monkeypatch.setattr(reg, "MONOREPO_ROOT", tmp_path)

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
