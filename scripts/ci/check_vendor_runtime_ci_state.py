#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import site


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _bootstrap_workspace_imports() -> None:
    for source_root in (PROJECT_ROOT / "src", *sorted((PROJECT_ROOT / "packages").glob("*/src"))):
        if source_root.is_dir():
            site.addsitedir(str(source_root))


_bootstrap_workspace_imports()

from hla2010_repo_internal.verification.vendor_runtime_ci_state import write_vendor_runtime_ci_state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate dedicated CI runtime state for vendor-green jobs.")
    parser.add_argument(
        "--profile",
        choices=("certi", "pitch", "matrix", "vendor-edge", "all"),
        required=True,
        help="Dedicated vendor CI profile to validate.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "analysis" / "vendor_runtime_ci_state"),
        help="Directory for generated CI runtime-state artifacts.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON summary to stdout.")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir) / args.profile.replace("-", "_")
    paths = write_vendor_runtime_ci_state(output_dir, profile=args.profile)
    if args.json:
        print(paths.summary_json.read_text(encoding="utf-8"), end="")
    else:
        print(paths.summary_json)
        print(paths.report_markdown)
    payload = json.loads(paths.summary_json.read_text(encoding="utf-8"))
    return int(payload["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
