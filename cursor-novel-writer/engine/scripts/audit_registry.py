"""Map novel audit modes to engine scripts."""

from __future__ import annotations

from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

AUDIT_MODES: dict[str, Path] = {
    "format": SCRIPTS_DIR / "chapter_format_lint.py",
    "deai": SCRIPTS_DIR / "deai_audit.py",
    "voice": SCRIPTS_DIR / "voice_brief_lint.py",
    "plot": SCRIPTS_DIR / "plot_scale_audit.py",
    "story": SCRIPTS_DIR / "story_init_audit.py",
    "canon": SCRIPTS_DIR / "canon_lint.py",
    "blocker": SCRIPTS_DIR / "review_blocker_scan.py",
    "revalidate": SCRIPTS_DIR / "revalidate_diff.py",
    "export": SCRIPTS_DIR / "export_audit.py",
    "intel": SCRIPTS_DIR / "intel_rubric_score.py",
}

VIDEO_AUDIT_MODES: dict[str, Path] = {
    "video-script": Path(__file__).resolve().parents[3]
    / "cursor-novel-video"
    / "engine"
    / "scripts"
    / "video_script_lint.py",
}

ALL_MODES = sorted(set(AUDIT_MODES) | set(VIDEO_AUDIT_MODES))
