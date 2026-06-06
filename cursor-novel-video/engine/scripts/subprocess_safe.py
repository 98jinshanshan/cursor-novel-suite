"""Safe subprocess helpers — list args only, no shell (Sprint 0 Day 3 / CHK-006)."""

from __future__ import annotations

import subprocess
from typing import Any


class ShellInjectionError(ValueError):
    """Raised when a subprocess call would use shell or string command."""


def _validate_cmd(cmd: list[str]) -> list[str]:
    if not isinstance(cmd, list):
        raise ShellInjectionError("Command must be a list of arguments, not a string")
    if not cmd:
        raise ShellInjectionError("Empty command")
    return [str(part) for part in cmd]


def run_command(
    cmd: list[str],
    *,
    timeout: float = 600,
    check: bool = False,
    capture_output: bool = False,
    text: bool = True,
    **kwargs: Any,
) -> subprocess.CompletedProcess[str]:
    """Run external process with array args and mandatory timeout."""
    if kwargs.pop("shell", False):
        raise ShellInjectionError("shell=True is forbidden")
    argv = _validate_cmd(cmd)
    return subprocess.run(
        argv,
        timeout=timeout,
        check=check,
        capture_output=capture_output,
        text=text,
        **kwargs,
    )


def check_output(cmd: list[str], *, timeout: float = 120, **kwargs: Any) -> str:
    if kwargs.pop("shell", False):
        raise ShellInjectionError("shell=True is forbidden")
    argv = _validate_cmd(cmd)
    return subprocess.check_output(argv, timeout=timeout, text=True, **kwargs)
