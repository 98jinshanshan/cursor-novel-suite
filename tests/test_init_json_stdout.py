"""Init --json must emit pure JSON on stdout (Agent-parseable contract)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_init_json_stdout_is_pure_json(tmp_path: Path):
    slug = "pure-json-init-test"
    active_path = REPO / "novels" / ".active"
    reg_path = REPO / "novels" / "_registry.json"
    prev_active_text = active_path.read_text(encoding="utf-8") if active_path.is_file() else None
    prev_reg: dict | None = None
    if reg_path.is_file():
        prev_reg = json.loads(reg_path.read_text(encoding="utf-8"))
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(REPO)}
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "novel_suite.cli",
            "writer",
            "init",
            "--title",
            "纯JSON测试",
            "--premise",
            "验证 stdout 仅含 JSON。",
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
        raw = r.stdout.strip()
        assert raw, "stdout empty"
        assert raw[0] == "{", f"stdout must be pure JSON, got prefix: {raw[:120]!r}"
        assert not raw.startswith("OK:"), raw[:200]
        data = json.loads(raw)
        assert data["status"] == "ok"
        assert data["code"] == "INIT_OK"
        legacy = data.get("details", {}).get("legacy_output")
        if legacy:
            assert isinstance(legacy, list)
            joined = "\n".join(str(x) for x in legacy)
            assert "bible scaffold" in joined or "Initialized:" in joined
    finally:
        project = REPO / "novels" / slug
        if project.exists():
            import shutil

            shutil.rmtree(project, ignore_errors=True)
        if prev_reg is not None:
            reg_path.write_text(json.dumps(prev_reg, ensure_ascii=False, indent=2), encoding="utf-8")
        if prev_active_text is not None:
            active_path.write_text(prev_active_text, encoding="utf-8")
        elif active_path.is_file():
            active_path.unlink(missing_ok=True)
