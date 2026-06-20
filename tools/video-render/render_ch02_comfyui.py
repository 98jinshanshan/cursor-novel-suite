#!/usr/bin/env python3
"""VideoRender-2R-Quality-Fix — 强制质量检测版
生成后立即检测，不合格自动删除重渲染
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CH02 = ROOT / "novels" / "novel-837dd4f1" / "video" / "ch02"
ADAPTER = ROOT / "tools" / "comfyui-adapter"
LOCAL_ACCEL = ROOT / "tools" / "local-accel" / "local_accel.py"
COMFYUI_URL = "http://127.0.0.1:8188"
MAX_RETRY_PER_SHOT = 3  # 每个镜头最多重试3次

if str(ADAPTER) not in sys.path:
    sys.path.insert(0, str(ADAPTER))
if str(ROOT / "cursor-novel-video" / "adapters") not in sys.path:
    sys.path.insert(0, str(ROOT / "cursor-novel-video" / "adapters"))

if str(ROOT / "tools" / "video-render") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools" / "video-render"))

# 导入质量检测模块
QUALITY_CHECK_AVAILABLE = False
try:
    from image_quality_check import run_quality_check, batch_check_directory
    from openpose_asset import ASSET_NAME, ensure_openpose_asset
    QUALITY_CHECK_AVAILABLE = True
    print("✓ 质量检测模块已加载")
except ImportError as e:
    ensure_openpose_asset = None  # type: ignore[misc, assignment]
    ASSET_NAME = "novel_suite_openpose_single.png"
    print(f"⚠ 质量检测模块导入失败: {e}")
    print("  仍将渲染，但不会进行质量检测和自动删除")

from comfyui_client import (
    fetch_output,
    object_info,
    queue_prompt,
    system_stats,
    upload_image,
    validate_url,
    wait_for_history,
    workflow_hash,
)
from model_audit import run_audit
from workflow_adapter import build_input_mapping, list_checkpoints_from_object_info, load_shots
from comfyui_workflow import controlnet_openpose_workflow

OPENPOSE_IMAGE_NAME = ASSET_NAME


def write_recheck_report(doctor: dict) -> None:
    lines = [
        "# ComfyUI Recheck Report — VideoRender-2R-Quality-Fix",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## ComfyUI",
        f"- available: {doctor.get('comfyui', {}).get('available')}",
        f"- url: {doctor.get('comfyui', {}).get('url', COMFYUI_URL)}",
        "",
        "## GPU",
        f"- available: {doctor.get('gpu', {}).get('available')}",
        f"- name: {doctor.get('gpu', {}).get('name')}",
        "",
        "## FFmpeg",
        f"- available: {doctor.get('ffmpeg', {}).get('available')}",
        f"- nvenc: {doctor.get('ffmpeg', {}).get('nvenc', [])}",
        "",
        "## Quality Control",
        f"- quality_check_available: {QUALITY_CHECK_AVAILABLE}",
        f"- max_retry_per_shot: {MAX_RETRY_PER_SHOT}",
        f"- workflow: controlnet_openpose (mandatory)",
        f"- openpose_control: {OPENPOSE_IMAGE_NAME}",
        "",
        "```json",
        json.dumps(doctor, ensure_ascii=False, indent=2),
        "```",
    ]
    CH02.mkdir(parents=True, exist_ok=True)
    (CH02 / "comfyui_recheck_report.md").write_text("\n".join(lines), encoding="utf-8")


def run_local_accel() -> dict:
    py = sys.executable
    out: dict = {}
    for cmd, key in [
        (["comfyui-check"], "comfyui"),
        (["gpu-check"], "gpu"),
        (["ffmpeg-check"], "ffmpeg"),
    ]:
        proc = subprocess.run([py, str(LOCAL_ACCEL), *cmd, "--json"], capture_output=True, text=True, timeout=30)
        try:
            out[key] = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError:
            out[key] = {"available": False, "error": proc.stderr[:200]}
    return out


def ensure_openpose_uploaded(url: str) -> str:
    """Upload single-subject OpenPose control map to ComfyUI input folder."""
    if ensure_openpose_asset is None:
        raise RuntimeError("openpose_asset 模块不可用")
    asset = ensure_openpose_asset()
    uploaded = upload_image(url, asset, overwrite=True)
    name = uploaded.get("filename") or OPENPOSE_IMAGE_NAME
    print(f"✓ OpenPose 控制图已上传: {name}")
    return name


def build_controlnet_workflow(
    positive: str,
    *,
    ckpt: str,
    openpose_image: str,
    width: int,
    height: int,
    seed: int,
) -> dict:
    """强制 ControlNet OpenPose workflow — 禁止 safe_text2img 保底路径。"""
    return controlnet_openpose_workflow(
        positive,
        ckpt=ckpt,
        openpose_image=openpose_image,
        width=width,
        height=height,
        seed=seed,
    )


def render_single_shot(
    url: str,
    shot: dict,
    ckpt: str,
    openpose_image: str,
    width: int = 768,
    height: int = 1344,
) -> tuple[dict | None, dict]:
    """渲染单个镜头，带质量检测和自动重试"""
    sid = shot["shot_id"]
    positive = shot["positive_prompt"]
    seed = int(shot["seed"])
    
    visuals_dir = CH02 / "visuals_comfyui"
    visuals_dir.mkdir(parents=True, exist_ok=True)
    
    quality_result = {}
    
    for attempt in range(MAX_RETRY_PER_SHOT):
        attempt_seed = seed + attempt * 1000
        
        print(f"  [{sid}] 尝试 {attempt+1}/{MAX_RETRY_PER_SHOT}, seed={attempt_seed}")
        
        wf = build_controlnet_workflow(
            positive,
            ckpt=ckpt,
            openpose_image=openpose_image,
            width=width,
            height=height,
            seed=attempt_seed,
        )
        wf["7"]["inputs"]["filename_prefix"] = f"shot_{sid}"
        
        wh = workflow_hash(wf)
        
        try:
            queued = queue_prompt(url, wf)
            prompt_id = queued.get("prompt_id")
            if not prompt_id:
                print(f"  [sh{sid}] 排队失败: {queued}")
                continue
            
            max_wait = 120
            try:
                wait_for_history(url, prompt_id, timeout=max_wait)
            except TimeoutError:
                print(f"  [sh{sid}] 渲染超时")
                continue

            img_path = visuals_dir / f"shot_{sid}.png"
            try:
                fetched = fetch_output(url, prompt_id, visuals_dir)
                downloaded = Path(fetched["path"])
                if downloaded.resolve() != img_path.resolve():
                    if img_path.exists():
                        img_path.unlink()
                    downloaded.rename(img_path)
                print(f"  [sh{sid}] 已落盘: {img_path.name} ({fetched.get('bytes', 0)} bytes)")
            except Exception as dl_err:
                print(f"  [sh{sid}] 下载输出失败: {dl_err}")
                continue
            
            # 质量检测（如果可用）
            if QUALITY_CHECK_AVAILABLE and img_path.exists():
                quality_result = run_quality_check(
                    img_path,
                    prompt=positive,
                    workflow_data=wf,
                    auto_delete=True,
                )
                
                if quality_result["overall_passed"]:
                    print(f"  [sh{sid}] ✓ 质量检测通过")
                    return {
                        "shot_id": sid,
                        "prompt_id": prompt_id,
                        "workflow_hash": wh,
                        "seed": attempt_seed,
                        "positive_prompt": positive,
                        "path": str(img_path),
                        "source": "comfyui",
                        "workflow": "controlnet_openpose",
                        "openpose_control": openpose_image,
                        "bytes": img_path.stat().st_size if img_path.exists() else 0,
                        "quality_check": quality_result,
                        "attempts": attempt + 1,
                    }, quality_result
                else:
                    del_reason = quality_result.get("delete_reason", "未知")
                    print(f"  [sh{sid}] ✗ 质量检测失败，已删除: {del_reason}")
                    if quality_result.get("auto_delete_executed"):
                        print(f"  [sh{sid}] 已自动删除，将重试...")
                        continue
            elif not QUALITY_CHECK_AVAILABLE:
                # 没有质量检测，直接返回（不推荐）
                return {
                    "shot_id": sid,
                    "prompt_id": prompt_id,
                    "workflow_hash": wh,
                    "seed": attempt_seed,
                    "positive_prompt": positive,
                    "path": str(img_path),
                    "source": "comfyui",
                    "bytes": img_path.stat().st_size if img_path.exists() else 0,
                    "quality_check": {"skipped": True, "reason": "module not available"},
                    "attempts": attempt + 1,
                }, quality_result
            
        except Exception as e:
            print(f"  [sh{sid}] 错误: {e}")
            continue
    
    # 所有重试都失败
    print(f"  [sh{sid}] ✗ 所有 {MAX_RETRY_PER_SHOT} 次尝试均失败")
    return None, quality_result


def render_shots(
    url: str,
    *,
    ckpt: str,
    openpose_image: str,
    max_shots: int = 10,
    width: int = 768,
    height: int = 1344,
) -> tuple[list[dict], list[dict]]:
    shots_data = build_input_mapping(ckpt=ckpt, width=width, height=height)["shots"][:max_shots]
    
    rendered: list[dict] = []
    failures: list[dict] = []
    
    print(f"\n=== 开始渲染 {len(shots_data)} 个镜头（ControlNet OpenPose / 每镜头最多重试{MAX_RETRY_PER_SHOT}次）===")
    
    for shot in shots_data:
        result, _ = render_single_shot(url, shot, ckpt, openpose_image, width, height)
        if result:
            rendered.append(result)
        else:
            failures.append({"shot_id": shot["shot_id"], "error": "all_retries_failed"})
    
    print(f"\n=== 渲染完成 ===")
    print(f"  成功: {len(rendered)}/{len(shots_data)}")
    print(f"  失败: {len(failures)}/{len(shots_data)}")
    
    # 批量质量复查
    if QUALITY_CHECK_AVAILABLE:
        print("\n=== 批量质量复查 ===")
        visuals_dir = CH02 / "visuals_comfyui"
        manifest_path = CH02 / "comfyui_render_manifest.json"
        batch_result = batch_check_directory(
            visuals_dir,
            manifest_path,
            auto_delete=True,
            rendered_shots=rendered,
        )
        print(f"  通过率: {batch_result.get('overall_pass_rate', 0):.1%}")
        print(f"  自动删除: {batch_result.get('auto_deleted', 0)} 张不合格")
        
        if batch_result.get("auto_deleted", 0) > 0:
            print("  ⚠ 注意：部分图像因不合格被删除，需要补充渲染或降低pass标准")
    
    return rendered, failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=COMFYUI_URL)
    parser.add_argument("--max-shots", type=int, default=10)
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=1344)
    parser.add_argument("--no-quality-check", action="store_true", help="禁用质量检测（不推荐）")
    parser.add_argument(
        "--enable-quality-check",
        action="store_true",
        help="显式启用质量检测（默认已启用，与 --no-quality-check 互斥）",
    )
    parser.add_argument(
        "--skip-mp4",
        action="store_true",
        help="单镜头验证模式：跳过 MP4 合成（节点 4 试渲染用）",
    )
    args = parser.parse_args()
    
    if args.no_quality_check:
        print("✗ 禁止禁用质量检测（VideoRender-2R-Quality-Fix 强制门禁）")
        return 1
    
    global QUALITY_CHECK_AVAILABLE
    if args.enable_quality_check:
        QUALITY_CHECK_AVAILABLE = True
    if not QUALITY_CHECK_AVAILABLE:
        print("✗ 质量检测模块未加载，无法继续渲染")
        return 1
    
    print("=" * 60)
    print("VideoRender-2R-Quality-Fix — 强制质量检测版")
    print("=" * 60)
    
    url = validate_url(args.url)
    print(f"ComfyUI URL: {url}")
    
    # Precheck
    print("\n=== 环境检查 ===")
    doctor = run_local_accel()
    write_recheck_report(doctor)
    
    if not doctor.get("comfyui", {}).get("available"):
        print("✗ ComfyUI不可用，退出")
        return 1
    
    # 获取checkpoint
    print("\n=== 获取模型信息 ===")
    obj_info = object_info(url)
    ckpts = list_checkpoints_from_object_info(obj_info)
    ckpt = ckpts[0] if ckpts else "Realistic_Vision_V5.1_fp16-no-ema.safetensors"
    print(f"使用Checkpoint: {ckpt}")
    
    print("\n=== 上传 OpenPose 控制图 ===")
    try:
        openpose_image = ensure_openpose_uploaded(url)
    except Exception as exc:
        print(f"✗ OpenPose 控制图上传失败: {exc}")
        return 1
    
    # 渲染
    rendered, failures = render_shots(
        url,
        ckpt=ckpt,
        openpose_image=openpose_image,
        max_shots=args.max_shots,
        width=args.width,
        height=args.height,
    )
    
    # 保存manifest
    manifest = {
        "pipeline": "VideoRender-2R-Quality-Fix",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "comfyui_url": url,
        "comfyui_available": True,
        "checkpoint": ckpt,
        "quality_check_enabled": QUALITY_CHECK_AVAILABLE,
        "max_retry_per_shot": MAX_RETRY_PER_SHOT,
        "workflow": "controlnet_openpose",
        "openpose_control": openpose_image,
        "human_anomaly_check": "critical",
        "rendered_shots": rendered,
        "failures": failures,
        "i2v_available": True,
        "commercial_release_allowed": False,
        "verdict": "blocked",
    }
    
    manifest_path = CH02 / "comfyui_render_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\nManifest已保存: {manifest_path}")
    
    # 只有全部通过才合成MP4
    if args.skip_mp4:
        print("\n=== 单镜头验证模式：跳过 MP4 合成 ===")
        if len(failures) == 0 and len(rendered) >= args.max_shots:
            print(f"  质量门禁通过: {len(rendered)}/{args.max_shots} 镜头")
            return 0
        print(f"  质量门禁未通过。成功: {len(rendered)}, 失败: {len(failures)}")
        return 1

    if len(failures) == 0 and len(rendered) >= args.max_shots:
        print("\n=== 全部镜头通过，合成MP4 ===")
        # TODO: 调用FFmpeg合成（节点 6 实现）
        print("  (FFmpeg合成需要实现)")
    else:
        print(f"\n✗ 检测失败，不合成MP4。成功: {len(rendered)}, 失败: {len(failures)}")
        return 1
    
    return 0 if len(failures) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

