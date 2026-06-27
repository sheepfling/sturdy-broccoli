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

from hla.verification.repo_internal.verification.siso_runtime_surface_matrix import write_siso_runtime_surface_matrix_artifacts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the SISO runtime surface matrix and write API, visualizer, and bridge artifacts.")
    parser.add_argument("--manifest", type=Path, default=None, help="Optional SISO runtime showcase manifest JSON.")
    parser.add_argument("--family", action="append", dest="families", default=None)
    parser.add_argument("--edition", action="append", dest="editions", default=None)
    parser.add_argument("--topology", action="append", dest="topologies", default=None)
    parser.add_argument("--scenario", action="append", dest="scenarios", default=None)
    parser.add_argument("--surface-profile", action="append", dest="surface_profiles", default=None)
    parser.add_argument("--preset", action="append", dest="presets", default=None, help="Named row-selection preset such as micro-bridge-smoke, showcase-hydrated, or stress-mixed.")
    parser.add_argument("--with-screenshots", action="store_true", help="Attempt visualizer and bridge screenshots when Playwright is available.")
    parser.add_argument("--fail-on-screenshot-errors", action="store_true", help="Fail instead of degrading when screenshots cannot be captured.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd() / "artifacts" / "siso_runtime_surface_matrix",
        help="Directory for summary, matrix CSV, manifest, per-row API snapshots, and optional galleries.",
    )
    args = parser.parse_args(argv)
    paths = write_siso_runtime_surface_matrix_artifacts(
        args.output_dir,
        manifest_path=args.manifest,
        families=args.families,
        editions=args.editions,
        topologies=args.topologies,
        scenarios=args.scenarios,
        surface_profiles=args.surface_profiles,
        presets=args.presets,
        include_screenshots=args.with_screenshots,
        fail_on_screenshot_errors=args.fail_on_screenshot_errors,
    )
    print(paths.summary_json)
    print(paths.results_csv)
    print(paths.manifest_json)
    print(paths.report_markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
