"""Agent protocol helpers — parse Result Contract from CLI stdout."""

from __future__ import annotations

import json
from typing import Any

from novel_suite.core.result import Result


def parse_result(stdout: str) -> Result:
    data: dict[str, Any] = json.loads(stdout.strip())
    return Result(
        status=data["status"],
        code=data.get("code", ""),
        message=data.get("message", ""),
        artifacts=list(data.get("artifacts", [])),
        next_actions=list(data.get("next_actions", [])),
        required=list(data.get("required", [])),
        details={k: v for k, v in data.items() if k not in Result.__dataclass_fields__},
    )
