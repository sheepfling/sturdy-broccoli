#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hla2010.testing.two_federate_suite import write_two_federate_suite_artifacts


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
