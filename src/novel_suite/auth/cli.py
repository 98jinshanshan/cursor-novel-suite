"""CLI handlers for platform authentication."""

from __future__ import annotations

import argparse
from typing import Any

from novel_suite.core import errors as E
from novel_suite.core.result import Result, error_result, ok_result
from novel_suite.auth.token_store import all_token_statuses, delete_token, token_status
from novel_suite.platforms._registry import list_platform_keys, validate_platform


def cmd_auth_login(args: argparse.Namespace) -> Result:
    platform: str = (args.platform or "").strip().lower()
    if not validate_platform(platform):
        return error_result(E.PLATFORM_UNKNOWN, f"Unknown platform: {platform}")

    result: dict[str, Any]
    if platform == "douyin":
        from novel_suite.auth.platforms.douyin import login_douyin

        result = login_douyin()
    elif platform == "kuaishou":
        from novel_suite.auth.platforms.kuaishou import login_kuaishou

        result = login_kuaishou()
    elif platform == "bilibili":
        from novel_suite.auth.platforms.bilibili import login_bilibili

        result = login_bilibili()
    elif platform == "fanqie":
        from novel_suite.auth.platforms.fanqie import login_fanqie

        result = login_fanqie()
    else:
        result = {
            "ok": False,
            "message": f"{platform} OAuth login not yet implemented (Phase B)",
            "platform": platform,
        }

    if result.get("ok"):
        return ok_result(
            E.AUTH_LOGIN_OK,
            str(result.get("message", "Login successful")),
            platform=platform,
            auth_result=result,
        )
    return error_result(
        E.AUTH_LOGIN_FAILED,
        str(result.get("message", "Login failed")),
        platform=platform,
        auth_result=result,
        next_actions=[f"novel-suite auth login --platform {platform} --json"],
    )


def cmd_auth_logout(args: argparse.Namespace) -> Result:
    platform: str = (args.platform or "").strip().lower()
    if not validate_platform(platform):
        return error_result(E.PLATFORM_UNKNOWN, f"Unknown platform: {platform}")
    delete_token(platform)
    return ok_result(E.AUTH_LOGOUT_OK, f"Logged out from {platform}", platform=platform)


def cmd_auth_status(args: argparse.Namespace) -> Result:
    platform = getattr(args, "platform", None)
    if platform:
        key = platform.strip().lower()
        if not validate_platform(key):
            return error_result(E.PLATFORM_UNKNOWN, f"Unknown platform: {key}")
        status = token_status(key)
        code = E.AUTH_STATUS_OK if status["valid"] else E.AUTH_STATUS_EMPTY
        return ok_result(
            code,
            f"Auth status for {key}",
            platform=key,
            statuses=[status],
        )

    statuses = all_token_statuses()
    logged_in = sum(1 for s in statuses if s.get("valid"))
    return ok_result(
        E.AUTH_STATUS_OK,
        f"Auth status: {logged_in}/{len(statuses)} platform(s) logged in",
        statuses=statuses,
        platforms=list_platform_keys(),
    )
