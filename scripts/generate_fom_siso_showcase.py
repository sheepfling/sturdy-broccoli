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

from hla.verification.repo_internal.fom_siso_showcase import write_fom_siso_showcase


DEFAULT_OUTPUT_DIR = Path.cwd() / "artifacts" / "fom_siso_showcase"
PACKET_CHOICES = (
    "link16-standalone-template",
    "link16-rpr2-integrated",
    "rpr3-annex-a-normative",
    "rpr3-merged-informative-1516-2010",
    "space-fom-core",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate an artifact-backed showcase packet for Link 16, RPR 3.0, and Space FOM using the repo validation, round-trip, overview, and workbench surfaces.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for the generated showcase artifacts.",
    )
    parser.add_argument(
        "--packet",
        action="append",
        choices=PACKET_CHOICES,
        help="Optional packet id to limit the run. May be passed more than once.",
    )
    parser.add_argument(
        "--strict-identification",
        action="store_true",
        help="Enable stricter identification checks in the validator stage.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional custom report title.",
    )
    args = parser.parse_args(argv)

    json_path, md_path, html_path, report = write_fom_siso_showcase(
        args.output_dir,
        packet_ids=tuple(args.packet) if args.packet else None,
        strict_identification=args.strict_identification,
        title=args.title or "High-Value SISO FOM Showcase",
    )
    print(json_path)
    print(md_path)
    print(html_path)
    print(report.workbench_snapshot_path)
    print(report.workbench_html_path)
    print(f"packets: {len(report.packet_results)}")
    print(f"passed: {report.passed}")
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
