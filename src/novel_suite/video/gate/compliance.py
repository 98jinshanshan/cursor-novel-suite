"""Content compliance check — sensitive words, AI label, platform policy."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from novel_suite.core.paths import video_root
from novel_suite.video._legacy import load_video_script

SENSITIVE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"色情|淫秽|露骨", re.UNICODE),
    re.compile(r"血腥|残忍\s*杀害|分尸", re.UNICODE),
    re.compile(r"领导人[\u4e00-\u9fff]{0,4}(?:名字|姓名)", re.UNICODE),
]

PLATFORM_REQUIREMENTS: dict[str, dict[str, Any]] = {
    "douyin": {
        "min_duration_sec": 10,
        "max_duration_sec": 180,
        "ai_label_required": True,
        "aspect_ratio": "9:16",
        "width": 1080,
        "height": 1920,
    },
    "kuaishou": {
        "min_duration_sec": 10,
        "max_duration_sec": 120,
        "ai_label_required": True,
        "aspect_ratio": "9:16",
        "width": 1080,
        "height": 1920,
    },
}

_ASPECT_TOLERANCE = 0.02


def _run_command(cmd: list[str], *, timeout: float = 30.0) -> str:
    run_command = load_video_script("subprocess_safe").run_command
    proc = run_command(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    return (proc.stdout or "").strip()


@lru_cache(maxsize=1)
def _load_spec_keywords() -> tuple[str, ...]:
    spec_path = video_root() / "references" / "platform-publish-spec.json"
    if not spec_path.is_file():
        return ()
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        keywords = spec.get("content_redlines", {}).get("narration_keywords_block", [])
        return tuple(str(k) for k in keywords if k)
    except (OSError, json.JSONDecodeError, TypeError):
        return ()


def check_sensitive_content(text: str) -> list[dict[str, Any]]:
    """Return sensitive-content hits for *text* (regex + engine spec keywords)."""
    hits: list[dict[str, Any]] = []
    for pattern in SENSITIVE_PATTERNS:
        for match in pattern.finditer(text):
            hits.append(
                {
                    "pattern": pattern.pattern,
                    "match": match.group(),
                    "position": (match.start(), match.end()),
                    "source": "regex",
                }
            )
    for keyword in _load_spec_keywords():
        start = 0
        while True:
            idx = text.find(keyword, start)
            if idx < 0:
                break
            hits.append(
                {
                    "pattern": keyword,
                    "match": keyword,
                    "position": (idx, idx + len(keyword)),
                    "source": "platform_spec",
                }
            )
            start = idx + len(keyword)
    return hits


def _probe_duration(video_path: Path) -> float:
    stdout = _run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path.resolve()),
        ],
        timeout=30,
    )
    return float(stdout)


def _probe_resolution(video_path: Path) -> tuple[int, int]:
    stdout = _run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0:s=x",
            str(video_path.resolve()),
        ],
        timeout=30,
    )
    if "x" not in stdout:
        raise ValueError(f"Cannot parse resolution from ffprobe: {stdout!r}")
    w_str, h_str = stdout.split("x", 1)
    return int(w_str), int(h_str)


def _resolution_matches(width: int, height: int, expected_w: int, expected_h: int) -> bool:
    if expected_w <= 0 or expected_h <= 0:
        return True
    w_ok = abs(width - expected_w) / expected_w <= _ASPECT_TOLERANCE
    h_ok = abs(height - expected_h) / expected_h <= _ASPECT_TOLERANCE
    return w_ok and h_ok


def check_platform_requirements(
    video_path: Path,
    platform: str = "douyin",
) -> list[str]:
    """Check video file size, duration, and resolution against platform minimums."""
    violations: list[str] = []
    reqs = PLATFORM_REQUIREMENTS.get(platform, {})

    if not video_path.is_file():
        violations.append(f"Video file not found: {video_path}")
        return violations

    size = video_path.stat().st_size
    if size < 1024:
        violations.append(f"Video file too small ({size} bytes)")

    try:
        duration = _probe_duration(video_path)
        min_dur = float(reqs.get("min_duration_sec", 0))
        max_dur = float(reqs.get("max_duration_sec", 9999))
        if duration < min_dur:
            violations.append(f"Duration {duration:.1f}s < minimum {min_dur}s for {platform}")
        if duration > max_dur:
            violations.append(f"Duration {duration:.1f}s > maximum {max_dur}s for {platform}")
    except (OSError, RuntimeError, ValueError) as exc:
        violations.append(f"Cannot probe duration: {exc}")

    expected_w = int(reqs.get("width", 0) or 0)
    expected_h = int(reqs.get("height", 0) or 0)
    if expected_w and expected_h:
        try:
            width, height = _probe_resolution(video_path)
            if not _resolution_matches(width, height, expected_w, expected_h):
                violations.append(
                    f"Resolution {width}x{height} != expected {expected_w}x{expected_h} "
                    f"for {platform} ({reqs.get('aspect_ratio', '')})"
                )
        except (OSError, RuntimeError, ValueError) as exc:
            violations.append(f"Cannot probe resolution: {exc}")

    return violations


def check_ai_label(storyboard: dict[str, Any]) -> list[str]:
    """Metadata checks for AI disclosure readiness."""
    warnings: list[str] = []
    if not storyboard.get("source_chapter", ""):
        warnings.append("Storyboard missing source_chapter — AI label cannot be verified")
    if not storyboard.get("ai_generated") and not storyboard.get("ai_label"):
        warnings.append(
            "Storyboard missing ai_generated/ai_label metadata — "
            "add before publish (see platform-publish-spec ai_disclosure)"
        )
    return warnings


def run_compliance_check(
    video_path: Path,
    storyboard_path: Path,
    platform: str = "douyin",
) -> dict[str, Any]:
    """Run full compliance gate checks."""
    result: dict[str, Any] = {
        "platform": platform,
        "video_path": str(video_path),
        "passed": True,
        "checks": {},
    }

    sensitive_issues: list[dict[str, Any]] = []
    if storyboard_path.is_file():
        sb = json.loads(storyboard_path.read_text(encoding="utf-8"))
        for scene in sb.get("scenes", []):
            text = str(scene.get("narration", "") or "")
            sensitive_issues.extend(check_sensitive_content(text))
    result["checks"]["sensitive_content"] = {
        "passed": len(sensitive_issues) == 0,
        "issues": sensitive_issues,
    }
    if sensitive_issues:
        result["passed"] = False

    platform_issues = check_platform_requirements(video_path, platform)
    result["checks"]["platform_requirements"] = {
        "passed": len(platform_issues) == 0,
        "issues": platform_issues,
    }
    if platform_issues:
        result["passed"] = False

    if storyboard_path.is_file():
        sb = json.loads(storyboard_path.read_text(encoding="utf-8"))
        ai_warnings = check_ai_label(sb)
        result["checks"]["ai_label"] = {
            "passed": len(ai_warnings) == 0,
            "warnings": ai_warnings,
        }

    return result
