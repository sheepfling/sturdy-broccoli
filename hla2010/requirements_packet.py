from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path


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
class ImportedHLAPacket:
    root: Path
    manifest: PacketManifest
    master_rows: tuple[MasterRequirementRow, ...]
    verification_rows: tuple[VerificationMatrixRow, ...]
    clause_tracker_rows: tuple[ClauseTrackerRow, ...]

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
    return ImportedHLAPacket(
        root=root,
        manifest=_load_manifest(root),
        master_rows=tuple(MasterRequirementRow(**row) for row in _read_csv_dicts(latest / "hla_1516_requirements_master_v1_0.csv")),
        verification_rows=tuple(VerificationMatrixRow(**row) for row in _read_csv_dicts(latest / "hla_1516_verification_matrix_v1_0.csv")),
        clause_tracker_rows=tuple(ClauseTrackerRow(**row) for row in _read_csv_dicts(latest / "hla_1516_clause_tracker_v1_0.csv")),
    )
