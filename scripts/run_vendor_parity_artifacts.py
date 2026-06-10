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

from hla2010_repo_internal.verification.vendor_parity_artifacts import write_vendor_parity_artifacts


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
