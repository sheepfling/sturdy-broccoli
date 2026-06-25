#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla.verification.repo_internal.fom_schema_baseline import write_fom_schema_baseline


DEFAULT_OUTPUT_DIR = Path.cwd() / "artifacts" / "fom_schema_baseline"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the repo's dedicated XML schema baseline and keep edition-scope labels aligned with the surrounding report stack.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for the generated schema baseline report.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional custom report title.",
    )
    args = parser.parse_args(argv)

    json_path, md_path, report = write_fom_schema_baseline(output_root=args.output_dir, title=args.title or "FOM Schema Validation Baseline")
    print(json_path)
    print(md_path)
    print(f"cases: {len(report.case_results)}")
    print(f"passed: {report.passed}")
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
