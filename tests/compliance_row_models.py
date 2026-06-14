from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


def _string_tuple(value: object) -> tuple[str, ...]:
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    return ()


@dataclass(frozen=True)
class RequirementDispositionRow:
    document: str
    clause_root: str
    requirement_id: str
    matrix_id: str
    kind: str
    title: str
    applicability: str
    notes: str
    runtime_disposition: str
    pitch_disposition: str
    pitch_jpype_disposition: str
    pitch_py4j_disposition: str
    evidence_refs: tuple[str, ...]
    pitch_jpype_evidence_refs: tuple[str, ...]
    pitch_py4j_evidence_refs: tuple[str, ...]

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> RequirementDispositionRow:
        return cls(
            document=str(row.get("document", "")).strip(),
            clause_root=str(row.get("clause_root", "")).strip(),
            requirement_id=str(row.get("requirement_id", "")).strip(),
            matrix_id=str(row.get("matrix_id", "")).strip(),
            kind=str(row.get("kind", "")).strip(),
            title=str(row.get("title", "")).strip(),
            applicability=str(row.get("applicability", "")).strip(),
            notes=str(row.get("notes", "")).strip(),
            runtime_disposition=str(row.get("runtime_disposition", "")).strip(),
            pitch_disposition=str(row.get("pitch_disposition", "")).strip(),
            pitch_jpype_disposition=str(row.get("pitch_jpype_disposition", "")).strip(),
            pitch_py4j_disposition=str(row.get("pitch_py4j_disposition", "")).strip(),
            evidence_refs=_string_tuple(row.get("evidence_refs")),
            pitch_jpype_evidence_refs=_string_tuple(row.get("pitch_jpype_evidence_refs")),
            pitch_py4j_evidence_refs=_string_tuple(row.get("pitch_py4j_evidence_refs")),
        )

    @property
    def identifier(self) -> str:
        return self.requirement_id or self.matrix_id

    @property
    def clause_key(self) -> str:
        clause_root = "" if self.clause_root.lower() == "unknown" else self.clause_root
        return f"{self.document} §{clause_root}" if clause_root else f"{self.document} unknown"

    def disposition_for(self, field_name: str) -> str:
        return {
            "runtime_disposition": self.runtime_disposition,
            "pitch_disposition": self.pitch_disposition,
            "pitch_jpype_disposition": self.pitch_jpype_disposition,
            "pitch_py4j_disposition": self.pitch_py4j_disposition,
        }[field_name]

    def evidence_refs_for(self, field_name: str) -> tuple[str, ...]:
        return {
            "evidence_refs": self.evidence_refs,
            "pitch_jpype_evidence_refs": self.pitch_jpype_evidence_refs,
            "pitch_py4j_evidence_refs": self.pitch_py4j_evidence_refs,
        }[field_name]


@dataclass(frozen=True)
class VendorBacklogRow:
    requirement_id: str
    section_ref: str
    backend_id: str
    backend_family: str
    current_status: str
    row_kind: str
    scope: str
    priority: str
    recommended_next_action: str
    source_artifact: str
    rationale: str
    evidence_tests: tuple[str, ...]

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> VendorBacklogRow:
        return cls(
            requirement_id=str(row.get("requirement_id", "")).strip(),
            section_ref=str(row.get("section_ref", "")).strip(),
            backend_id=str(row.get("backend_id", "")).strip(),
            backend_family=str(row.get("backend_family", "")).strip(),
            current_status=str(row.get("current_status", "")).strip(),
            row_kind=str(row.get("row_kind", "")).strip(),
            scope=str(row.get("scope", "")).strip(),
            priority=str(row.get("priority", "")).strip(),
            recommended_next_action=str(row.get("recommended_next_action", "")).strip(),
            source_artifact=str(row.get("source_artifact", "")).strip(),
            rationale=str(row.get("rationale", "")).strip(),
            evidence_tests=_string_tuple(row.get("evidence_tests")),
        )

    @property
    def section_or_requirement(self) -> str:
        return self.requirement_id or self.section_ref


@dataclass(frozen=True)
class BackendCatalogRow:
    backend_id: str
    backend_family: str
    matrices_present: tuple[str, ...]
    section_refs: tuple[str, ...]
    status_counts: dict[str, int]

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any]) -> BackendCatalogRow:
        status_counts_raw = row.get("status_counts", {})
        return cls(
            backend_id=str(row.get("backend_id", "")).strip(),
            backend_family=str(row.get("backend_family", "")).strip(),
            matrices_present=_string_tuple(row.get("matrices_present")),
            section_refs=_string_tuple(row.get("section_refs")),
            status_counts={
                str(key): int(value)
                for key, value in status_counts_raw.items()
            }
            if isinstance(status_counts_raw, Mapping)
            else {},
        )


@dataclass(frozen=True)
class ReferenceCsvRow:
    cells: dict[str, str]

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> ReferenceCsvRow:
        return cls(
            cells={
                str(key): str(value).strip()
                for key, value in row.items()
            }
        )

    def values(self) -> tuple[str, ...]:
        return tuple(self.cells.values())
