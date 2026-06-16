"""Tests for Novel Suite product layer (B2 read-only CLI)."""

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
    run_product_list,
    run_product_validate,
    validate_product_layer,
)

REPO = Path(__file__).resolve().parents[1]


def test_list_product_assets_categories(repo_root: Path):
    data = list_product_assets()
    cats = data["categories"]
    for key in (
        "workflows",
        "contracts",
        "gates",
        "prompt_packs",
        "rules_packs",
        "adapters",
        "examples",
    ):
        assert key in cats, key
        assert isinstance(cats[key], list)
    assert any(a["name"] == "chapter_writing" for a in cats["workflows"])
    assert data["asset_count"] > 0


def test_read_product_asset_workflow(repo_root: Path):
    asset = read_product_asset("workflows", "chapter_writing")
    assert asset["category"] == "workflows"
    assert asset["name"] == "chapter_writing"
    assert "chapter" in asset["content"].lower() or "章" in asset["content"]
    assert asset["type"] == "markdown"


def test_read_product_asset_rejects_traversal():
    with pytest.raises(ValueError) as exc:
        read_product_asset("workflows", "../secrets")
    assert E.PRODUCT_INVALID_NAME in str(exc.value) or E.PRODUCT_PATH_TRAVERSAL in str(exc.value)


def test_validate_product_layer_ok(repo_root: Path):
    checks = validate_product_layer()
    failed = [c for c in checks if not c.get("ok")]
    assert not failed, failed


def test_run_product_list_ok():
    result = run_product_list()
    assert result.status == "ok"
    assert result.code == "PRODUCT_LIST_OK"


def test_run_product_validate_ok():
    result = run_product_validate()
    assert result.status == "ok"
    assert result.code == "PRODUCT_VALIDATE_OK"


def test_cli_product_list_json(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "product", "list", "--json"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    data = json.loads(r.stdout)
    assert data["status"] == "ok"
    assert data["code"] == "PRODUCT_LIST_OK"
    assert "categories" in data["details"]


def test_cli_product_validate_json(repo_root: Path):
    env = {**os.environ, "NOVEL_SUITE_ROOT": str(repo_root)}
    r = subprocess.run(
        [sys.executable, "-m", "novel_suite.cli", "product", "validate", "--json"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    data = json.loads(r.stdout)
    assert data["status"] == "ok"
    assert data["code"] == "PRODUCT_VALIDATE_OK"
