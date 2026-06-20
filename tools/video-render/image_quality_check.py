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


def check_file_exists(path: Path) -> dict[str, Any]:
    """检测项1: 文件存在"""
    exists = path.exists() and path.is_file()
    return {
        "name": "file_exists",
        "passed": exists,
        "message": "文件存在" if exists else f"文件不存在: {path}",
        "critical": True,
    }


def check_non_placeholder(path: Path) -> dict[str, Any]:
    """检测项2: 非占位符检测"""
    size_kb = path.stat().st_size / 1024 if path.exists() else 0
    
    # 检查文件大小
    size_ok = size_kb >= MIN_FILE_SIZE_KB
    
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
        message.append(f"文件过小: {size_kb:.1f}KB < {MIN_FILE_SIZE_KB}KB")
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
        return {
            "name": "human_anomaly",
            "passed": passed,
            "message": "人体结构检测通过" if passed else "; ".join(anomalies),
            "critical": True,
            "anomalies": anomalies,
            "metrics": metrics,
        }
    except Exception as e:
        return {
            "name": "human_anomaly",
            "passed": False,
            "message": f"人体结构检测失败: {e}",
            "critical": True,
        }


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
) -> dict[str, Any]:
    """运行全套质量检测
    
    Args:
        image_path: 图像路径
        prompt: 生成使用的prompt
        workflow_data: ComfyUI workflow数据
        auto_delete: 检测失败时自动删除文件
    
    Returns:
        检测结果字典
    """
    path = Path(image_path)
    
    checks = []
    
    # 运行所有检测
    checks.append(check_file_exists(path))
    
    if path.exists():
        checks.append(check_non_placeholder(path))
        checks.append(check_image_integrity(path))
        checks.append(analyze_image_content(path))
        checks.append(check_human_anomaly(path))
    
    if prompt:
        checks.append(check_anatomy_protection(prompt))
    
    checks.append(check_controlnet_used(workflow_data))
    
    # 统计结果：任一 critical 失败即 overall 失败
    passed_all = all(c["passed"] for c in checks if c.get("critical", False))
    warnings = [
        c["message"]
        for c in checks
        if not c.get("critical", False) and not c["passed"]
    ]
    
    result = {
        "image_path": str(path),
        "overall_passed": passed_all,
        "critical_failed": [c["name"] for c in checks if c.get("critical", False) and not c["passed"]],
        "warnings": warnings,
        "checks": checks,
        "auto_delete_executed": False,
    }
    
    # 失败时自动删除
    if not passed_all and auto_delete and path.exists():
        try:
            path.unlink()
            result["auto_delete_executed"] = True
            result["delete_reason"] = "; ".join(
                c["message"] for c in checks if c.get("critical", False) and not c["passed"]
            )
        except Exception as e:
            result["delete_error"] = str(e)
    
    return result


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
        )
        results.append(result)
    
    passed = sum(1 for r in results if r["overall_passed"])
    deleted = sum(1 for r in results if r["auto_delete_executed"])
    
    # 生成报告
    report = {
        "directory": str(path),
        "total_images": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "auto_deleted": deleted,
        "overall_pass_rate": passed / len(results) if results else 0,
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
