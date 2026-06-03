"""CLI smoke for writer init --json."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_writer_init_json():
    novels = REPO / "novels"
    slug = "cli-init-smoke-test"
    project = novels / slug
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
            reg = REPO / "novels" / "_registry.json"
            if reg.is_file():
                data = json.loads(reg.read_text(encoding="utf-8"))
                data["novels"] = [n for n in data.get("novels", []) if n.get("slug") != slug]
                if data.get("active_slug") == slug:
                    data["active_slug"] = None
                reg.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
