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

from hla.verification.repo_internal.verification.siso_runtime_showcase import write_siso_runtime_showcase_artifacts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the SISO FOM runtime showcase and write summary artifacts.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd() / "artifacts" / "siso_runtime_showcase",
        help="Directory for summary JSON, scenario CSV, backend matrix CSV, and markdown report.",
    )
    args = parser.parse_args(argv)
    paths = write_siso_runtime_showcase_artifacts(args.output_dir)
    print(paths.summary_json)
    print(paths.scenario_csv)
    print(paths.backend_matrix_csv)
    print(paths.scenario_manifest_json)
    print(paths.listener_index_json)
    print(paths.listener_index_html)
    print(paths.report_markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
