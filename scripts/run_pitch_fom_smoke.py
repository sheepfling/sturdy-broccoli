#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path.cwd()


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla.verification.repo_internal.verification.pitch_fom_smoke import (
    build_default_pitch_fom_smoke_specs,
    probe_pitch_fom_support,
    write_pitch_fom_smoke,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Probe how the two Pitch runtimes handle the example 2010 FOM families.")
    parser.add_argument(
        "--kind",
        action="append",
        dest="kinds",
        choices=("pitch-jpype", "pitch-py4j", "pitch-202x-jpype", "pitch-202x-py4j"),
        help="Pitch route kind(s) to probe. Defaults to the two real 2010 vendor runtimes.",
    )
    parser.add_argument(
        "--packet",
        action="append",
        dest="packets",
        help="Packet ids to probe. Defaults to the built-in example set.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "artifacts" / "pitch_fom_smoke"),
        help="Directory for generated artifacts.",
    )
    args = parser.parse_args(argv)

    specs = build_default_pitch_fom_smoke_specs()
    if args.packets:
        wanted = set(args.packets)
        specs = tuple(spec for spec in specs if spec.id in wanted)
    summary = probe_pitch_fom_support(
        runtime_kinds=tuple(args.kinds or ("pitch-jpype", "pitch-py4j")),
        specs=specs,
    )
    paths = write_pitch_fom_smoke(args.output_dir, summary)
    print(paths.summary_json)
    print(paths.report_markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
