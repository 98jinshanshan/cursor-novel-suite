"""SVM-06: unified RESULT JSON line for video pipeline scripts."""

from __future__ import annotations

import json
import sys
from typing import Any


def emit_result(status: str, **fields: Any) -> None:
    payload = {"status": status, **fields}
    print(f"RESULT: {json.dumps(payload, ensure_ascii=False)}", flush=True)


def emit_error(message: str, **fields: Any) -> None:
    print(message, file=sys.stderr)
    emit_result("error", message=message, **fields)
