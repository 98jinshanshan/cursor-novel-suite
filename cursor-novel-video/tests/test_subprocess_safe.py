"""Shell-injection guards for FFmpeg/subprocess (Sprint 0 Day 3)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "engine" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from subprocess_safe import ShellInjectionError, check_output, run_command  # noqa: E402


def test_run_command_rejects_string():
    with pytest.raises(ShellInjectionError):
        run_command("ffmpeg -i x")  # type: ignore[arg-type]


def test_run_command_rejects_shell_true():
    with pytest.raises(ShellInjectionError):
        run_command(["echo", "hi"], shell=True)


def test_run_command_accepts_list():
    proc = run_command(
        ["python", "-c", "print('ok')"],
        capture_output=True,
        timeout=30,
    )
    assert proc.returncode == 0
    assert "ok" in (proc.stdout or "")


def test_check_output_echo():
    out = check_output(
        ["python", "-c", "print('probe')"],
        timeout=30,
    )
    assert "probe" in out.strip()
