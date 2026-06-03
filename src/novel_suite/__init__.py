"""Novel Suite 2.0 — installable package for writer/video agent tooling."""

from novel_suite.core.result import Result, artifact, error_result, ok_result

__version__ = "2.0.0"

__all__ = [
    "Result",
    "__version__",
    "artifact",
    "error_result",
    "ok_result",
]
