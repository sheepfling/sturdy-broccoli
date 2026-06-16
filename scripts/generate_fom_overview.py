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

from hla.verification.repo_internal.fom_overview import write_fom_overview, write_fom_overview_html


DEFAULT_OUTPUT_DIR = Path.cwd() / "analysis" / "fom_overview"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate an at-a-glance visual overview of one or more FOM modules.")
    parser.add_argument(
        "sources",
        nargs="*",
        help="FOM/MIM module designators to visualize. Defaults to TargetRadarFOMmodule.xml.",
    )
    parser.add_argument(
        "--no-standard-mim",
        action="store_true",
        help="Do not merge the built-in standard MIM into the overview.",
    )
    parser.add_argument(
        "--mim",
        default=None,
        help="Optional explicit MIM designator to merge before the user modules.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for the generated overview artifacts.",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Also write an interactive HTML overview alongside the JSON and Markdown outputs.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional custom report title.",
    )
    args = parser.parse_args(argv)

    sources = args.sources or ("TargetRadarFOMmodule.xml",)
    write_fom_overview(
        sources,
        output_dir=args.output_dir,
        include_standard_mim=not args.no_standard_mim,
        mim_source=args.mim,
        title=args.title,
    )
    if args.html:
        write_fom_overview_html(
            sources,
            output_dir=args.output_dir,
            include_standard_mim=not args.no_standard_mim,
            mim_source=args.mim,
            title=args.title,
        )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
