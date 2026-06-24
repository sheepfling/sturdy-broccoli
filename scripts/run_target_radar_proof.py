#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
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

from hla.verification.repo_internal.verification.target_radar_proof import write_target_radar_proof_artifacts

DEFAULT_BACKENDS = [
    "python1516e",
    "java-shim-jpype",
    "java-shim-py4j",
]


def _parse_backend_option(value: str) -> tuple[str, str, object]:
    backend, separator, remainder = value.partition(":")
    if not separator or not backend or "=" not in remainder:
        raise argparse.ArgumentTypeError("expected backend:key=value")
    key, _, raw_value = remainder.partition("=")
    if not key:
        raise argparse.ArgumentTypeError("expected backend:key=value")
    try:
        parsed_value: object = ast.literal_eval(raw_value)
    except Exception:
        parsed_value = raw_value
    return backend, key, parsed_value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the target/radar proof packet generator.")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "analysis" / "target_radar_proof"),
        help="Directory for generated artifacts",
    )
    parser.add_argument("--backend", action="append", default=[], help="Backend kind to include in the matrix; repeat as needed")
    parser.add_argument("--proof-backend", default="python1516e", help="Backend to use for the detailed proof trace")
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--dt", type=float, default=1.0)
    parser.add_argument(
        "--backend-option",
        action="append",
        default=[],
        metavar="BACKEND:KEY=VALUE",
        help="Backend-specific override; repeat as needed",
    )
    args = parser.parse_args(argv)

    backends = args.backend or DEFAULT_BACKENDS
    backend_options_by_kind: dict[str, dict[str, object]] = {}
    for raw in args.backend_option:
        backend, key, value = _parse_backend_option(raw)
        backend_options_by_kind.setdefault(backend, {})[key] = value

    paths = write_target_radar_proof_artifacts(
        args.output_dir,
        backends,
        proof_backend=args.proof_backend,
        target_radar_steps=args.steps,
        dt=args.dt,
        backend_options_by_kind=backend_options_by_kind,
    )
    summary = json.loads(paths.summary_json.read_text())
    print(paths.summary_json)
    print(paths.backend_results_csv)
    print(paths.target_truth_csv)
    print(paths.radar_events_csv)
    print(paths.track_reports_csv)
    print(paths.report_markdown)
    print(paths.overview_png)
    print(paths.timeline_png)
    print(paths.trajectory_png)
    print(paths.rcs_exchange_png)
    print(paths.overview_svg)
    print(paths.timeline_svg)
    print(paths.trajectory_svg)
    if summary["backend_matrix"]["failed"] > 0:
        print(f"target/radar proof packet reported {summary['backend_matrix']['failed']} failed backend(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
