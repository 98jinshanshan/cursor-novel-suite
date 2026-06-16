"""Fanqie (番茄小说) API Key auth."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from novel_suite.auth.token_store import save_token
from novel_suite.core.env_config import getenv


def login_fanqie() -> dict[str, Any]:
    api_key = getenv("FANQIE_API_KEY")
    if not api_key:
        return {
            "ok": False,
            "message": "Set FANQIE_API_KEY in environment or .env",
            "platform": "fanqie",
        }
    expires = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
    save_token(
        "fanqie",
        {
            "auth_type": "api_key",
            "api_key": api_key,
            "expires_at": expires,
        },
    )
    return {"ok": True, "message": "Fanqie API key saved", "platform": "fanqie"}
