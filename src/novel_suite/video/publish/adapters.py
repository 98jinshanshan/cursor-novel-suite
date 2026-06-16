"""Platform adapter factory — registry-driven video upload."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, Protocol

from novel_suite.platforms._registry import get_platform, validate_platform
from novel_suite.video._legacy import load_video_script
from novel_suite.video.publish.cookie_manager import cookies_dir, load_cookies, save_cookies

_PLAYWRIGHT_SCRIPT = Path(__file__).parent / "_upload_playwright.py"


class UploadFunction(Protocol):
    def __call__(
        self,
        video_path: Path,
        title: str,
        *,
        cookies: list[dict[str, Any]] | None = None,
        headless: bool = True,
    ) -> dict[str, Any]: ...


_UPLOADERS: dict[str, UploadFunction] = {}


def register(platform: str, fn: UploadFunction) -> None:
    _UPLOADERS[platform.strip().lower()] = fn


def _run_command(cmd: list[str], *, timeout: float = 300.0) -> str:
    run_command = load_video_script("subprocess_safe").run_command
    proc = run_command(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    return proc.stdout or ""


def _check_playwright_deps() -> list[str]:
    warnings: list[str] = []
    try:
        import playwright  # noqa: F401
    except ImportError:
        warnings.append("pip install playwright")
    try:
        _run_command(["playwright", "--version"], timeout=10)
    except (OSError, RuntimeError, ValueError):
        warnings.append("playwright install chromium")
    return warnings


def _persist_cookies(platform: str, save_path: Path) -> None:
    if not save_path.is_file():
        return
    try:
        raw = json.loads(save_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return
    if isinstance(raw, list):
        save_cookies(platform, raw)


def playwright_upload(
    video_path: Path,
    title: str,
    *,
    creator_url: str,
    upload_url: str,
    aspect: str = "9:16",
    platform: str = "douyin",
    cookies: list[dict[str, Any]] | None = None,
    headless: bool = True,
) -> dict[str, Any]:
    """Run generic Playwright upload subprocess for a video platform."""
    deps = _check_playwright_deps()
    if deps:
        return {"ok": False, "error": f"Missing dependencies: {'; '.join(deps)}"}

    if not video_path.is_file():
        return {"ok": False, "error": f"Video not found: {video_path}"}

    platform = platform.strip().lower()
    cookie_dir = cookies_dir()
    save_path = cookie_dir / f"{platform}.json"
    export_path = cookie_dir / f"{platform}_export.json"

    cmd = [
        sys.executable,
        str(_PLAYWRIGHT_SCRIPT),
        "--video",
        str(video_path.resolve()),
        "--title",
        title,
        "--creator-url",
        creator_url,
        "--upload-url",
        upload_url,
        "--aspect",
        aspect,
        "--save-cookies",
        str(save_path),
    ]
    if headless:
        cmd.append("--headless")

    session_cookies = cookies if cookies is not None else load_cookies(platform)
    if session_cookies:
        export_path.write_text(json.dumps(session_cookies, ensure_ascii=False), encoding="utf-8")
        cmd.extend(["--cookies", str(export_path)])

    try:
        stdout = _run_command(cmd, timeout=300)
        output = json.loads(stdout) if stdout.strip() else {"ok": False, "error": "empty stdout"}
        if output.get("ok"):
            _persist_cookies(platform, save_path)
        output["platform"] = platform
        return output
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc), "platform": platform}


def _registry_uploader(platform_key: str) -> UploadFunction:
    def _upload(
        video_path: Path,
        title: str,
        *,
        cookies: list[dict[str, Any]] | None = None,
        headless: bool = True,
    ) -> dict[str, Any]:
        info = get_platform(platform_key) or {}
        return playwright_upload(
            video_path,
            title,
            creator_url=str(info.get("creator_url", "")),
            upload_url=str(info.get("upload_api", info.get("creator_url", ""))),
            aspect=str(info.get("aspect", "9:16")),
            platform=platform_key,
            cookies=cookies,
            headless=headless,
        )

    return _upload


def upload(
    platform: str,
    video_path: Path,
    title: str,
    *,
    cookies: list[dict[str, Any]] | None = None,
    headless: bool = True,
) -> dict[str, Any]:
    """Unified upload entry — select adapter by platform key."""
    key = platform.strip().lower()
    if not validate_platform(key):
        return {"ok": False, "error": f"Unknown platform: {platform}"}

    info = get_platform(key) or {}
    if info.get("type") != "video":
        return {"ok": False, "error": f"Platform {platform} is not a video platform"}

    uploader = _UPLOADERS.get(key)
    if uploader is None:
        return {"ok": False, "error": f"No upload adapter for {platform}"}

    return uploader(video_path, title, cookies=cookies, headless=headless)


def _register_defaults() -> None:
    for key in ("douyin", "kuaishou", "bilibili"):
        if validate_platform(key):
            register(key, _registry_uploader(key))


_register_defaults()
