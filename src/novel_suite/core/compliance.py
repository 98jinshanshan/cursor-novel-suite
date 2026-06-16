"""Commercial release compliance — read-only static checks (no network)."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

from novel_suite.core.paths import suite_root


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _pyproject_data(root: Path) -> dict[str, Any]:
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    return data.get("project", {})


def _dep_names(deps: list[str]) -> set[str]:
    names: set[str] = set()
    for line in deps:
        name = re.split(r"[<>=!~\[]", line.strip())[0].strip().lower()
        if name:
            names.add(name)
    return names


def check_commercial_release_gate() -> list[dict[str, Any]]:
    """Return checklist items with ok/name/detail (read-only, no side effects)."""
    root = suite_root()
    checks: list[dict[str, Any]] = []
    project = _pyproject_data(root)
    runtime = _dep_names(project.get("dependencies", []))
    optional = project.get("optional-dependencies", {})
    dev = _dep_names(optional.get("dev", []))
    epub = _dep_names(optional.get("epub", []))

    checks.append(
        {
            "name": "pyproject.runtime_no_ebooklib",
            "ok": "ebooklib" not in runtime,
            "detail": "ebooklib must not be in [project] dependencies",
        }
    )
    checks.append(
        {
            "name": "pyproject.dev_no_ebooklib",
            "ok": "ebooklib" not in dev,
            "detail": "ebooklib must not be in dev optional extra",
        }
    )
    checks.append(
        {
            "name": "pyproject.epub_extra_has_ebooklib",
            "ok": "ebooklib" in epub,
            "detail": "epub optional extra must include ebooklib",
        }
    )

    notices = _read_text(root / "THIRD_PARTY_NOTICES.md")
    policy = _read_text(root / "THIRD_PARTY_POLICY.md")
    gate = _read_text(root / "COMMERCIAL_RELEASE_GATE.md")
    readme = _read_text(root / "README.md")

    notice_keywords = (
        "ebooklib",
        "edge-tts",
        "FFmpeg",
        "Stable Diffusion",
        "ControlNet",
        "MediaCrawler",
    )
    for kw in notice_keywords:
        checks.append(
            {
                "name": f"notices.mentions_{kw.replace(' ', '_').lower()}",
                "ok": kw.lower() in notices.lower() or kw in notices,
                "detail": f"THIRD_PARTY_NOTICES.md should mention {kw}",
            }
        )
    checks.append(
        {
            "name": "notices.mentions_platform_or_oauth",
            "ok": "OAuth" in notices or "平台" in notices,
            "detail": "THIRD_PARTY_NOTICES.md should mention platform/OAuth",
        }
    )

    for phrase in ("默认关闭", "禁入商业核心", "人工确认"):
        checks.append(
            {
                "name": f"policy.contains_{phrase}",
                "ok": phrase in policy,
                "detail": f"THIRD_PARTY_POLICY.md should contain {phrase!r}",
            }
        )

    checks.append(
        {
            "name": "commercial_release_gate.exists",
            "ok": (root / "COMMERCIAL_RELEASE_GATE.md").is_file(),
            "detail": "COMMERCIAL_RELEASE_GATE.md must exist",
        }
    )
    checks.append(
        {
            "name": "commercial_release_gate.legal_review_pending",
            "ok": "待法律" in gate or "待人工法律" in gate,
            "detail": "Gate must state legal review pending",
        }
    )
    checks.append(
        {
            "name": "commercial_release_gate.not_allowed_default",
            "ok": "不允许" in gate,
            "detail": "Gate must default to commercial release not allowed",
        }
    )

    for phrase in ("默认关闭", "人工确认"):
        checks.append(
            {
                "name": f"readme.contains_{phrase}",
                "ok": phrase in readme,
                "detail": f"README.md should contain {phrase!r}",
            }
        )

    publish_idx = readme.find("publish upload")
    if publish_idx >= 0:
        window = readme[max(0, publish_idx - 400) : publish_idx + 200]
        checks.append(
            {
                "name": "readme.publish_upload_has_adapter_warning",
                "ok": "默认关闭" in window or "人工确认" in window or "可选适配器" in window,
                "detail": "README near publish upload must warn about adapters",
            }
        )

    return checks
