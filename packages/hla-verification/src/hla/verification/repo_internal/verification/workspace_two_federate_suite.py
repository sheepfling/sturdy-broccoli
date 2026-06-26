"""Repo-level two-federate suite entrypoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .two_federate_suite_runner import (
    SuitePaths,
    run_python_two_federate_suite,
    run_two_federate_suite,
    write_two_federate_suite_artifacts,
)

from .two_federate_runtime_launchers import build_two_federate_runtime_launchers


def run_workspace_two_federate_suite(
    *,
    target_radar_steps: int = 4,
    event_sink: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Run the suite with repo-level vendor launcher injection enabled."""
    return run_two_federate_suite(
        target_radar_steps=target_radar_steps,
        runtime_launchers=build_two_federate_runtime_launchers(),
        event_sink=event_sink,
    )


def write_workspace_two_federate_suite_artifacts(
    output_dir: Path | str,
    *,
    target_radar_steps: int = 4,
    event_sink: Callable[[dict[str, Any]], None] | None = None,
) -> SuitePaths:
    """Write suite artifacts with repo-level vendor launcher injection enabled."""
    return write_two_federate_suite_artifacts(
        output_dir,
        target_radar_steps=target_radar_steps,
        runtime_launchers=build_two_federate_runtime_launchers(),
        event_sink=event_sink,
    )


__all__ = [
    "SuitePaths",
    "build_two_federate_runtime_launchers",
    "run_python_two_federate_suite",
    "run_two_federate_suite",
    "run_workspace_two_federate_suite",
    "write_two_federate_suite_artifacts",
    "write_workspace_two_federate_suite_artifacts",
]
