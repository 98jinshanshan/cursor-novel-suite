"""Workspace doctor — skills, roots, layout version, novel-suite core layer."""

from __future__ import annotations

from typing import Any

from novel_suite.core import errors as E
from novel_suite.core.contracts import run_core_contract_checks
from novel_suite.core.result import Result, artifact, emit, error_result, ok_result
from novel_suite.core.paths import suite_root
from novel_suite.writer._legacy import load_script_module


def run_core_contracts_doctor() -> Result:
    try:
        root = suite_root()
    except RuntimeError as exc:
        return error_result(
            E.SUITE_ROOT_NOT_FOUND,
            str(exc),
            next_actions=["Set NOVEL_SUITE_ROOT or open monorepo containing .novel-suite-root"],
        )

    checks, code = run_core_contract_checks()
    failed = [c for c in checks if not c.get("ok")]
    arts = [
        artifact("novel-suite/README.md", kind="file", label="novel_suite_product"),
        artifact(str(root), kind="directory", label="suite_root"),
    ]

    if code == 0:
        return ok_result(
            "DOCTOR_CORE_OK",
            "Novel Suite core contracts and product layer: all checks passed.",
            artifacts=arts,
            checks=checks,
            next_actions=[
                "powershell -File platforms/install-rules-packs.ps1 -DryRun",
                "See novel-suite/docs/IMPLEMENTATION_SEQUENCE.md",
            ],
        )

    return error_result(
        E.DOCTOR_CORE_FAIL,
        f"Novel Suite core layer: {len(failed)} check(s) failed.",
        required=[c["name"] for c in failed],
        next_actions=[
            "Fix missing paths under novel-suite/",
            "See NOVEL_SUITE_ALIGNMENT_REPORT.md",
        ],
        artifacts=arts,
        checks=checks,
    )


def run_doctor(
    *,
    core_only: bool = False,
    core_contracts: bool = False,
    agents: list[str] | None = None,
) -> Result:
    if core_contracts and not core_only:
        return run_core_contracts_doctor()

    try:
        root = suite_root()
    except RuntimeError as exc:
        return error_result(
            E.SUITE_ROOT_NOT_FOUND,
            str(exc),
            next_actions=["Set NOVEL_SUITE_ROOT or open monorepo containing .novel-suite-root"],
        )

    legacy = load_script_module("suite_doctor")
    checks, code = legacy.run_doctor(core_only=core_only, agents=agents)
    arts: list[dict[str, Any]] = [artifact(str(root), kind="directory", label="suite_root")]

    if core_contracts:
        core_checks, core_code = run_core_contract_checks()
        checks = checks + core_checks
        if core_code != 0:
            code = core_code

    failed = [c for c in checks if not c.get("ok")]
    if code == 0:
        msg = "Doctor: all checks passed."
        result_code = "DOCTOR_OK"
        if core_contracts:
            msg = "Doctor + Novel Suite core layer: all checks passed."
            result_code = "DOCTOR_OK"
        return ok_result(
            result_code,
            msg,
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


def cmd_doctor(
    *,
    json_out: bool,
    core_only: bool,
    core_contracts: bool,
    agents: list[str] | None,
) -> int:
    return emit(
        run_doctor(core_only=core_only, core_contracts=core_contracts, agents=agents),
        json_out=json_out,
    )
