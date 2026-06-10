#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import site


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _bootstrap_workspace_imports() -> None:
    for source_root in (PROJECT_ROOT / "src", *sorted((PROJECT_ROOT / "packages").glob("*/src"))):
        if source_root.is_dir():
            site.addsitedir(str(source_root))


_bootstrap_workspace_imports()

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
