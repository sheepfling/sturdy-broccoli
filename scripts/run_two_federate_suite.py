#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import _bootstrap  # noqa: F401

from hla2010_fom_target_radar.testing.two_federate_suite_runner import write_two_federate_suite_artifacts

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the composite two-federate suite and write artifacts.")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "analysis" / "two_federate_suite"),
        help="Directory for generated artifacts",
    )
    parser.add_argument("--target-radar-steps", type=int, default=4)
    args = parser.parse_args(argv)

    paths = write_two_federate_suite_artifacts(
        args.output_dir,
        target_radar_steps=args.target_radar_steps,
    )
    print(paths.summary_json)
    print(paths.track_reports_csv)
    print(paths.callbacks_csv)
    print(paths.report_markdown)
    print(paths.summary_svg)
    print(paths.timeline_svg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
