"""Legacy novel_cli.py promote remains compatible with novel_suite."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ENGINE = REPO / "cursor-novel-writer" / "engine"


def test_novel_cli_promote_from_drafts(tmp_path: Path):
    project = tmp_path / "proj"
    drafts = project / "chapters" / ".drafts"
    drafts.mkdir(parents=True)
    (drafts / "05_legacy.md").write_text("# 第五章\n\nlegacy promote 测试。\n", encoding="utf-8")

    r = subprocess.run(
        [
            sys.executable,
            str(ENGINE / "novel_cli.py"),
            "promote",
            "05_legacy.md",
            "--project",
            str(project),
        ],
        cwd=str(REPO / "cursor-novel-writer"),
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    target = project / "chapters" / "05_legacy.md"
    assert target.is_file()
    assert "legacy promote" in target.read_text(encoding="utf-8")
    assert "Promoted" in r.stdout or "CHAPTER_PROMOTE_OK" in r.stdout
