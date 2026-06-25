#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path.cwd()


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla.verification.repo_internal.verification.workspace_two_federate_suite import write_workspace_two_federate_suite_artifacts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the composite two-federate suite and write artifacts.")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "artifacts" / "two_federate_suite"),
        help="Directory for generated artifacts",
    )
    parser.add_argument("--target-radar-steps", type=int, default=4)
    args = parser.parse_args(argv)

    paths = write_workspace_two_federate_suite_artifacts(
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
