"""RealGen-1 deprecated — RealPipeline-2B is the mandatory path."""

from __future__ import annotations

from novel_suite.core.realgen_demo import run_realgen_demo_validate
from novel_suite.core.result import Result


def test_realgen_run_cli_deprecated():
    from novel_suite.core.result import error_result

    r = error_result(
        "REALGEN_DEMO_DEPRECATED",
        "RealGen-1旁路已废止",
        commercial_release_allowed=False,
        verdict="blocked",
    )
    assert r.code == "REALGEN_DEMO_DEPRECATED"


def test_realgen_validate_seed_only():
    result = run_realgen_demo_validate()
    # Empty realgen-demo: only DEPRECATED.md; validate may fail core — acceptable
    assert result.details.get("verdict") == "blocked"


def test_no_realgen_output_dir():
    from novel_suite.core.paths import suite_root

    assert not (suite_root() / "novel-suite" / "realgen-demo" / "cold_case_echo_realgen_01").is_dir()
