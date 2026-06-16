"""Route modules — re-export app handlers for contract clarity."""

from novel_suite.server.app import (
    handle_artifacts,
    handle_doctor,
    handle_events,
    handle_market_scan_run,
    handle_project_status,
    handle_projects_active,
    handle_projects_list,
    handle_projects_use,
)

__all__ = [
    "handle_doctor",
    "handle_projects_list",
    "handle_projects_active",
    "handle_projects_use",
    "handle_project_status",
    "handle_market_scan_run",
    "handle_artifacts",
    "handle_events",
]
