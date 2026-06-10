#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import site


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _bootstrap_workspace_imports() -> None:
    for source_root in (PROJECT_ROOT / "src", *sorted((PROJECT_ROOT / "packages").glob("*/src"))):
        if source_root.is_dir():
            site.addsitedir(str(source_root))


_bootstrap_workspace_imports()

from hla2010_repo_internal.verification.vendor_probe_stability import canonical_operator_command, write_vendor_probe_stability


def _load_attempts(path: Path) -> list[dict[str, int]]:
    attempts: list[dict[str, int]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            attempts.append(
                {
                    "iteration": int(row["iteration"]),
                    "exit_code": int(row["exit_code"]),
                    "duration_seconds": int(row["duration_seconds"]),
                }
            )
    return attempts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write repeated-run stability artifacts for a vendor profile.")
    parser.add_argument("--profile", required=True, help="Vendor profile being exercised repeatedly.")
    parser.add_argument("--repeat-count", required=True, type=int, help="Requested repeat count.")
    parser.add_argument(
        "--command",
        help="Canonical operator command representing the repeated probe route. Defaults from the profile map.",
    )
    parser.add_argument(
        "--executor-command",
        help="Actual delegate command used for each attempt when it differs from the canonical operator route.",
    )
    parser.add_argument("--attempts-file", required=True, type=Path, help="CSV file containing attempt rows.")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "analysis" / "vendor_probe_stability"),
        help="Directory for generated stability artifacts.",
    )
    args = parser.parse_args(argv)

    paths = write_vendor_probe_stability(
        args.output_dir,
        profile=args.profile,
        repeat_count=args.repeat_count,
        command=args.command or canonical_operator_command(args.profile),
        executor_command=args.executor_command,
        attempts=_load_attempts(args.attempts_file),
    )
    print(paths.summary_json)
    print(paths.report_markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
