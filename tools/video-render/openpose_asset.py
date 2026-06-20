#!/usr/bin/env python3
"""Generate a single-subject OpenPose-style control map (no external models)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

# OpenPose limb colors (approximate COCO render palette)
_COLORS = {
    "head": (255, 0, 0),
    "torso": (255, 85, 0),
    "arm_r": (255, 170, 0),
    "arm_l": (255, 255, 0),
    "leg_r": (170, 255, 0),
    "leg_l": (85, 255, 0),
}

ASSET_NAME = "novel_suite_openpose_single.png"
ASSET_PATH = Path(__file__).resolve().parent / "assets" / ASSET_NAME


def _line(draw: ImageDraw.ImageDraw, a: tuple[int, int], b: tuple[int, int], color: tuple[int, int, int], w: int = 8) -> None:
    draw.line([a, b], fill=color, width=w)


def generate_openpose_single(width: int = 768, height: int = 1344) -> Image.Image:
    """Single standing figure centered — one person only, no stacked poses."""
    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx = width // 2

    # Normalized vertical anchors (single subject, mid-frame)
    y_head = int(height * 0.14)
    y_neck = int(height * 0.20)
    y_shoulder = int(height * 0.24)
    y_hip = int(height * 0.52)
    y_knee = int(height * 0.72)
    y_ankle = int(height * 0.92)

    shoulder_w = int(width * 0.11)
    hip_w = int(width * 0.07)
    head_r = int(width * 0.045)

    head = (cx, y_head)
    neck = (cx, y_neck)
    l_sh = (cx - shoulder_w, y_shoulder)
    r_sh = (cx + shoulder_w, y_shoulder)
    l_hip = (cx - hip_w, y_hip)
    r_hip = (cx + hip_w, y_hip)
    l_knee = (cx - hip_w, y_knee)
    r_knee = (cx + hip_w, y_knee)
    l_ank = (cx - hip_w, y_ankle)
    r_ank = (cx + hip_w, y_ankle)
    l_elbow = (cx - int(shoulder_w * 1.35), int((y_shoulder + y_hip) * 0.45))
    r_elbow = (cx + int(shoulder_w * 1.35), int((y_shoulder + y_hip) * 0.45))
    l_wrist = (cx - int(shoulder_w * 1.15), int(y_hip * 0.78))
    r_wrist = (cx + int(shoulder_w * 1.15), int(y_hip * 0.78))

    draw.ellipse(
        [head[0] - head_r, head[1] - head_r, head[0] + head_r, head[1] + head_r],
        fill=_COLORS["head"],
    )
    _line(draw, head, neck, _COLORS["head"], 6)
    _line(draw, neck, l_sh, _COLORS["torso"], 8)
    _line(draw, neck, r_sh, _COLORS["torso"], 8)
    _line(draw, l_sh, l_hip, _COLORS["torso"], 8)
    _line(draw, r_sh, r_hip, _COLORS["torso"], 8)
    _line(draw, l_hip, r_hip, _COLORS["torso"], 8)
    _line(draw, l_sh, l_elbow, _COLORS["arm_l"], 7)
    _line(draw, l_elbow, l_wrist, _COLORS["arm_l"], 7)
    _line(draw, r_sh, r_elbow, _COLORS["arm_r"], 7)
    _line(draw, r_elbow, r_wrist, _COLORS["arm_r"], 7)
    _line(draw, l_hip, l_knee, _COLORS["leg_l"], 7)
    _line(draw, l_knee, l_ank, _COLORS["leg_l"], 7)
    _line(draw, r_hip, r_knee, _COLORS["leg_r"], 7)
    _line(draw, r_knee, r_ank, _COLORS["leg_r"], 7)
    return img


def ensure_openpose_asset() -> Path:
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not ASSET_PATH.is_file() or ASSET_PATH.stat().st_size < 1000:
        generate_openpose_single().save(ASSET_PATH, format="PNG")
    return ASSET_PATH
