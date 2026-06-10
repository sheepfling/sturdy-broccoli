#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import site


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_workspace_imports() -> None:
    for source_root in (PROJECT_ROOT / "src", *sorted((PROJECT_ROOT / "packages").glob("*/src"))):
        if source_root.is_dir():
            site.addsitedir(str(source_root))


_bootstrap_workspace_imports()

from hla2010_repo_internal.verification.vendor_gap_profiles import write_vendor_gap_profile


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
