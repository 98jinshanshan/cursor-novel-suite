"""Tests for VideoRender-2R-Quality-Fix image quality gate."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
VIDEO_RENDER = ROOT / "tools" / "video-render"
ADAPTERS = ROOT / "cursor-novel-video" / "adapters"

sys.path.insert(0, str(VIDEO_RENDER))
sys.path.insert(0, str(ADAPTERS))

from image_quality_check import (  # noqa: E402
    check_controlnet_used,
    check_human_anomaly,
    run_quality_check,
)
from comfyui_workflow import controlnet_openpose_workflow, safe_text2img_workflow  # noqa: E402


def _make_stacked_ghost(path: Path, width: int = 768, height: int = 1344) -> None:
    """Synthetic vertical twin — mimics stacked duplicate figures."""
    img = Image.new("RGB", (width, height), (40, 40, 50))
    draw = ImageDraw.Draw(img)
    figure_h = height // 3
    for offset in (int(height * 0.12), int(height * 0.48)):
        cx = width // 2
        draw.ellipse([cx - 40, offset, cx + 40, offset + 80], fill=(180, 160, 150))
        draw.rectangle([cx - 55, offset + 80, cx + 55, offset + figure_h - 40], fill=(90, 100, 120))
        draw.rectangle([cx - 90, offset + 100, cx - 55, offset + 200], fill=(90, 100, 120))
        draw.rectangle([cx + 55, offset + 100, cx + 90, offset + 200], fill=(90, 100, 120))
        draw.rectangle([cx - 40, offset + figure_h - 40, cx - 5, offset + figure_h + 60], fill=(60, 70, 80))
        draw.rectangle([cx + 5, offset + figure_h - 40, cx + 40, offset + figure_h + 60], fill=(60, 70, 80))
    img.save(path)


def _make_single_figure(path: Path, width: int = 768, height: int = 1344) -> None:
    img = Image.new("RGB", (width, height), (30, 30, 40))
    draw = ImageDraw.Draw(img)
    cx = width // 2
    y0 = int(height * 0.2)
    draw.ellipse([cx - 35, y0, cx + 35, y0 + 70], fill=(200, 180, 170))
    draw.rectangle([cx - 50, y0 + 70, cx + 50, y0 + 320], fill=(100, 110, 130))
    draw.rectangle([cx - 35, y0 + 320, cx - 5, y0 + 480], fill=(70, 80, 90))
    draw.rectangle([cx + 5, y0 + 320, cx + 35, y0 + 480], fill=(70, 80, 90))
    img.save(path)


def test_human_anomaly_rejects_stacked_ghost(tmp_path: Path):
    ghost = tmp_path / "ghost.png"
    _make_stacked_ghost(ghost)
    result = check_human_anomaly(ghost)
    assert result["passed"] is False
    assert result["critical"] is True
    assert result["anomalies"]


def test_human_anomaly_accepts_single_figure(tmp_path: Path):
    single = tmp_path / "single.png"
    _make_single_figure(single)
    result = check_human_anomaly(single)
    assert result["passed"] is True


def test_controlnet_is_critical():
    safe = safe_text2img_workflow("test")
    cn = controlnet_openpose_workflow("test")
    safe_result = check_controlnet_used(safe)
    cn_result = check_controlnet_used(cn)
    assert safe_result["critical"] is True
    assert safe_result["passed"] is False
    assert cn_result["passed"] is True


def test_run_quality_check_fails_without_controlnet(tmp_path: Path):
    img = tmp_path / "one.png"
    _make_single_figure(img)
    wf = safe_text2img_workflow("test prompt")
    result = run_quality_check(img, prompt="test", workflow_data=wf, auto_delete=False)
    assert result["overall_passed"] is False
    assert "controlnet_used" in result["critical_failed"]


def test_run_quality_check_fails_stacked_ghost_with_controlnet(tmp_path: Path):
    img = tmp_path / "ghost.png"
    _make_stacked_ghost(img)
    wf = controlnet_openpose_workflow("test prompt")
    result = run_quality_check(img, prompt="test", workflow_data=wf, auto_delete=True)
    assert result["overall_passed"] is False
    assert "human_anomaly" in result["critical_failed"]
    assert result["auto_delete_executed"] is True
    assert not img.exists()
