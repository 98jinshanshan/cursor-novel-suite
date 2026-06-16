"""Adapter execution policy — all adapters default-off, dry-run only (C5)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class AdapterPolicyError(ValueError):
    """Raised when adapter policy forbids execution."""


@dataclass
class AdapterPolicy:
    adapter: str
    enabled: bool = False
    dry_run: bool = True
    allow_external_call: bool = False
    manual_execution_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def default_adapter_policy(adapter_name: str) -> dict[str, Any]:
    """Return default closed policy for an adapter skeleton."""
    return AdapterPolicy(adapter=adapter_name).to_dict()


def assert_dry_run_only(policy: dict[str, Any]) -> None:
    """Reject any policy that would permit real external execution."""
    if policy.get("enabled"):
        raise AdapterPolicyError(
            f"Adapter {policy.get('adapter', '?')!r}: enabled=True is forbidden (dry-run only)"
        )
    if policy.get("allow_external_call"):
        raise AdapterPolicyError(
            f"Adapter {policy.get('adapter', '?')!r}: allow_external_call=True is forbidden"
        )
    if not policy.get("dry_run", True):
        raise AdapterPolicyError(
            f"Adapter {policy.get('adapter', '!')!r}: dry_run must be True"
        )
