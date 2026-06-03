"""Workspace doctor — skills, roots, layout version."""

from __future__ import annotations

from novel_suite.core import errors as E
from novel_suite.core.result import Result, artifact, emit, error_result, ok_result
from novel_suite.core.paths import suite_root
from novel_suite.writer._legacy import load_script_module


def run_doctor(*, core_only: bool = False, agents: list[str] | None = None) -> Result:
    try:
        root = suite_root()
    except RuntimeError as exc:
        return error_result(
            E.SUITE_ROOT_NOT_FOUND,
            str(exc),
            next_actions=[f"Set NOVEL_SUITE_ROOT or open monorepo containing .novel-suite-root"],
        )

    legacy = load_script_module("suite_doctor")
    checks, code = legacy.run_doctor(core_only=core_only, agents=agents)
    failed = [c for c in checks if not c["ok"]]
    arts = [artifact(str(root), kind="directory", label="suite_root")]

    if code == 0:
        return ok_result(
            "DOCTOR_OK",
            "Doctor: all checks passed.",
            artifacts=arts,
            checks=checks,
        )

    return error_result(
        E.DOCTOR_FAIL,
        f"Doctor: {len(failed)} check(s) failed.",
        required=[c["name"] for c in failed],
        next_actions=["Fix FAIL items in doctor output", "See docs/verification/trae-cn.md"],
        artifacts=arts,
        checks=checks,
    )


def cmd_doctor(*, json_out: bool, core_only: bool, agents: list[str] | None) -> int:
    return emit(run_doctor(core_only=core_only, agents=agents), json_out=json_out)
