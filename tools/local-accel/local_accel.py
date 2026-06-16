#!/usr/bin/env python3
"""Local capability detection — doctor/gpu/ffmpeg/comfyui/ollama. No auto-start."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any


def _http_ok(url: str, timeout: float = 3.0) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310
            return resp.status == 200, f"HTTP {resp.status}"
    except urllib.error.URLError as exc:
        return False, str(exc.reason) if hasattr(exc, "reason") else str(exc)
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def gpu_check() -> dict[str, Any]:
    out: dict[str, Any] = {"available": False, "name": None, "driver": None, "vram_mb": None}
    if not shutil.which("nvidia-smi"):
        out["error"] = "nvidia-smi not found"
        return out
    try:
        proc = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total",
                "--format=csv,noheader",
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        line = (proc.stdout or "").strip().splitlines()[0] if proc.stdout else ""
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 3:
            out["available"] = True
            out["name"] = parts[0]
            out["driver"] = parts[1]
            out["vram_mb"] = parts[2].replace(" MiB", "").strip()
    except (OSError, subprocess.TimeoutExpired, IndexError) as exc:
        out["error"] = str(exc)
    return out


def ffmpeg_check() -> dict[str, Any]:
    out: dict[str, Any] = {"available": False, "version": None, "nvenc": []}
    if not shutil.which("ffmpeg"):
        out["error"] = "ffmpeg not found"
        return out
    try:
        proc = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=15, check=False)
        first = (proc.stdout or "").splitlines()[0] if proc.stdout else ""
        out["available"] = proc.returncode == 0
        out["version"] = first
        enc = subprocess.run(["ffmpeg", "-encoders"], capture_output=True, text=True, timeout=15, check=False)
        for name in ("h264_nvenc", "hevc_nvenc", "av1_nvenc"):
            if name in (enc.stdout or ""):
                out["nvenc"].append(name)
    except (OSError, subprocess.TimeoutExpired) as exc:
        out["error"] = str(exc)
    return out


def comfyui_check() -> dict[str, Any]:
    urls = ["http://127.0.0.1:8188/system_stats", "http://127.0.0.1:8000/system_stats"]
    for url in urls:
        ok, detail = _http_ok(url)
        if ok:
            return {"available": True, "url": url.rsplit("/", 1)[0], "detail": detail, "started_by_us": False}
    return {"available": False, "urls_tried": urls, "started_by_us": False}


def ollama_check() -> dict[str, Any]:
    ok, detail = _http_ok("http://127.0.0.1:11434/api/tags")
    return {"available": ok, "url": "http://127.0.0.1:11434", "detail": detail, "started_by_us": False}


def doctor() -> dict[str, Any]:
    return {
        "gpu": gpu_check(),
        "ffmpeg": ffmpeg_check(),
        "comfyui": comfyui_check(),
        "ollama": ollama_check(),
        "note": "Cloud LLM does not auto-use local GPU; adapters off by default",
    }


def _emit(data: dict[str, Any], *, json_out: bool) -> int:
    if json_out:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Local acceleration capability checks")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("doctor", "gpu-check", "ffmpeg-check", "comfyui-check", "ollama-check"):
        p = sub.add_parser(name.replace("-", "_") if False else name)
        p.add_argument("--json", action="store_true")
    args = ap.parse_args()
    mapping = {
        "doctor": doctor,
        "gpu-check": gpu_check,
        "ffmpeg-check": ffmpeg_check,
        "comfyui-check": comfyui_check,
        "ollama-check": ollama_check,
    }
    data = mapping[args.cmd]()
    return _emit(data, json_out=getattr(args, "json", False))


if __name__ == "__main__":
    raise SystemExit(main())
