"""Tests for video-production + handoff product layer (C4 read-only mount)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from novel_suite.core import errors as E
from novel_suite.core.product_layer import (
    list_product_assets,
    read_product_asset,
    run_product_validate,
    tool_product_list,
    tool_product_read,
    tool_product_validate,
    validate_product_layer,
)

VIDEO_CATEGORIES = (
    "video_production_contracts",
    "video_production_workflows",
    "video_production_gates",
    "video_production_adapters",
    "video_quality_definitions",
    "video_quality_gates",
    "video_quality_taxonomies",
    "video_quality_repair",
    "video_quality_reports",
    "video_handoff_common",
    "video_handoff_ai_generation",
    "video_handoff_timeline",
    "video_handoff_vfx",
    "video_handoff_local_processing",
    "video_handoff_rights_risk",
    "video_production_examples",
)


def test_list_includes_video_production_categories():
    data = list_product_assets()
    cats = data["categories"]
    for key in VIDEO_CATEGORIES:
        assert key in cats, key
    assert data.get("video_production_root") is not None


def test_video_production_contracts_count():
    cats = list_product_assets()["categories"]
    assert len(cats["video_production_contracts"]) >= 5


def test_video_production_workflows_count():
    cats = list_product_assets()["categories"]
    assert len(cats["video_production_workflows"]) >= 7


def test_video_production_adapters_count():
    cats = list_product_assets()["categories"]
    assert len(cats["video_production_adapters"]) >= 11


def test_video_quality_taxonomies_names():
    names = {a["name"] for a in list_product_assets()["categories"]["video_quality_taxonomies"]}
    for expected in ("transition_taxonomy", "effects_taxonomy", "defect_taxonomy"):
        assert expected in names, expected


def test_video_handoff_common_has_package_structure():
    names = {a["name"] for a in list_product_assets()["categories"]["video_handoff_common"]}
    assert "handoff_package_structure" in names


def test_read_video_production_workflow():
    asset = read_product_asset("video_production_workflows", "novel_to_short_drama")
    assert asset["category"] == "video_production_workflows"
    assert asset["name"] == "novel_to_short_drama"
    assert len(asset["content"]) > 100


def test_read_video_quality_definition():
    asset = read_product_asset("video_quality_definitions", "high_quality_video_definition")
    assert asset["category"] == "video_quality_definitions"
    assert "quality" in asset["content"].lower() or "质量" in asset["content"]


def test_read_video_handoff_common():
    asset = read_product_asset("video_handoff_common", "handoff_package_structure")
    assert asset["category"] == "video_handoff_common"
    assert "handoff" in asset["content"].lower() or "交接" in asset["content"]


def test_read_rejects_traversal():
    with pytest.raises(ValueError) as exc:
        read_product_asset("video_handoff_common", "../secrets")
    msg = str(exc.value)
    assert E.PRODUCT_INVALID_NAME in msg or E.PRODUCT_PATH_TRAVERSAL in msg


def test_validate_product_layer_includes_video_production():
    checks = validate_product_layer()
    names = {c["name"] for c in checks}
    assert any("video-production" in n or "contracts" in n for n in names)
    failed = [c for c in checks if not c.get("ok")]
    assert not failed, failed


def test_run_product_validate_ok():
    result = run_product_validate()
    assert result.status == "ok"
    assert result.code == "PRODUCT_VALIDATE_OK"


@pytest.mark.parametrize(
    "category,name",
    [
        ("video_production_workflows", "novel_to_short_drama"),
        ("video_quality_taxonomies", "transition_taxonomy"),
        ("video_handoff_common", "handoff_package_structure"),
    ],
)
def test_cli_product_read_video(repo_root: Path, category: str, name: str):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "novel_suite.cli",
            "product",
            "read",
            "--category",
            category,
            "--name",
            name,
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
    assert data["code"] == "PRODUCT_READ_OK"
    assert data["details"]["asset"]["name"] == name


def test_mcp_tool_product_list_video_categories():
    data = tool_product_list()
    assert data["status"] == "ok"
    cats = data["details"]["categories"]
    assert "video_production_workflows" in cats
    assert "video_handoff_common" in cats


def test_mcp_tool_product_read_workflow():
    data = tool_product_read("video_production_workflows", "novel_to_short_drama")
    assert data["status"] == "ok"
    assert data["details"]["asset"]["name"] == "novel_to_short_drama"


def test_mcp_tool_product_read_handoff():
    data = tool_product_read("video_handoff_common", "handoff_package_structure")
    assert data["status"] == "ok"
    assert data["details"]["asset"]["name"] == "handoff_package_structure"


def test_mcp_tool_product_validate_ok():
    data = tool_product_validate()
    assert data["status"] == "ok"
    assert data["code"] == "PRODUCT_VALIDATE_OK"


def test_mcp_tool_product_read_invalid_name():
    data = tool_product_read("video_handoff_common", "../evil")
    assert data["status"] == "error"
    assert data["code"] in (E.PRODUCT_INVALID_NAME, E.PRODUCT_NOT_FOUND)
