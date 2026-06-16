"""Douyin video upload — thin wrapper over platform adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from novel_suite.video.publish.adapters import upload


def douyin_upload(
    video_path: Path,
    title: str,
    *,
    headless: bool = True,
) -> dict[str, Any]:
    """Upload video to Douyin via shared Playwright adapter."""
    return upload("douyin", video_path, title, headless=headless)
