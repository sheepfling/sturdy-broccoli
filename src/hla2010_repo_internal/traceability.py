from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
SPEC_SOURCE_ROOT = ROOT / "packages" / "hla2010-spec" / "src" / "hla2010"
TRACEABILITY_MATRIX_PATH = ROOT / "requirements" / "traceability_matrix.csv"
REQUIREMENTS_LEDGER_PATH = ROOT / "analysis" / "compliance" / "requirements_ledger.csv"
SERVICE_TRACE_INDEX_CSV_PATH = ROOT / "analysis" / "traceability" / "service_trace_index.csv"
SERVICE_TRACE_INDEX_JSON_PATH = ROOT / "analysis" / "traceability" / "service_trace_index.json"
SERVICE_TRACE_INDEX_MD_PATH = ROOT / "analysis" / "traceability" / "service_trace_index.md"

FORBIDDEN_STALE_PATH_PREFIXES = (
    "hla2010/backends/python/",
    "src/hla2010/backends/",
)


@dataclass(frozen=True)
class TraceValidationError:
    source: str
    row_id: str
    field: str
    ref: str
    message: str


@dataclass(frozen=True)
class ServiceTraceIndexRow:
    requirement_id: str
    section: str
    service_group: str
    hla_method: str
    python_name: str
    implementation_ref: str
    backend_package: str
    test_refs: str
    artifact_refs: str
    status: str
    notes: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def split_refs(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def path_exists(ref: str) -> bool:
    path = ROOT / ref
    if path.exists():
        return True
    if ref.startswith("hla2010/"):
        return (SPEC_SOURCE_ROOT / ref.removeprefix("hla2010/")).exists()
    return False


def _file_anchor_exists(ref: str) -> bool:
    file_ref, _, anchor = ref.partition("::")
    if not file_ref or not path_exists(file_ref):
        return False
    if not anchor:
        return True
    base_path = ROOT / file_ref
    if not base_path.exists() and file_ref.startswith("hla2010/"):
        base_path = SPEC_SOURCE_ROOT / file_ref.removeprefix("hla2010/")
    text = base_path.read_text(encoding="utf-8")
    return f"def {anchor}(" in text or anchor in text


def _explicit_marker(ref: str) -> bool:
    return ref.startswith("generated:") or ref.startswith("external:")


def _descriptive_token_with_companion_file(ref: str, refs_in_field: Iterable[str]) -> bool:
    if "/" in ref or "." in ref:
        return False
    if not any(char.isspace() for char in ref):
        return False
    return any(path_exists(item) for item in refs_in_field if item != ref)


def _dotted_symbol_has_companion_file(ref: str, refs_in_field: Iterable[str]) -> bool:
    if "/" in ref or "." not in ref:
        return False
    return any((item.endswith(".py") or item.startswith("hla2010/")) and path_exists(item) for item in refs_in_field)


def validate_ref_field(
    *,
    source: str,
    row_id: str,
    field: str,
    refs: Iterable[str],
    mode: str,
) -> list[TraceValidationError]:
    errors: list[TraceValidationError] = []
    refs_list = list(refs)
    for ref in refs_list:
        if any(ref.startswith(prefix) for prefix in FORBIDDEN_STALE_PATH_PREFIXES):
            errors.append(
                TraceValidationError(
                    source=source,
                    row_id=row_id,
                    field=field,
                    ref=ref,
                    message="stale backend root path is forbidden in active traceability files",
                )
            )
            continue
        if _explicit_marker(ref):
            continue
        if mode == "test":
            if _file_anchor_exists(ref):
                continue
            errors.append(
                TraceValidationError(
                    source=source,
                    row_id=row_id,
                    field=field,
                    ref=ref,
                    message="test ref does not resolve to an existing file or file::anchor",
                )
            )
            continue
        if mode == "artifact":
            if path_exists(ref):
                continue
            errors.append(
                TraceValidationError(
                    source=source,
                    row_id=row_id,
                    field=field,
                    ref=ref,
                    message="artifact ref does not resolve to an existing path",
                )
            )
            continue
        if mode == "implementation":
            if path_exists(ref) or _file_anchor_exists(ref):
                continue
            if _dotted_symbol_has_companion_file(ref, refs_list):
                continue
            if _descriptive_token_with_companion_file(ref, refs_list):
                continue
            errors.append(
                TraceValidationError(
                    source=source,
                    row_id=row_id,
                    field=field,
                    ref=ref,
                    message="implementation ref does not resolve to an existing file or file-backed symbol",
                )
            )
            continue
        raise ValueError(f"unknown validation mode: {mode}")
    return errors


def validate_traceability_matrix() -> list[TraceValidationError]:
    rows = load_csv_rows(TRACEABILITY_MATRIX_PATH)
    errors: list[TraceValidationError] = []
    source = TRACEABILITY_MATRIX_PATH.relative_to(ROOT).as_posix()
    for row in rows:
        row_id = row["requirement_id"]
        implementation_refs = split_refs(row.get("implementation_refs", ""))
        test_refs = split_refs(row.get("test_refs", ""))
        artifact_refs = split_refs(row.get("artifact_refs", ""))
        errors.extend(
            validate_ref_field(
                source=source,
                row_id=row_id,
                field="implementation_refs",
                refs=implementation_refs,
                mode="implementation",
            )
        )
        if test_refs:
            errors.extend(
                validate_ref_field(
                    source=source,
                    row_id=row_id,
                    field="test_refs",
                    refs=test_refs,
                    mode="test",
                )
            )
        errors.extend(
            validate_ref_field(
                source=source,
                row_id=row_id,
                field="artifact_refs",
                refs=artifact_refs,
                mode="artifact",
            )
        )
        status = row.get("status", "")
        if status == "mapped" and not (test_refs or artifact_refs):
            errors.append(
                TraceValidationError(
                    source=source,
                    row_id=row_id,
                    field="status",
                    ref=status,
                    message="mapped row must have at least one test or artifact ref",
                )
            )
        if status == "partial" and "supported" not in row.get("notes", "").casefold():
            errors.append(
                TraceValidationError(
                    source=source,
                    row_id=row_id,
                    field="notes",
                    ref=row.get("notes", ""),
                    message="partial row must include a supported-boundary note",
                )
            )
    return errors


def validate_requirements_ledger() -> list[TraceValidationError]:
    rows = load_csv_rows(REQUIREMENTS_LEDGER_PATH)
    errors: list[TraceValidationError] = []
    source = REQUIREMENTS_LEDGER_PATH.relative_to(ROOT).as_posix()
    for row in rows:
        row_id = row["requirement_id"]
        implementation_refs = split_refs(row.get("implementation_refs", ""))
        positive_refs = split_refs(row.get("positive_test_refs", ""))
        negative_refs = split_refs(row.get("negative_test_refs", ""))
        artifact_refs = split_refs(row.get("artifact_refs", ""))
        errors.extend(
            validate_ref_field(
                source=source,
                row_id=row_id,
                field="implementation_refs",
                refs=implementation_refs,
                mode="implementation",
            )
        )
        errors.extend(
            validate_ref_field(
                source=source,
                row_id=row_id,
                field="positive_test_refs",
                refs=positive_refs,
                mode="test",
            )
        )
        if negative_refs:
            errors.extend(
                validate_ref_field(
                    source=source,
                    row_id=row_id,
                    field="negative_test_refs",
                    refs=negative_refs,
                    mode="test",
                )
            )
        errors.extend(
            validate_ref_field(
                source=source,
                row_id=row_id,
                field="artifact_refs",
                refs=artifact_refs,
                mode="artifact",
            )
        )
    return errors


def validate_active_traceability() -> list[TraceValidationError]:
    return [*validate_traceability_matrix(), *validate_requirements_ledger()]


def build_service_trace_index_rows() -> list[ServiceTraceIndexRow]:
    rows: list[ServiceTraceIndexRow] = []
    for row in load_csv_rows(REQUIREMENTS_LEDGER_PATH):
        test_refs = split_refs(row.get("positive_test_refs", "")) + split_refs(row.get("negative_test_refs", ""))
        test_refs = list(dict.fromkeys(test_refs))
        implementation_refs = split_refs(row.get("implementation_refs", ""))
        rows.append(
            ServiceTraceIndexRow(
                requirement_id=row["requirement_id"],
                section=row["section"],
                service_group=row["service_group"],
                hla_method=row["method"],
                python_name=row["python_name"],
                implementation_ref="; ".join(implementation_refs),
                backend_package="hla2010-rti-python",
                test_refs="; ".join(test_refs),
                artifact_refs=row["artifact_refs"],
                status=row["outcome"],
                notes=row["rationale"],
            )
        )
    return rows


def write_service_trace_index() -> tuple[Path, Path, Path]:
    SERVICE_TRACE_INDEX_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = build_service_trace_index_rows()
    fieldnames = [
        "requirement_id",
        "section",
        "service_group",
        "hla_method",
        "python_name",
        "implementation_ref",
        "backend_package",
        "test_refs",
        "artifact_refs",
        "status",
        "notes",
    ]
    with SERVICE_TRACE_INDEX_CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.as_dict())

    payload = {
        "source": REQUIREMENTS_LEDGER_PATH.relative_to(ROOT).as_posix(),
        "row_count": len(rows),
        "rows": [row.as_dict() for row in rows],
    }
    SERVICE_TRACE_INDEX_JSON_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Service Trace Index",
        "",
        f"Generated from `{REQUIREMENTS_LEDGER_PATH.relative_to(ROOT).as_posix()}`.",
        "",
        "| requirement_id | section | service_group | hla_method | python_name | implementation_ref | backend_package | test_refs | artifact_refs | status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row.requirement_id}` | `{row.section}` | {row.service_group} | `{row.hla_method}` | "
            f"`{row.python_name}` | `{row.implementation_ref}` | `{row.backend_package}` | "
            f"`{row.test_refs}` | `{row.artifact_refs}` | `{row.status}` |"
        )
    SERVICE_TRACE_INDEX_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return SERVICE_TRACE_INDEX_CSV_PATH, SERVICE_TRACE_INDEX_JSON_PATH, SERVICE_TRACE_INDEX_MD_PATH


__all__ = [
    "FORBIDDEN_STALE_PATH_PREFIXES",
    "REQUIREMENTS_LEDGER_PATH",
    "SERVICE_TRACE_INDEX_CSV_PATH",
    "SERVICE_TRACE_INDEX_JSON_PATH",
    "SERVICE_TRACE_INDEX_MD_PATH",
    "TRACEABILITY_MATRIX_PATH",
    "TraceValidationError",
    "build_service_trace_index_rows",
    "load_csv_rows",
    "split_refs",
    "validate_active_traceability",
    "validate_requirements_ledger",
    "validate_traceability_matrix",
    "write_service_trace_index",
]
