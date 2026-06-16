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

from hla.verification.repo_internal.verification.vendor_gap_profiles import write_vendor_gap_profile


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write a machine-readable known-gap vendor runtime profile artifact.")
    parser.add_argument("--profile", required=True, help="Known-gap profile name")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "analysis" / "vendor_gap_profiles"),
        help="Directory for generated artifacts",
    )
    args = parser.parse_args(argv)
    path = write_vendor_gap_profile(args.output_dir, args.profile)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
