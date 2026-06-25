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

from hla.verification.repo_internal.verification.siso_runtime_showcase_launcher import (
    write_siso_runtime_showcase_launcher_artifacts,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run selected SISO runtime showcase rows from the explicit manifest.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd() / "artifacts" / "siso_runtime_showcase_launcher",
        help="Directory for summary JSON, results CSV, selected manifest JSON, and markdown report.",
    )
    parser.add_argument("--manifest", type=Path, default=None, help="Explicit manifest JSON path to read.")
    parser.add_argument("--family", action="append", dest="families", default=None)
    parser.add_argument("--edition", action="append", dest="editions", default=None)
    parser.add_argument("--topology", action="append", dest="topologies", default=None)
    parser.add_argument("--scenario", action="append", dest="scenarios", default=None)
    parser.add_argument("--backend", default=None, help="Optional backend override for all selected rows.")
    args = parser.parse_args(argv)
    paths = write_siso_runtime_showcase_launcher_artifacts(
        args.output_dir,
        manifest_path=args.manifest,
        families=args.families,
        editions=args.editions,
        topologies=args.topologies,
        scenarios=args.scenarios,
        backend=args.backend,
    )
    print(paths.summary_json)
    print(paths.results_csv)
    print(paths.selected_manifest_json)
    print(paths.report_markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
