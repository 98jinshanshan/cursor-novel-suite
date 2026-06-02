#!/usr/bin/env python3
"""NEC V0 smoke: synthetic job completion manifest (no FFmpeg)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
MONOREPO = ENGINE.parent.parent
WRITER = MONOREPO / "cursor-novel-writer"
DEMO_CH = WRITER / "examples" / "demo-novel" / "chapters" / "01_试章.md"

sys.path.insert(0, str(ENGINE))
sys.path.insert(0, str(ENGINE / "scripts"))

import video_cli  # noqa: E402
import video_node_completion  # noqa: E402


def main() -> int:
    jobs_root = MONOREPO / "cursor-novel-video" / "tmp" / "video_jobs"
    jobs_root.mkdir(parents=True, exist_ok=True)
    video_cli.DEFAULT_JOBS = jobs_root

    if not DEMO_CH.is_file():
        print(f"ERROR: missing demo chapter {DEMO_CH}", file=sys.stderr)
        return 1

    job = video_cli.create_job("summary", DEMO_CH, "9:16")
    out = job / "output"
    out.mkdir(exist_ok=True)
    mp4 = out / f"{job.name}_summary.mp4"
    mp4.write_bytes(b"\x00\x00\x00\x18ftypmp42")
    path = video_node_completion.write_job_completion(job, artifact=mp4, qc_ok=True, mode="summary")
    data = json.loads(path.read_text(encoding="utf-8"))
    pending = [s["id"] for s in data.get("subtasks", []) if s.get("status") == "pending"]
    report = {
        "job_dir": str(job),
        "completion": str(path),
        "status": data.get("status"),
        "pending": pending,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if data.get("status") != "complete" or pending:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
