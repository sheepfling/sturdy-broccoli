"""Compatibility facade for the artifact-producing two-federate suite."""
from __future__ import annotations

from .two_federate_suite_runner import (
    run_python_two_federate_suite,
    run_two_federate_suite,
    write_two_federate_suite_artifacts,
)
from .two_federate_suite_types import SuitePaths

__all__ = [
    "SuitePaths",
    "run_python_two_federate_suite",
    "run_two_federate_suite",
    "write_two_federate_suite_artifacts",
]
