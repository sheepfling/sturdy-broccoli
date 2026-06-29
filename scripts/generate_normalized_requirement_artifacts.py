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

from hla.verification.repo_internal.requirements import (  # noqa: E402
    write_2010_backend_resolution_catalog,
    write_2010_backend_resolution_catalog_csv,
    write_2010_canonical_requirement_catalog,
    write_2010_canonical_requirement_catalog_csv,
    write_2010_canonical_row_triage,
    write_2010_projection_requirement_catalog,
    write_2025_backend_resolution_catalog,
    write_2025_backend_resolution_catalog_csv,
    write_2025_canonical_requirement_catalog,
    write_2025_canonical_requirement_catalog_csv,
    write_requirement_artifact_survey,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write normalized requirement-model artifacts.")
    parser.add_argument(
        "--survey-output",
        default=str(PROJECT_ROOT / "requirements" / "normalized" / "row_shape_survey.json"),
        help="Output path for the row-shape survey artifact",
    )
    parser.add_argument(
        "--canonical-2010-output",
        default=str(PROJECT_ROOT / "requirements" / "2010" / "canonical_requirements.json"),
        help="Output path for the normalized 2010 canonical requirement catalog",
    )
    parser.add_argument(
        "--backend-2010-output",
        default=str(PROJECT_ROOT / "requirements" / "2010" / "backend_resolution.json"),
        help="Output path for the normalized 2010 backend-resolution catalog",
    )
    parser.add_argument(
        "--canonical-2010-csv-output",
        default=str(PROJECT_ROOT / "requirements" / "2010" / "canonical_requirements.csv"),
        help="Output path for the normalized 2010 canonical requirement CSV projection",
    )
    parser.add_argument(
        "--backend-2010-csv-output",
        default=str(PROJECT_ROOT / "requirements" / "2010" / "backend_resolution.csv"),
        help="Output path for the normalized 2010 backend-resolution CSV projection",
    )
    parser.add_argument(
        "--triage-2010-output",
        default=str(PROJECT_ROOT / "requirements" / "2010" / "canonical_row_triage.json"),
        help="Output path for the 2010 canonical row normalization triage artifact",
    )
    parser.add_argument(
        "--projection-2010-output",
        default=str(PROJECT_ROOT / "requirements" / "2010" / "canonical_projection_rows.json"),
        help="Output path for the 2010 demoted rollup projection artifact",
    )
    parser.add_argument(
        "--canonical-2025-output",
        default=str(PROJECT_ROOT / "requirements" / "2025" / "canonical_requirements.json"),
        help="Output path for the normalized 2025 canonical requirement catalog",
    )
    parser.add_argument(
        "--backend-2025-output",
        default=str(PROJECT_ROOT / "requirements" / "2025" / "backend_resolution.json"),
        help="Output path for the normalized 2025 backend-resolution catalog",
    )
    parser.add_argument(
        "--canonical-2025-csv-output",
        default=str(PROJECT_ROOT / "requirements" / "2025" / "canonical_requirements.csv"),
        help="Output path for the normalized 2025 canonical requirement CSV projection",
    )
    parser.add_argument(
        "--backend-2025-csv-output",
        default=str(PROJECT_ROOT / "requirements" / "2025" / "backend_resolution.csv"),
        help="Output path for the normalized 2025 backend-resolution CSV projection",
    )
    args = parser.parse_args(argv)

    canonical_2010_path = write_2010_canonical_requirement_catalog(PROJECT_ROOT, Path(args.canonical_2010_output))
    backend_2010_path = write_2010_backend_resolution_catalog(PROJECT_ROOT, Path(args.backend_2010_output))
    canonical_2010_csv_path = write_2010_canonical_requirement_catalog_csv(PROJECT_ROOT, Path(args.canonical_2010_csv_output))
    backend_2010_csv_path = write_2010_backend_resolution_catalog_csv(PROJECT_ROOT, Path(args.backend_2010_csv_output))
    triage_2010_path = write_2010_canonical_row_triage(PROJECT_ROOT, Path(args.triage_2010_output))
    projection_2010_path = write_2010_projection_requirement_catalog(PROJECT_ROOT, Path(args.projection_2010_output))
    canonical_2025_path = write_2025_canonical_requirement_catalog(PROJECT_ROOT, Path(args.canonical_2025_output))
    backend_2025_path = write_2025_backend_resolution_catalog(PROJECT_ROOT, Path(args.backend_2025_output))
    canonical_2025_csv_path = write_2025_canonical_requirement_catalog_csv(PROJECT_ROOT, Path(args.canonical_2025_csv_output))
    backend_2025_csv_path = write_2025_backend_resolution_catalog_csv(PROJECT_ROOT, Path(args.backend_2025_csv_output))
    survey_path = write_requirement_artifact_survey(PROJECT_ROOT, Path(args.survey_output))
    print(survey_path)
    print(canonical_2010_path)
    print(backend_2010_path)
    print(canonical_2010_csv_path)
    print(backend_2010_csv_path)
    print(triage_2010_path)
    print(projection_2010_path)
    print(canonical_2025_path)
    print(backend_2025_path)
    print(canonical_2025_csv_path)
    print(backend_2025_csv_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
