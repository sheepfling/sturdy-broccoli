#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import site


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_workspace_imports() -> None:
    for source_root in (PROJECT_ROOT / "src", *sorted((PROJECT_ROOT / "packages").glob("*/src"))):
        if source_root.is_dir():
            site.addsitedir(str(source_root))


_bootstrap_workspace_imports()

from hla2010_repo_internal.verification.vendor_runtime_status import write_vendor_runtime_status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify vendor runtime preflight artifacts for repo-green or vendor-green lanes.")
    parser.add_argument(
        "--artifact-dir",
        default=str(PROJECT_ROOT / "analysis" / "preflight_artifacts"),
        help="Directory containing certi-preflight.json and/or pitch-preflight.json",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "analysis" / "vendor_runtime_status"),
        help="Directory for generated summary artifacts",
    )
    parser.add_argument(
        "--lane",
        choices=("repo-green", "vendor-green"),
        default="repo-green",
        help="Classification policy to apply",
    )
    parser.add_argument(
        "--vendor",
        action="append",
        choices=("certi", "pitch"),
        dest="vendors",
        help="Vendor to classify; repeat to select more than one. Defaults to both.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the generated JSON summary to stdout",
    )
    args = parser.parse_args(argv)

    vendors = tuple(args.vendors or ("certi", "pitch"))
    paths = write_vendor_runtime_status(
        args.output_dir,
        artifact_dir=args.artifact_dir,
        lane=args.lane,
        vendors=vendors,
    )
    if args.json:
        print(paths.summary_json.read_text(encoding="utf-8"), end="")
    else:
        print(paths.summary_json)
        print(paths.report_markdown)
    summary = json.loads(paths.summary_json.read_text(encoding="utf-8"))
    return int(summary["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
