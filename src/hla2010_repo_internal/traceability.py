from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from hla2010_repo_internal.requirements_source import (
    load_source_of_truth,
    match_requirement_spec_prefix,
    requirement_document_title_for_alias,
)


ROOT = Path(__file__).resolve().parents[2]
SPEC_SOURCE_ROOT = ROOT / "packages" / "hla2010-spec" / "src" / "hla2010"
TRACEABILITY_MATRIX_PATH = ROOT / "requirements" / "traceability_matrix.csv"
REQUIREMENTS_LEDGER_PATH = ROOT / "analysis" / "compliance" / "requirements_ledger.csv"
SERVICE_TRACE_INDEX_CSV_PATH = ROOT / "analysis" / "traceability" / "service_trace_index.csv"
SERVICE_TRACE_INDEX_JSON_PATH = ROOT / "analysis" / "traceability" / "service_trace_index.json"
SERVICE_TRACE_INDEX_MD_PATH = ROOT / "analysis" / "traceability" / "service_trace_index.md"
REQUIREMENTS_AUTHORING_INDEX_CSV_PATH = ROOT / "analysis" / "traceability" / "requirements_authoring_index.csv"
REQUIREMENTS_AUTHORING_INDEX_JSON_PATH = ROOT / "analysis" / "traceability" / "requirements_authoring_index.json"
REQUIREMENTS_AUTHORING_INDEX_MD_PATH = ROOT / "analysis" / "traceability" / "requirements_authoring_index.md"
ACTIVE_SERVICE_INDEX_CSV_PATH = ROOT / "analysis" / "traceability" / "active_service_requirements_index.csv"
ACTIVE_SERVICE_INDEX_JSON_PATH = ROOT / "analysis" / "traceability" / "active_service_requirements_index.json"
ACTIVE_SERVICE_INDEX_MD_PATH = ROOT / "analysis" / "traceability" / "active_service_requirements_index.md"

FORBIDDEN_STALE_PATH_PREFIXES = (
    "hla2010/backends/python/",
    "src/hla2010/backends/",
)
FAMILY_SEED_CLAUSES = frozenset({"Framework concepts", "Federation and federate rules"})


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


@dataclass(frozen=True)
class RequirementsAuthoringIndexRow:
    requirement_id: str
    lane: str
    lane_reason: str
    source_document: str
    clause: str
    canonical_topic: str
    current_artifact_id: str
    status: str
    implementation_refs: str
    test_refs: str
    artifact_refs: str

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
    normalized_anchor = anchor.split("[", 1)[0]
    base_path = ROOT / file_ref
    if not base_path.exists() and file_ref.startswith("hla2010/"):
        base_path = SPEC_SOURCE_ROOT / file_ref.removeprefix("hla2010/")
    text = base_path.read_text(encoding="utf-8")
    return f"def {normalized_anchor}(" in text or anchor in text or normalized_anchor in text


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
    source_of_truth = load_source_of_truth()
    for row in rows:
        row_id = row["requirement_id"]
        match = match_requirement_spec_prefix(row_id, source_of_truth)
        if match is None:
            errors.append(
                TraceValidationError(
                    source=source,
                    row_id=row_id,
                    field="requirement_id",
                    ref=row_id,
                    message="requirement_id does not resolve to a registered spec prefix",
                )
            )
        else:
            alias, _ = match
            expected_document = requirement_document_title_for_alias(alias, source_of_truth)
            actual_document = row.get("source_document", "")
            if actual_document != expected_document:
                errors.append(
                    TraceValidationError(
                        source=source,
                        row_id=row_id,
                        field="source_document",
                        ref=actual_document,
                        message=f"source_document must be {expected_document!r}",
                    )
                )
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


def classify_traceability_row(row: dict[str, str]) -> tuple[str, str]:
    clause = str(row.get("clause", "")).strip()
    status = str(row.get("status", "")).strip()
    if status == "seeded":
        return "family_seed", "seeded status"
    if clause.startswith("Clause "):
        return "family_seed", "broad clause family row"
    if clause in FAMILY_SEED_CLAUSES:
        return "family_seed", "framework or architectural family row"
    return "active_service", "service-level or implementation-driving row"


def build_requirements_authoring_index_rows() -> list[RequirementsAuthoringIndexRow]:
    rows: list[RequirementsAuthoringIndexRow] = []
    for row in load_csv_rows(TRACEABILITY_MATRIX_PATH):
        lane, lane_reason = classify_traceability_row(row)
        rows.append(
            RequirementsAuthoringIndexRow(
                requirement_id=row["requirement_id"],
                lane=lane,
                lane_reason=lane_reason,
                source_document=row["source_document"],
                clause=row["clause"],
                canonical_topic=row["canonical_topic"],
                current_artifact_id=row["current_artifact_id"],
                status=row["status"],
                implementation_refs=row["implementation_refs"],
                test_refs=row["test_refs"],
                artifact_refs=row["artifact_refs"],
            )
        )
    return rows


def write_requirements_authoring_index() -> tuple[Path, Path, Path]:
    REQUIREMENTS_AUTHORING_INDEX_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = build_requirements_authoring_index_rows()
    fieldnames = [
        "requirement_id",
        "lane",
        "lane_reason",
        "source_document",
        "clause",
        "canonical_topic",
        "current_artifact_id",
        "status",
        "implementation_refs",
        "test_refs",
        "artifact_refs",
    ]
    with REQUIREMENTS_AUTHORING_INDEX_CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.as_dict())

    lane_counts: dict[str, int] = {}
    for row in rows:
        lane_counts[row.lane] = lane_counts.get(row.lane, 0) + 1
    payload = {
        "source": TRACEABILITY_MATRIX_PATH.relative_to(ROOT).as_posix(),
        "row_count": len(rows),
        "lane_counts": lane_counts,
        "rows": [row.as_dict() for row in rows],
    }
    REQUIREMENTS_AUTHORING_INDEX_JSON_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    active_rows = [row for row in rows if row.lane == "active_service"]
    family_rows = [row for row in rows if row.lane == "family_seed"]
    lines = [
        "# Requirements Authoring Index",
        "",
        f"Generated from `{TRACEABILITY_MATRIX_PATH.relative_to(ROOT).as_posix()}`.",
        "",
        "## Lane Summary",
        "",
        f"- `active_service`: {len(active_rows)} rows",
        f"- `family_seed`: {len(family_rows)} rows",
        "",
        "Normal contributors should start with `active_service` rows.",
        "",
        "## Family Seed Rows",
        "",
        "| requirement_id | clause | status | lane_reason | canonical_topic |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in family_rows:
        lines.append(
            f"| `{row.requirement_id}` | `{row.clause}` | `{row.status}` | `{row.lane_reason}` | {row.canonical_topic} |"
        )
    lines.extend(
        [
            "",
            "## Active Service Examples",
            "",
            "| requirement_id | clause | current_artifact_id | status | canonical_topic |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in active_rows[:25]:
        lines.append(
            f"| `{row.requirement_id}` | `{row.clause}` | `{row.current_artifact_id or '-'}` | `{row.status}` | {row.canonical_topic} |"
        )
    REQUIREMENTS_AUTHORING_INDEX_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return (
        REQUIREMENTS_AUTHORING_INDEX_CSV_PATH,
        REQUIREMENTS_AUTHORING_INDEX_JSON_PATH,
        REQUIREMENTS_AUTHORING_INDEX_MD_PATH,
    )


def write_active_service_index() -> tuple[Path, Path, Path]:
    ACTIVE_SERVICE_INDEX_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = [row for row in build_requirements_authoring_index_rows() if row.lane == "active_service"]
    fieldnames = [
        "requirement_id",
        "source_document",
        "clause",
        "canonical_topic",
        "current_artifact_id",
        "status",
        "implementation_refs",
        "test_refs",
        "artifact_refs",
    ]
    with ACTIVE_SERVICE_INDEX_CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "requirement_id": row.requirement_id,
                    "source_document": row.source_document,
                    "clause": row.clause,
                    "canonical_topic": row.canonical_topic,
                    "current_artifact_id": row.current_artifact_id,
                    "status": row.status,
                    "implementation_refs": row.implementation_refs,
                    "test_refs": row.test_refs,
                    "artifact_refs": row.artifact_refs,
                }
            )

    payload = {
        "source": TRACEABILITY_MATRIX_PATH.relative_to(ROOT).as_posix(),
        "row_count": len(rows),
        "lane": "active_service",
        "rows": [
            {
                "requirement_id": row.requirement_id,
                "source_document": row.source_document,
                "clause": row.clause,
                "canonical_topic": row.canonical_topic,
                "current_artifact_id": row.current_artifact_id,
                "status": row.status,
                "implementation_refs": row.implementation_refs,
                "test_refs": row.test_refs,
                "artifact_refs": row.artifact_refs,
            }
            for row in rows
        ],
    }
    ACTIVE_SERVICE_INDEX_JSON_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Active Service Requirements Index",
        "",
        f"Generated from `{TRACEABILITY_MATRIX_PATH.relative_to(ROOT).as_posix()}`.",
        "",
        "This is the normal contributor authoring lane. Family and seed rows are intentionally excluded.",
        "",
        f"- row_count: {len(rows)}",
        "",
        "| requirement_id | clause | canonical_topic | current_artifact_id | status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row.requirement_id}` | `{row.clause}` | {row.canonical_topic} | `{row.current_artifact_id or '-'}` | `{row.status}` |"
        )
    ACTIVE_SERVICE_INDEX_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return (
        ACTIVE_SERVICE_INDEX_CSV_PATH,
        ACTIVE_SERVICE_INDEX_JSON_PATH,
        ACTIVE_SERVICE_INDEX_MD_PATH,
    )


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
    "ACTIVE_SERVICE_INDEX_CSV_PATH",
    "ACTIVE_SERVICE_INDEX_JSON_PATH",
    "ACTIVE_SERVICE_INDEX_MD_PATH",
    "FAMILY_SEED_CLAUSES",
    "FORBIDDEN_STALE_PATH_PREFIXES",
    "REQUIREMENTS_AUTHORING_INDEX_CSV_PATH",
    "REQUIREMENTS_AUTHORING_INDEX_JSON_PATH",
    "REQUIREMENTS_AUTHORING_INDEX_MD_PATH",
    "REQUIREMENTS_LEDGER_PATH",
    "RequirementsAuthoringIndexRow",
    "SERVICE_TRACE_INDEX_CSV_PATH",
    "SERVICE_TRACE_INDEX_JSON_PATH",
    "SERVICE_TRACE_INDEX_MD_PATH",
    "TRACEABILITY_MATRIX_PATH",
    "TraceValidationError",
    "build_requirements_authoring_index_rows",
    "build_service_trace_index_rows",
    "classify_traceability_row",
    "load_csv_rows",
    "split_refs",
    "validate_active_traceability",
    "validate_requirements_ledger",
    "validate_traceability_matrix",
    "write_active_service_index",
    "write_requirements_authoring_index",
    "write_service_trace_index",
]
