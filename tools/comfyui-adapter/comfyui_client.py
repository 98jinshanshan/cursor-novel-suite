#!/usr/bin/env python3
"""ComfyUI HTTP client — localhost only, timeout-bounded, evidence logging."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_TIMEOUT = 120.0
POLL_INTERVAL = 2.0
MAX_POLL_SEC = 300.0
LOG_DIR = Path(".tmp/comfyui-adapter")


def _ensure_log_dir() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR


def validate_url(url: str) -> str:
    base = url.strip().rstrip("/")
    if not base.startswith(("http://127.0.0.1:", "http://localhost:")):
        raise ValueError(f"Only localhost ComfyUI URLs allowed: {url}")
    return base


def workflow_hash(workflow: dict[str, Any]) -> str:
    raw = json.dumps(workflow, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _request_json(url: str, *, method: str = "GET", payload: dict | None = None, timeout: float = DEFAULT_TIMEOUT) -> Any:
    data = None
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:3000]
        raise RuntimeError(f"HTTP {exc.code} {url}: {body or exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"URL error {url}: {exc.reason}") from exc


def system_stats(url: str) -> dict[str, Any]:
    base = validate_url(url)
    return _request_json(f"{base}/system_stats")


def object_info(url: str) -> dict[str, Any]:
    base = validate_url(url)
    return _request_json(f"{base}/object_info", timeout=60.0)


def queue_prompt(url: str, workflow: dict[str, Any], *, client_id: str | None = None) -> dict[str, Any]:
    base = validate_url(url)
    cid = client_id or str(uuid.uuid4())
    payload = {"prompt": workflow, "client_id": cid}
    data = _request_json(f"{base}/prompt", method="POST", payload=payload)
    pid = data.get("prompt_id")
    if not pid:
        raise RuntimeError(f"No prompt_id in response: {data}")
    wh = workflow_hash(workflow)
    log = _ensure_log_dir() / f"queue_{pid}.json"
    log.write_text(
        json.dumps({"prompt_id": pid, "workflow_hash": wh, "response": data}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"prompt_id": str(pid), "client_id": cid, "workflow_hash": wh, "log_path": str(log)}


def get_history(url: str, prompt_id: str) -> dict[str, Any] | None:
    base = validate_url(url)
    data = _request_json(f"{base}/history/{prompt_id}")
    entry = data.get(prompt_id)
    if entry:
        log = _ensure_log_dir() / f"history_{prompt_id}.json"
        log.write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
    return entry


def wait_for_history(url: str, prompt_id: str, *, timeout: float = MAX_POLL_SEC) -> dict[str, Any]:
    deadline = time.time() + timeout
    last: dict[str, Any] | None = None
    while time.time() < deadline:
        last = get_history(url, prompt_id)
        if last and last.get("outputs"):
            return last
        time.sleep(POLL_INTERVAL)
    raise TimeoutError(f"ComfyUI history timeout for prompt_id={prompt_id}")


def find_first_image(outputs: dict[str, Any]) -> dict[str, Any] | None:
    for node_out in outputs.values():
        for img in node_out.get("images", []):
            if img.get("filename"):
                return img
    return None


def upload_image(url: str, file_path: Path, *, overwrite: bool = True, image_type: str = "input") -> dict[str, Any]:
    """Upload an image to ComfyUI input folder for LoadImage nodes."""
    base = validate_url(url)
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")
    boundary = f"----ComfyUIBoundary{uuid.uuid4().hex}"
    filename = path.name
    file_bytes = path.read_bytes()
    mime = "image/png" if filename.lower().endswith(".png") else "image/jpeg"
    body = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode(),
            f"Content-Type: {mime}\r\n\r\n".encode(),
            file_bytes,
            b"\r\n",
            f"--{boundary}\r\n".encode(),
            b'Content-Disposition: form-data; name="overwrite"\r\n\r\n',
            b"true\r\n" if overwrite else b"false\r\n",
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="type"\r\n\r\n'.encode(),
            f"{image_type}\r\n".encode(),
            f"--{boundary}--\r\n".encode(),
        ]
    )
    req = Request(
        f"{base}/upload/image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:  # noqa: S310
            data = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")[:3000]
        raise RuntimeError(f"Upload failed HTTP {exc.code}: {body_text or exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"Upload URL error: {exc.reason}") from exc
    uploaded_name = data.get("name") or filename
    log = _ensure_log_dir() / f"upload_{uploaded_name}.json"
    log.write_text(json.dumps({"uploaded": uploaded_name, "response": data}, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"filename": uploaded_name, "response": data, "log_path": str(log)}


def fetch_output(url: str, prompt_id: str, out_dir: Path) -> dict[str, Any]:
    base = validate_url(url)
    hist = wait_for_history(base, prompt_id)
    outputs = hist.get("outputs") or {}
    img = find_first_image(outputs)
    if not img:
        err = hist.get("status", {}).get("messages") or hist.get("status")
        raise RuntimeError(f"No image in history for {prompt_id}: {err}")
    out_dir.mkdir(parents=True, exist_ok=True)
    params = urlencode(
        {
            "filename": img["filename"],
            "subfolder": img.get("subfolder", ""),
            "type": img.get("type", "output"),
        }
    )
    view_url = f"{base}/view?{params}"
    req = Request(view_url, method="GET")
    with urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:  # noqa: S310
        raw = resp.read()
    dest = out_dir / img["filename"]
    dest.write_bytes(raw)
    return {
        "prompt_id": prompt_id,
        "workflow_hash": None,
        "filename": img["filename"],
        "path": str(dest.resolve()),
        "bytes": len(raw),
        "history_log": str(_ensure_log_dir() / f"history_{prompt_id}.json"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="ComfyUI localhost HTTP client")
    ap.add_argument("command", choices=["system-stats", "object-info", "queue-prompt", "history", "fetch-output"])
    ap.add_argument("--url", default="http://127.0.0.1:8188")
    ap.add_argument("--workflow", default="", help="Workflow JSON path for queue-prompt")
    ap.add_argument("--prompt-id", default="")
    ap.add_argument("--out", default="", help="Output directory for fetch-output")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        if args.command == "system-stats":
            result = {"status": "ok", "data": system_stats(args.url)}
        elif args.command == "object-info":
            data = object_info(args.url)
            result = {"status": "ok", "node_count": len(data), "log_path": str(_ensure_log_dir() / "object_info_summary.json")}
            summary = {k: list(v.keys())[:5] if isinstance(v, dict) else v for k, v in list(data.items())[:20]}
            (_ensure_log_dir() / "object_info_full.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            (_ensure_log_dir() / "object_info_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
            result["sample_nodes"] = list(data.keys())[:30]
        elif args.command == "queue-prompt":
            if not args.workflow:
                raise ValueError("--workflow required")
            wf = json.loads(Path(args.workflow).read_text(encoding="utf-8"))
            result = {"status": "ok", **queue_prompt(args.url, wf)}
        elif args.command == "history":
            if not args.prompt_id:
                raise ValueError("--prompt-id required")
            hist = get_history(args.url, args.prompt_id)
            result = {"status": "ok" if hist else "pending", "history": hist}
        elif args.command == "fetch-output":
            if not args.prompt_id or not args.out:
                raise ValueError("--prompt-id and --out required")
            result = {"status": "ok", **fetch_output(args.url, args.prompt_id, Path(args.out))}
        else:
            result = {"status": "error", "message": "unknown command"}
    except Exception as exc:  # noqa: BLE001
        result = {"status": "error", "message": str(exc)[:500]}
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result, file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
