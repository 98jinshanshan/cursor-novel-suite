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


def emit_human(result: Result) -> None:
    stream = sys.stderr if result.status == "error" else sys.stdout
    print(result.message, file=stream)
    for item in result.required:
        print(f"  required: {item}", file=sys.stderr)
    for action in result.next_actions:
        print(f"  next: {action}", file=sys.stderr)
    for art in result.artifacts:
        print(f"  artifact: {art.get('path', art)}", file=stream)


def emit(result: Result, *, json_out: bool) -> int:
    if json_out:
        from novel_suite.core.json_stdout import write_json_stdout

        write_json_stdout(result.to_dict())
    else:
        emit_human(result)
    return result.exit_code()
