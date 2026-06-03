"""Result Contract serialization and exit codes."""

from __future__ import annotations

import json

from novel_suite.core.result import Result, artifact, emit, error_result, ok_result


def test_ok_result_to_dict():
    r = ok_result("GATE_OK", "passed", artifacts=[artifact("novels/x")], phase=1)
    d = r.to_dict()
    assert d["status"] == "ok"
    assert d["code"] == "GATE_OK"
    assert d["artifacts"][0]["path"] == "novels/x"
    assert d["details"]["phase"] == 1


def test_error_result_required_and_next_actions():
    r = error_result(
        "PHASE0_NOT_COMPLETE",
        "Phase 0 incomplete",
        required=["task_plan.md Phase 0 [x]"],
        next_actions=["Run writer scan"],
    )
    assert r.exit_code() == 1
    d = r.to_dict()
    assert d["status"] == "error"
    assert len(d["required"]) == 1
    assert len(d["next_actions"]) == 1


def test_emit_json(capsys):
    code = emit(ok_result("TEST", "ok"), json_out=True)
    assert code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["status"] == "ok"
