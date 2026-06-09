from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict
from typing import Iterable


KNOWN_PACKET_PARENT_GAPS = frozenset(
    {
        "HLA1516.1-FM-4_11-001",
        "HLA1516.1-MOM-11.6-001",
    }
)


@dataclass(frozen=True, slots=True)
class CanonicalAssetSummary:
    clause_tracker_rows: int
    cpp_api_catalog_rows: int
    master_requirements_rows: int
    verification_rows: int


@dataclass(frozen=True, slots=True)
class PacketManifestEntry:
    path: str
    bytes: int
    sha256: str
    source_path: str


@dataclass(frozen=True, slots=True)
class PacketManifest:
    packet_name: str
    packet_version: str
    created_utc: str
    notes: tuple[str, ...]
    canonical_asset_summary: CanonicalAssetSummary
    included_files: tuple[PacketManifestEntry, ...]
    missing_requested_files: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MasterRequirementRow:
    requirement_id: str
    standard: str
    clause: str
    source_title: str
    capability: str
    feature: str
    requirement_text: str
    normative_keyword: str
    implementation_area: str
    verification_method: str
    test_id: str
    status: str
    priority: str
    source_note: str
    requirement_type: str
    parent_requirement_id: str
    source_detail: str
    service_name: str
    service_direction: str
    transport_scope: str
    mom_observable: str
    verification_notes: str


@dataclass(frozen=True, slots=True)
class VerificationMatrixRow:
    test_id: str
    requirement_id: str
    capability: str
    feature: str
    test_level: str
    transport: str
    status: str
    expected_evidence: str
    verification_notes: str


@dataclass(frozen=True, slots=True)
class ClauseTrackerRow:
    standard: str
    clause: str
    title: str
    document_area: str
    normative_status: str
    priority: str
    detail_status_v1_0: str
    rows_in_catalog_v1_0: str
    decomposition_level: str
    next_action: str
    notes: str


@dataclass(frozen=True, slots=True)
class RequirementsSummaryRow:
    metric: str
    value: str
    notes: str


@dataclass(frozen=True, slots=True)
class CppApiCatalogRow:
    header: str
    class_or_scope: str
    clause: str
    method_name: str
    signature: str
    exceptions: str


@dataclass(frozen=True, slots=True)
class ApiServiceCatalogRow:
    interface: str
    direction: str
    clause: str
    service_title: str
    method_name: str
    overload_index: str
    return_type: str
    arguments: str
    exceptions: str
    signature: str


@dataclass(frozen=True, slots=True)
class MimCatalogRow:
    category: str
    path_or_owner: str
    name: str
    parent_path: str
    data_type: str
    update_type: str
    ownership: str
    sharing: str
    transportation: str
    order: str
    dimensions: str
    semantics: str


@dataclass(frozen=True, slots=True)
class XsdCatalogRow:
    category: str
    schema: str
    name: str
    type_or_kind: str
    minOccurs: str
    maxOccurs: str
    ref_or_mixed: str


@dataclass(frozen=True, slots=True)
class WsdlCatalogRow:
    operation: str
    input: str
    output: str


@dataclass(frozen=True, slots=True)
class ImportedHLAPacket:
    root: Path
    manifest: PacketManifest
    master_rows: tuple[MasterRequirementRow, ...]
    verification_rows: tuple[VerificationMatrixRow, ...]
    clause_tracker_rows: tuple[ClauseTrackerRow, ...]
    summary_rows: tuple[RequirementsSummaryRow, ...]
    delta_rows: tuple[MasterRequirementRow, ...]
    clauses5_11_detailed_rows: tuple[MasterRequirementRow, ...]
    clause6_11_detailed_rows: tuple[MasterRequirementRow, ...]
    omt_xml_detailed_rows: tuple[MasterRequirementRow, ...]
    cpp_api_rows: tuple[CppApiCatalogRow, ...]
    api_service_catalog_rows: tuple[ApiServiceCatalogRow, ...]
    mim_catalog_rows: tuple[MimCatalogRow, ...]
    xsd_catalog_rows: tuple[XsdCatalogRow, ...]
    wsdl_catalog_rows: tuple[WsdlCatalogRow, ...]

    def resolve_manifest_path(self, path: str) -> Path:
        if path.startswith("requirements/"):
            return self.root / path.removeprefix("requirements/")
        if path.startswith("WORK_PACKET/"):
            return self.root / "work_packet" / path.removeprefix("WORK_PACKET/")
        if path in {"MANIFEST.json", "README.md"}:
            return self.root / path
        raise ValueError(f"unexpected manifest path: {path}")

    @property
    def requirements_by_id(self) -> dict[str, MasterRequirementRow]:
        return {row.requirement_id: row for row in self.master_rows}

    @property
    def requirements_by_standard(self) -> dict[str, tuple[MasterRequirementRow, ...]]:
        grouped: dict[str, list[MasterRequirementRow]] = {}
        for row in self.master_rows:
            grouped.setdefault(row.standard, []).append(row)
        return {key: tuple(value) for key, value in grouped.items()}

    @property
    def requirements_by_clause(self) -> dict[str, tuple[MasterRequirementRow, ...]]:
        grouped: dict[str, list[MasterRequirementRow]] = {}
        for row in self.master_rows:
            grouped.setdefault(row.clause, []).append(row)
        return {key: tuple(value) for key, value in grouped.items()}

    @property
    def requirements_by_capability(self) -> dict[str, tuple[MasterRequirementRow, ...]]:
        grouped: dict[str, list[MasterRequirementRow]] = {}
        for row in self.master_rows:
            grouped.setdefault(row.capability, []).append(row)
        return {key: tuple(value) for key, value in grouped.items()}

    @property
    def requirements_by_feature(self) -> dict[str, tuple[MasterRequirementRow, ...]]:
        grouped: dict[str, list[MasterRequirementRow]] = {}
        for row in self.master_rows:
            grouped.setdefault(row.feature, []).append(row)
        return {key: tuple(value) for key, value in grouped.items()}

    @property
    def verification_by_requirement_id(self) -> dict[str, tuple[VerificationMatrixRow, ...]]:
        grouped: dict[str, list[VerificationMatrixRow]] = {}
        for row in self.verification_rows:
            grouped.setdefault(row.requirement_id, []).append(row)
        return {key: tuple(value) for key, value in grouped.items()}

    @property
    def verification_by_test_id(self) -> dict[str, tuple[VerificationMatrixRow, ...]]:
        grouped: dict[str, list[VerificationMatrixRow]] = {}
        for row in self.verification_rows:
            grouped.setdefault(row.test_id, []).append(row)
        return {key: tuple(value) for key, value in grouped.items()}

    @property
    def clause_tracker_pairs(self) -> set[tuple[str, str]]:
        return {(row.standard, row.clause) for row in self.clause_tracker_rows}

    @property
    def summary_by_metric(self) -> dict[str, RequirementsSummaryRow]:
        return {row.metric: row for row in self.summary_rows}

    @property
    def cpp_api_by_clause(self) -> dict[str, tuple[CppApiCatalogRow, ...]]:
        grouped: dict[str, list[CppApiCatalogRow]] = {}
        for row in self.cpp_api_rows:
            grouped.setdefault(row.clause, []).append(row)
        return {key: tuple(value) for key, value in grouped.items()}

    @property
    def api_service_catalog_by_clause(self) -> dict[str, tuple[ApiServiceCatalogRow, ...]]:
        grouped: dict[str, list[ApiServiceCatalogRow]] = {}
        for row in self.api_service_catalog_rows:
            grouped.setdefault(row.clause, []).append(row)
        return {key: tuple(value) for key, value in grouped.items()}


def imported_hla_packet_root(project_root: Path | None = None) -> Path:
    base = project_root or Path(__file__).resolve().parents[1]
    return base / "requirements" / "imports" / "hla_1516_requirements_codebase_packet_v1_0"


def _read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(handle)]


def _load_manifest(root: Path) -> PacketManifest:
    payload = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
    summary = payload["canonical_asset_summary"]
    return PacketManifest(
        packet_name=str(payload["packet_name"]),
        packet_version=str(payload["packet_version"]),
        created_utc=str(payload["created_utc"]),
        notes=tuple(str(item) for item in payload.get("notes", [])),
        canonical_asset_summary=CanonicalAssetSummary(
            clause_tracker_rows=int(summary["clause_tracker_rows"]),
            cpp_api_catalog_rows=int(summary["cpp_api_catalog_rows"]),
            master_requirements_rows=int(summary["master_requirements_rows"]),
            verification_rows=int(summary["verification_rows"]),
        ),
        included_files=tuple(
            PacketManifestEntry(
                path=str(item["path"]),
                bytes=int(item["bytes"]),
                sha256=str(item["sha256"]),
                source_path=str(item["source_path"]),
            )
            for item in payload["included_files"]
        ),
        missing_requested_files=tuple(str(item) for item in payload.get("missing_requested_files", [])),
    )


def load_imported_hla_packet(project_root: Path | None = None) -> ImportedHLAPacket:
    root = imported_hla_packet_root(project_root)
    latest = root / "latest"
    catalogs = root / "catalogs"
    return ImportedHLAPacket(
        root=root,
        manifest=_load_manifest(root),
        master_rows=tuple(MasterRequirementRow(**row) for row in _read_csv_dicts(latest / "hla_1516_requirements_master_v1_0.csv")),
        verification_rows=tuple(VerificationMatrixRow(**row) for row in _read_csv_dicts(latest / "hla_1516_verification_matrix_v1_0.csv")),
        clause_tracker_rows=tuple(ClauseTrackerRow(**row) for row in _read_csv_dicts(latest / "hla_1516_clause_tracker_v1_0.csv")),
        summary_rows=tuple(RequirementsSummaryRow(**row) for row in _read_csv_dicts(latest / "hla_1516_requirements_summary_v1_0.csv")),
        delta_rows=tuple(MasterRequirementRow(**row) for row in _read_csv_dicts(latest / "hla_1516_requirements_delta_v1_0.csv")),
        clauses5_11_detailed_rows=tuple(MasterRequirementRow(**row) for row in _read_csv_dicts(latest / "hla_1516_clauses5_11_detailed_requirements_v1_0.csv")),
        clause6_11_detailed_rows=tuple(MasterRequirementRow(**row) for row in _read_csv_dicts(latest / "hla_1516_clause6_11_detailed_requirements_v1_0.csv")),
        omt_xml_detailed_rows=tuple(MasterRequirementRow(**row) for row in _read_csv_dicts(latest / "hla_1516_omt_xml_detailed_requirements_v1_0.csv")),
        cpp_api_rows=tuple(CppApiCatalogRow(**row) for row in _read_csv_dicts(latest / "hla_1516_cpp_api_catalog_v1_0.csv")),
        api_service_catalog_rows=tuple(ApiServiceCatalogRow(**row) for row in _read_csv_dicts(catalogs / "hla_1516_api_service_catalog_v0_3.csv")),
        mim_catalog_rows=tuple(MimCatalogRow(**row) for row in _read_csv_dicts(catalogs / "hla_1516_mim_catalog_v0_3.csv")),
        xsd_catalog_rows=tuple(XsdCatalogRow(**row) for row in _read_csv_dicts(catalogs / "hla_1516_xsd_catalog_v0_3.csv")),
        wsdl_catalog_rows=tuple(WsdlCatalogRow(**row) for row in _read_csv_dicts(catalogs / "hla_1516_wsdl_catalog_v0_3.csv")),
    )


def _markdown_table(headers: list[str], rows: Iterable[list[str]]) -> list[str]:
    lines = [
        f"| {' | '.join(headers)} |",
        f"|{'|'.join(['---'] * len(headers))}|",
    ]
    for row in rows:
        lines.append(f"| {' | '.join(row)} |")
    return lines


def build_imported_hla_packet_markdown_views(project_root: Path | None = None) -> dict[str, list[str]]:
    packet = load_imported_hla_packet(project_root)
    rows = packet.master_rows

    by_standard: dict[str, list[MasterRequirementRow]] = defaultdict(list)
    by_clause: dict[tuple[str, str], list[MasterRequirementRow]] = defaultdict(list)
    by_capability: dict[str, list[MasterRequirementRow]] = defaultdict(list)
    by_service_group: dict[tuple[str, str, str], list[MasterRequirementRow]] = defaultdict(list)
    for row in rows:
        by_standard[row.standard].append(row)
        by_clause[(row.standard, row.clause)].append(row)
        by_capability[row.capability].append(row)
        if row.service_name.strip():
            by_service_group[(row.standard, row.clause, row.service_name)].append(row)

    baseline_note = (
        "The imported v1.0 packet is an engineering baseline, not a certified paragraph-by-paragraph compliance extraction. "
        "Use these generated views for harmonization and review, not as a substitute for source-PDF peer review."
    )

    views: dict[str, list[str]] = {}
    views["README.md"] = [
        "# Imported HLA Packet Requirements v1.0",
        "",
        baseline_note,
        "",
        "Generated views:",
        "",
        "- [by_standard.md](by_standard.md): grouped by source standard",
        "- [by_clause.md](by_clause.md): grouped by standard and clause",
        "- [by_capability.md](by_capability.md): grouped by packet capability code",
        "- [by_service_group.md](by_service_group.md): grouped by standard, clause, and service name",
        "",
        "Summary:",
        "",
        f"- Master requirement rows: {len(rows)}",
        f"- Standards: {len(by_standard)}",
        f"- Clauses: {len(by_clause)}",
        f"- Capabilities: {len(by_capability)}",
        f"- Service groups: {len(by_service_group)}",
    ]

    standard_lines = ["# Imported Packet Requirements By Standard", "", baseline_note, ""]
    for standard, group in sorted(by_standard.items()):
        standard_lines.extend(
            [
                f"## {standard}",
                "",
                f"- Requirement rows: {len(group)}",
                f"- Clauses represented: {len({row.clause for row in group})}",
                f"- Capabilities represented: {len({row.capability for row in group})}",
                "",
            ]
        )
        standard_lines.extend(
            _markdown_table(
                ["Clause", "Rows", "Capabilities"],
                [
                    [
                        clause,
                        str(len(clause_group)),
                        ", ".join(sorted({row.capability for row in clause_group})[:4]),
                    ]
                    for clause, clause_group in sorted(
                        ((clause, [row for row in group if row.clause == clause]) for clause in {row.clause for row in group}),
                        key=lambda item: item[0],
                    )
                ],
            )
        )
        standard_lines.append("")
    views["by_standard.md"] = standard_lines

    clause_lines = ["# Imported Packet Requirements By Clause", "", baseline_note, ""]
    for (standard, clause), group in sorted(by_clause.items()):
        titles = sorted({row.source_title for row in group if row.source_title.strip()})
        clause_lines.extend(
            [
                f"## {standard} Clause {clause}",
                "",
                f"- Requirement rows: {len(group)}",
                f"- Source titles: {', '.join(titles[:3]) or '-'}",
                f"- Features: {len({row.feature for row in group})}",
                "",
            ]
        )
        clause_lines.extend(
            _markdown_table(
                ["Requirement ID", "Type", "Feature", "Service", "Priority"],
                [
                    [
                        row.requirement_id,
                        row.requirement_type,
                        row.feature,
                        row.service_name or "-",
                        row.priority,
                    ]
                    for row in group[:20]
                ],
            )
        )
        if len(group) > 20:
            clause_lines.extend(["", f"_Truncated to first 20 rows; full clause row count is {len(group)}._", ""])
        else:
            clause_lines.append("")
    views["by_clause.md"] = clause_lines

    capability_lines = ["# Imported Packet Requirements By Capability", "", baseline_note, ""]
    for capability, group in sorted(by_capability.items()):
        capability_lines.extend(
            [
                f"## {capability}",
                "",
                f"- Requirement rows: {len(group)}",
                f"- Standards represented: {len({row.standard for row in group})}",
                f"- Clauses represented: {len({(row.standard, row.clause) for row in group})}",
                "",
            ]
        )
        capability_lines.extend(
            _markdown_table(
                ["Standard", "Clause", "Rows", "Example feature"],
                [
                    [
                        standard,
                        clause,
                        str(len(clause_group)),
                        clause_group[0].feature,
                    ]
                    for (standard, clause), clause_group in sorted(
                        (
                            (key, [row for row in group if (row.standard, row.clause) == key])
                            for key in {(row.standard, row.clause) for row in group}
                        ),
                        key=lambda item: (item[0][0], item[0][1]),
                    )
                ],
            )
        )
        capability_lines.append("")
    views["by_capability.md"] = capability_lines

    service_lines = ["# Imported Packet Requirements By Service Group", "", baseline_note, ""]
    for (standard, clause, service_name), group in sorted(by_service_group.items()):
        service_lines.extend(
            [
                f"## {standard} Clause {clause} {service_name}",
                "",
                f"- Requirement rows: {len(group)}",
                f"- Requirement types: {', '.join(sorted({row.requirement_type for row in group}))}",
                "",
            ]
        )
        service_lines.extend(
            _markdown_table(
                ["Requirement ID", "Type", "Feature", "Verification method"],
                [
                    [
                        row.requirement_id,
                        row.requirement_type,
                        row.feature,
                        row.verification_method,
                    ]
                    for row in group
                ],
            )
        )
        service_lines.append("")
    views["by_service_group.md"] = service_lines

    return views


def write_imported_hla_packet_markdown_views(output_dir: Path, project_root: Path | None = None) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for name, lines in build_imported_hla_packet_markdown_views(project_root).items():
        path = output_dir / name
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        written[name] = path
    return written
