#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
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

from hla.verification.repo_internal.verification.vendor_probe_stability import canonical_operator_command, write_vendor_probe_stability


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
