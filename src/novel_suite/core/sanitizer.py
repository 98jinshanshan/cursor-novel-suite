"""Input/output sanitization — LLM prompt injection protection (Sprint 0 Day 4)."""

from __future__ import annotations

import re

INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(above|previous|all)\s+instructions", re.IGNORECASE),
    re.compile(r"forget\s+(everything|all)\s+(above|previous)", re.IGNORECASE),
    re.compile(r"you\s+are\s+(now|not)\s+(required|allowed|obligated)", re.IGNORECASE),
    re.compile(r"system\s*(prompt|instruction|message)", re.IGNORECASE),
]

MAX_INPUT_LENGTH = 2000

OUTPUT_SENSITIVE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"system\s*(prompt|instruction|message)", re.IGNORECASE),
    re.compile(r"process\.env", re.IGNORECASE),
    re.compile(r"fs\.(read|write|append)File", re.IGNORECASE),
    re.compile(r"exec\(|execSync\(|shell=True", re.IGNORECASE),
]


class OutputFilterResult:
    __slots__ = ("safe", "violations")

    def __init__(self, safe: bool, violations: list[str]) -> None:
        self.safe = safe
        self.violations = violations


def sanitize_prompt_input(text: str) -> str:
    """Strip injection phrases, truncate length, remove control chars."""
    cleaned = text or ""
    for pattern in INJECTION_PATTERNS:
        cleaned = pattern.sub("[FILTERED]", cleaned)

    if len(cleaned) > MAX_INPUT_LENGTH:
        cleaned = cleaned[:MAX_INPUT_LENGTH]

    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", cleaned)
    return cleaned


def detect_injection(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text or ""):
            hits.append(pattern.pattern)
    return hits


def filter_llm_output(output: str) -> OutputFilterResult:
    violations: list[str] = []
    for pattern in OUTPUT_SENSITIVE_PATTERNS:
        if pattern.search(output or ""):
            violations.append(pattern.pattern)
    return OutputFilterResult(safe=len(violations) == 0, violations=violations)
