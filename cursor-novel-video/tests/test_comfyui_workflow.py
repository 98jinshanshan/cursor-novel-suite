"""Tests for ComfyUI UI→API workflow conversion (L2)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ADAPTERS = Path(__file__).resolve().parents[1] / "adapters"
sys.path.insert(0, str(ADAPTERS))

from comfyui_workflow import minimal_image_workflow, ui_workflow_to_api  # noqa: E402


def test_minimal_image_workflow_has_save_image():
    api = minimal_image_workflow("test prompt")
    assert "7" in api
    assert api["7"]["class_type"] == "SaveImage"
    assert api["2"]["inputs"]["text"] == "test prompt"


def test_ui_workflow_to_api_minimal_nodes():
    ui = {
        "nodes": [
            {
                "id": 1,
                "type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "model.safetensors"},
                "outputs": ["MODEL", "CLIP", "VAE"],
            },
            {
                "id": 2,
                "type": "CLIPTextEncode",
                "inputs": {"text": "hello", "clip": [1, 1, "CLIP"]},
                "outputs": ["CONDITIONING"],
            },
        ]
    }
    api = ui_workflow_to_api(ui)
    assert api["1"]["class_type"] == "CheckpointLoaderSimple"
    assert api["2"]["inputs"]["clip"] == ["1", 1]


def test_ui_workflow_already_api_format():
    api_in = {"3": {"class_type": "SaveImage", "inputs": {"images": ["2", 0]}}}
    assert ui_workflow_to_api(api_in) == api_in


def test_convert_external_workflow_file():
    wf = Path(
        r"G:\Projects\AI-Creative\video-editing-workflow\workflows\动态漫工作流\文本到动态漫画视频_fixed.json"
    )
    if not wf.is_file():
        pytest.skip("external ComfyUI workflow not on disk")
    data = json.loads(wf.read_text(encoding="utf-8"))
    api = ui_workflow_to_api(data, node_ids={1, 2, 3, 4, 5, 6})
    assert len(api) >= 6
    assert all("class_type" in n for n in api.values())
