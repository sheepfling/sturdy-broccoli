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

from hla.verification.repo_internal.verification.vendor_parity_artifacts import write_vendor_parity_artifacts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the harmonized vendor parity artifact packet.")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Repository root used for default analysis artifact locations.",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory for generated artifacts",
    )
    args = parser.parse_args(argv)
    project_root = args.project_root.resolve()
    output_dir = args.output_dir or str(project_root / "analysis" / "vendor_parity_artifacts")

    paths = write_vendor_parity_artifacts(output_dir)
    print(paths.summary_json)
    print(paths.artifact_manifest_csv)
    print(paths.report_markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
