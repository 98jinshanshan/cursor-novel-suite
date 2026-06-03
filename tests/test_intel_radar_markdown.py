"""CI contract: intel_scan.render_radar output must pass markdownlint."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
ENGINE = REPO / "cursor-novel-writer" / "engine" / "scripts"


@pytest.fixture(scope="module")
def intel_scan():
    sys.path.insert(0, str(ENGINE))
    import intel_scan as mod  # noqa: PLC0415

    return mod


def _demo_hits(mod):
    from intel_scan import Hit  # noqa: PLC0415

    platforms = list(mod.PLATFORM_SITES.keys())[:5]
    hits = []
    for i, p in enumerate(platforms):
        hits.append(
            Hit(
                platform=p,
                title=f"示例标题 {i + 1}",
                url=f"https://example.com/demo/{p}-1",
                snippet=f"示例正文 {p} 悬疑刑侦推理",
            )
        )
    return platforms, hits


def test_render_radar_passes_markdownlint(intel_scan, tmp_path: Path):
    mod = intel_scan
    platforms, hits = _demo_hits(mod)
    topic_scores, topic_coverage = mod.score_topics(hits)
    md = mod.render_radar(
        period="week",
        platforms=platforms,
        hits=hits,
        topic_scores=topic_scores,
        topic_coverage=topic_coverage,
    )
    radar = tmp_path / "radar-sample.md"
    radar.write_text(md, encoding="utf-8")

    assert "[链接](" in md, "URLs must be markdown links, not bare"
    assert "### 1." in md
    assert "\n\n- 短视频适配" in md, "heading must be followed by blank line before list"
    assert not re.search(r"\|\s[^|]+\|\shttps?://", md), "table cells must not contain bare URLs"

    if not shutil.which("npx"):
        pytest.skip("npx not on PATH")
    r = subprocess.run(
        ["npx", "--yes", "markdownlint-cli2", str(radar)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        shell=sys.platform == "win32",
    )
    assert r.returncode == 0, r.stdout + r.stderr
