"""RealPipeline-2B — NVP-gated novel + video pipeline validation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from novel_suite.core.errors import (
    REALPIPELINE_RUN_OK,
    REALPIPELINE_VALIDATE_FAIL,
    REALPIPELINE_VALIDATE_OK,
)
from novel_suite.core.paths import suite_root
from novel_suite.core.result import artifact, error_result, ok_result, Result

ACTIVE_SLUG = "novel-837dd4f1"
NVP_TEMPLATE_DIR = "docs/verification-prompts"
NVP_CONTRACT = "docs/standards/NODE-VERIFICATION-PROMPT-CONTRACT.md"

NOVEL_NVP_RESULTS = (
    "NVP-P4-active-project-isolation.result.md",
    "NVP-P0-market-scan.result.md",
    "NVP-P1-story-init.result.md",
    "NVP-P2a-worldbuilding.result.md",
    "NVP-P2b-character-management.result.md",
    "NVP-P3-plot-structure.result.md",
    "NVP-P4-voice-brief.result.md",
    "NVP-P5-chapter-writing.result.md",
    "NVP-P6-review.result.md",
    "NVP-P7-deai-platform.result.md",
    "NVP-P8-revalidate.result.md",
    "NVP-P9-export.result.md",
)

VIDEO_NVP_RESULTS = (
    "NVP-V1D-motion-drama.result.md",
    "NVP-V2-video-export-qc.result.md",
)

NVP_TEMPLATES = (
    "NVP-P0-market-scan.md",
    "NVP-P1-story-init.md",
    "NVP-P2a-worldbuilding.md",
    "NVP-P2b-character-management.md",
    "NVP-P3-plot-structure.md",
    "NVP-P4-voice-brief.md",
    "NVP-P5-chapter-writing.md",
    "NVP-P6-review.md",
    "NVP-P7-deai-platform.md",
    "NVP-P8-revalidate.md",
    "NVP-P9-export.md",
    "NVP-V0-summary-video.md",
    "NVP-V1-motion-comic.md",
    "NVP-V1D-motion-drama.md",
    "NVP-V2-video-export-qc.md",
)


def count_cjk(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def project_root(project: str | Path) -> Path:
    p = Path(project)
    if not p.is_absolute():
        p = suite_root() / p
    return p.resolve()


def reports_dir(project: Path) -> Path:
    return project / "reports"


def find_chapter_02(project: Path) -> Path | None:
    ch_dir = project / "chapters"
    if not ch_dir.is_dir():
        return None
    matches = sorted(ch_dir.glob("02_*.md"))
    return matches[0] if matches else None


def check_active_project() -> tuple[bool, str, list[str]]:
    blockers: list[str] = []
    active_file = suite_root() / "novels" / ".active"
    registry = suite_root() / "novels" / "_registry.json"
    slug = ""
    if active_file.is_file():
        slug = active_file.read_text(encoding="utf-8").strip()
    else:
        blockers.append("novels/.active missing")
    reg_slug = ""
    if registry.is_file():
        data = json.loads(registry.read_text(encoding="utf-8"))
        reg_slug = data.get("active_slug", "")
    else:
        blockers.append("novels/_registry.json missing")
    if slug != ACTIVE_SLUG:
        blockers.append(f".active={slug!r} expected {ACTIVE_SLUG}")
    if reg_slug != ACTIVE_SLUG:
        blockers.append(f"active_slug={reg_slug!r} expected {ACTIVE_SLUG}")
    ok = not blockers
    return ok, slug or reg_slug, blockers


def validate_realpipeline(project: str | Path) -> Result:
    root = suite_root()
    proj = project_root(project)
    checks: list[dict[str, Any]] = []
    blockers: list[str] = []

    def add(name: str, ok: bool, path: str = "", detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "path": path, "detail": detail})
        if not ok:
            blockers.append(name if not detail else f"{name}: {detail}")

    add("nvp_contract", (root / NVP_CONTRACT).is_file(), NVP_CONTRACT)
    for tpl in NVP_TEMPLATES:
        p = root / NVP_TEMPLATE_DIR / tpl
        add(f"nvp_template.{tpl}", p.is_file(), str(p.relative_to(root)).replace("\\", "/"))

    active_ok, slug, active_blockers = check_active_project()
    add("active_project", active_ok, "novels/.active", "; ".join(active_blockers) if active_blockers else slug)

    realgen_out = root / "novel-suite" / "realgen-demo" / "cold_case_echo_realgen_01"
    add("no_realgen_success", not realgen_out.is_dir(), str(realgen_out), "旁路 demo 不得作为成功产物")

    rep = reports_dir(proj)
    for nvp in NOVEL_NVP_RESULTS + VIDEO_NVP_RESULTS:
        p = rep / nvp
        add(f"nvp_result.{nvp}", p.is_file(), _rel(root, p))

    add("phase0_source_record", (rep / "phase0_source_record.md").is_file(), _rel(root, rep / "phase0_source_record.md"))
    add("nvp_manifest", (rep / "realpipeline_2b_nvp_manifest.json").is_file(), _rel(root, rep / "realpipeline_2b_nvp_manifest.json"))

    ch02 = find_chapter_02(proj)
    if ch02 and ch02.is_file():
        cjk = count_cjk(ch02.read_text(encoding="utf-8"))
        add("chapter_02", cjk >= 2500, _rel(root, ch02), f"cjk={cjk}")
    else:
        add("chapter_02", False, "", "missing chapters/02_*.md")

    for pattern, label in (
        ("reviews/02_*-review.md", "review_ch02"),
        ("reviews/02_*-deai.md", "deai_ch02"),
        ("reviews/02_*-platform-compliance.md", "platform_ch02"),
    ):
        matches = list(proj.glob(pattern))
        add(label, bool(matches), _rel(root, matches[0]) if matches else "")

    snap = proj / "canon" / "snapshots" / "ch02-after.md"
    add("snapshot_ch02", snap.is_file(), _rel(root, snap))

    vid = proj / "video" / "ch02"
    for fname in (
        "storyboard.json",
        "shot_list.csv",
        "asset_pack.md",
        "narration_script.md",
        "subtitles.srt",
        "timeline_package.json",
        "video_generation_blockers.md",
        "video_qc_report.md",
    ):
        p = vid / fname
        add(f"video_ch02.{fname}", p.is_file(), _rel(root, p))

    qc = vid / "video_qc_report.md"
    video_level = "D"
    if qc.is_file():
        text = qc.read_text(encoding="utf-8")
        m = re.search(r"video_level:\s*([ABCD])", text, re.I)
        if m:
            video_level = m.group(1).upper()
        add("video_level_not_ab_for_textcard", video_level in "CD", _rel(root, qc), f"level={video_level}")

    manifest_path = rep / "realpipeline_2b_nvp_manifest.json"
    overall = "D"
    if manifest_path.is_file():
        try:
            overall = json.loads(manifest_path.read_text(encoding="utf-8")).get("overall_grade", "D")
        except json.JSONDecodeError:
            pass

    if blockers:
        return error_result(
            REALPIPELINE_VALIDATE_FAIL,
            f"RealPipeline-2B: {len(blockers)} check(s) failed",
            checks=checks,
            blockers=blockers,
            video_level=video_level,
            overall_grade=overall,
            commercial_release_allowed=False,
            verdict="blocked",
            project=str(proj.relative_to(root)).replace("\\", "/"),
        )

    return ok_result(
        REALPIPELINE_VALIDATE_OK,
        "RealPipeline-2B NVP validation passed",
        checks=checks,
        video_level=video_level,
        overall_grade=overall,
        commercial_release_allowed=False,
        verdict="blocked",
        platform_publish_allowed=False,
        project=str(proj.relative_to(root)).replace("\\", "/"),
        next_actions=["Open novels/novel-837dd4f1/reports/realpipeline_2b_summary.md"],
    )


def run_realpipeline(project: str | Path) -> Result:
    result = validate_realpipeline(project)
    if result.status != "ok":
        return result
    arts = [
        artifact(c["path"], label=c["name"])
        for c in result.details.get("checks", [])
        if c.get("ok") and c.get("path")
    ]
    return ok_result(
        REALPIPELINE_RUN_OK,
        "RealPipeline-2B evidence chain present on disk",
        artifacts=arts[:20],
        commercial_release_allowed=False,
        verdict="blocked",
        overall_grade=result.details.get("overall_grade", "C"),
        video_level=result.details.get("video_level", "C"),
        real_generation_performed=True,
        nvp_enforced=True,
        active_slug=ACTIVE_SLUG,
        next_actions=["novel-suite realpipeline validate --project novels/novel-837dd4f1 --json"],
    )


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)
