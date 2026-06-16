"""Tests for G1 delivery hub package (read-only validation)."""



from __future__ import annotations



import json

import os

import subprocess

import sys

from pathlib import Path



from novel_suite.core import errors as E

from novel_suite.core.delivery_readiness import run_delivery_hub_validate, validate_delivery_hub





def test_delivery_hub_files_exist(repo_root: Path):

    checks = validate_delivery_hub()

    failed = [c for c in checks if not c.get("ok")]

    assert len(checks) >= 15

    assert not failed, failed





def test_delivery_hub_sample_blocked(repo_root: Path):

    data = json.loads(

        (repo_root / "novel-suite" / "delivery-hub" / "delivery-hub.sample.json").read_text(encoding="utf-8")

    )

    assert data["commercial_release_allowed"] is False

    assert data["verdict"] == "blocked"

    assert data["safe_demo_only"] is True





def test_four_roles_documented(repo_root: Path):

    text = (repo_root / "novel-suite" / "delivery-hub" / "role-based-onboarding.md").read_text(encoding="utf-8")

    for role in ("creator", "developer", "reviewer", "trial"):

        assert role in text.lower()





def test_run_delivery_hub_validate_ok():

    result = run_delivery_hub_validate()

    assert result.status == "ok"

    assert result.code == E.DELIVERY_HUB_VALIDATE_OK

    assert result.details.get("verdict") == "blocked"





def test_cli_delivery_hub_validate(repo_root: Path):

    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}

    r = subprocess.run(

        [sys.executable, "-m", "novel_suite.cli", "delivery-hub", "validate", "--json"],

        cwd=str(repo_root),

        capture_output=True,

        text=True,

        env=env,

    )

    assert r.returncode == 0, r.stderr + r.stdout

    data = json.loads(r.stdout)

    assert data["code"] == E.DELIVERY_HUB_VALIDATE_OK

