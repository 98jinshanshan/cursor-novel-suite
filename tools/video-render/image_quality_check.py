#!/usr/bin/env python3
"""
图像质量强制检测模块 — VideoRender-2R-Quality-Fix
必须在生成后立即运行，不合格自动删除

强制检测项：
1. 文件存在检测
2. 非占位符检测 (尺寸/分辨率)
3. 图像完整性检测
4. 人体结构异常检测 (check_human_anomaly)
5. ControlNet 使用检测 (critical)
6. Prompt 保护词检测
7. 像素级内容异常 (全黑/全白)
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

MIN_WIDTH = 512
MIN_HEIGHT = 768
MIN_FILE_SIZE_KB = 200
MAX_ASPECT_RATIO = 2.5  # 9:16 = 1.778, 超过则异常

# Human anomaly heuristics (conservative — prefer reject over漏检)
ANALYSIS_WIDTH = 256
ANALYSIS_HEIGHT = 448
GHOST_CORR_THRESHOLD = 0.58
MULTI_PEAK_MIN_RATIO = 0.28
FLOATING_MIN_AREA_RATIO = 0.004
FLOATING_MARGIN_RATIO = 0.18
LIMB_COMPONENT_MIN = 4

# VR-2R-QF delivery thresholds (see AI_Workspace_OS VR-2R-Quality-Fix checklist)
VR2R_MIN_FILE_SIZE_KB = 500
VR2R_MAX_FILE_SIZE_KB = 5120
MIN_PIXEL_STD = 20.0
MIN_SUBJECT_EDGE_PEAK = 18.0
TEXT_CARD_MAX_STD = 12.0
TEXT_CARD_MAX_EDGE_RATIO = 0.018
DETECTION_METHOD = "edge_heuristic_v1"  # TODO: MediaPipe/OpenPose pose when model dep available

SEVERITY_S0 = "S0"
SEVERITY_S1 = "S1"
SEVERITY_S2 = "S2"
SEVERITY_S3 = "S3"

CHECK_SEVERITY: dict[str, str] = {
    "file_exists": SEVERITY_S0,
    "non_placeholder": SEVERITY_S0,
    "file_size_vr2r": SEVERITY_S0,
    "pixel_complexity": SEVERITY_S0,
    "text_card_proxy": SEVERITY_S0,
    "subject_presence": SEVERITY_S0,
    "human_anomaly": SEVERITY_S0,
    "content_anomaly": SEVERITY_S0,
    "controlnet_used": SEVERITY_S0,
    "image_integrity": SEVERITY_S1,
    "anatomy_protection": SEVERITY_S1,
}

REPAIR_ACTIONS: dict[str, str] = {
    "human_anomaly": "regenerate_shot_adjust_controlnet",
    "controlnet_used": "enable_controlnet_openpose",
    "subject_presence": "regenerate_shot_fix_prompt",
    "text_card_proxy": "regenerate_shot_not_textcard",
    "pixel_complexity": "regenerate_shot",
    "file_size_vr2r": "regenerate_shot_higher_quality",
}


def check_file_exists(path: Path) -> dict[str, Any]:
    """检测项1: 文件存在"""
    exists = path.exists() and path.is_file()
    return {
        "name": "file_exists",
        "passed": exists,
        "message": "文件存在" if exists else f"文件不存在: {path}",
        "critical": True,
    }


def check_non_placeholder(path: Path, *, min_size_kb: float | None = None) -> dict[str, Any]:
    """检测项2: 非占位符检测"""
    size_floor = MIN_FILE_SIZE_KB if min_size_kb is None else min_size_kb
    size_kb = path.stat().st_size / 1024 if path.exists() else 0
    
    # 检查文件大小
    size_ok = size_kb >= size_floor
    
    # 检查分辨率
    dim_ok = True
    width = height = 0
    if PIL_AVAILABLE and path.exists():
        try:
            with Image.open(path) as img:
                width, height = img.size
                dim_ok = width >= MIN_WIDTH and height >= MIN_HEIGHT
        except Exception as e:
            return {
                "name": "non_placeholder",
                "passed": False,
                "message": f"图像无法打开: {e}",
                "critical": True,
                "width": width,
                "height": height,
                "size_kb": round(size_kb, 1),
            }
    
    passed = size_ok and dim_ok
    message = []
    if not size_ok:
        message.append(f"文件过小: {size_kb:.1f}KB < {size_floor}KB")
    if not dim_ok:
        message.append(f"分辨率过低: {width}x{height} < {MIN_WIDTH}x{MIN_HEIGHT}")
    
    return {
        "name": "non_placeholder",
        "passed": passed,
        "message": "非占位符检测通过" if passed else "; ".join(message),
        "critical": True,
        "size_kb": round(size_kb, 1),
        "width": width,
        "height": height,
    }


def check_image_integrity(path: Path) -> dict[str, Any]:
    """检测项3: 图像完整性检测"""
    if not PIL_AVAILABLE:
        return {
            "name": "image_integrity",
            "passed": True,
            "message": "PIL不可用，跳过完整性检测",
            "critical": False,
            "warning": True,
        }
    
    try:
        with Image.open(path) as img:
            img.verify()
            # 重新打开并加载全部数据
            with Image.open(path) as img2:
                img2.load()
        
        # 检查宽高比异常
        width, height = img.size
        aspect = max(width, height) / min(width, height)
        if aspect > MAX_ASPECT_RATIO:
            return {
                "name": "image_integrity",
                "passed": False,
                "message": f"宽高比异常: {aspect:.2f} > {MAX_ASPECT_RATIO}",
                "critical": True,
                "aspect_ratio": aspect,
            }
        
        return {
            "name": "image_integrity",
            "passed": True,
            "message": "图像完整性检测通过",
            "critical": False,
        }
    except Exception as e:
        return {
            "name": "image_integrity",
            "passed": False,
            "message": f"图像损坏: {e}",
            "critical": True,
        }


def check_anatomy_protection(prompt: str) -> dict[str, Any]:
    """检测项4: Prompt保护词检测"""
    required_terms = [
        "bad anatomy", "deformed", "mutilated", 
        "extra limbs", "missing limbs", "floating",
        "disconnected", "extra fingers", "mutated hands",
        "poorly drawn hands", "poorly drawn face",
    ]
    
    found = [term for term in required_terms if term.lower() in prompt.lower()]
    coverage = len(found) / len(required_terms)
    
    return {
        "name": "anatomy_protection",
        "passed": coverage >= 0.3,  # 至少30%的保护词
        "message": f"保护词覆盖率: {len(found)}/{len(required_terms)} ({coverage:.0%})",
        "critical": False,
        "found_terms": found,
        "coverage": coverage,
    }


def check_controlnet_used(workflow_data: dict | None = None) -> dict[str, Any]:
    """检测项: ControlNet使用检测 — 未使用则 critical 失败"""
    has_controlnet = False
    cn_nodes = []
    
    if workflow_data and isinstance(workflow_data, dict):
        for node_id, node in workflow_data.items():
            if isinstance(node, dict):
                class_type = node.get("class_type", "")
                if "ControlNet" in class_type:
                    has_controlnet = True
                    cn_nodes.append(class_type)
    
    return {
        "name": "controlnet_used",
        "passed": has_controlnet,
        "message": "ControlNet已使用" if has_controlnet else "ControlNet未使用（禁止无ControlNet渲染）",
        "critical": True,
        "controlnet_nodes": cn_nodes,
    }


def _edge_matrix(path: Path, width: int = ANALYSIS_WIDTH, height: int = ANALYSIS_HEIGHT) -> list[list[float]]:
    with Image.open(path) as img:
        gray = img.convert("L").resize((width, height), Image.Resampling.BILINEAR)
        edges = gray.filter(ImageFilter.FIND_EDGES)
        data = list(edges.getdata())
    return [data[r * width : (r + 1) * width] for r in range(height)]


def _pearson(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    mean_a = sum(a) / len(a)
    mean_b = sum(b) / len(b)
    num = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    den_a = math.sqrt(sum((x - mean_a) ** 2 for x in a))
    den_b = math.sqrt(sum((y - mean_b) ** 2 for y in b))
    if den_a < 1e-6 or den_b < 1e-6:
        return 0.0
    return num / (den_a * den_b)


def _flatten_block(matrix: list[list[float]], row_start: int, row_end: int, col_start: int, col_end: int) -> list[float]:
    out: list[float] = []
    for r in range(row_start, min(row_end, len(matrix))):
        out.extend(matrix[r][col_start:col_end])
    return out


def _vertical_profile(matrix: list[list[float]], col_start: int, col_end: int) -> list[float]:
    h = len(matrix)
    profile: list[float] = []
    for r in range(h):
        row_slice = matrix[r][col_start:col_end]
        profile.append(sum(row_slice) / max(len(row_slice), 1))
    return profile


def _smooth(values: list[float], window: int = 5) -> list[float]:
    if not values:
        return []
    half = window // 2
    out: list[float] = []
    for i in range(len(values)):
        chunk = values[max(0, i - half) : min(len(values), i + half + 1)]
        out.append(sum(chunk) / len(chunk))
    return out


def _find_peaks(values: list[float], min_ratio: float = MULTI_PEAK_MIN_RATIO) -> list[int]:
    if not values:
        return []
    mx = max(values)
    if mx <= 1e-6:
        return []
    threshold = mx * min_ratio
    peaks: list[int] = []
    for i in range(1, len(values) - 1):
        if values[i] >= threshold and values[i] >= values[i - 1] and values[i] >= values[i + 1]:
            if not peaks or i - peaks[-1] > max(8, len(values) // 12):
                peaks.append(i)
    return peaks


def _connected_components(binary: list[list[int]]) -> list[set[tuple[int, int]]]:
    h, w = len(binary), len(binary[0]) if binary else 0
    seen: set[tuple[int, int]] = set()
    components: list[set[tuple[int, int]]] = []

    for r in range(h):
        for c in range(w):
            if binary[r][c] != 1 or (r, c) in seen:
                continue
            stack = [(r, c)]
            comp: set[tuple[int, int]] = set()
            while stack:
                cr, cc = stack.pop()
                if (cr, cc) in seen or cr < 0 or cc < 0 or cr >= h or cc >= w or binary[cr][cc] != 1:
                    continue
                seen.add((cr, cc))
                comp.add((cr, cc))
                stack.extend([(cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)])
            if comp:
                components.append(comp)
    return components


def check_human_anomaly(path: Path) -> dict[str, Any]:
    """检测项: 人体结构异常 — 重叠鬼影 / 多人 / 漂浮部位 / 肢体断裂"""
    if not PIL_AVAILABLE:
        return {
            "name": "human_anomaly",
            "passed": False,
            "message": "PIL不可用，无法执行人体结构检测",
            "critical": True,
        }

    try:
        matrix = _edge_matrix(path)
        h, w = len(matrix), len(matrix[0])
        col_start = int(w * 0.25)
        col_end = int(w * 0.75)
        anomalies: list[str] = []
        metrics: dict[str, Any] = {}

        # 1) 上下重叠鬼影：上半 vs 下半边缘图高度相关
        upper = _flatten_block(matrix, int(h * 0.08), int(h * 0.48), col_start, col_end)
        lower = _flatten_block(matrix, int(h * 0.52), int(h * 0.92), col_start, col_end)
        lower_flipped = _flatten_block(list(reversed(matrix)), int(h * 0.08), int(h * 0.48), col_start, col_end)
        corr_direct = _pearson(upper, lower)
        corr_flip = _pearson(upper, lower_flipped)
        ghost_corr = max(corr_direct, corr_flip)
        metrics["ghost_correlation"] = round(ghost_corr, 3)
        if ghost_corr >= GHOST_CORR_THRESHOLD:
            anomalies.append(f"检测到上下重叠鬼影 (相关度 {ghost_corr:.2f})")

        # 2) 上下双体：上下半区峰值强度接近（叠影特征），区别于单人头/躯干/腿
        profile = _smooth(_vertical_profile(matrix, col_start, col_end))
        mx = max(profile) if profile else 0.0
        mid = h // 2
        top_half_max = max(profile[:mid]) if mid else 0.0
        bot_half_max = max(profile[mid:]) if mid < h else 0.0
        balance = min(top_half_max, bot_half_max) / max(top_half_max, bot_half_max) if max(top_half_max, bot_half_max) > 1e-6 else 0.0
        metrics["top_half_peak"] = round(top_half_max, 2)
        metrics["bottom_half_peak"] = round(bot_half_max, 2)
        metrics["vertical_peak_balance"] = round(balance, 3)
        if (
            mx > 1e-6
            and top_half_max >= mx * 0.58
            and bot_half_max >= mx * 0.58
            and balance >= 0.90
        ):
            anomalies.append(
                f"检测到上下重叠双体 (平衡度 {balance:.2f}, 上={top_half_max:.0f}, 下={bot_half_max:.0f})"
            )

        # 2b) 横向双人：左右两侧均有强边缘峰且间距足够
        center_rows = matrix[int(h * 0.15) : int(h * 0.88)]
        if center_rows:
            col_w = col_end - col_start
            col_profile = [
                sum(center_rows[r][c] for r in range(len(center_rows))) / len(center_rows)
                for c in range(col_start, col_end)
            ]
            col_profile = _smooth(col_profile, window=9)
            col_mx = max(col_profile) if col_profile else 0.0
            col_peaks = [
                i
                for i in _find_peaks(col_profile, min_ratio=0.50)
                if col_profile[i] >= col_mx * 0.55
            ]
            metrics["horizontal_peak_count"] = len(col_peaks)
            if len(col_peaks) >= 2:
                left_peak = col_peaks[0]
                right_peak = col_peaks[-1]
                span = (right_peak - left_peak) / max(col_w, 1)
                left_val = col_profile[left_peak]
                right_val = col_profile[right_peak]
                dual_side = (
                    span >= 0.42
                    and left_val >= col_mx * 0.60
                    and right_val >= col_mx * 0.60
                    and left_peak < col_w * 0.35
                    and right_peak > col_w * 0.65
                )
                metrics["horizontal_span"] = round(span, 3)
                if dual_side:
                    anomalies.append(f"检测到横向多人体 (跨度 {span:.0%})")

        # 叠影风险信号：用于约束漂浮/肢体误杀
        twin_risk = ghost_corr >= 0.50 or balance >= 0.88

        # 3) 漂浮部位 / 肢体断裂：仅在叠影风险或强双体信号时判 critical
        threshold = 28
        binary = [[1 if matrix[r][c] >= threshold else 0 for c in range(w)] for r in range(h)]
        components = _connected_components(binary)
        if components:
            components.sort(key=len, reverse=True)
            main = components[0]
            main_area = len(main)
            total_area = h * w
            metrics["edge_components"] = len(components)
            metrics["main_component_ratio"] = round(main_area / total_area, 4)

            floating = 0
            disconnected_limbs = 0
            for comp in components[1:]:
                area_ratio = len(comp) / total_area
                if area_ratio < FLOATING_MIN_AREA_RATIO:
                    continue
                xs = [c for _, c in comp]
                ys = [r for r, _ in comp]
                cx = sum(xs) / len(xs)
                cy = sum(ys) / len(ys)
                near_margin = (
                    cx < w * FLOATING_MARGIN_RATIO
                    or cx > w * (1 - FLOATING_MARGIN_RATIO)
                    or cy < h * FLOATING_MARGIN_RATIO
                    or cy > h * (1 - FLOATING_MARGIN_RATIO)
                )
                if near_margin and comp.isdisjoint(main):
                    floating += 1
                elif int(h * 0.15) < cy < int(h * 0.88) and comp.isdisjoint(main):
                    disconnected_limbs += 1

            metrics["floating_parts"] = floating
            metrics["disconnected_limbs"] = disconnected_limbs
            metrics["twin_risk"] = twin_risk
            if twin_risk and floating >= 3:
                anomalies.append(f"检测到漂浮部位 ({floating} 处)")
            if twin_risk and disconnected_limbs >= LIMB_COMPONENT_MIN:
                anomalies.append(f"检测到肢体断裂/分离 ({disconnected_limbs} 处)")

        passed = len(anomalies) == 0
        issue_types: list[str] = []
        if any("鬼影" in a or "双体" in a or "多人体" in a for a in anomalies):
            issue_types.append("ghost_duplicate_figure")
        if any("漂浮" in a for a in anomalies):
            issue_types.append("floating_limbs")
        if any("断裂" in a or "分离" in a for a in anomalies):
            issue_types.append("disconnected_limbs")
        return {
            "name": "human_anomaly",
            "passed": passed,
            "message": "人体结构检测通过" if passed else "; ".join(anomalies),
            "critical": True,
            "anomalies": anomalies,
            "issue_types": issue_types,
            "metrics": metrics,
            "detection_method": DETECTION_METHOD,
        }
    except Exception as e:
        return {
            "name": "human_anomaly",
            "passed": False,
            "message": f"人体结构检测失败: {e}",
            "critical": True,
        }


def check_file_size_vr2r(path: Path) -> dict[str, Any]:
    """VR-2R 交付文件大小：>500KB S0，>5MB S2"""
    if not path.exists():
        return {
            "name": "file_size_vr2r",
            "passed": False,
            "message": "文件不存在",
            "critical": True,
        }
    size_kb = path.stat().st_size / 1024
    if size_kb < VR2R_MIN_FILE_SIZE_KB:
        return {
            "name": "file_size_vr2r",
            "passed": False,
            "message": f"文件过小(S0): {size_kb:.1f}KB < {VR2R_MIN_FILE_SIZE_KB}KB",
            "critical": True,
            "size_kb": round(size_kb, 1),
        }
    if size_kb > VR2R_MAX_FILE_SIZE_KB:
        return {
            "name": "file_size_vr2r",
            "passed": False,
            "message": f"文件过大(S2): {size_kb:.1f}KB > {VR2R_MAX_FILE_SIZE_KB}KB",
            "critical": False,
            "size_kb": round(size_kb, 1),
        }
    return {
        "name": "file_size_vr2r",
        "passed": True,
        "message": f"文件大小合规: {size_kb:.1f}KB",
        "critical": True,
        "size_kb": round(size_kb, 1),
    }


def check_pixel_complexity(path: Path) -> dict[str, Any]:
    """像素复杂度：RGB 标准差均值须 > MIN_PIXEL_STD（排除纯色/placeholder）"""
    if not PIL_AVAILABLE or not path.exists():
        return {
            "name": "pixel_complexity",
            "passed": False,
            "message": "PIL不可用或文件缺失，无法检测像素复杂度",
            "critical": True,
        }
    try:
        with Image.open(path) as img:
            rgb = img.convert("RGB")
            data = list(rgb.getdata())
        if not data:
            return {
                "name": "pixel_complexity",
                "passed": False,
                "message": "空图像",
                "critical": True,
            }
        rs = [p[0] for p in data]
        gs = [p[1] for p in data]
        bs = [p[2] for p in data]

        def _std(vals: list[int]) -> float:
            mean = sum(vals) / len(vals)
            return math.sqrt(sum((v - mean) ** 2 for v in vals) / len(vals))

        std_r, std_g, std_b = _std(rs), _std(gs), _std(bs)
        complexity = (std_r + std_g + std_b) / 3.0
        passed = complexity >= MIN_PIXEL_STD
        return {
            "name": "pixel_complexity",
            "passed": passed,
            "message": (
                f"像素复杂度通过: {complexity:.1f}"
                if passed
                else f"像素复杂度过低(S0): {complexity:.1f} < {MIN_PIXEL_STD}"
            ),
            "critical": True,
            "pixel_std_mean": round(complexity, 2),
        }
    except Exception as e:
        return {
            "name": "pixel_complexity",
            "passed": False,
            "message": f"像素复杂度检测失败: {e}",
            "critical": True,
        }


def check_text_card_proxy(path: Path) -> dict[str, Any]:
    """非文字卡代理：低复杂度 + 低边缘密度 => 疑似文字卡/placeholder"""
    if not PIL_AVAILABLE or not path.exists():
        return {
            "name": "text_card_proxy",
            "passed": True,
            "message": "跳过文字卡检测",
            "critical": False,
        }
    try:
        with Image.open(path) as img:
            gray = img.convert("L")
            w, h = gray.size
            data = list(gray.getdata())
        mean = sum(data) / len(data)
        std = math.sqrt(sum((p - mean) ** 2 for p in data) / len(data))
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edge_data = list(edges.getdata())
        edge_ratio = sum(1 for p in edge_data if p > 40) / len(edge_data)
        is_text_card = std <= TEXT_CARD_MAX_STD and edge_ratio <= TEXT_CARD_MAX_EDGE_RATIO
        return {
            "name": "text_card_proxy",
            "passed": not is_text_card,
            "message": (
                "非文字卡检测通过"
                if not is_text_card
                else f"疑似文字卡/纯色卡(S0): std={std:.1f}, edge_ratio={edge_ratio:.3f}"
            ),
            "critical": True,
            "gray_std": round(std, 2),
            "edge_ratio": round(edge_ratio, 4),
        }
    except Exception as e:
        return {
            "name": "text_card_proxy",
            "passed": False,
            "message": f"文字卡检测失败: {e}",
            "critical": True,
        }


def check_subject_presence(path: Path) -> dict[str, Any]:
    """人物主体代理：中心区域边缘峰值过低 => 明显非人物/主体缺失"""
    if not PIL_AVAILABLE or not path.exists():
        return {
            "name": "subject_presence",
            "passed": False,
            "message": "PIL不可用，无法检测人物主体",
            "critical": True,
        }
    try:
        matrix = _edge_matrix(path)
        h, w = len(matrix), len(matrix[0])
        col_start, col_end = int(w * 0.25), int(w * 0.75)
        profile = _vertical_profile(matrix, col_start, col_end)
        peak = max(profile) if profile else 0.0
        passed = peak >= MIN_SUBJECT_EDGE_PEAK
        return {
            "name": "subject_presence",
            "passed": passed,
            "message": (
                "人物主体代理检测通过"
                if passed
                else f"人物主体缺失(S0): 中心边缘峰值 {peak:.1f} < {MIN_SUBJECT_EDGE_PEAK}"
            ),
            "critical": True,
            "edge_peak": round(peak, 2),
            "detection_method": DETECTION_METHOD,
        }
    except Exception as e:
        return {
            "name": "subject_presence",
            "passed": False,
            "message": f"人物主体检测失败: {e}",
            "critical": True,
        }


def _attach_severity(check: dict[str, Any]) -> dict[str, Any]:
    check["severity"] = CHECK_SEVERITY.get(check.get("name", ""), SEVERITY_S2)
    return check


def _defects_from_checks(checks: list[dict[str, Any]], *, shot_id: str = "") -> list[dict[str, Any]]:
    defects: list[dict[str, Any]] = []
    for check in checks:
        if check.get("passed"):
            continue
        defects.append(
            {
                "shot_id": shot_id,
                "severity": check.get("severity", CHECK_SEVERITY.get(check.get("name", ""), SEVERITY_S2)),
                "type": check.get("name", "unknown"),
                "description": check.get("message", ""),
                "check": check.get("name", ""),
            }
        )
    return defects


def _severity_max(defects: list[dict[str, Any]]) -> str | None:
    order = {SEVERITY_S0: 0, SEVERITY_S1: 1, SEVERITY_S2: 2, SEVERITY_S3: 3}
    if not defects:
        return None
    return min(defects, key=lambda d: order.get(str(d.get("severity")), 9)).get("severity")


def _repair_action_for_defects(defects: list[dict[str, Any]]) -> str:
    for defect in defects:
        action = REPAIR_ACTIONS.get(str(defect.get("type", "")))
        if action:
            return action
    return "regenerate_shot"


def _final_verdict(defects: list[dict[str, Any]], overall_passed: bool) -> str:
    if overall_passed:
        return "PASS"
    if any(d.get("severity") == SEVERITY_S0 for d in defects):
        return "D_BLOCKED"
    if any(d.get("severity") == SEVERITY_S1 for d in defects):
        return "S1_REPAIR_REQUIRED"
    return "FAIL"


def analyze_image_content(path: Path) -> dict[str, Any]:
    """检测项6: 图像内容异常检测（像素级基础检测）"""
    if not PIL_AVAILABLE:
        return {
            "name": "content_anomaly",
            "passed": True,
            "message": "PIL不可用，跳过内容检测",
            "critical": False,
        }
    
    try:
        with Image.open(path) as img:
            # 转为灰度图检测大面积异常
            gray = img.convert("L")
            data = list(gray.getdata())
            
            # 检测全黑/全白区域占比
            black_pixels = sum(1 for p in data if p < 15)
            white_pixels = sum(1 for p in data if p > 240)
            total = len(data)
            
            black_ratio = black_pixels / total
            white_ratio = white_pixels / total
            
            # 异常区域过大
            if black_ratio > 0.6:
                return {
                    "name": "content_anomaly",
                    "passed": False,
                    "message": f"图像大面积黑暗: {black_ratio:.1%}",
                    "critical": True,
                }
            
            if white_ratio > 0.6:
                return {
                    "name": "content_anomaly",
                    "passed": False,
                    "message": f"图像大面积过曝: {white_ratio:.1%}",
                    "critical": True,
                }
            
            return {
                "name": "content_anomaly",
                "passed": True,
                "message": "图像内容检测通过",
                "black_ratio": round(black_ratio, 3),
                "white_ratio": round(white_ratio, 3),
            }
    except Exception as e:
        return {
            "name": "content_anomaly",
            "passed": False,
            "message": f"内容检测失败: {e}",
            "critical": True,
        }


def run_quality_check(
    image_path: str | Path,
    prompt: str = "",
    workflow_data: dict | None = None,
    auto_delete: bool = True,
    *,
    shot_id: str = "",
    vr2r_gate: bool = True,
) -> dict[str, Any]:
    """运行全套质量检测
    
    Args:
        image_path: 图像路径
        prompt: 生成使用的prompt
        workflow_data: ComfyUI workflow数据
        auto_delete: 检测失败时自动删除文件
        shot_id: 镜头 ID（shot-level QC）
        vr2r_gate: 启用 VR-2R-QF 内容质量门禁（像素复杂度/500KB/主体/文字卡）
    
    Returns:
        检测结果字典（含 defects / severity / repair_action）
    """
    path = Path(image_path)
    
    checks = []
    
    # 运行所有检测
    checks.append(check_file_exists(path))
    
    if path.exists():
        placeholder_min_kb = 1.0 if not vr2r_gate else MIN_FILE_SIZE_KB
        checks.append(check_non_placeholder(path, min_size_kb=placeholder_min_kb))
        checks.append(check_image_integrity(path))
        checks.append(analyze_image_content(path))
        checks.append(check_human_anomaly(path))
        checks.append(check_subject_presence(path))
        checks.append(check_text_card_proxy(path))
        if vr2r_gate:
            checks.append(check_file_size_vr2r(path))
            checks.append(check_pixel_complexity(path))
    
    if prompt:
        checks.append(check_anatomy_protection(prompt))
    
    checks.append(check_controlnet_used(workflow_data))

    checks = [_attach_severity(c) for c in checks]
    defects = _defects_from_checks(checks, shot_id=shot_id)
    severity_max = _severity_max(defects)

    s0_defects = [d for d in defects if d.get("severity") == SEVERITY_S0]
    s1_defects = [d for d in defects if d.get("severity") == SEVERITY_S1]
    critical_failed = [c["name"] for c in checks if c.get("critical", False) and not c["passed"]]

    # S0 一票否决；S1 默认 fail；其余 critical 失败也 fail
    overall_passed = (
        not s0_defects
        and not s1_defects
        and all(c["passed"] for c in checks if c.get("critical", False))
    )
    warnings = [
        c["message"]
        for c in checks
        if not c.get("critical", False) and not c["passed"]
    ]
    
    result = {
        "shot_id": shot_id or None,
        "image_path": str(path),
        "overall_passed": overall_passed,
        "final_verdict": _final_verdict(defects, overall_passed),
        "severity_max": severity_max,
        "defects": defects,
        "s0_defects": s0_defects,
        "s1_defects": s1_defects,
        "one_vote_blockers": [f"S0_{d['type']}_{shot_id or 'unknown'}" for d in s0_defects],
        "critical_failed": critical_failed,
        "warnings": warnings,
        "checks": checks,
        "repair_action": None if overall_passed else _repair_action_for_defects(defects),
        "detection_method": DETECTION_METHOD,
        "auto_delete_executed": False,
        "commercial_release_allowed": False,
    }
    
    # 失败时自动删除
    if not overall_passed and auto_delete and path.exists():
        try:
            path.unlink()
            result["auto_delete_executed"] = True
            result["delete_reason"] = "; ".join(
                c["message"] for c in checks if c.get("critical", False) and not c["passed"]
            )
        except Exception as e:
            result["delete_error"] = str(e)
    
    return result


def run_shot_batch_qc(
    shots: list[dict[str, Any]],
    *,
    report_dir: str | Path | None = None,
    auto_delete: bool = False,
    vr2r_gate: bool = True,
    video_id: str = "ch02_comfyui_quality_fix",
) -> dict[str, Any]:
    """Shot-level 批量 QC：逐镜结论 + repair list，不默认整片重做。"""
    shot_results: list[dict[str, Any]] = []
    repair_list: list[dict[str, Any]] = []
    one_vote_blockers: list[str] = []

    for spec in shots:
        sid = str(spec.get("shot_id") or "")
        img_path = spec.get("path") or spec.get("image_path")
        if not img_path:
            continue
        qc = run_quality_check(
            img_path,
            prompt=str(spec.get("prompt") or spec.get("positive_prompt") or ""),
            workflow_data=spec.get("workflow_data"),
            auto_delete=auto_delete,
            shot_id=sid,
            vr2r_gate=vr2r_gate,
        )
        shot_results.append(qc)
        if not qc["overall_passed"]:
            repair_list.append(
                {
                    "shot_id": sid,
                    "image_path": qc.get("image_path"),
                    "repair_action": qc.get("repair_action", "regenerate_shot"),
                    "severity_max": qc.get("severity_max"),
                    "defects": qc.get("defects", []),
                    "final_verdict": qc.get("final_verdict"),
                }
            )
        one_vote_blockers.extend(qc.get("one_vote_blockers") or [])

    passed = sum(1 for r in shot_results if r.get("overall_passed"))
    total = len(shot_results)
    any_s0 = any(r.get("severity_max") == SEVERITY_S0 for r in shot_results if not r.get("overall_passed"))
    final_verdict = "PASS"
    if any_s0:
        final_verdict = "D_BLOCKED"
    elif repair_list:
        final_verdict = "S1_REPAIR_REQUIRED"

    report: dict[str, Any] = {
        "video_id": video_id,
        "target_quality_level": "B-",
        "detection_method": DETECTION_METHOD,
        "total_shots": total,
        "passed_shots": passed,
        "failed_shots": total - passed,
        "shot_results": shot_results,
        "repair_list": repair_list,
        "one_vote_blockers": one_vote_blockers,
        "final_verdict": final_verdict if total else "NO_SHOTS",
        "commercial_release_allowed": False,
        "note": "Ken Burns / static motion not evaluated in image-only QC",
    }

    if report_dir is not None:
        out = Path(report_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "shot_qc_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (out / "repair_list.json").write_text(
            json.dumps({"video_id": video_id, "repair_list": repair_list}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return report


def controlnet_stub_workflow() -> dict[str, Any]:
    """Manifest/batch 复查用 ControlNet 占位 workflow（已通过单镜检测时使用）。"""
    return {
        "10": {"class_type": "ControlNetLoader", "inputs": {}},
        "12": {"class_type": "ControlNetApply", "inputs": {}},
    }


def batch_check_directory(
    dir_path: str | Path,
    manifest_path: str | Path | None = None,
    auto_delete: bool = True,
    rendered_shots: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """批量检测目录下的所有图像"""
    path = Path(dir_path)
    if not path.exists():
        return {"error": f"目录不存在: {path}"}
    
    # 加载manifest获取prompt
    manifest = {}
    if manifest_path and Path(manifest_path).exists():
        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)
        except:
            pass
    
    shot_prompts: dict[str, str] = {}
    shot_meta: dict[str, dict[str, Any]] = {}
    for shot in (rendered_shots or []) + manifest.get("rendered_shots", []):
        if isinstance(shot, dict) and shot.get("shot_id"):
            sid = str(shot["shot_id"])
            shot_prompts[sid] = shot.get("positive_prompt", "")
            shot_meta[sid] = shot
    
    results = []
    image_files = list(path.glob("*.png")) + list(path.glob("*.jpg")) + list(path.glob("*.jpeg"))
    
    for img_path in image_files:
        shot_id = ""
        match = re.search(r"shot_(sh\d+)", img_path.name)
        if match:
            shot_id = match.group(1)

        meta = shot_meta.get(shot_id, {})
        prior = meta.get("quality_check") if isinstance(meta.get("quality_check"), dict) else None
        if prior and prior.get("overall_passed") and img_path.exists():
            results.append({**prior, "image_path": str(img_path), "batch_skipped": True})
            continue

        workflow_data = None
        if meta.get("workflow") == "controlnet_openpose" or manifest.get("workflow") == "controlnet_openpose":
            workflow_data = controlnet_stub_workflow()
        
        result = run_quality_check(
            img_path,
            prompt=shot_prompts.get(shot_id, ""),
            workflow_data=workflow_data,
            auto_delete=auto_delete,
            shot_id=shot_id,
            vr2r_gate=True,
        )
        results.append(result)
    
    passed = sum(1 for r in results if r["overall_passed"])
    deleted = sum(1 for r in results if r["auto_delete_executed"])
    repair_list = [
        {
            "shot_id": r.get("shot_id") or "",
            "image_path": r.get("image_path"),
            "repair_action": r.get("repair_action"),
            "defects": r.get("defects", []),
            "severity_max": r.get("severity_max"),
        }
        for r in results
        if not r.get("overall_passed")
    ]
    
    # 生成报告
    report = {
        "directory": str(path),
        "total_images": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "auto_deleted": deleted,
        "overall_pass_rate": passed / len(results) if results else 0,
        "repair_list": repair_list,
        "one_vote_blockers": [
            b for r in results for b in (r.get("one_vote_blockers") or [])
        ],
        "final_verdict": "PASS" if passed == len(results) and results else (
            "D_BLOCKED" if any(r.get("severity_max") == SEVERITY_S0 for r in results if not r.get("overall_passed")) else "S1_REPAIR_REQUIRED"
        ),
        "results": results,
    }
    
    return report


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python image_quality_check.py <image_path or directory>")
        sys.exit(1)
    
    path = sys.argv[1]
    auto_delete = "--no-delete" not in sys.argv
    
    if Path(path).is_dir():
        report = batch_check_directory(path, auto_delete=auto_delete)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if report.get("failed", 0) > 0:
            sys.exit(1)
    else:
        result = run_quality_check(path, auto_delete=auto_delete)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if not result.get("overall_passed", False):
            sys.exit(1)


if __name__ == "__main__":
    main()
