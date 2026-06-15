from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SectionComplianceSummary:
    section_ref: str
    interface_counts: dict[str, int]
    implementation_status_counts: dict[str, int]
    verification_status_counts: dict[str, int]
    exact_requirement_evidence_rows: int
    no_requirement_evidence_rows: int
    known_gap_rows: int
    methods: tuple[str, ...]


@dataclass(frozen=True)
class PublicClassInventoryRow:
    module: str
    class_name: str
    exported_via_package: bool
    mapping_status: str
    rationale: str


@dataclass(frozen=True)
class GapSectionSummary:
    section_root: str
    section_label: str
    row_count: int
    core_priority: int
    representative_methods: tuple[str, ...]


@dataclass(frozen=True)
class NegativePathLedgerRow:
    section_ref: str
    interface: str
    method_name: str
    verification_status: str
    negative_path_status: str
    declared_exception_count: int
    actionable_exception_count: int
    negative_executed_count: int
    declared_exceptions: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class Section8BackendMatrixRow:
    backend_id: str
    backend_family: str
    section_ref: str
    method_name: str
    status: str
    scope: str
    session_status: str
    supports_immediate_inline: bool
    evidence_tests: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class CoreBackendMatrixRow:
    backend_id: str
    backend_family: str
    slice_id: str
    section_refs: tuple[str, ...]
    status: str
    scope: str
    session_status: str
    evidence_tests: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class CompletionChecklistRow:
    checklist_id: str
    area: str
    status: str
    evidence: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class UnfinishedWorkRow:
    priority: str
    claim_value_rank: int
    work_id: str
    area: str
    current_state: str
    target_state: str
    evidence: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class PitchRequirementDispositionRow:
    matrix_id: str
    requirement_id: str
    document: str
    section_ref: str
    clause_root: str
    kind: str
    title: str
    python_runtime_status: str
    pitch_runtime_status: str
    pitch_disposition: str
    pitch_jpype_disposition: str
    pitch_py4j_disposition: str
    applicability: str
    evidence_refs: tuple[str, ...]
    pitch_jpype_evidence_refs: tuple[str, ...]
    pitch_py4j_evidence_refs: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class BackendRequirementDispositionRow:
    matrix_id: str
    requirement_id: str
    document: str
    section_ref: str
    clause_root: str
    kind: str
    title: str
    runtime_status: str
    runtime_disposition: str
    evidence_refs: tuple[str, ...]
    notes: str


BACKEND_DISPOSITION_ARTIFACT_META: dict[str, dict[str, str]] = {
    "python": {
        "disposition_field": "python_runtime_disposition",
        "status_field": "python_runtime_status",
        "title": "Python Requirement Disposition",
        "label": "python",
        "output_stem": "python_requirement_disposition",
    },
    "certi": {
        "disposition_field": "certi_runtime_disposition",
        "status_field": "certi_runtime_status",
        "title": "CERTI Requirement Disposition",
        "label": "certi",
        "output_stem": "certi_requirement_disposition",
    },
    "portico": {
        "disposition_field": "portico_runtime_disposition",
        "status_field": "portico_runtime_status",
        "title": "Portico Requirement Disposition",
        "label": "portico",
        "output_stem": "portico_requirement_disposition",
    },
}


SUPPORTED_SUBSET_POLICY_DEFS: dict[str, dict[str, str]] = {
    "logical-time-update-rate-only": {
        "title": "Logical-time update-rate subset",
        "supported_behavior": (
            "Update-rate reduction is implemented as logical-time-based throttling. "
            "Explicit and FOM-declared update-rate designators apply across direct, inherited, "
            "and regioned subscriptions when there is a logical-time basis."
        ),
        "broad_gap": (
            "The backend does not invent a wall-clock or unmanaged receive-order throttling policy, "
            "so broader vendor-style update-rate semantics remain out of scope."
        ),
    },
    "reliable-best-effort-transport-only": {
        "title": "Reliable and best-effort transport subset",
        "supported_behavior": (
            "Transportation semantics are implemented for the standard HLAreliable and HLAbestEffort pair, "
            "including FOM-defined defaults, explicit overrides, callback/query reporting, and restore persistence."
        ),
        "broad_gap": (
            "The backend does not model arbitrary custom transportation-type behavior beyond the reliable/best-effort subset."
        ),
    },
    "unbatched-callback-delivery-only": {
        "title": "Unbatched callback delivery subset",
        "supported_behavior": (
            "The backend preserves externally visible delivery semantics with direct unbatched callbacks."
        ),
        "broad_gap": (
            "Message combination, packaging, and passelization are not explicitly modeled, so the permissive broad row stays partial by policy."
        ),
    },
}


__all__ = [
    "BACKEND_DISPOSITION_ARTIFACT_META",
    "BackendRequirementDispositionRow",
    "CompletionChecklistRow",
    "CoreBackendMatrixRow",
    "GapSectionSummary",
    "NegativePathLedgerRow",
    "PitchRequirementDispositionRow",
    "PublicClassInventoryRow",
    "SUPPORTED_SUBSET_POLICY_DEFS",
    "Section8BackendMatrixRow",
    "SectionComplianceSummary",
    "UnfinishedWorkRow",
]
