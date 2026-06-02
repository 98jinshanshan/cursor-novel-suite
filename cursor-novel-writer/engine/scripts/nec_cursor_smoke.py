#!/usr/bin/env python3
"""One-shot NEC smoke for Cursor validation; writes JSON report to stdout or --out."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WRITER = ROOT / "cursor-novel-writer"
ENGINE = WRITER / "engine"
CLI = ENGINE / "novel_cli.py"
DEMO = WRITER / "examples" / "demo-novel"
INTEL = WRITER / "skills" / "novel-market-scan" / "scripts" / "intel_scan.py"


def run(cmd: list[str], cwd: Path | None = None) -> dict:
    r = subprocess.run(
        cmd,
        cwd=str(cwd or ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {
        "cmd": " ".join(cmd),
        "exit": r.returncode,
        "stdout": r.stdout.strip(),
        "stderr": r.stderr.strip(),
    }


def manifest_summary(path: Path) -> dict | None:
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    subs = data.get("subtasks") or []
    done = sum(1 for s in subs if s.get("status") == "done")
    pending = [s["id"] for s in subs if s.get("status") == "pending"]
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "phase": data.get("phase"),
        "status": data.get("status"),
        "skill": data.get("skill"),
        "subtasks_total": len(subs),
        "subtasks_done": done,
        "pending_ids": pending,
    }


def main() -> int:
    out_path = None
    if "--out" in sys.argv:
        i = sys.argv.index("--out")
        out_path = Path(sys.argv[i + 1])

    report: dict = {
        "platform": "cursor",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "steps": [],
        "manifests": {},
        "gaps": [],
    }

    report["steps"].append({"name": "suite_doctor", **run([sys.executable, str(CLI), "suite", "doctor"])})

    report["steps"].append(
        {"name": "phase0_intel_scan_demo", **run([sys.executable, str(INTEL), "--demo"])}
    )

    report["steps"].append(
        {
            "name": "pipeline_status",
            **run(
                [sys.executable, str(CLI), "pipeline", "status", "--project", str(DEMO)]
            ),
        }
    )

    for phase in range(1, 10):
        sync = run(
            [
                sys.executable,
                str(CLI),
                "node",
                "sync",
                "--phase",
                str(phase),
                "--project",
                str(DEMO),
            ]
        )
        report["steps"].append({"name": f"phase{phase}_node_sync", **sync})

        val = run(
            [
                sys.executable,
                str(CLI),
                "node",
                "validate",
                "--phase",
                str(phase),
                "--project",
                str(DEMO),
            ]
        )
        report["steps"].append({"name": f"phase{phase}_node_validate", **val})

        if phase >= 2:
            gate = run(
                [
                    sys.executable,
                    str(CLI),
                    "pipeline",
                    "gate",
                    "--phase",
                    str(phase),
                    "--project",
                    str(DEMO),
                ]
            )
            report["steps"].append({"name": f"phase{phase}_pipeline_gate", **gate})

    export = run(
        [sys.executable, str(CLI), "export", "--project", str(DEMO)]
    )
    report["steps"].append({"name": "export_epub", **export})

    sync9 = run(
        [
            sys.executable,
            str(CLI),
            "node",
            "sync",
            "--phase",
            "9",
            "--project",
            str(DEMO),
        ]
    )
    report["steps"].append({"name": "phase9_node_sync_after_export", **sync9})

    nodes_dir = DEMO / "canon" / "nodes"
    for p in range(0, 10):
        m = manifest_summary(nodes_dir / f"phase-{p}.completion.json")
        if m:
            report["manifests"][f"phase-{p}"] = m

    radar = list((ROOT / "intel" / "radar").glob("*.completion.json")) if (ROOT / "intel" / "radar").is_dir() else []
    for f in radar:
        report["manifests"][f"radar:{f.name}"] = manifest_summary(f)

    # Design checks
    nec_skills = list((WRITER / "skills").glob("*/SKILL.md"))
    dispatch_count = len(list((WRITER / "skills").glob("*/references/node-dispatch.md")))
    report["inventory"] = {
        "skills_with_skill_md": len(nec_skills),
        "node_dispatch_files": dispatch_count,
    }

    for step in report["steps"]:
        if step.get("exit", 0) != 0:
            report["gaps"].append(f"CLI failed: {step['name']} exit={step['exit']}")

    for key, m in report["manifests"].items():
        if m and m.get("status") != "complete":
            report["gaps"].append(f"manifest incomplete: {key} status={m.get('status')}")
        if m and m.get("pending_ids"):
            report["gaps"].append(f"manifest pending subtasks: {key} {m['pending_ids']}")

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
    print(text)
    return 1 if report["gaps"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
