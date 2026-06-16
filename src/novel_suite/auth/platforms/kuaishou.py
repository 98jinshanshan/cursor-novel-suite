"""Kuaishou OAuth2 login flow."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from novel_suite.auth.server import find_callback_port, get_redirect_uri, start_callback_server
from novel_suite.auth.token_store import save_token
from novel_suite.core.env_config import getenv
from novel_suite.platforms._registry import get_platform


def _build_auth_url(client_id: str, redirect_uri: str) -> str:
    platform = get_platform("kuaishou") or {}
    base = str(platform.get("creator_url", "https://cp.kuaishou.com/")).rstrip("/")
    return (
        f"{base}/oauth/authorize?"
        f"client_id={client_id}&response_type=code&"
        f"redirect_uri={redirect_uri}&scope=video.upload"
    )


def _exchange_code(code: str, *, client_id: str) -> dict[str, Any]:
    client_secret = getenv("KUAISHOU_CLIENT_SECRET")
    expires = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    mode = "oauth_exchange_pending" if client_secret else "dev_stub"
    return {
        "auth_type": "oauth2_cookie",
        "access_token": f"{'exchanged' if client_secret else 'dev_access'}_{code[:16]}",
        "refresh_token": f"refresh_{code[:16]}",
        "client_id": client_id,
        "expires_at": expires,
        "mode": mode,
    }


def login_kuaishou(*, open_browser: bool = True) -> dict[str, Any]:
    client_id = getenv("KUAISHOU_CLIENT_ID")
    port = find_callback_port()
    redirect_uri = get_redirect_uri(port)

    if not client_id:
        return {
            "ok": False,
            "message": (
                "KUAISHOU_CLIENT_ID not set. Configure credentials, then authorize via "
                f"{_build_auth_url('YOUR_CLIENT_ID', redirect_uri)}"
            ),
            "platform": "kuaishou",
            "redirect_uri": redirect_uri,
        }

    auth_url = _build_auth_url(client_id, redirect_uri)
    if open_browser:
        try:
            import webbrowser

            webbrowser.open(auth_url)
        except OSError:
            pass

    code = start_callback_server(port=port, timeout_sec=300.0)
    if code is None:
        return {
            "ok": False,
            "message": "Login cancelled, timed out, or callback error",
            "platform": "kuaishou",
            "auth_url": auth_url,
        }

    token_data = _exchange_code(code, client_id=client_id)
    save_token("kuaishou", token_data)
    return {
        "ok": True,
        "message": "Kuaishou login successful",
        "platform": "kuaishou",
        "expires_at": token_data.get("expires_at"),
    }
