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

from hla.verification.repo_internal.siso_corpus import write_siso_inventory


DEFAULT_OUTPUT_ROOT = Path.cwd() / "analysis" / "siso_downloads"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract and catalog locally downloaded SISO DataFiles packages into a repo-readable inventory."
    )
    parser.add_argument(
        "--download-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Directory containing downloaded SISO archives and/or extracted XMLs.",
    )
    parser.add_argument(
        "--output-root",
        default=None,
        help="Optional directory for the generated inventory files. Defaults to the download root.",
    )
    args = parser.parse_args(argv)

    json_path, md_path, entries = write_siso_inventory(
        output_root=args.output_root,
        download_root=Path(args.download_root),
    )
    print(json_path)
    print(md_path)
    print(f"entries: {len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
