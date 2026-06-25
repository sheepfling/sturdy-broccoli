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

from hla.verification.repo_internal.verification.siso_pitch_micro_parity import write_siso_pitch_micro_parity_artifacts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Pitch-eligible SISO micro scenarios and write parity artifacts.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd() / "artifacts" / "siso_pitch_micro_parity",
        help="Directory for summary JSON, results CSV, selected manifest JSON, and markdown report.",
    )
    parser.add_argument(
        "--backend",
        action="append",
        dest="backends",
        default=None,
        help="Optional backend filter, e.g. --backend pitch-jpype",
    )
    args = parser.parse_args(argv)
    paths = write_siso_pitch_micro_parity_artifacts(args.output_dir, backends=args.backends)
    print(paths.summary_json)
    print(paths.results_csv)
    print(paths.selected_manifest_json)
    print(paths.report_markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
