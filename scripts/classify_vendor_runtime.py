#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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

from hla.verification.repo_internal.verification.vendor_runtime_status import write_vendor_runtime_status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify vendor runtime preflight artifacts for repo-green or vendor-green lanes.")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Repository root used for default generated artifact locations.",
    )
    parser.add_argument(
        "--artifact-dir",
        help="Directory containing certi-preflight.json and/or pitch-preflight.json",
    )
    parser.add_argument(
        "--output-dir",
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

    project_root = args.project_root.resolve()
    artifact_dir = args.artifact_dir or str(project_root / "artifacts" / "preflight_artifacts")
    output_dir = args.output_dir or str(project_root / "artifacts" / "vendor_runtime_status")
    vendors = tuple(args.vendors or ("certi", "pitch"))
    paths = write_vendor_runtime_status(
        output_dir,
        artifact_dir=artifact_dir,
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
