#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path
SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path.cwd()


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla2010_repo_internal.verification.vendor_probe_promotion_review import write_vendor_probe_promotion_review


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write a promotion-review artifact over repeated-run vendor probe evidence.")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "analysis" / "vendor_probe_promotion_review"),
        help="Directory for generated promotion-review artifacts.",
    )
    args = parser.parse_args(argv)
    paths = write_vendor_probe_promotion_review(args.output_dir)
    print(paths.summary_json)
    print(paths.report_markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
