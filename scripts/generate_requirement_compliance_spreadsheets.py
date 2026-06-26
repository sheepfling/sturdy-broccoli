from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable

from openpyxl import Workbook


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "analysis" / "compliance" / "presentation_packets"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _autosize_worksheet(ws) -> None:
    for column_cells in ws.columns:
        width = max(len(str(cell.value or "")) for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 80)


def _write_sheet(ws, rows: list[dict[str, str]]) -> None:
    if not rows:
        ws.append(["no rows"])
        return
    headers = list(rows[0].keys())
    ws.append(headers)
    for row in rows:
        ws.append([row.get(header, "") for header in headers])
    _autosize_worksheet(ws)


def _export_workbook(path: Path, summary_rows: list[dict[str, str]], detail_rows: list[dict[str, str]], metadata_rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws_summary = wb.active
    ws_summary.title = "summary"
    _write_sheet(ws_summary, summary_rows)

    ws_detail = wb.create_sheet("detail")
    _write_sheet(ws_detail, detail_rows)

    ws_meta = wb.create_sheet("metadata")
    _write_sheet(ws_meta, metadata_rows)
    wb.save(path)


def build_2010_rows() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    matrix_path = ROOT / "analysis" / "compliance" / "requirements_matrix_2010.csv"
    rows = _read_csv(matrix_path)
    detail_rows: list[dict[str, str]] = []
    for row in rows:
        detail_rows.append(
            {
                "requirement_id": row.get("requirement_id", ""),
                "matrix_id": row.get("matrix_id", ""),
                "service_group": row.get("service_group", ""),
                "title": row.get("title", ""),
                "section_ref": row.get("section_ref", ""),
                "canonical_status": row.get("status", ""),
                "python_runtime_disposition": row.get("python_runtime_disposition", ""),
                "certi_runtime_disposition": row.get("certi_runtime_disposition", ""),
                "pitch_runtime_disposition": row.get("pitch_runtime_disposition", ""),
                "portico_runtime_disposition": row.get("portico_runtime_disposition", ""),
                "claim_scope": row.get("claim_scope", ""),
                "artifact_refs": row.get("artifact_refs", ""),
                "notes": row.get("notes", ""),
            }
        )

    status_counts = Counter(row["canonical_status"] for row in detail_rows)
    python_counts = Counter(row["python_runtime_disposition"] for row in detail_rows)
    certi_counts = Counter(row["certi_runtime_disposition"] for row in detail_rows)
    pitch_counts = Counter(row["pitch_runtime_disposition"] for row in detail_rows)
    portico_counts = Counter(row["portico_runtime_disposition"] for row in detail_rows)

    summary_rows = [
        {"metric": "edition", "value": "2010 / 1516e"},
        {"metric": "row_count", "value": str(len(detail_rows))},
        {"metric": "canonical_status_counts", "value": json.dumps(status_counts, sort_keys=True)},
        {"metric": "python_runtime_disposition_counts", "value": json.dumps(python_counts, sort_keys=True)},
        {"metric": "certi_runtime_disposition_counts", "value": json.dumps(certi_counts, sort_keys=True)},
        {"metric": "pitch_runtime_disposition_counts", "value": json.dumps(pitch_counts, sort_keys=True)},
        {"metric": "portico_runtime_disposition_counts", "value": json.dumps(portico_counts, sort_keys=True)},
        {"metric": "source_artifact", "value": "analysis/compliance/requirements_matrix_2010.csv"},
    ]
    metadata_rows = [
        {"field": "edition", "value": "2010 / 1516e"},
        {"field": "primary_source", "value": "analysis/compliance/requirements_matrix_2010.csv"},
        {"field": "front_door", "value": "docs/requirements/ieee-1516-2010/README.md"},
        {"field": "inventory", "value": "requirements/2010/README.md"},
        {"field": "notes", "value": "Boss-facing export generated from canonical CSV/JSON artifacts; spreadsheets are secondary presentation surfaces."},
    ]
    return summary_rows, detail_rows, metadata_rows


def build_2025_rows() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    worklist_path = ROOT / "requirements" / "2025" / "harmonization" / "hla_2025_harmonization_worklist.csv"
    rows = _read_csv(worklist_path)
    detail_rows: list[dict[str, str]] = []
    for row in rows:
        detail_rows.append(
            {
                "closure_wave": row.get("closure_wave", ""),
                "priority": row.get("priority", ""),
                "area": row.get("area", ""),
                "service_group": row.get("service_group", ""),
                "canonical_disposition": row.get("canonical_disposition", ""),
                "python_runtime_resolution": row.get("python_runtime_resolution", ""),
                "java_cpp_binding_resolution": row.get("java_cpp_binding_resolution", ""),
                "hosted_fedpro_resolution": row.get("hosted_fedpro_resolution", ""),
                "pitch_202x_resolution": row.get("pitch_202x_resolution", ""),
                "row_count": row.get("row_count", ""),
                "backend_resolution_reference": row.get("backend_resolution_reference", ""),
                "acceptance_gate": row.get("acceptance_gate", ""),
            }
        )

    disposition_counts = Counter(row["canonical_disposition"] for row in detail_rows)
    area_counts = Counter(row["area"] for row in detail_rows)

    summary_rows = [
        {"metric": "edition", "value": "2025 / 1516_2025"},
        {"metric": "group_count", "value": str(len(detail_rows))},
        {"metric": "canonical_disposition_counts", "value": json.dumps(disposition_counts, sort_keys=True)},
        {"metric": "area_counts", "value": json.dumps(area_counts, sort_keys=True)},
        {"metric": "source_artifact", "value": "requirements/2025/harmonization/hla_2025_harmonization_worklist.csv"},
    ]
    metadata_rows = [
        {"field": "edition", "value": "2025 / 1516_2025"},
        {"field": "primary_source", "value": "requirements/2025/harmonization/hla_2025_harmonization_worklist.csv"},
        {"field": "front_door", "value": "docs/requirements/ieee-1516-2025/README.md"},
        {"field": "inventory", "value": "requirements/2025/README.md"},
        {"field": "notes", "value": "Boss-facing export generated from grouped 2025 harmonization and backend-resolution surfaces; spreadsheets are secondary presentation surfaces."},
    ]
    return summary_rows, detail_rows, metadata_rows


def generate_exports(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    for stem, builder in (
        ("requirements_2010_backend_compliance", build_2010_rows),
        ("requirements_2025_backend_compliance", build_2025_rows),
    ):
        summary_rows, detail_rows, metadata_rows = builder()
        summary_csv = output_dir / f"{stem}_summary.csv"
        detail_csv = output_dir / f"{stem}_detail.csv"
        workbook = output_dir / f"{stem}.xlsx"

        _write_csv(summary_csv, list(summary_rows[0].keys()), summary_rows)
        _write_csv(detail_csv, list(detail_rows[0].keys()), detail_rows)
        _export_workbook(workbook, summary_rows, detail_rows, metadata_rows)
        created.extend([summary_csv, detail_csv, workbook])

    return created


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate boss-facing requirement compliance spreadsheets for 2010 and 2025.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where CSV and XLSX exports should be written.",
    )
    args = parser.parse_args()
    created = generate_exports(args.output_dir)
    for path in created:
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
