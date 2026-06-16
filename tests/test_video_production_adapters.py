"""Tests for C5 default-off video-production adapter dry-run skeletons."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from novel_suite.core import errors as E
from novel_suite.video_production.adapters import (
    AdapterPolicyError,
    assert_dry_run_only,
    default_adapter_policy,
    run_comfyui_dry_run,
    run_davinci_dry_run,
    run_otio_dry_run,
)
from novel_suite.video_production.cli import run_adapter_dry_run

EXAMPLE = "cold_case_echo_short_drama"


def _handoff_dir(repo_root: Path) -> Path:
    return (
        repo_root
        / "novel-suite"
        / "video-production"
        / "examples"
        / EXAMPLE
        / "handoff"
    )


def test_default_adapter_policy_closed():
    policy = default_adapter_policy("comfyui")
    assert policy["enabled"] is False
    assert policy["dry_run"] is True
    assert policy["allow_external_call"] is False
    assert policy["manual_execution_required"] is True


def test_assert_dry_run_only_rejects_enabled():
    policy = default_adapter_policy("otio")
    policy["enabled"] = True
    with pytest.raises(AdapterPolicyError):
        assert_dry_run_only(policy)


def test_assert_dry_run_only_rejects_external_call():
    policy = default_adapter_policy("davinci-resolve")
    policy["allow_external_call"] = True
    with pytest.raises(AdapterPolicyError):
        assert_dry_run_only(policy)


def test_comfyui_dry_run_writes_plan(repo_root: Path, tmp_path: Path):
    handoff = _handoff_dir(repo_root)
    with patch("socket.socket") as mock_socket:
        plan = run_comfyui_dry_run(handoff, tmp_path)
        mock_socket.assert_not_called()
    out = tmp_path / "comfyui_plan.json"
    assert out.is_file()
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved["adapter"] == "comfyui"
    assert saved["enabled"] is False
    assert saved["external_call_performed"] is False
    assert saved["prompt_count"] >= 1
    assert plan["mode"] == "dry_run_plan_only"


def test_otio_dry_run_writes_outline(repo_root: Path, tmp_path: Path):
    handoff = _handoff_dir(repo_root)
    assert "opentimelineio" not in sys.modules
    plan = run_otio_dry_run(handoff, tmp_path)
    out = tmp_path / "otio_outline.generated.json"
    assert out.is_file()
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved["adapter"] == "opentimelineio"
    assert saved["external_call_performed"] is False
    assert saved["external_dependency_required"] == "opentimelineio"
    assert len(saved["clips"]) >= 1
    assert plan["mode"] == "dry_run_outline_only"


def test_davinci_dry_run_writes_import_plan(repo_root: Path, tmp_path: Path):
    handoff = _handoff_dir(repo_root)
    plan = run_davinci_dry_run(handoff, tmp_path)
    out = tmp_path / "davinci_import_plan.json"
    assert out.is_file()
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved["adapter"] == "davinci-resolve"
    assert saved["manual_execution_required"] is True
    assert saved["external_call_performed"] is False
    assert len(saved["timeline_clips"]) >= 1
    assert plan["mode"] == "dry_run_import_plan_only"


@pytest.mark.parametrize("adapter", ["comfyui", "otio", "davinci"])
def test_cli_adapter_dry_run(repo_root: Path, adapter: str):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    out_rel = f".tmp/novel-suite-c5-pytest-{adapter}"
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "novel_suite.cli",
            "video-production",
            "adapter",
            "dry-run",
            "--adapter",
            adapter,
            "--example",
            EXAMPLE,
            "--output",
            out_rel,
            "--json",
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    data = json.loads(r.stdout)
    assert data["status"] == "ok"
    assert data["code"] == E.VIDEO_PRODUCTION_ADAPTER_DRY_RUN_OK
    plan = data["details"]["plan"]
    assert plan["external_call_performed"] is False
    assert Path(plan["output_path"]).is_file()


def test_run_adapter_dry_run_no_network(repo_root: Path):
    with patch("urllib.request.urlopen") as mock_urlopen:
        result = run_adapter_dry_run("comfyui", EXAMPLE, ".tmp/novel-suite-c5-net-test")
        mock_urlopen.assert_not_called()
    assert result.status == "ok"
    assert result.code == E.VIDEO_PRODUCTION_ADAPTER_DRY_RUN_OK


def test_run_adapter_dry_run_unknown_adapter():
    result = run_adapter_dry_run("runway", EXAMPLE, None)
    assert result.status == "error"
    assert result.code == E.VIDEO_PRODUCTION_ADAPTER_UNKNOWN
