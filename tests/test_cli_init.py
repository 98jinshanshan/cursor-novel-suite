"""CLI smoke for writer init --json."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_writer_init_help_shows_target_platform():
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(REPO)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "writer", "init", "--help"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr
    assert "--target-platform" in r.stdout
    assert "fanqie" in r.stdout


def test_writer_init_json():
    novels = REPO / "novels"
    slug = "cli-init-smoke-test"
    project = novels / slug
    active_path = novels / ".active"
    reg_path = novels / "_registry.json"
    prev_active_text = active_path.read_text(encoding="utf-8") if active_path.is_file() else None
    prev_reg: dict | None = None
    if reg_path.is_file():
        prev_reg = json.loads(reg_path.read_text(encoding="utf-8"))
    if project.exists():
        import shutil

        shutil.rmtree(project, ignore_errors=True)

    env = {**os.environ, "NOVEL_SUITE_ROOT": str(REPO)}
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "novel_suite.cli",
            "writer",
            "init",
            "--title",
            "CLI验收书",
            "--premise",
            "CLI smoke init 梗概。",
            "--slug",
            slug,
            "--json",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )
    try:
        assert r.returncode == 0, r.stderr + r.stdout
        data = json.loads(r.stdout)
        assert data["code"] == "INIT_OK"
        assert data["details"]["slug"] == slug
        assert (project / "story.md").is_file()
        assert (project / "canon" / "progress.json").is_file()
    finally:
        if project.exists():
            import shutil

            shutil.rmtree(project, ignore_errors=True)
        if prev_reg is not None:
            reg_path.write_text(json.dumps(prev_reg, ensure_ascii=False, indent=2), encoding="utf-8")
        if prev_active_text is not None:
            active_path.write_text(prev_active_text, encoding="utf-8")
        elif active_path.is_file():
            active_path.unlink(missing_ok=True)
