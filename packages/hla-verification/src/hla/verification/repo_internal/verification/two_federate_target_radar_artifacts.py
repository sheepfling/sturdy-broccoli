"""Target/Radar-owned artifact helpers for the two-federate suite."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Mapping


def write_two_federate_target_radar_track_csv(path: Path, reports: list[dict[str, Any]]) -> Path:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "track_id",
                "target_name",
                "position_x",
                "position_y",
                "position_z",
                "range_m",
                "bearing_rad",
                "rcs_square_meters",
                "time_seconds",
            ],
        )
        writer.writeheader()
        for report in reports:
            position = report["position"]
            writer.writerow(
                {
                    "track_id": report["track_id"],
                    "target_name": report["target_name"],
                    "position_x": position["x"],
                    "position_y": position["y"],
                    "position_z": position["z"],
                    "range_m": report["range_m"],
                    "bearing_rad": report["bearing_rad"],
                    "rcs_square_meters": report["rcs_square_meters"],
                    "time_seconds": report["time_seconds"],
                }
            )
    return path


def build_two_federate_target_radar_artifact_summary(summary: Mapping[str, Any]) -> dict[str, Any]:
    reports = list(summary["target_radar"]["track_reports"])
    return {
        "reports": reports,
        "track_report_count": len(reports),
        "suite_description": (
            "A two-federate verification suite exercising exchange, timestamped delivery, "
            "synchronization, ownership transfer, negotiated ownership, save/restore, DDM "
            "region filtering, Pitch-safe time-window future-exclusion and restore-state "
            "proofs, and a realistic target/radar flow."
        ),
        "overview_caption": (
            "Composite Python in-memory run covering exchange/time, sync, ownership, negotiated "
            "ownership, time-window safety/restore, and target/radar."
        ),
        "range_chart_title": "Target/radar range growth",
    }


__all__ = [
    "build_two_federate_target_radar_artifact_summary",
    "write_two_federate_target_radar_track_csv",
]
