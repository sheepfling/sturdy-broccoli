#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path.cwd() / "artifacts" / "fom_stress"


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla.verification.repo_internal.fom_stress import write_fom_stress_report


def _parse_years(value: str) -> tuple[int, ...]:
    years: list[int] = []
    for chunk in value.split(","):
        item = chunk.strip()
        if not item:
            continue
        years.append(int(item))
    if not years:
        raise ValueError("at least one year is required")
    return tuple(years)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh the public baseline and generate a FOM stress-lane report that distinguishes merge, round-trip, template-fail-fast, and runtime-backed roles.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for the generated stress artifacts.",
    )
    parser.add_argument(
        "--years",
        default="2010,2025",
        help="Comma-separated years to exercise. Defaults to 2010,2025.",
    )
    parser.add_argument(
        "--refresh-baseline",
        action="store_true",
        help="Refresh the public baseline XML corpus and any local SISO inventory before running the stress report.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional custom report title.",
    )
    args = parser.parse_args(argv)

    if args.refresh_baseline:
        from fetch_public_fom_baseline import main as refresh_public_baseline
        from generate_siso_inventory import main as refresh_siso_inventory

        refresh_public_baseline([])
        refresh_siso_inventory([])

    json_path, md_path, report = write_fom_stress_report(
        args.output_dir,
        years=_parse_years(args.years),
        title=args.title,
    )
    print(json_path)
    print(md_path)
    print(f"families passed: {sum(1 for row in report.families if row.passed)} / {len(report.families)}")
    return 0 if all(row.passed for row in report.families) else 1


if __name__ == "__main__":
    raise SystemExit(main())
