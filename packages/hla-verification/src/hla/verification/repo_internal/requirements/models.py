from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


def _string(value: object) -> str:
    return str(value or "").strip()


def _string_tuple(value: object) -> tuple[str, ...]:
    if isinstance(value, (list, tuple)):
        return tuple(_string(item) for item in value if _string(item))
    if isinstance(value, str):
        return tuple(item.strip() for item in value.split(";") if item.strip())
    return ()


def _int(value: object) -> int:
    if value in (None, ""):
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    return 0


def _mapping_sequence(value: object) -> tuple[Mapping[str, object], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


@dataclass(frozen=True, slots=True)
class CanonicalRequirementRow:
    edition: str
    requirement_id: str
    source_document: str
    clause: str
    page: str
    area: str
    service_group: str
    service_or_check: str
    priority: str
    closure_wave: str
    requirement_text: str
    normative_level: str
    row_kind: str
    parent_requirement_id: str
    canonical_status: str
    canonical_status_reason: str
    owner_doc: str
    primary_test_shard: str
    primary_command: str
    evidence_refs: tuple[str, ...]
    boundary_note: str
    source_trace_strength: str
    repo_evidence_status: str
    tags: tuple[str, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> CanonicalRequirementRow:
        return cls(
            edition=_string(payload.get("edition")),
            requirement_id=_string(payload.get("requirement_id")),
            source_document=_string(payload.get("source_document")),
            clause=_string(payload.get("clause")),
            page=_string(payload.get("page")),
            area=_string(payload.get("area")),
            service_group=_string(payload.get("service_group")),
            service_or_check=_string(payload.get("service_or_check")),
            priority=_string(payload.get("priority")),
            closure_wave=_string(payload.get("closure_wave")),
            requirement_text=_string(payload.get("requirement_text")),
            normative_level=_string(payload.get("normative_level")),
            row_kind=_string(payload.get("row_kind")),
            parent_requirement_id=_string(payload.get("parent_requirement_id")),
            canonical_status=_string(payload.get("canonical_status")),
            canonical_status_reason=_string(payload.get("canonical_status_reason")),
            owner_doc=_string(payload.get("owner_doc")),
            primary_test_shard=_string(payload.get("primary_test_shard")),
            primary_command=_string(payload.get("primary_command")),
            evidence_refs=_string_tuple(payload.get("evidence_refs")),
            boundary_note=_string(payload.get("boundary_note")),
            source_trace_strength=_string(payload.get("source_trace_strength")),
            repo_evidence_status=_string(payload.get("repo_evidence_status")),
            tags=_string_tuple(payload.get("tags")),
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "edition": self.edition,
            "requirement_id": self.requirement_id,
            "source_document": self.source_document,
            "clause": self.clause,
            "page": self.page,
            "area": self.area,
            "service_group": self.service_group,
            "service_or_check": self.service_or_check,
            "priority": self.priority,
            "closure_wave": self.closure_wave,
            "requirement_text": self.requirement_text,
            "normative_level": self.normative_level,
            "row_kind": self.row_kind,
            "parent_requirement_id": self.parent_requirement_id,
            "canonical_status": self.canonical_status,
            "canonical_status_reason": self.canonical_status_reason,
            "owner_doc": self.owner_doc,
            "primary_test_shard": self.primary_test_shard,
            "primary_command": self.primary_command,
            "evidence_refs": list(self.evidence_refs),
            "boundary_note": self.boundary_note,
            "source_trace_strength": self.source_trace_strength,
            "repo_evidence_status": self.repo_evidence_status,
            "tags": list(self.tags),
        }


@dataclass(frozen=True, slots=True)
class NormalizedRequirementCatalog:
    artifact: str
    edition: str
    generated_from: tuple[str, ...]
    row_count: int
    rows: tuple[CanonicalRequirementRow, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> NormalizedRequirementCatalog:
        raw_rows = _mapping_sequence(payload.get("rows"))
        return cls(
            artifact=_string(payload.get("artifact")),
            edition=_string(payload.get("edition")),
            generated_from=_string_tuple(payload.get("generated_from")),
            row_count=_int(payload.get("row_count")),
            rows=tuple(CanonicalRequirementRow.from_mapping(row) for row in raw_rows),
        )

    def to_mapping(self) -> dict[str, Any]:
        return {
            "artifact": self.artifact,
            "edition": self.edition,
            "generated_from": list(self.generated_from),
            "row_count": self.row_count,
            "rows": [row.to_mapping() for row in self.rows],
        }


@dataclass(frozen=True, slots=True)
class RequirementArtifactSurveyEntry:
    path: str
    format: str
    edition: str
    family: str
    classification_basis: str
    fields: tuple[str, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> RequirementArtifactSurveyEntry:
        return cls(
            path=_string(payload.get("path")),
            format=_string(payload.get("format")),
            edition=_string(payload.get("edition")),
            family=_string(payload.get("family")),
            classification_basis=_string(payload.get("classification_basis")),
            fields=_string_tuple(payload.get("fields")),
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "path": self.path,
            "format": self.format,
            "edition": self.edition,
            "family": self.family,
            "classification_basis": self.classification_basis,
            "fields": list(self.fields),
        }


@dataclass(frozen=True, slots=True)
class RequirementArtifactSurvey:
    artifact: str
    scoped_roots: tuple[str, ...]
    entry_count: int
    entries: tuple[RequirementArtifactSurveyEntry, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> RequirementArtifactSurvey:
        raw_entries = _mapping_sequence(payload.get("entries"))
        return cls(
            artifact=_string(payload.get("artifact")),
            scoped_roots=_string_tuple(payload.get("scoped_roots")),
            entry_count=_int(payload.get("entry_count")),
            entries=tuple(RequirementArtifactSurveyEntry.from_mapping(entry) for entry in raw_entries),
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "artifact": self.artifact,
            "scoped_roots": list(self.scoped_roots),
            "entry_count": self.entry_count,
            "entries": [entry.to_mapping() for entry in self.entries],
        }


@dataclass(frozen=True, slots=True)
class CanonicalRowTriageEntry:
    requirement_id: str
    row_kind: str
    triage_decision: str
    triage_basis: str
    source_document: str
    clause: str
    service_group: str
    service_or_check: str
    canonical_status: str
    owner_doc: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> CanonicalRowTriageEntry:
        return cls(
            requirement_id=_string(payload.get("requirement_id")),
            row_kind=_string(payload.get("row_kind")),
            triage_decision=_string(payload.get("triage_decision")),
            triage_basis=_string(payload.get("triage_basis")),
            source_document=_string(payload.get("source_document")),
            clause=_string(payload.get("clause")),
            service_group=_string(payload.get("service_group")),
            service_or_check=_string(payload.get("service_or_check")),
            canonical_status=_string(payload.get("canonical_status")),
            owner_doc=_string(payload.get("owner_doc")),
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "requirement_id": self.requirement_id,
            "row_kind": self.row_kind,
            "triage_decision": self.triage_decision,
            "triage_basis": self.triage_basis,
            "source_document": self.source_document,
            "clause": self.clause,
            "service_group": self.service_group,
            "service_or_check": self.service_or_check,
            "canonical_status": self.canonical_status,
            "owner_doc": self.owner_doc,
        }


@dataclass(frozen=True, slots=True)
class CanonicalRowTriageArtifact:
    artifact: str
    edition: str
    generated_from: tuple[str, ...]
    row_count: int
    decision_counts: dict[str, int]
    rows: tuple[CanonicalRowTriageEntry, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> CanonicalRowTriageArtifact:
        raw_rows = _mapping_sequence(payload.get("rows"))
        decision_counts_raw = payload.get("decision_counts", {})
        return cls(
            artifact=_string(payload.get("artifact")),
            edition=_string(payload.get("edition")),
            generated_from=_string_tuple(payload.get("generated_from")),
            row_count=_int(payload.get("row_count")),
            decision_counts={
                _string(key): _int(value)
                for key, value in decision_counts_raw.items()
            }
            if isinstance(decision_counts_raw, Mapping)
            else {},
            rows=tuple(CanonicalRowTriageEntry.from_mapping(row) for row in raw_rows),
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "artifact": self.artifact,
            "edition": self.edition,
            "generated_from": list(self.generated_from),
            "row_count": self.row_count,
            "decision_counts": dict(self.decision_counts),
            "rows": [row.to_mapping() for row in self.rows],
        }


@dataclass(frozen=True, slots=True)
class RequirementMappingRow:
    edition: str
    source_requirement_id: str
    canonical_requirement_id: str
    mapping_kind: str
    current_status: str
    requirement_text: str
    mapping_notes: str
    source_packet_file: str
    owner_doc: str
    evidence_refs: tuple[str, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> RequirementMappingRow:
        return cls(
            edition=_string(payload.get("edition")),
            source_requirement_id=_string(payload.get("source_requirement_id")),
            canonical_requirement_id=_string(payload.get("canonical_requirement_id")),
            mapping_kind=_string(payload.get("mapping_kind")),
            current_status=_string(payload.get("current_status")),
            requirement_text=_string(payload.get("requirement_text")),
            mapping_notes=_string(payload.get("mapping_notes")),
            source_packet_file=_string(payload.get("source_packet_file")),
            owner_doc=_string(payload.get("owner_doc")),
            evidence_refs=_string_tuple(payload.get("evidence_refs")),
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "edition": self.edition,
            "source_requirement_id": self.source_requirement_id,
            "canonical_requirement_id": self.canonical_requirement_id,
            "mapping_kind": self.mapping_kind,
            "current_status": self.current_status,
            "requirement_text": self.requirement_text,
            "mapping_notes": self.mapping_notes,
            "source_packet_file": self.source_packet_file,
            "owner_doc": self.owner_doc,
            "evidence_refs": list(self.evidence_refs),
        }


@dataclass(frozen=True, slots=True)
class BackendResolutionRow:
    edition: str
    requirement_id: str
    row_kind: str
    resolution_type: str
    canonical_owner: str
    canonical_status: str
    primary_shard: str
    primary_command: str
    evidence_artifact: str
    evidence_refs: tuple[str, ...]
    boundary_note: str
    backend_fields: dict[str, str]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> BackendResolutionRow:
        backend_fields_raw = payload.get("backend_fields", {})
        return cls(
            edition=_string(payload.get("edition")),
            requirement_id=_string(payload.get("requirement_id")),
            row_kind=_string(payload.get("row_kind")),
            resolution_type=_string(payload.get("resolution_type")),
            canonical_owner=_string(payload.get("canonical_owner")),
            canonical_status=_string(payload.get("canonical_status")),
            primary_shard=_string(payload.get("primary_shard")),
            primary_command=_string(payload.get("primary_command")),
            evidence_artifact=_string(payload.get("evidence_artifact")),
            evidence_refs=_string_tuple(payload.get("evidence_refs")),
            boundary_note=_string(payload.get("boundary_note")),
            backend_fields={
                _string(key): _string(value)
                for key, value in backend_fields_raw.items()
            }
            if isinstance(backend_fields_raw, Mapping)
            else {},
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "edition": self.edition,
            "requirement_id": self.requirement_id,
            "row_kind": self.row_kind,
            "resolution_type": self.resolution_type,
            "canonical_owner": self.canonical_owner,
            "canonical_status": self.canonical_status,
            "primary_shard": self.primary_shard,
            "primary_command": self.primary_command,
            "evidence_artifact": self.evidence_artifact,
            "evidence_refs": list(self.evidence_refs),
            "boundary_note": self.boundary_note,
            "backend_fields": dict(self.backend_fields),
        }


@dataclass(frozen=True, slots=True)
class BackendResolutionCatalog:
    artifact: str
    edition: str
    generated_from: tuple[str, ...]
    row_count: int
    rows: tuple[BackendResolutionRow, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> BackendResolutionCatalog:
        raw_rows = _mapping_sequence(payload.get("rows"))
        return cls(
            artifact=_string(payload.get("artifact")),
            edition=_string(payload.get("edition")),
            generated_from=_string_tuple(payload.get("generated_from")),
            row_count=_int(payload.get("row_count")),
            rows=tuple(BackendResolutionRow.from_mapping(row) for row in raw_rows),
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "artifact": self.artifact,
            "edition": self.edition,
            "generated_from": list(self.generated_from),
            "row_count": self.row_count,
            "rows": [row.to_mapping() for row in self.rows],
        }


@dataclass(frozen=True, slots=True)
class CanonicalBackendRequirementRow:
    edition: str
    requirement_id: str
    source_document: str
    clause: str
    service_group: str
    service_or_check: str
    row_kind: str
    canonical_status: str
    canonical_status_reason: str
    owner_doc: str
    primary_test_shard: str
    primary_command: str
    requirement_evidence_refs: tuple[str, ...]
    backend_evidence_refs: tuple[str, ...]
    boundary_note: str
    backend_fields: dict[str, str]

    @classmethod
    def from_rows(
        cls,
        requirement_row: CanonicalRequirementRow,
        backend_row: BackendResolutionRow,
    ) -> CanonicalBackendRequirementRow:
        return cls(
            edition=requirement_row.edition,
            requirement_id=requirement_row.requirement_id,
            source_document=requirement_row.source_document,
            clause=requirement_row.clause,
            service_group=requirement_row.service_group,
            service_or_check=requirement_row.service_or_check,
            row_kind=requirement_row.row_kind,
            canonical_status=requirement_row.canonical_status,
            canonical_status_reason=requirement_row.canonical_status_reason,
            owner_doc=requirement_row.owner_doc,
            primary_test_shard=requirement_row.primary_test_shard,
            primary_command=requirement_row.primary_command,
            requirement_evidence_refs=requirement_row.evidence_refs,
            backend_evidence_refs=backend_row.evidence_refs,
            boundary_note=backend_row.boundary_note or requirement_row.boundary_note,
            backend_fields=dict(backend_row.backend_fields),
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "edition": self.edition,
            "requirement_id": self.requirement_id,
            "source_document": self.source_document,
            "clause": self.clause,
            "service_group": self.service_group,
            "service_or_check": self.service_or_check,
            "row_kind": self.row_kind,
            "canonical_status": self.canonical_status,
            "canonical_status_reason": self.canonical_status_reason,
            "owner_doc": self.owner_doc,
            "primary_test_shard": self.primary_test_shard,
            "primary_command": self.primary_command,
            "requirement_evidence_refs": list(self.requirement_evidence_refs),
            "backend_evidence_refs": list(self.backend_evidence_refs),
            "boundary_note": self.boundary_note,
            "backend_fields": dict(self.backend_fields),
        }
