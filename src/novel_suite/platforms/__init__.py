"""Platform registry — all supported platforms defined here."""

from novel_suite.platforms._registry import (
    get_platform,
    list_platforms,
    list_platform_keys,
    validate_platform,
)

__all__ = ["get_platform", "list_platform_keys", "list_platforms", "validate_platform"]
