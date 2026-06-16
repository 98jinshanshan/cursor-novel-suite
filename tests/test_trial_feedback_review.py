"""Tests for C11 trial feedback review package (read-only validation)."""



from __future__ import annotations



import json

import os

import subprocess

import sys

from pathlib import Path



from novel_suite.core import errors as E

from novel_suite.core.future_backends import (

    run_trial_feedback_review_validate,

    validate_trial_feedback_review,

)





def test_c11_files_exist(repo_root: Path):

    checks = validate_trial_feedback_review()

    failed = [c for c in checks if not c.get("ok")]

    assert len(checks) >= 16

    assert not failed, failed





def test_feedback_classification_categories(repo_root: Path):

    path = repo_root / "novel-suite" / "trial-feedback-review" / "feedback_classification.sample.json"

    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["commercial_release_allowed"] is False

    assert data["external_call_attempted"] is False

    assert len(data["categories"]) >= 1

    schema = json.loads(

        (repo_root / "novel-suite" / "trial-feedback-review" / "feedback_classification.schema.json").read_text(

            encoding="utf-8"

        )

    )

    allowed = set(schema["properties"]["categories"]["items"]["enum"])

    assert set(data["categories"]) <= allowed





def test_revision_rules_exist(repo_root: Path):

    base = repo_root / "novel-suite" / "trial-feedback-review"

    for name in (

        "prompt_pack_revision_rules.md",

        "rules_pack_revision_rules.md",

        "workflow_contract_revision_rules.md",

        "trace_state_revision_rules.md",

        "commercial_claims_revision_rules.md",

    ):

        assert (base / name).is_file(), name





def test_run_trial_feedback_review_validate_ok():

    result = run_trial_feedback_review_validate()

    assert result.status == "ok"

    assert result.code == E.TRIAL_FEEDBACK_REVIEW_VALIDATE_OK





def test_cli_trial_feedback_review_validate(repo_root: Path):

    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}

    r = subprocess.run(

        [sys.executable, "-m", "novel_suite.cli", "trial-feedback-review", "validate", "--json"],

        cwd=str(repo_root),

        capture_output=True,

        text=True,

        env=env,

    )

    assert r.returncode == 0, r.stderr + r.stdout

    data = json.loads(r.stdout)

    assert data["code"] == E.TRIAL_FEEDBACK_REVIEW_VALIDATE_OK

