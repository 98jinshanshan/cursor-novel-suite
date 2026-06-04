"""NEC-11: unified AUDIT JSON line for writer pipeline scripts."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

Severity = Literal["blocker", "warn", "nit"]
AuditStatus = Literal["ok", "warn", "error"]


@dataclass
class AuditHit:
    rule_id: str
    severity: Severity
    message: str
    line: int | None = None
    excerpt: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if not d.get("excerpt"):
            d.pop("excerpt", None)
        if d.get("line") is None:
            d.pop("line", None)
        return d


@dataclass
class AuditReport:
    mode: str
    status: AuditStatus = "ok"
    project: str = ""
    chapter: str = ""
    output_path: str = ""
    hits: list[AuditHit] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def add(self, hit: AuditHit) -> None:
        self.hits.append(hit)

    def finalize(self) -> None:
        blockers = sum(1 for h in self.hits if h.severity == "blocker")
        warns = sum(1 for h in self.hits if h.severity == "warn")
        nits = sum(1 for h in self.hits if h.severity == "nit")
        extra = dict(self.summary)
        self.summary = {
            **extra,
            "total_hits": len(self.hits),
            "blockers": blockers,
            "warns": warns,
            "nits": nits,
        }
        if blockers:
            self.status = "error"
        elif warns:
            self.status = "warn"
        else:
            self.status = "ok"

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "status": self.status,
            "project": self.project,
            "chapter": self.chapter,
            "output_path": self.output_path,
            "hits": [h.to_dict() for h in self.hits],
            "summary": self.summary,
        }


def emit_audit(report: AuditReport, *, json_only: bool = False) -> None:
    report.finalize()
    payload = report.to_dict()
    line = f"AUDIT: {json.dumps(payload, ensure_ascii=False)}"
    print(line, flush=True)
    if not json_only:
        print(
            f"Status: {report.status} | hits={report.summary.get('total_hits', 0)} "
            f"(blocker={report.summary.get('blockers', 0)})",
            file=sys.stderr,
        )


def write_audit_file(path: Path, report: AuditReport) -> None:
    from pathlib import Path as P

    report.finalize()
    out = P(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report.output_path = str(out.resolve())
