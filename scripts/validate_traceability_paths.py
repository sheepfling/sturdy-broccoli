from __future__ import annotations

import argparse
from pathlib import Path

from hla2010_repo_internal.traceability import (
    ROOT,
    SERVICE_TRACE_INDEX_CSV_PATH,
    SERVICE_TRACE_INDEX_JSON_PATH,
    SERVICE_TRACE_INDEX_MD_PATH,
    TRACEABILITY_MATRIX_PATH,
    validate_active_traceability,
    write_service_trace_index,
)


def cmd_check(_: argparse.Namespace) -> int:
    errors = validate_active_traceability()
    if errors:
        print("Traceability path validation failed")
        for error in errors:
            print(
                f"- {error.source}:{error.row_id}:{error.field}: {error.message}: {error.ref}"
            )
        return 1
    print("Traceability path validation passed")
    print(f"- active traceability matrix: {TRACEABILITY_MATRIX_PATH.relative_to(ROOT).as_posix()}")
    print(f"- active generated ledger: analysis/compliance/requirements_ledger.csv")
    return 0


def cmd_generate(_: argparse.Namespace) -> int:
    errors = validate_active_traceability()
    if errors:
        print("Traceability path validation failed; refusing to generate index")
        for error in errors:
            print(
                f"- {error.source}:{error.row_id}:{error.field}: {error.message}: {error.ref}"
            )
        return 1
    paths = write_service_trace_index()
    print("Generated service trace index artifacts")
    for path in paths:
        print(f"- {path.relative_to(ROOT).as_posix()}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scripts/validate_traceability_paths.py",
        description="Validate active traceability refs and generate the human-facing service trace index.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="validate active traceability refs")
    check_parser.set_defaults(func=cmd_check)

    generate_parser = subparsers.add_parser("generate", help="validate refs and generate service_trace_index artifacts")
    generate_parser.set_defaults(func=cmd_generate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
