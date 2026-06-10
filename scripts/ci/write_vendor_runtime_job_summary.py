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

from hla2010_repo_internal.verification.vendor_runtime_job_summary import (
    VendorRuntimeJobSummaryPaths,
    build_vendor_runtime_job_summary,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a GitHub-job-friendly vendor runtime summary from normalized status artifacts.")
    parser.add_argument(
        "--status-dir",
        default=str(PROJECT_ROOT / "analysis" / "vendor_runtime_status"),
        help="Directory containing vendor_runtime_status summary subdirectories.",
    )
    parser.add_argument(
        "--parity-dir",
        default=str(PROJECT_ROOT / "analysis" / "vendor_parity_artifacts"),
        help="Directory containing vendor_parity_artifacts_summary.json.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the rendered Markdown to this path instead of stdout.",
    )
    args = parser.parse_args(argv)

    rendered = build_vendor_runtime_job_summary(
        VendorRuntimeJobSummaryPaths(
            status_dir=Path(args.status_dir),
            parity_dir=Path(args.parity_dir),
        )
    )
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
