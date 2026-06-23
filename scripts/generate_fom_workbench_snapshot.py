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

from hla.verification.repo_internal.fom_workbench import (
    apply_repo_owned_fom_edits,
    build_fom_workbench_snapshot,
    write_fom_workbench_html,
)


DEFAULT_OUTPUT_DIR = Path.cwd() / "analysis" / "fom_workbench"


def _parse_custom_load_set_specs(values: list[str]) -> dict[str, tuple[str, ...]]:
    parsed: dict[str, tuple[str, ...]] = {}
    for value in values:
        name, separator, members = value.partition("=")
        if not separator:
            raise ValueError(f"Invalid --custom-load-set value {value!r}; expected NAME=id1,id2")
        member_ids = tuple(item.strip() for item in members.split(",") if item.strip())
        if not member_ids:
            raise ValueError(f"Invalid --custom-load-set value {value!r}; expected at least one member id")
        parsed[name.strip()] = member_ids
    return parsed


def _parse_diff_specs(values: list[str]) -> tuple[tuple[str, str], ...]:
    rows: list[tuple[str, str]] = []
    for value in values:
        left, separator, right = value.partition(":")
        if not separator:
            raise ValueError(f"Invalid --diff value {value!r}; expected left:right")
        rows.append((left.strip(), right.strip()))
    return tuple(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the JSON and optional HTML artifacts backing the FOM workbench UI with edition-scope labels.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for the generated FOM workbench snapshot.",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Also generate a small local HTML workbench that consumes the snapshot.",
    )
    parser.add_argument(
        "--custom-load-set",
        action="append",
        default=[],
        help="Named custom load set in the form NAME=id1,id2,id3. Repeatable.",
    )
    parser.add_argument(
        "--diff",
        action="append",
        default=[],
        help="Named diff request in the form left:right. Names may be family names or custom load-set names.",
    )
    parser.add_argument("--edit-entry", default=None, help="Inventory entry id to edit through the guarded repo-owned flow.")
    parser.add_argument("--set-description", default=None, help="Replacement modelIdentification description for guarded edit flow.")
    parser.add_argument("--add-keyword", action="append", default=[], help="Keyword to append in guarded edit flow. Repeatable.")
    parser.add_argument("--add-note", action="append", default=[], help="Note to append in guarded edit flow. Repeatable.")
    parser.add_argument("--in-place", action="store_true", help="Apply guarded edit directly to the repo-owned XML instead of writing a copy.")
    parser.add_argument("--edit-output", default=None, help="Optional output path for guarded edit copies.")
    args = parser.parse_args(argv)
    if args.edit_entry:
        apply_repo_owned_fom_edits(
            args.edit_entry,
            description=args.set_description,
            add_keywords=tuple(args.add_keyword),
            add_notes=tuple(args.add_note),
            output_path=args.edit_output,
            in_place=args.in_place,
        )
        return 0

    custom_load_sets = _parse_custom_load_set_specs(args.custom_load_set)
    diff_specs = _parse_diff_specs(args.diff)
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    snapshot = build_fom_workbench_snapshot(custom_load_sets=custom_load_sets, diff_specs=diff_specs)
    (output_path / "fom_workbench_snapshot.json").write_text(snapshot.to_json() + "\n", encoding="utf-8")
    if args.html:
        write_fom_workbench_html(output_dir=args.output_dir, custom_load_sets=custom_load_sets, diff_specs=diff_specs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
