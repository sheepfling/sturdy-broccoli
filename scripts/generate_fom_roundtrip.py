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

from hla.verification.repo_internal.fom_roundtrip import write_fom_roundtrip


DEFAULT_OUTPUT_DIR = Path.cwd() / "analysis" / "fom_roundtrip"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Round-trip FOM XML through the year-specific FedPro protobuf JSON layer and back."
    )
    parser.add_argument("year", choices=("2010", "2025"), help="FedPro schema year to exercise.")
    parser.add_argument(
        "sources",
        nargs="*",
        help="FOM/XML module designators to exercise. Defaults to the bundled 2010 surface or the 2025 target-radar module.",
    )
    parser.add_argument(
        "--mim-source",
        default=None,
        help="Optional explicit MIM XML path or designator to include in the merge baseline.",
    )
    parser.add_argument(
        "--no-standard-mim",
        action="store_true",
        help="Do not inject the bundled standard MIM automatically in the 2010 lane.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for the generated JSON and Markdown artifacts.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional custom report title.",
    )
    args = parser.parse_args(argv)

    write_fom_roundtrip(
        int(args.year),
        args.sources or None,
        output_dir=args.output_dir,
        include_standard_mim=not args.no_standard_mim,
        mim_source=args.mim_source,
        title=args.title,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
