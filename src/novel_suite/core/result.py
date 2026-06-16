"""JSON Result Contract — unified agent-parseable CLI output."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from typing import Any, Literal


Status = Literal["ok", "error"]


@dataclass
class Result:
    status: Status
    code: str
    message: str
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    required: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {k: v for k, v in data.items() if v or k in ("status", "code", "message")}

    def exit_code(self) -> int:
        return 0 if self.status == "ok" else 1


def artifact(path: str, *, kind: str = "file", label: str = "") -> dict[str, Any]:
    entry: dict[str, Any] = {"type": kind, "path": path}
    if label:
        entry["label"] = label
    return entry


def ok_result(
    code: str,
    message: str,
    *,
    artifacts: list[dict[str, Any]] | None = None,
    next_actions: list[str] | None = None,
    **details: Any,
) -> Result:
    return Result(
        status="ok",
        code=code,
        message=message,
        artifacts=artifacts or [],
        next_actions=next_actions or [],
        details=details,
    )


def error_result(
    code: str,
    message: str,
    *,
    required: list[str] | None = None,
    next_actions: list[str] | None = None,
    artifacts: list[dict[str, Any]] | None = None,
    **details: Any,
) -> Result:
    return Result(
        status="error",
        code=code,
        message=message,
        required=required or [],
        next_actions=next_actions or [],
        artifacts=artifacts or [],
        details=details,
    )


EMOJI_MAP: dict[str, str] = {
    "MEMORY_STORE_OK": "💾",
    "MEMORY_SEARCH_OK": "🔍",
    "MEMORY_PROBE_OK": "📡",
    "MEMORY_SYNC_OK": "🔄",
    "MEMORY_STATUS_OK": "💾",
    "SCAN_OK": "📊",
    "INIT_OK": "📖",
    "CHAPTER_DRAFT_OK": "✍️",
    "EXPORT_OK": "📦",
    "STORYBOARD_OK": "🎬",
    "STILLS_GENERATE_OK": "🖼️",
    "COMPOSE_OK": "🎥",
    "PIPELINE_OK": "🎞️",
    "GATE_OK": "✅",
    "PUBLISH_OK": "🚀",
    "PUBLISH_LIST_OK": "📋",
    "COOKIE_OK": "🔑",
    "AUTH_LOGIN_OK": "🔓",
    "AUTH_LOGOUT_OK": "🔒",
    "AUTH_STATUS_OK": "🔑",
    "ANALYTICS_RECORD_OK": "📝",
    "ANALYTICS_STATUS_OK": "📈",
    "ANALYTICS_REPORT_OK": "📈",
    "ANALYTICS_CROSS_OK": "📊",
    "MCP_SERVE_OK": "🌐",
    "DOCTOR_OK": "🩺",
    "DOCTOR_CORE_OK": "🩺",
    "PRODUCT_LIST_OK": "📚",
    "PRODUCT_READ_OK": "📄",
    "PRODUCT_VALIDATE_OK": "✅",
    "CLEAN_OK": "🧹",
    "CLEAN_DRY_RUN_OK": "🧹",
    "VERSION_OK": "ℹ️",
    "LIST_OK": "📋",
    "ACTIVE_OK": "ℹ️",
    "USE_OK": "ℹ️",
}


def _emoji_for_code(code: str, *, status: Status) -> str:
    if status == "error":
        return "❌"
    return EMOJI_MAP.get(code, "ℹ️")


def _supports_color() -> bool:
    if not hasattr(sys.stdout, "isatty"):
        return False
    try:
        return sys.stdout.isatty()
    except (ValueError, OSError):
        return False


def emit_human(result: Result) -> None:
    emoji = _emoji_for_code(result.code, status=result.status)
    use_color = _supports_color()
    if result.status == "ok":
        color = "\033[32m" if use_color else ""
    else:
        color = "\033[31m" if use_color else ""
    reset = "\033[0m" if use_color else ""

    stream = sys.stderr if result.status == "error" else sys.stdout
    print(f"{emoji} {color}{result.code}{reset} — {result.message}", file=stream)

    for item in result.required:
        print(f"  ⚠️ required: {item}", file=sys.stderr)
    if result.next_actions:
        print("  💡 下一步：", file=stream if result.status == "ok" else sys.stderr)
        for action in result.next_actions[:3]:
            target = stream if result.status == "ok" else sys.stderr
            print(f"     {action}", file=target)
    for art in result.artifacts[:5]:
        print(f"  📎 {art.get('path', art)}", file=stream)


def emit(result: Result, *, json_out: bool, blocked_summary: bool = False) -> int:
    if json_out:
        from novel_suite.core.json_stdout import write_json_stdout

        payload = result.to_dict()
        payload["emoji"] = _emoji_for_code(result.code, status=result.status)
        if blocked_summary:
            details = payload.get("details") or {}
            payload["commercial_release_allowed"] = details.get("commercial_release_allowed", False)
            payload["verdict"] = details.get("verdict", "blocked")
        write_json_stdout(payload)
    else:
        emit_human(result)
    return result.exit_code()
