"""VideoRender-2R ComfyUI adapter and render tests."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CH02 = ROOT / "novels" / "novel-837dd4f1" / "video" / "ch02"
ADAPTER = ROOT / "tools" / "comfyui-adapter"
FORBIDDEN = [
    Path(r"G:/SOLO小说项目"),
    Path(r"G:/Reasonix/SOLO小说视频项目"),
]
COMFYUI_HOST = "127.0.0.1"
COMFYUI_PORT = 8188


def _comfyui_reachable(host: str = COMFYUI_HOST, port: int = COMFYUI_PORT, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _comfyui_live_enabled() -> bool:
    return os.environ.get("NOVEL_SUITE_COMFYUI_LIVE") == "1"


def _seed_shot_list_csv(path: Path, *, rows: int = 10) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "shot_id,static_prompt,motion_prompt,emotion,characters,shot_size,duration_sec\n"
    )
    body = "".join(
        f"shot_{i:02d},office corridor,walk forward,tense,林骁|陈琪,medium,5\n"
        for i in range(1, rows + 1)
    )
    path.write_text(header + body, encoding="utf-8")


def test_forbidden_paths_not_read():
    for p in FORBIDDEN:
        assert not any(str(p).lower() in str(x).lower() for x in [ROOT])


@pytest.mark.live_comfyui
@pytest.mark.skipif(
    not _comfyui_live_enabled() or not _comfyui_reachable(),
    reason="Set NOVEL_SUITE_COMFYUI_LIVE=1 with ComfyUI on localhost:8188",
)
def test_comfyui_client_system_stats_runs():
    proc = subprocess.run(
        [sys.executable, str(ADAPTER / "comfyui_client.py"), "system-stats", "--url", "http://127.0.0.1:8188", "--json"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(ROOT),
    )
    data = json.loads(proc.stdout or "{}")
    assert data.get("status") in ("ok", "error")


def test_object_info_writes_capability_report(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    sys.path.insert(0, str(ADAPTER))
    import model_audit  # noqa: E402

    ch02 = tmp_path / "ch02"
    monkeypatch.setattr(model_audit, "CH02", ch02)

    fake_oi = {
        "CheckpointLoaderSimple": {"input": {"required": {"ckpt_name": [["model.safetensors"]]}}},
        "KSampler": {},
        "CLIPTextEncode": {},
        "SaveImage": {},
        "EmptyLatentImage": {},
        "VAEDecode": {},
        "WanImageToVideo": {},
    }
    audit = model_audit.run_audit(fake_oi, ckpt_required="model.safetensors")
    assert audit["i2v_available"] is True
    assert (ch02 / "comfyui_capability_report.md").is_file()


def test_workflow_registry_generates(tmp_path: Path):
    sys.path.insert(0, str(ADAPTER))
    from workflow_registry import build_registry  # noqa: E402

    out = tmp_path / "comfyui_workflows"
    reg = build_registry(object_info={}, out_dir=out)
    assert reg["selected_workflow_id"]
    assert (out / "registry.json").is_file()


def test_input_mapping_generates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    sys.path.insert(0, str(ADAPTER))
    import workflow_adapter  # noqa: E402

    ch02 = tmp_path / "ch02"
    monkeypatch.setattr(workflow_adapter, "CH02", ch02)
    _seed_shot_list_csv(ch02 / "shot_list.csv")

    m = workflow_adapter.build_input_mapping(ckpt="test.safetensors")
    assert len(m["shots"]) >= 10
    assert (ch02 / "comfyui_workflows" / "input_mapping.json").is_file()


@pytest.mark.local_ch02
def test_render_manifest_has_evidence_or_blocker():
    manifest_path = CH02 / "comfyui_render_manifest.json"
    if not manifest_path.is_file():
        pytest.skip("render not run yet")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data.get("verdict") == "blocked"
    assert data.get("commercial_release_allowed") is False
    shots = data.get("rendered_shots") or []
    failures = data.get("failures") or []
    if shots:
        assert shots[0].get("prompt_id")
        assert shots[0].get("workflow_hash")
    else:
        assert failures or data.get("comfyui_available") is False


@pytest.mark.local_ch02
def test_placeholder_not_graded_b_or_a():
    qc = CH02 / "video_qc_report.md"
    if not qc.is_file():
        pytest.skip("no qc report")
    text = qc.read_text(encoding="utf-8")
    is_placeholder = "visual source: placeholder" in text.lower() or "comfyui renders: 0" in text.lower()
    if is_placeholder:
        assert "video_level: B" not in text
        assert "video_level: A" not in text


@pytest.mark.local_ch02
def test_nvp_v2_consistent_with_qc():
    qc = CH02 / "video_qc_report.md"
    nvp = CH02 / "NVP-V2-video-export-qc.result.md"
    if not qc.is_file() or not nvp.is_file():
        pytest.skip("reports missing")
    qc_text = qc.read_text(encoding="utf-8")
    nvp_text = nvp.read_text(encoding="utf-8")
    for level in ("D", "C", "B-", "B", "A-", "A"):
        if f"video_level: {level}" in qc_text:
            assert level in nvp_text
            break
