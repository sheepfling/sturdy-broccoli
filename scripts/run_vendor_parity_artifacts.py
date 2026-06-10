#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import _bootstrap  # noqa: F401

from hla2010.testing.vendor_parity_artifacts import write_vendor_parity_artifacts

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the harmonized vendor parity artifact packet.")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "analysis" / "vendor_parity_artifacts"),
        help="Directory for generated artifacts",
    )
    args = parser.parse_args(argv)

    paths = write_vendor_parity_artifacts(args.output_dir)
    print(paths.summary_json)
    print(paths.artifact_manifest_csv)
    print(paths.report_markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
