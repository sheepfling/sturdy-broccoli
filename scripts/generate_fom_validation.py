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

from hla.verification.repo_internal.fom_validate import write_fom_validation, write_fom_validation_html


DEFAULT_OUTPUT_DIR = Path.cwd() / "analysis" / "fom_validation"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate one or more FOM/MIM XML sources with a human-readable report.")
    parser.add_argument("sources", nargs="*", help="XML file paths or repo-known FOM designators such as DemoFOMmodule.xml")
    parser.add_argument(
        "--family",
        action="append",
        default=[],
        help="Inventory scenario family to validate as its default ordered/base load set. Repeatable.",
    )
    parser.add_argument(
        "--edition",
        choices=("auto", "2010", "2025"),
        default="auto",
        help="Validator path to use. Defaults to auto-detection by inventory and XML namespace.",
    )
    parser.add_argument(
        "--profile",
        choices=("auto", "dif", "omt"),
        default="auto",
        help="2010 XML schema profile. Ignored on the 2025 validator path.",
    )
    parser.add_argument(
        "--schema",
        default=None,
        help="Optional explicit 2025 OMT XSD path.",
    )
    parser.add_argument(
        "--strict-identification",
        action="store_true",
        help="Enable stricter 2025 identification-table validation.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for generated JSON and Markdown validation reports.",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Also write an interactive HTML view alongside the JSON and Markdown reports.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional custom report title.",
    )
    args = parser.parse_args(argv)
    if not args.sources and not args.family:
        parser.error("at least one source or --family is required")

    json_path, md_path, report = write_fom_validation(
        args.sources,
        output_dir=args.output_dir,
        families=args.family,
        edition=args.edition,
        profile=args.profile,
        strict_identification=args.strict_identification,
        schema_path=args.schema,
        title=args.title,
    )
    if args.html:
        html_path = write_fom_validation_html(
            args.sources,
            output_dir=args.output_dir,
            families=args.family,
            edition=args.edition,
            profile=args.profile,
            strict_identification=args.strict_identification,
            schema_path=args.schema,
            title=args.title,
        )
    else:
        html_path = None
    for row in report.source_reports:
        print(
            f"{row.source}: {row.verdict} "
            f"(edition={row.effective_edition}, schema={'ok' if row.schema_valid else 'fail'}, "
            f"parsed={'ok' if row.parsed else 'fail'}, semantic={'ok' if row.semantic_valid else 'fail'})"
        )
    for row in report.load_set_reports:
        print(
            f"load-set:{row.name}: {row.verdict} "
            f"(edition={row.effective_edition}, parsed={'ok' if row.parsed else 'fail'}, "
            f"semantic={'ok' if row.semantic_valid else 'fail'}, members={len(row.source_paths)})"
        )
    print(f"json: {json_path}")
    print(f"markdown: {md_path}")
    if html_path is not None:
        print(f"html: {html_path}")
    all_rows_passed = all(row.passed for row in report.source_reports) and all(row.passed for row in report.load_set_reports)
    return 0 if all_rows_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
