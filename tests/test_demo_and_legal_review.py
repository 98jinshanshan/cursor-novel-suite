"""Tests for G2 demo roadmap and G3 legal review packages."""



from __future__ import annotations



import json

import os

import subprocess

import sys

from pathlib import Path



from novel_suite.core import errors as E

from novel_suite.core.delivery_readiness import (

    run_demo_roadmap_validate,

    run_legal_release_review_validate,

    validate_demo_roadmap,

    validate_legal_release_review,

)





def test_demo_roadmap_files_exist(repo_root: Path):

    checks = validate_demo_roadmap()

    failed = [c for c in checks if not c.get("ok")]

    assert len(checks) >= 16

    assert not failed, failed





def test_demo_scripts_exist(repo_root: Path):

    base = repo_root / "novel-suite" / "demo-roadmap"

    assert (base / "demo_script_15min.md").is_file()

    assert (base / "demo_script_45min.md").is_file()





def test_demo_sample_no_external(repo_root: Path):

    data = json.loads(

        (repo_root / "novel-suite" / "demo-roadmap" / "demo-roadmap.sample.json").read_text(encoding="utf-8")

    )

    assert data["external_calls_allowed"] is False

    assert data["commercial_release_allowed"] is False





def test_legal_review_files_and_signatures(repo_root: Path):

    checks = validate_legal_release_review()

    failed = [c for c in checks if not c.get("ok")]

    assert len(checks) >= 18

    assert not failed, failed





def test_legal_sample_requires_manual(repo_root: Path):

    data = json.loads(

        (

            repo_root / "novel-suite" / "legal-release-review" / "legal-release-review.sample.json"

        ).read_text(encoding="utf-8")

    )

    assert data["legal_conclusion_auto_generated"] is False

    assert data["verdict"] == "blocked"

    assert len(data["signatures_required"]) >= 2





def test_run_demo_and_legal_validate_ok():

    demo = run_demo_roadmap_validate()

    legal = run_legal_release_review_validate()

    assert demo.code == E.DEMO_ROADMAP_VALIDATE_OK

    assert legal.code == E.LEGAL_RELEASE_REVIEW_VALIDATE_OK





def test_cli_demo_and_legal_validate(repo_root: Path):

    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}

    for cmd, code in (

        (["demo-roadmap", "validate"], E.DEMO_ROADMAP_VALIDATE_OK),

        (["legal-release-review", "validate"], E.LEGAL_RELEASE_REVIEW_VALIDATE_OK),

    ):

        r = subprocess.run(

            [sys.executable, "-m", "novel_suite.cli", *cmd, "--json"],

            cwd=str(repo_root),

            capture_output=True,

            text=True,

            env=env,

        )

        assert r.returncode == 0, r.stderr + r.stdout

        assert json.loads(r.stdout)["code"] == code

