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

from hla.verification.repo_internal.spec2025_finish_line import write_spec2025_finish_line
from hla.verification.repo_internal.verification.spec2025_traceability_matrix import write_spec2025_traceability_matrix


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the IEEE 1516-2025 closeout-reporting artifacts.")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "docs" / "plans"),
        help="Directory for generated 2025 closeout-reporting artifacts",
    )
    args = parser.parse_args(argv)
    output_paths = write_spec2025_finish_line(Path(args.output_dir), PROJECT_ROOT)
    for path in output_paths.values():
        print(path)
    print(write_spec2025_traceability_matrix(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
