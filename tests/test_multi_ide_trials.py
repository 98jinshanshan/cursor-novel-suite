"""Tests for C10 multi-IDE trials package (read-only validation)."""



from __future__ import annotations



import json

import os

import subprocess

import sys

from pathlib import Path



from novel_suite.core import errors as E

from novel_suite.core.trace_state import run_multi_ide_trials_validate, validate_multi_ide_trials





def test_multi_ide_trials_files_exist(repo_root: Path):

    checks = validate_multi_ide_trials()

    failed = [c for c in checks if not c.get("ok")]

    assert len(checks) >= 18

    assert not failed, failed





def test_feedback_sample_schema_fields(repo_root: Path):

    path = repo_root / "novel-suite" / "multi-ide-trials" / "trial_feedback_form.sample.json"

    data = json.loads(path.read_text(encoding="utf-8"))

    for field in (

        "trial_id",

        "ide_name",

        "agent_surface",

        "task_id",

        "workflow_id",

        "success",

        "failure_type",

        "confusion_points",

        "missing_context",

        "unexpected_behavior",

        "trace_sample_path",

        "suggested_fix",

        "risk_observed",

        "external_call_attempted",

    ):

        assert field in data, field

    assert data["external_call_attempted"] is False





def test_trial_cards_exist(repo_root: Path):

    cards = repo_root / "novel-suite" / "multi-ide-trials" / "trial_cards"

    expected = {

        "cursor_trial_card.md",

        "codex_trial_card.md",

        "trae_cn_trial_card.md",

        "qoder_trial_card.md",

        "openclaw_trial_card.md",

        "generic_agent_trial_card.md",

    }

    found = {p.name for p in cards.glob("*.md")}

    assert expected <= found





def test_run_multi_ide_trials_validate_ok():

    result = run_multi_ide_trials_validate()

    assert result.status == "ok"

    assert result.code == E.MULTI_IDE_TRIALS_VALIDATE_OK





def test_cli_multi_ide_trials_validate(repo_root: Path):

    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}

    r = subprocess.run(

        [sys.executable, "-m", "novel_suite.cli", "multi-ide-trials", "validate", "--json"],

        cwd=str(repo_root),

        capture_output=True,

        text=True,

        env=env,

    )

    assert r.returncode == 0, r.stderr + r.stdout

    data = json.loads(r.stdout)

    assert data["code"] == E.MULTI_IDE_TRIALS_VALIDATE_OK

