"""Tests for Novel Suite MCP product-layer tools (B2)."""

from __future__ import annotations

from novel_suite.core import errors as E
from novel_suite.core.product_layer import (
    tool_product_list,
    tool_product_read,
    tool_product_validate,
)


def test_tool_product_list_categories():
    data = tool_product_list()
    assert data["status"] == "ok"
    assert data["code"] == "PRODUCT_LIST_OK"
    cats = data["details"]["categories"]
    assert "workflows" in cats
    assert "contracts" in cats


def test_tool_product_validate_ok():
    data = tool_product_validate()
    assert data["status"] == "ok"
    assert data["code"] == "PRODUCT_VALIDATE_OK"
    assert data["details"].get("checks")


def test_tool_product_read_workflow():
    data = tool_product_read("workflows", "chapter_writing")
    assert data["status"] == "ok"
    assert data["code"] == "PRODUCT_READ_OK"
    asset = data["details"]["asset"]
    assert asset["name"] == "chapter_writing"
    assert "content" in asset


def test_tool_product_read_invalid_name():
    data = tool_product_read("workflows", "../evil")
    assert data["status"] == "error"
    assert data["code"] in (E.PRODUCT_INVALID_NAME, E.PRODUCT_NOT_FOUND)
