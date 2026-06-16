"""Cookie lifecycle management for platform accounts.

Storage: ~/.novel-suite/cookies/{platform}.json (override via NOVEL_SUITE_COOKIE_DIR).
Encryption: plaintext with file mode 600; AES-GCM upgrade planned.
"""

from __future__ import annotations

import json
import os
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

COOKIE_MAX_AGE_DAYS = 7


def cookies_dir() -> Path:
    override = os.environ.get("NOVEL_SUITE_COOKIE_DIR", "").strip()
    base = Path(override) if override else Path.home() / ".novel-suite" / "cookies"
    base.mkdir(parents=True, exist_ok=True)
    try:
        base.chmod(stat.S_IRWXU)
    except (OSError, NotImplementedError):
        pass
    return base


def _cookie_path(platform: str) -> Path:
    return cookies_dir() / f"{platform}.json"


def save_cookies(platform: str, cookies: list[dict[str, Any]]) -> Path:
    """Persist cookies with metadata wrapper and file mode 600."""
    path = _cookie_path(platform)
    data = {
        "platform": platform,
        "cookies": cookies,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except (OSError, NotImplementedError):
        pass
    return path


def load_cookies(platform: str) -> list[dict[str, Any]] | None:
    """Load cookies; return None when missing or older than COOKIE_MAX_AGE_DAYS."""
    path = _cookie_path(platform)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    saved_at = data.get("saved_at", "")
    if saved_at:
        try:
            dt = datetime.fromisoformat(saved_at)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age_days = (datetime.now(timezone.utc) - dt).days
            if age_days > COOKIE_MAX_AGE_DAYS:
                return None
        except (ValueError, TypeError):
            return None

    cookies = data.get("cookies")
    return cookies if isinstance(cookies, list) else None


def cookie_status(platform: str) -> dict[str, Any]:
    """Return cookie validity report for a platform."""
    path = _cookie_path(platform)
    cookies = load_cookies(platform)
    if cookies is None:
        reason = "not_found_or_expired" if not path.is_file() else "expired"
        return {"platform": platform, "valid": False, "reason": reason}
    return {
        "platform": platform,
        "valid": True,
        "cookie_count": len(cookies),
        "file": str(path),
        "file_size": path.stat().st_size,
    }
