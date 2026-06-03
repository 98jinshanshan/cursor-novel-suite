"""Doctor returns Result Contract."""

from __future__ import annotations

from novel_suite.writer import doctor


def test_doctor_core_only_ok(repo_root):
    result = doctor.run_doctor(core_only=True)
    assert result.status == "ok"
    assert result.code == "DOCTOR_OK"
    assert any(a.get("label") == "suite_root" for a in result.artifacts)
