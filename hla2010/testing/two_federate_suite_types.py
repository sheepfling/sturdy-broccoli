"""Shared types for the two-federate suite packet."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SuitePaths:
    output_dir: Path
    summary_json: Path
    track_reports_csv: Path
    callbacks_csv: Path
    report_markdown: Path
    summary_svg: Path
    timeline_svg: Path


__all__ = ["SuitePaths"]
