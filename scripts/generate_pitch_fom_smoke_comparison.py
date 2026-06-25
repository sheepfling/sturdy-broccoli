#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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

from hla.verification.repo_internal.verification.pitch_fom_smoke_compare import write_pitch_fom_smoke_comparison


def _load_json(path: str) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare real Pitch 2010 FOM smoke with pitch-202x adapter FOM smoke.")
    parser.add_argument(
        "--real-summary",
        default=str(PROJECT_ROOT / "artifacts" / "pitch_fom_smoke" / "pitch_fom_smoke_summary.json"),
        help="Real Pitch 2010 smoke summary JSON.",
    )
    parser.add_argument(
        "--adapter-summary",
        default=str(PROJECT_ROOT / "artifacts" / "pitch_fom_smoke_202x_adapters" / "pitch_fom_smoke_summary.json"),
        help="Pitch 202X adapter smoke summary JSON.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "artifacts" / "pitch_fom_smoke_compare"),
        help="Directory for generated comparison artifacts.",
    )
    args = parser.parse_args(argv)
    paths = write_pitch_fom_smoke_comparison(
        args.output_dir,
        _load_json(args.real_summary),
        _load_json(args.adapter_summary),
    )
    print(paths.summary_json)
    print(paths.report_markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
