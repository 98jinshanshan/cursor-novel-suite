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
        reg = REPO / "novels" / "_registry.json"
        if reg.is_file():
            payload = json.loads(reg.read_text(encoding="utf-8"))
            payload["novels"] = [n for n in payload.get("novels", []) if n.get("slug") != slug]
            if payload.get("active_slug") == slug:
                payload["active_slug"] = None
            reg.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
