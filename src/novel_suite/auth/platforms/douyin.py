"""Douyin OAuth2 login flow (authorization code + local callback)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from novel_suite.auth.server import find_callback_port, get_redirect_uri, start_callback_server
from novel_suite.auth.token_store import save_token
from novel_suite.core.env_config import getenv
from novel_suite.platforms._registry import get_platform


def _build_auth_url(client_id: str, redirect_uri: str) -> str:
    platform = get_platform("douyin") or {}
    base = str(platform.get("creator_url", "https://creator.douyin.com/")).rstrip("/")
    return (
        f"{base}/oauth/authorize?"
        f"client_id={client_id}&response_type=code&"
        f"redirect_uri={redirect_uri}&scope=video.upload"
    )


def _exchange_code(code: str, *, client_id: str) -> dict[str, Any]:
    """Exchange authorization code for tokens.

    Production should call Douyin OpenAPI. Dev mode stores a derived stub when no secret.
    """
    client_secret = getenv("DOUYIN_CLIENT_SECRET")
    if not client_secret:
        expires = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        return {
            "auth_type": "oauth2_cookie",
            "access_token": f"dev_access_{code[:16]}",
            "refresh_token": f"dev_refresh_{code[:16]}",
            "client_id": client_id,
            "expires_at": expires,
            "mode": "dev_stub",
        }
    # Placeholder for real HTTP token exchange when credentials are configured.
    expires = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    return {
        "auth_type": "oauth2_cookie",
        "access_token": f"exchanged_{code[:16]}",
        "refresh_token": f"refresh_{code[:16]}",
        "client_id": client_id,
        "expires_at": expires,
        "mode": "oauth_exchange_pending",
    }


def login_douyin(*, open_browser: bool = True) -> dict[str, Any]:
    client_id = getenv("DOUYIN_CLIENT_ID")
    port = find_callback_port()
    redirect_uri = get_redirect_uri(port)

    if not client_id:
        return {
            "ok": False,
            "message": (
                "DOUYIN_CLIENT_ID not set. Configure Open Platform credentials, "
                f"then open: {_build_auth_url('YOUR_CLIENT_ID', redirect_uri)}"
            ),
            "platform": "douyin",
            "redirect_uri": redirect_uri,
        }

    auth_url = _build_auth_url(client_id, redirect_uri)
    messages: list[str] = [f"Open this URL to authorize Douyin: {auth_url}"]

    if open_browser:
        try:
            import webbrowser

            webbrowser.open(auth_url)
            messages.append("Browser opened for Douyin login.")
        except OSError:
            messages.append("Could not open browser automatically.")

    code = start_callback_server(port=port, timeout_sec=300.0)
    if code is None:
        return {
            "ok": False,
            "message": "Login cancelled, timed out, or callback error",
            "platform": "douyin",
            "auth_url": auth_url,
            "hints": messages,
        }

    token_data = _exchange_code(code, client_id=client_id)
    save_token("douyin", token_data)
    return {
        "ok": True,
        "message": "Douyin login successful",
        "platform": "douyin",
        "expires_at": token_data.get("expires_at"),
        "mode": token_data.get("mode"),
    }
