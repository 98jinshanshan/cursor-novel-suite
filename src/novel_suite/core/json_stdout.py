"""Ensure --json CLI mode writes only JSON to stdout."""

from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
from collections.abc import Iterator
from typing import Any
from unittest.mock import patch


@contextlib.contextmanager
def capture_legacy_output() -> Iterator[list[str]]:
    """Capture subprocess + print noise while scaffolding; lines for details.legacy_output."""
    lines: list[str] = []
    real_run = subprocess.run

    def _quiet_run(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        kwargs = dict(kwargs)
        kwargs["capture_output"] = True
        kwargs["text"] = True
        proc = real_run(*args, **kwargs)
        if proc.stdout:
            lines.extend(ln for ln in proc.stdout.splitlines() if ln.strip())
        if proc.stderr:
            lines.extend(ln for ln in proc.stderr.splitlines() if ln.strip())
        return proc

    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        with patch("subprocess.run", _quiet_run):
            yield lines


def write_json_stdout(payload: dict[str, Any]) -> None:
    """Write a single JSON document to stdout (no extra text)."""
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    sys.stdout.flush()
