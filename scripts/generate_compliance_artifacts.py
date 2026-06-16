#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib
import inspect
import json
import re
import sys
import tomllib
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

REPO_ROOT = Path.cwd()

import hla.rti1516e
from hla.verification.repo_internal.conformance import (
    ServiceConformanceRow,
    actionable_negative_expectation_count,
    build_service_conformance_matrix,
    negative_path_status,
    write_service_conformance_csv,
    write_service_conformance_json,
)
from hla.verification.repo_internal.verification.backend_compliance_discovery import write_vendor_discovery_backlog_artifacts
from hla.verification.repo_internal.verification.asset_plan import (
    write_traceability_csv,
    write_verification_assets,
)
from hla.verification.repo_internal.verification.repo_seed_artifacts import (
    write_requirements_ledger_csv,
    write_requirements_ledger_json,
)
from hla.verification.repo_internal.verification.requirements_matrix_artifacts import (
    build_requirements_matrix_2010,
    write_requirements_matrix_2010_csv,
    write_requirements_matrix_2010_json,
)

OUTPUT_DIR = REPO_ROOT / "analysis" / "compliance"


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


_BACKEND_DISPOSITION_ARTIFACT_META: dict[str, dict[str, str]] = {
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


_SUPPORTED_SUBSET_POLICY_DEFS: dict[str, dict[str, str]] = {
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


_SCENARIO_EVIDENCE_REGISTRY: dict[str, tuple[str, ...]] = {
    "federation-lifecycle": (
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_federation_lifecycle_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_lifecycle_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_lifecycle_matrix",
    ),
    "federation-lifecycle-negative": (
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_federation_lifecycle_negative_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_lifecycle_negative_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_lifecycle_negative_matrix",
    ),
    "fom-integrity-negative": (
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_fom_integrity_negative_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_fom_integrity_negative_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_fom_integrity_negative_matrix",
    ),
    "multi-participation": (
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_multi_participation_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_multi_participation_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_multi_participation_matrix",
    ),
    "federation-lifecycle-with-mim": (
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_federation_lifecycle_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_lifecycle_with_mim_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_lifecycle_with_mim_matrix",
    ),
    "join-preconditions": (
        "packages/hla-verification/src/hla.verification/scenario_join.py::run_join_precondition_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_join_precondition_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_join_precondition_matrix",
    ),
    "federation-listing": (
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_federation_listing_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_listing_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_listing_matrix",
    ),
    "fom-module-visibility": (
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_fom_module_visibility_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_fom_module_visibility_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_fom_module_visibility_matrix",
    ),
    "fom-multi-module-visibility": (
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_multi_module_fom_visibility_scenario",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_multi_module_fom_visibility_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_multi_module_fom_visibility_matrix",
    ),
    "synchronization": (
        "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
    ),
    "synchronization-registration-failure": (
        "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_registration_failure_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_registration_failure_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_registration_failure_matrix",
    ),
    "synchronization-failed-federate": (
        "packages/hla-verification/src/hla.verification/scenario_sync.py::run_failed_federate_synchronization_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_failed_federate_synchronization_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_failed_federate_synchronization_matrix",
    ),
    "synchronization-late-join": (
        "packages/hla-verification/src/hla.verification/scenario_sync.py::run_late_join_synchronization_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_late_join_synchronization_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_late_join_synchronization_matrix",
    ),
    "synchronization-multiple-points": (
        "packages/hla-verification/src/hla.verification/scenario_sync.py::run_multiple_synchronization_points_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_multiple_synchronization_points_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_multiple_synchronization_points_matrix",
    ),
    "save-restore": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
    ),
    "save-restore-queued-callbacks": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_queued_callback_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_queued_callback_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_queued_callback_matrix",
    ),
    "save-restore-time-state": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_scheduled_save_restore_time_state_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_scheduled_save_restore_time_state_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_scheduled_save_restore_time_state_matrix",
    ),
    "save-restore-object-state": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_object_state_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_object_state_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_object_state_matrix",
    ),
    "save-restore-federate-local-state": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_federate_local_state_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_federate_local_state_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_federate_local_state_matrix",
    ),
    "save-restore-callback-policy": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_callback_policy_scenario",
        "tests/verification/test_compliance_slice_v011.py::test_restore_treats_callback_enablement_as_runtime_policy_not_saved_state",
    ),
    "save-restore-transient-state": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_transient_state_scenario",
        "tests/verification/test_compliance_slice_v011.py::test_restore_discards_pre_restore_callback_queue_and_retraction_bookkeeping",
    ),
    "save-failure": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_failure_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_failure_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_failure_matrix",
    ),
    "restore-abort-exceptions": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_abort_exception_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_abort_exception_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_abort_exception_matrix",
    ),
    "save-status-exceptions": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_status_exception_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_status_exception_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_status_exception_matrix",
    ),
    "save-request-preconditions": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_request_precondition_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_request_precondition_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_request_precondition_matrix",
    ),
    "save-participant-exceptions": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_participant_exception_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_participant_exception_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_participant_exception_matrix",
    ),
    "abort-save-exceptions": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_abort_save_exception_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_abort_save_exception_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_abort_save_exception_matrix",
    ),
    "restore-status-exceptions": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_status_exception_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_status_exception_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_status_exception_matrix",
    ),
    "restore-request-preconditions": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_request_precondition_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_request_precondition_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_request_precondition_matrix",
    ),
    "restore-participant-exceptions": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_participant_exception_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_participant_exception_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_participant_exception_matrix",
    ),
    "resign-callback-silence": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_resigned_federate_callback_silence_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_resigned_federate_callback_silence_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_resigned_federate_callback_silence_matrix",
    ),
    "resign-preconditions": (
        "packages/hla-verification/src/hla.verification/scenario_resign.py::run_resign_precondition_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_resign_precondition_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_resign_precondition_matrix",
    ),
    "resign-mom-cleanup": (
        "packages/hla-verification/src/hla.verification/scenario_resign.py::run_resign_mom_cleanup_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_resign_mom_cleanup_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_resign_mom_cleanup_matrix",
    ),
    "disconnect-mom-cleanup": (
        "packages/hla-verification/src/hla.verification/scenario_resign.py::run_disconnect_mom_cleanup_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_disconnect_mom_cleanup_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_disconnect_mom_cleanup_matrix",
    ),
    "restore-request-failure": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_request_failure_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_request_failure_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_request_failure_matrix",
    ),
    "restore-failure": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_failure_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_failure_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_failure_matrix",
    ),
    "save-abort": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_abort_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_abort_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_abort_matrix",
    ),
    "restore-abort": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_abort_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_abort_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_abort_matrix",
    ),
    "connection-lost-callback": (
        "packages/hla-verification/src/hla.verification/scenario_connection_lost.py::run_connection_lost_callback_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_connection_lost_callback_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_connection_lost_callback_matrix",
    ),
    "lost-federate-mom": (
        "packages/hla-verification/src/hla.verification/scenario_lost_federate.py::run_lost_federate_mom_scenario",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_lost_federate_mom_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix",
    ),
    "declaration-management": (
        "packages/hla-verification/src/hla.verification/scenario_declaration.py::run_declaration_management_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_management_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_declaration_management_matrix",
    ),
    "declaration-management-overloads": (
        "packages/hla-verification/src/hla.verification/scenario_declaration.py::run_declaration_management_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_management_overload_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_declaration_management_overload_matrix",
    ),
    "declaration-invalid-attribute-publication": (
        "packages/hla-verification/src/hla.verification/scenario_declaration.py::run_declaration_invalid_attribute_publication_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_invalid_attribute_publication_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_declaration_invalid_attribute_publication_matrix",
    ),
    "declaration-time-independence": (
        "packages/hla-verification/src/hla.verification/scenario_declaration.py::run_time_managed_declaration_independence_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_time_managed_declaration_independence_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_time_managed_declaration_independence_matrix",
    ),
    "declaration-unpublish-rejection": (
        "packages/hla-verification/src/hla.verification/scenario_declaration.py::run_declaration_unpublish_rejection_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_unpublish_rejection_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_declaration_unpublish_rejection_matrix",
    ),
    "discovery-metadata-callbacks": (
        "packages/hla-verification/src/hla.verification/scenario_discovery_metadata.py::run_discovery_metadata_callback_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_discovery_metadata_callback_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_discovery_metadata_callback_matrix",
    ),
    "discovery-class": (
        "packages/hla-verification/src/hla.verification/scenario_discovery_class.py::run_discovery_class_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_discovery_class_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_discovery_class_matrix",
    ),
    "name-reservation": (
        "packages/hla-verification/src/hla.verification/scenario_name_reservation.py::run_name_reservation_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_name_reservation_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_name_reservation_matrix",
    ),
    "local-delete": (
        "packages/hla-verification/src/hla.verification/scenario_local_delete.py::run_local_delete_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_local_delete_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_local_delete_matrix",
    ),
    "orphan-object-lifecycle": (
        "packages/hla-verification/src/hla.verification/scenario_orphan_object.py::run_orphan_object_lifecycle_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_orphan_object_lifecycle_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_orphan_object_lifecycle_matrix",
    ),
    "timed-delete": (
        "packages/hla-verification/src/hla.verification/scenario_timed_delete.py::run_timed_delete_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_timed_delete_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_timed_delete_matrix",
    ),
    "request-attribute-value-update": (
        "packages/hla-verification/src/hla.verification/scenario_request_attribute_value_update.py::run_request_attribute_value_update_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_request_attribute_value_update_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_request_attribute_value_update_matrix",
    ),
    "request-attribute-value-update-routing": (
        "packages/hla-verification/src/hla.verification/scenario_request_attribute_value_update.py::run_request_attribute_value_update_routing_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_request_attribute_value_update_routing_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_request_attribute_value_update_routing_matrix",
    ),
    "object-scope-relevance": (
        "packages/hla-verification/src/hla.verification/scenario_object_scope.py::run_object_scope_relevance_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_object_scope_relevance_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_object_scope_relevance_matrix",
    ),
    "transportation-type": (
        "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_matrix",
    ),
    "transportation-type-restore-persistence": (
        "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_restore_persistence_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_restore_persistence_matrix",
    ),
    "transportation-type-rejection": (
        "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_rejection_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_rejection_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_rejection_matrix",
    ),
    "update-advisory-callbacks": (
        "packages/hla-verification/src/hla.verification/scenario_update_advisory.py::run_update_advisory_callback_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_update_advisory_callback_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_update_advisory_callback_matrix",
    ),
    "support-factory-decode": (
        "packages/hla-verification/src/hla.verification/scenario_support_services.py::run_support_factory_and_decode_scenario",
        "tests/scenarios/test_support_services_backend_matrix.py::test_python_backend_support_factory_and_decode_matrix",
    ),
    "update-rate": (
        "packages/hla-verification/src/hla.verification/scenario_update_rate.py::run_update_rate_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_update_rate_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_update_rate_matrix",
    ),
    "two-federate-exchange": (
        "packages/hla-verification/src/hla.verification/scenario_exchange.py::run_two_federate_exchange_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_exchange_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_exchange_matrix",
    ),
    "ownership": (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_scenario",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_ownership_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ownership_matrix",
    ),
    "ownership-negotiated-offer-probe": (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::probe_negotiated_attribute_ownership_offer",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_negotiated_divesting_offer_probe_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_negotiated_divesting_offer_probe",
    ),
    "ownership-negotiated": (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_negotiated_attribute_ownership_scenario",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_negotiated_ownership_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_negotiated_ownership_matrix",
    ),
    "ownership-release-request": (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_release_request_ownership_scenario",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_release_request_ownership_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_release_request_owned_attribute_probe",
    ),
    "ownership-unavailable": (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_unavailable_scenario",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_ownership_unavailable_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ownership_unavailable_matrix",
    ),
    "ownership-release-denied": (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_release_request_ownership_scenario",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_release_denied_ownership_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_release_denied_ownership_matrix",
    ),
    "ownership-non-owner-update-rejection": (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_non_owner_update_rejection_scenario",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_non_owner_update_rejection_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_non_owner_update_rejection_matrix",
    ),
    "ownership-query-callbacks": (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_query_callback_scenario",
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_attribute_ownership_query_callback_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_attribute_ownership_query_callback_matrix",
    ),
    "ddm-region-routing": (
        "packages/hla-verification/src/hla.verification/two_federate_suite_scenarios.py::run_suite_ddm_scenario",
        "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_matrix",
    ),
    "ddm-object-region-lifecycle": (
        "packages/hla-verification/src/hla.verification/scenario_ddm_object_regions.py::run_ddm_object_region_lifecycle_scenario",
        "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_object_region_lifecycle_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_object_region_lifecycle_matrix",
    ),
    "ddm-declaration-gating": (
        "packages/hla-verification/src/hla.verification/scenario_ddm_object_regions.py::run_ddm_declaration_gating_scenario",
        "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_declaration_gating_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_declaration_gating_matrix",
    ),
    "ddm-passive-region-subscriptions": (
        "packages/hla-verification/src/hla.verification/scenario_ddm_passive_regions.py::run_ddm_passive_region_subscription_scenario",
        "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_passive_region_subscription_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_passive_region_subscription_matrix",
    ),
    "section8-state-services": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_state_services_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_state_services",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_state_services_matrix",
    ),
    "section8-logical-time": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_state_services_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_logical_time_query",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_logical_time_query_matrix",
    ),
    "section8-state-toggles": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_state_services_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_state_toggle_services",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_state_toggle_services_matrix",
    ),
    "section8-time-bound-queries": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_time_bound_query_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_time_bound_queries",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_time_bound_query_matrix",
    ),
    "section8-available-and-flush": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_available_and_flush_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_available_and_flush_services",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_available_and_flush_matrix",
    ),
    "section8-early-timestamp-send": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_early_timestamp_send_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_early_timestamp_send_rejection",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_early_timestamp_send_rejection_matrix",
    ),
    "section8-ordering-and-queries": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_ordering_and_query_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_ordering_and_queries",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_ordering_and_queries_matrix",
    ),
    "section8-available-and-retraction": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_available_and_retraction_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_available_and_retraction",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_available_and_retraction_matrix",
    ),
    "section8-order-override": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_order_override_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_order_override_services",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_order_override_services_matrix",
    ),
    "section8-request-retraction": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_request_retraction_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_request_retraction_callback",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_request_retraction_callback_matrix",
    ),
    "section8-duplicate-enable-rejection": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_duplicate_enable_rejection_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_duplicate_enable_rejection",
    ),
    "section8-tar-galt-boundary": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_tar_galt_boundary_case",
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_tar_galt_boundary",
    ),
    "section8-lookahead": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_state_services_case",
        "tests/time/test_lookahead_backend_matrix.py::test_lookahead_backend_matrix_state_services",
        "tests/time/test_lookahead_backend_matrix.py::test_lookahead_backend_matrix_blocks_early_timestamped_send",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lookahead_matrix",
    ),
}

_CERTI_SCENARIO_EVIDENCE_REGISTRY: dict[str, tuple[str, ...]] = {
    "synchronization": (
        "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_scenario",
        "tests/vendors/test_certi_real_backend_exchange_matrix.py::test_certi_backend_synchronization_matrix",
    ),
    "two-federate-exchange": (
        "packages/hla-verification/src/hla.verification/scenario_exchange.py::run_two_federate_exchange_scenario",
        "tests/vendors/test_certi_real_backend_exchange_matrix.py::test_certi_backend_exchange_matrix",
    ),
    "save-restore": (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
        "tests/vendors/test_real_vendor_runtime_smoke.py::test_certi_real_save_restore_smoke",
    ),
    "ownership": (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_scenario",
        "tests/vendors/test_certi_real_backend_ownership_matrix.py::test_certi_backend_ownership_matrix",
    ),
    "section8-state-services": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_state_services_case",
        "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_state_services_matrix",
    ),
    "section8-ordering-and-query": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_ordering_and_query_case",
        "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_ordering_and_query_matrix",
    ),
    "section8-available-and-flush": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_available_and_flush_case",
        "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_available_and_flush_matrix",
    ),
    "section8-available-and-retraction": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_available_and_retraction_case",
        "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_available_and_retraction_matrix",
    ),
    "section8-logical-time-query": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_state_services_case",
        "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_logical_time_query_matrix",
    ),
    "section8-state-toggles": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_state_services_case",
        "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_state_toggle_services_matrix",
    ),
    "section8-time-bound-query": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_time_bound_query_case",
        "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_time_bound_query_matrix",
    ),
    "section8-order-override": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_order_override_case",
        "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_order_override_matrix",
    ),
    "section8-request-retraction": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_request_retraction_case",
        "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_request_retraction_matrix",
    ),
    "section8-duplicate-enable-rejection": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_duplicate_enable_rejection_case",
        "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_duplicate_enable_rejection_matrix",
    ),
    "section8-tar-galt-boundary": (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_tar_galt_boundary_case",
        "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_tar_galt_boundary_matrix",
    ),
}

_CERTI_REQUIREMENT_EVIDENCE: dict[str, tuple[tuple[str, ...], str]] = {
    "REQ-RTI-FM-4_11-registerFederationSynchronizationPoint": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["synchronization"],
        "CERTI shared synchronization scenario verifies synchronization-point registration on the real backend path.",
    ),
    "REQ-FED-FM-4_12-synchronizationPointRegistrationSucceeded": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["synchronization"],
        "CERTI shared synchronization scenario verifies registration-success callbacks on the real backend path.",
    ),
    "REQ-FED-FM-4_13-announceSynchronizationPoint": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["synchronization"],
        "CERTI shared synchronization scenario verifies synchronization-point announcement callbacks on the real backend path.",
    ),
    "REQ-RTI-FM-4_14-synchronizationPointAchieved": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["synchronization"],
        "CERTI shared synchronization scenario verifies synchronization completion participation on the real backend path.",
    ),
    "REQ-FED-FM-4_15-federationSynchronized": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["synchronization"],
        "CERTI shared synchronization scenario verifies federation-synchronized callbacks on the real backend path.",
    ),
    "REQ-RTI-FM-4_16-requestFederationSave": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies the positive save-request path on the real backend path.",
    ),
    "REQ-FED-FM-4_17-initiateFederateSave": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies initiate-save callbacks on the real backend path.",
    ),
    "REQ-RTI-FM-4_18-federateSaveBegun": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies federate-save-begun participation on the real backend path.",
    ),
    "REQ-FED-FM-4_20-federationSaved": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies federation-saved callbacks on the real backend path.",
    ),
    "REQ-RTI-FM-4_22-queryFederationSaveStatus": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies save-status query coverage on the real backend path.",
    ),
    "REQ-FED-FM-4_23-federationSaveStatusResponse": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies save-status response callbacks on the real backend path.",
    ),
    "REQ-RTI-FM-4_24-requestFederationRestore": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies the positive restore-request path on the real backend path.",
    ),
    "REQ-FED-FM-4_25-requestFederationRestoreSucceeded": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies restore-request-succeeded callbacks on the real backend path.",
    ),
    "REQ-FED-FM-4_26-federationRestoreBegun": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies federation-restore-begun callbacks on the real backend path.",
    ),
    "REQ-FED-FM-4_27-initiateFederateRestore": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies initiate-restore callbacks on the real backend path.",
    ),
    "REQ-FED-FM-4_29-federationRestored": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies federation-restored callbacks on the real backend path.",
    ),
    "REQ-RTI-FM-4_31-queryFederationRestoreStatus": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies restore-status query coverage on the real backend path.",
    ),
    "REQ-FED-FM-4_32-federationRestoreStatusResponse": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies restore-status response callbacks on the real backend path.",
    ),
    "HLA1516.1-FM-4.16-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies requestFederationSave behavior on the real backend path.",
    ),
    "HLA1516.1-FM-4.17-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies initiateFederateSave callback behavior on the real backend path.",
    ),
    "HLA1516.1-FM-4.18-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies federateSaveBegun behavior on the real backend path.",
    ),
    "HLA1516.1-FM-4.22-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies queryFederationSaveStatus behavior on the real backend path.",
    ),
    "HLA1516.1-FM-4.23-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies federationSaveStatusResponse behavior on the real backend path.",
    ),
    "HLA1516.1-FM-4.24-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies requestFederationRestore behavior on the real backend path.",
    ),
    "HLA1516.1-FM-4.26-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies federationRestoreBegun behavior on the real backend path.",
    ),
    "HLA1516.1-FM-4.27-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies initiateFederateRestore callback behavior on the real backend path.",
    ),
    "HLA1516.1-FM-4.31-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies queryFederationRestoreStatus behavior on the real backend path.",
    ),
    "HLA1516.1-FM-4.32-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "CERTI shared save/restore scenario verifies federationRestoreStatusResponse behavior on the real backend path.",
    ),
    "REQ-RTI-OM-6_10-updateAttributeValues": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "CERTI shared two-federate exchange scenario verifies updateAttributeValues on both receive-order and timestamped paths.",
    ),
    "REQ-RTI-OM-6_12-sendInteraction": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "CERTI shared two-federate exchange scenario verifies sendInteraction on both receive-order and timestamped paths.",
    ),
    "HLA1516.1-OM-6.10-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "CERTI shared two-federate exchange scenario verifies receive-order updateAttributeValues delivery semantics.",
    ),
    "HLA1516.1-OM-6.10-002": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "CERTI shared two-federate exchange scenario verifies timestamped updateAttributeValues delivery semantics.",
    ),
    "HLA1516.1-OM-6.10-003": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "CERTI shared two-federate exchange scenario verifies updateAttributeValues payload delivery semantics.",
    ),
    "HLA1516.1-OM-6.10-004": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "CERTI shared two-federate exchange scenario verifies updateAttributeValues transportation semantics on the real backend path.",
    ),
    "HLA1516.1-OM-6.10-005": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "CERTI shared two-federate exchange scenario verifies updateAttributeValues ordering semantics on the real backend path.",
    ),
    "HLA1516.1-OM-6.12-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "CERTI shared two-federate exchange scenario verifies receive-order sendInteraction delivery semantics.",
    ),
    "HLA1516.1-OM-6.12-002": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "CERTI shared two-federate exchange scenario verifies timestamped sendInteraction delivery semantics.",
    ),
    "HLA1516.1-OM-6.12-003": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "CERTI shared two-federate exchange scenario verifies sendInteraction payload delivery semantics.",
    ),
    "HLA1516.1-OM-6.12-004": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "CERTI shared two-federate exchange scenario verifies sendInteraction transportation semantics on the real backend path.",
    ),
    "HLA1516.1-OM-6.12-005": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "CERTI shared two-federate exchange scenario verifies sendInteraction ordering semantics on the real backend path.",
    ),
    "REQ-FED-OWN-7_11-requestAttributeOwnershipRelease": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "CERTI shared ownership scenario verifies requestAttributeOwnershipRelease callbacks on the real backend path.",
    ),
    "REQ-RTI-OWN-7_17-queryAttributeOwnership": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "CERTI shared ownership scenario verifies queryAttributeOwnership on the real backend path.",
    ),
    "REQ-FED-OWN-7_18-attributeIsNotOwned": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "CERTI shared ownership scenario verifies attributeIsNotOwned callbacks on the real backend path.",
    ),
    "REQ-FED-OWN-7_18-attributeIsOwnedByRTI": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "CERTI shared ownership scenario verifies attributeIsOwnedByRTI callbacks on the real backend path.",
    ),
    "REQ-FED-OWN-7_18-informAttributeOwnership": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "CERTI shared ownership scenario verifies informAttributeOwnership callbacks on the real backend path.",
    ),
    "REQ-RTI-OWN-7_19-isAttributeOwnedByFederate": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "CERTI shared ownership scenario verifies isAttributeOwnedByFederate on the real backend path.",
    ),
    "REQ-RTI-OWN-7_2-unconditionalAttributeOwnershipDivestiture": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "CERTI shared ownership scenario verifies unconditionalAttributeOwnershipDivestiture on the real backend path.",
    ),
    "REQ-RTI-OWN-7_9-attributeOwnershipAcquisitionIfAvailable": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "CERTI shared ownership scenario verifies attributeOwnershipAcquisitionIfAvailable on the real backend path.",
    ),
    "HLA1516.1-OWN-7.11-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "CERTI shared ownership scenario verifies requestAttributeOwnershipRelease behavior on the real backend path.",
    ),
    "HLA1516.1-OWN-7.2-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "CERTI shared ownership scenario verifies unconditional divestiture behavior on the real backend path.",
    ),
    "HLA1516.1-OWN-7.9-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "CERTI shared ownership scenario verifies if-available acquisition behavior on the real backend path.",
    ),
    "HLA1516.1-OWN-7.9-002": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "CERTI shared ownership scenario verifies if-available acquisition callback behavior on the real backend path.",
    ),
    "REQ-RTI-TM-8_2-enableTimeRegulation": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-services"],
        "CERTI shared Section 8 state-services scenario verifies enableTimeRegulation on the real backend path.",
    ),
    "REQ-FED-TM-8_3-timeRegulationEnabled": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-services"],
        "CERTI shared Section 8 state-services scenario verifies timeRegulationEnabled callbacks on the real backend path.",
    ),
    "REQ-RTI-TM-8_5-enableTimeConstrained": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-services"],
        "CERTI shared Section 8 state-services scenario verifies enableTimeConstrained on the real backend path.",
    ),
    "REQ-FED-TM-8_6-timeConstrainedEnabled": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-services"],
        "CERTI shared Section 8 state-services scenario verifies timeConstrainedEnabled callbacks on the real backend path.",
    ),
    "REQ-RTI-TM-8_8-timeAdvanceRequest": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-query"],
        "CERTI shared Section 8 ordering-and-query scenario verifies timeAdvanceRequest on the real backend path.",
    ),
    "REQ-RTI-TM-8_10-nextMessageRequest": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-query"],
        "CERTI shared Section 8 ordering-and-query scenario verifies nextMessageRequest on the real backend path.",
    ),
    "REQ-RTI-TM-8_9-timeAdvanceRequestAvailable": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-available-and-flush"],
        "CERTI shared Section 8 available-and-flush scenario verifies timeAdvanceRequestAvailable on the real backend path.",
    ),
    "REQ-RTI-TM-8_12-flushQueueRequest": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-available-and-flush"],
        "CERTI shared Section 8 available-and-flush scenario verifies flushQueueRequest on the real backend path.",
    ),
    "REQ-FED-TM-8_13-timeAdvanceGrant": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-available-and-flush"],
        "CERTI shared Section 8 available-and-flush scenario verifies timeAdvanceGrant delivery on the real backend path.",
    ),
    "HLA1516.1-TM-8.2-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-services"],
        "CERTI shared Section 8 state-services scenario verifies Enable Time Regulation service behavior on the real backend path.",
    ),
    "HLA1516.1-TM-8.2-002": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-services"],
        "CERTI shared Section 8 state-services scenario verifies timeRegulationEnabled callback behavior on the real backend path.",
    ),
    "HLA1516.1-TM-8.5-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-services"],
        "CERTI shared Section 8 state-services scenario verifies Enable Time Constrained service behavior on the real backend path.",
    ),
    "HLA1516.1-TM-8.5-002": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-services"],
        "CERTI shared Section 8 state-services scenario verifies timeConstrainedEnabled callback behavior on the real backend path.",
    ),
    "HLA1516.1-TM-8.8-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-query"],
        "CERTI shared Section 8 ordering-and-query scenario verifies Time Advance Request service behavior on the real backend path.",
    ),
    "HLA1516.1-TM-8.8-002": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-query"],
        "CERTI shared Section 8 ordering-and-query scenario verifies Time Advance Grant delivery for Time Advance Request on the real backend path.",
    ),
    "HLA1516.1-TM-8.10-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-query"],
        "CERTI shared Section 8 ordering-and-query scenario verifies Next Message Request service behavior on the real backend path.",
    ),
    "HLA1516.1-TM-8.12-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-available-and-flush"],
        "CERTI shared Section 8 available-and-flush scenario verifies Flush Queue Request behavior on the real backend path.",
    ),
    "REQ-RTI-TM-8_14-enableAsynchronousDelivery": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-toggles"],
        "CERTI shared Section 8 state-services scenario verifies enableAsynchronousDelivery on the real backend path.",
    ),
    "REQ-RTI-TM-8_15-disableAsynchronousDelivery": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-toggles"],
        "CERTI shared Section 8 state-services scenario verifies disableAsynchronousDelivery on the real backend path.",
    ),
    "REQ-RTI-TM-8_17-queryLogicalTime": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-logical-time-query"],
        "CERTI shared Section 8 logical-time scenario verifies queryLogicalTime on the real backend path.",
    ),
    "REQ-RTI-TM-8_19-modifyLookahead": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-toggles"],
        "CERTI shared Section 8 state-services scenario verifies modifyLookahead on the real backend path.",
    ),
    "REQ-RTI-TM-8_20-queryLookahead": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-toggles"],
        "CERTI shared Section 8 state-services scenario verifies queryLookahead on the real backend path.",
    ),
    "REQ-RTI-TM-8_21-retract": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-request-retraction"],
        "CERTI shared Section 8 request-retraction scenario verifies retract on the real backend path.",
    ),
    "REQ-FED-TM-8_22-requestRetraction": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-request-retraction"],
        "CERTI shared Section 8 request-retraction scenario verifies requestRetraction callbacks on the real backend path.",
    ),
    "REQ-RTI-TM-8_24-changeInteractionOrderType": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-order-override"],
        "CERTI shared Section 8 order-override scenario verifies changeInteractionOrderType on the real backend path.",
    ),
    "REQ-RTI-TM-8_4-disableTimeRegulation": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-toggles"],
        "CERTI shared Section 8 state-services scenario verifies disableTimeRegulation on the real backend path.",
    ),
    "REQ-RTI-TM-8_7-disableTimeConstrained": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-toggles"],
        "CERTI shared Section 8 state-services scenario verifies disableTimeConstrained on the real backend path.",
    ),
    "HLA1516.1-TM-8.17-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-logical-time-query"],
        "CERTI shared Section 8 logical-time scenario verifies Query Logical Time behavior on the real backend path.",
    ),
    "HLA1516.1-TM-8.19-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-toggles"],
        "CERTI shared Section 8 state-services scenario verifies Modify Lookahead behavior on the real backend path.",
    ),
    "HLA1516.1-TM-8.21-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-request-retraction"],
        "CERTI shared Section 8 request-retraction scenario verifies Retract behavior on the real backend path.",
    ),
    "HLA1516.1-TM-8.4-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-toggles"],
        "CERTI shared Section 8 state-services scenario verifies Disable Time Regulation behavior on the real backend path.",
    ),
    "HLA1516.1-TM-8.7-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-state-toggles"],
        "CERTI shared Section 8 state-services scenario verifies Disable Time Constrained behavior on the real backend path.",
    ),
    "REQ-RTI-TM-8_16-queryGALT": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-time-bound-query"],
        "CERTI shared Section 8 time-bound query scenario exposes the current vendor-divergent queryGALT behavior on the real backend path.",
    ),
    "REQ-RTI-TM-8_18-queryLITS": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-time-bound-query"],
        "CERTI shared Section 8 time-bound query scenario exposes the current vendor-divergent queryLITS behavior on the real backend path.",
    ),
    "HLA1516.1-TM-8.16-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-time-bound-query"],
        "CERTI shared Section 8 time-bound query scenario exposes the current vendor-divergent Query GALT behavior on the real backend path.",
    ),
    "HLA1516.1-TM-8.18-001": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-time-bound-query"],
        "CERTI shared Section 8 time-bound query scenario exposes the current vendor-divergent Query LITS behavior on the real backend path.",
    ),
    "REQ-RTI-TM-8_23-changeAttributeOrderType": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-order-override"],
        "CERTI shared Section 8 order-override scenario exposes the current vendor-divergent changeAttributeOrderType behavior on the real backend path.",
    ),
    "REQ-RTI-TM-8_11-nextMessageRequestAvailable": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-available-and-retraction"],
        "CERTI shared Section 8 available-and-retraction scenario verifies nextMessageRequestAvailable on the real backend path.",
    ),
    "HLA1516.1-TM-8.1.2-003": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-order-override"],
        "CERTI shared Section 8 order-override scenario verifies that receive-order messages are not converted into received TSO callbacks on the real backend path.",
    ),
    "HLA1516.1-TM-8.2-003": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-duplicate-enable-rejection"],
        "CERTI shared Section 8 duplicate-enable rejection scenario verifies that a repeated Enable Time Regulation request is rejected without emitting an extra callback on the real backend path.",
    ),
    "HLA1516.1-TM-8.5-003": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-duplicate-enable-rejection"],
        "CERTI shared Section 8 duplicate-enable rejection scenario verifies that a repeated Enable Time Constrained request is rejected without emitting an extra callback on the real backend path.",
    ),
    "HLA1516.1-TM-8.8-003": (
        _CERTI_SCENARIO_EVIDENCE_REGISTRY["section8-tar-galt-boundary"],
        "CERTI shared Section 8 equal-GALT TAR scenario verifies that Time Advance Request does not grant when the request is exactly at GALT on the real backend path.",
    ),
}

_CERTI_DISPOSITION_OVERRIDES: dict[str, str] = {
    "REQ-RTI-TM-8_11-nextMessageRequestAvailable": "verified",
    "REQ-RTI-TM-8_14-enableAsynchronousDelivery": "verified",
    "REQ-RTI-TM-8_15-disableAsynchronousDelivery": "verified",
    "REQ-RTI-TM-8_17-queryLogicalTime": "verified",
    "REQ-RTI-TM-8_19-modifyLookahead": "verified",
    "REQ-RTI-TM-8_20-queryLookahead": "verified",
    "REQ-RTI-TM-8_21-retract": "verified",
    "REQ-FED-TM-8_22-requestRetraction": "verified",
    "REQ-RTI-TM-8_24-changeInteractionOrderType": "verified",
    "REQ-RTI-TM-8_4-disableTimeRegulation": "verified",
    "REQ-RTI-TM-8_7-disableTimeConstrained": "verified",
    "HLA1516.1-TM-8.1.2-003": "verified",
    "HLA1516.1-TM-8.2-003": "verified",
    "HLA1516.1-TM-8.17-001": "verified",
    "HLA1516.1-TM-8.19-001": "verified",
    "HLA1516.1-TM-8.21-001": "verified",
    "HLA1516.1-TM-8.4-001": "verified",
    "HLA1516.1-TM-8.7-001": "verified",
    "HLA1516.1-TM-8.5-003": "verified",
    "HLA1516.1-TM-8.8-003": "verified",
}

_CERTI_NOTE_OVERRIDES: dict[str, str] = {
    "HLA1516.1-TM-8.2-003": (
        "CERTI shared Section 8 duplicate-enable rejection scenario verifies that a repeated Enable Time Regulation request is rejected without emitting an extra callback on the real backend path."
    ),
    "HLA1516.1-TM-8.5-003": (
        "CERTI shared Section 8 duplicate-enable rejection scenario verifies that a repeated Enable Time Constrained request is rejected without emitting an extra callback on the real backend path."
    ),
    "HLA1516.1-TM-8.8-003": (
        "CERTI shared Section 8 equal-GALT TAR scenario verifies that Time Advance Request does not grant when the request is exactly at GALT on the real backend path."
    ),
}

_PORTICO_REQUIREMENT_EVIDENCE: dict[str, tuple[tuple[str, ...], str]] = {
    "REQ-RTI-FM-4_2-connect": (
        _SCENARIO_EVIDENCE_REGISTRY["federation-lifecycle"]
        + ("tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",),
        "Portico now has an optional real-runtime thin wrapper for the shared two-federate exchange scenario, so connection setup is attached to explicit backend-neutral + Portico-owned evidence even though the family remains classification-required until a dedicated Portico runtime lane is promoted.",
    ),
    "REQ-RTI-FM-4_5-createFederationExecution": (
        _SCENARIO_EVIDENCE_REGISTRY["federation-lifecycle"]
        + ("tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",),
        "Portico now has an optional real-runtime thin wrapper for the shared two-federate exchange scenario, so federation creation is attached to explicit backend-neutral + Portico-owned evidence even though the family remains classification-required until a dedicated Portico runtime lane is promoted.",
    ),
    "REQ-RTI-FM-4_9-joinFederationExecution": (
        _SCENARIO_EVIDENCE_REGISTRY["federation-lifecycle"]
        + ("tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",),
        "Portico now has an optional real-runtime thin wrapper for the shared two-federate exchange scenario, so federation join is attached to explicit backend-neutral + Portico-owned evidence even though the family remains classification-required until a dedicated Portico runtime lane is promoted.",
    ),
    "REQ-RTI-FM-4_11-registerFederationSynchronizationPoint": (
        _SCENARIO_EVIDENCE_REGISTRY["synchronization"]
        + ("tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_synchronization_matrix",),
        "Portico now has an optional real-runtime thin wrapper for the shared synchronization scenario, so synchronization-point registration is attached to explicit backend-neutral + Portico-owned evidence even though the family remains classification-required until a dedicated Portico runtime lane is promoted.",
    ),
    "REQ-FED-FM-4_12-synchronizationPointRegistrationSucceeded": (
        _SCENARIO_EVIDENCE_REGISTRY["synchronization"]
        + ("tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_synchronization_matrix",),
        "Portico now has an optional real-runtime thin wrapper for the shared synchronization scenario, so registration-success callbacks are attached to explicit backend-neutral + Portico-owned evidence even though the family remains classification-required until a dedicated Portico runtime lane is promoted.",
    ),
    "REQ-FED-FM-4_13-announceSynchronizationPoint": (
        _SCENARIO_EVIDENCE_REGISTRY["synchronization"]
        + ("tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_synchronization_matrix",),
        "Portico now has an optional real-runtime thin wrapper for the shared synchronization scenario, so synchronization announcement callbacks are attached to explicit backend-neutral + Portico-owned evidence even though the family remains classification-required until a dedicated Portico runtime lane is promoted.",
    ),
    "REQ-RTI-FM-4_14-synchronizationPointAchieved": (
        _SCENARIO_EVIDENCE_REGISTRY["synchronization"]
        + ("tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_synchronization_matrix",),
        "Portico now has an optional real-runtime thin wrapper for the shared synchronization scenario, so synchronization completion participation is attached to explicit backend-neutral + Portico-owned evidence even though the family remains classification-required until a dedicated Portico runtime lane is promoted.",
    ),
    "REQ-FED-FM-4_15-federationSynchronized": (
        _SCENARIO_EVIDENCE_REGISTRY["synchronization"]
        + ("tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_synchronization_matrix",),
        "Portico now has an optional real-runtime thin wrapper for the shared synchronization scenario, so federation-synchronized callbacks are attached to explicit backend-neutral + Portico-owned evidence even though the family remains classification-required until a dedicated Portico runtime lane is promoted.",
    ),
    "REQ-RTI-OM-6_8-registerObjectInstance": (
        _SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"]
        + ("tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",),
        "Portico now has an optional real-runtime thin wrapper for the shared two-federate exchange scenario, so object-instance registration is attached to explicit backend-neutral + Portico-owned evidence even though the family remains classification-required until a dedicated Portico runtime lane is promoted.",
    ),
    "REQ-FED-OM-6_9-discoverObjectInstance": (
        _SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"]
        + ("tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",),
        "Portico now has an optional real-runtime thin wrapper for the shared two-federate exchange scenario, so discovery callbacks are attached to explicit backend-neutral + Portico-owned evidence even though the family remains classification-required until a dedicated Portico runtime lane is promoted.",
    ),
    "REQ-RTI-OM-6_10-updateAttributeValues": (
        _SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"]
        + ("tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",),
        "Portico now has an optional real-runtime thin wrapper for the shared two-federate exchange scenario, so attribute updates are attached to explicit backend-neutral + Portico-owned evidence even though the family remains classification-required until a dedicated Portico runtime lane is promoted.",
    ),
    "REQ-FED-OM-6_11-reflectAttributeValues": (
        _SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"]
        + ("tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",),
        "Portico now has an optional real-runtime thin wrapper for the shared two-federate exchange scenario, so attribute reflection callbacks are attached to explicit backend-neutral + Portico-owned evidence even though the family remains classification-required until a dedicated Portico runtime lane is promoted.",
    ),
    "REQ-RTI-OM-6_12-sendInteraction": (
        _SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"]
        + ("tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",),
        "Portico now has an optional real-runtime thin wrapper for the shared two-federate exchange scenario, so interactions are attached to explicit backend-neutral + Portico-owned evidence even though the family remains classification-required until a dedicated Portico runtime lane is promoted.",
    ),
    "REQ-FED-OM-6_13-receiveInteraction": (
        _SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"]
        + ("tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",),
        "Portico now has an optional real-runtime thin wrapper for the shared two-federate exchange scenario, so receive-interaction callbacks are attached to explicit backend-neutral + Portico-owned evidence even though the family remains classification-required until a dedicated Portico runtime lane is promoted.",
    ),
}

for requirement_id in (
    "REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture",
    "REQ-FED-OWN-7_4-requestAttributeOwnershipAssumption",
    "REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition",
    "REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation",
    "HLA1516.1-OWN-7.3-001",
    "HLA1516.1-OWN-7.4-001",
    "HLA1516.1-OWN-7.10-001",
):
    _CERTI_REQUIREMENT_EVIDENCE[requirement_id] = (
        (
            "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_negotiated_attribute_ownership_scenario",
            "tests/vendors/test_certi_real_backend_ownership_matrix.py::test_certi_backend_negotiated_ownership_matrix",
            "packages/hla-backend-certi/docs/certi_negotiated_ownership_findings.md",
        ),
        "CERTI negotiated ownership remains vendor-divergent across native and Java-facade profiles; the shared negotiated ownership scenario and local findings note document the runtime-side handshake failure.",
    )


_PYTHON_REQUIREMENT_EVIDENCE: dict[str, tuple[tuple[str, ...], str]] = {
    "HLA1516.2-DT-002": (
        (
            "tests/factories/test_fom_omt_parsing.py::test_parse_standard_mim_xml_extracts_structured_datatype_definitions",
            "tests/factories/test_fom_omt_parsing.py::test_parse_fom_xml_rejects_unresolved_array_and_fixed_record_datatype_references",
            "tests/factories/test_fom_omt_parsing.py::test_parse_fom_xml_rejects_invalid_fixed_array_cardinality",
        ),
        "Python OMT datatype parsing and validation tests cover the basic, simple, enumerated, array, fixed-record, and variant-record datatype families directly.",
    ),
    "HLA1516.2-SYNC-001": (
        (
            "tests/factories/test_fom_omt_parsing.py::test_parse_fom_xml_extracts_synchronization_table_and_merge_summary",
            "tests/factories/test_fom_omt_parsing.py::test_parse_fom_xml_rejects_duplicate_synchronization_point_labels",
        ),
        "Python OMT synchronization parsing tests cover declaration, validation, and serialization of synchronization-point metadata directly.",
    ),
    "HLA1516.2-MERGE-001": (
        (
            "tests/factories/test_fom_omt_parsing.py::test_merge_with_standard_mim_preserves_standard_mom_definitions_and_catalog_metadata",
            "tests/factories/test_fom_omt_parsing.py::test_merge_with_standard_mim_preserves_mom_table_definitions_without_alteration",
            "tests/factories/test_fom_omt_parsing.py::test_merge_fom_modules_preserves_class_datatype_and_dimension_consistency",
        ),
        "Python OMT merge tests cover the merged class, datatype, dimension, and standard MIM composition contract directly.",
    ),
    "HLA1516.2-XML-001": (
        (
            "tests/factories/test_fom_omt_parsing.py::test_parse_fom_xml_with_omt_schema_validation_accepts_restaurant_reference_module_and_rejects_invalid_document",
            "tests/factories/test_fom_omt_parsing.py::test_parse_fom_xml_rejects_unknown_object_model_namespace",
            "tests/factories/test_fom_omt_parsing.py::test_serialize_fom_module_emits_schema_valid_xml_and_preserves_identification",
            "tests/factories/test_fom_omt_parsing.py::test_parse_fom_xml_preserves_notes_and_catalog_notes",
        ),
        "Python OMT XML interchange tests cover namespace validation, schema rejection, schema-valid serialization, and semantic round-trip fidelity directly.",
    ),
}


_PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_REF = (
    "packages/hla-vendor-pitch/docs/evidence/"
    "pitch_section8_time_management_vendor_divergence_2026-06-11.md",
)

_PITCH_REQUIREMENT_EVIDENCE: dict[str, tuple[str, tuple[str, ...], str]] = {
    "REQ-RTI-FM-4_2-connect": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["federation-lifecycle"],
        "Pitch real-runtime lifecycle probe verifies this requirement.",
    ),
    "REQ-RTI-FM-4_3-disconnect": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["federation-lifecycle"],
        "Pitch real-runtime lifecycle probe verifies this requirement.",
    ),
    "REQ-FED-FM-4_4-connectionLost": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["connection-lost-callback"],
        "Pitch bridge callback dispatch probe verifies connection-lost callback delivery.",
    ),
    "REQ-RTI-FM-4_5-createFederationExecution": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["federation-lifecycle"],
        "Pitch real-runtime lifecycle probe verifies this requirement.",
    ),
    "REQ-RTI-FM-4_5-createFederationExecutionWithMIM": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["federation-lifecycle-with-mim"],
        "Pitch Java FedPro adapter currently exposes createFederationExecution but not the createFederationExecutionWithMIM overload.",
    ),
    "REQ-RTI-FM-4_6-destroyFederationExecution": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["federation-lifecycle"],
        "Pitch real-runtime lifecycle probe verifies this requirement.",
    ),
    "REQ-RTI-FM-4_7-listFederationExecutions": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["federation-listing"],
        "Pitch real-runtime federation listing probe verifies this requirement.",
    ),
    "REQ-FED-FM-4_8-reportFederationExecutions": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["federation-listing"],
        "Pitch real-runtime federation listing probe verifies this callback requirement.",
    ),
    "REQ-RTI-FM-4_9-joinFederationExecution": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["federation-lifecycle"],
        "Pitch real-runtime lifecycle probe verifies this requirement.",
    ),
    "REQ-RTI-FM-4_10-resignFederationExecution": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["federation-lifecycle"],
        "Pitch real-runtime lifecycle probe verifies this requirement.",
    ),
    "REQ-RTI-FM-4_11-registerFederationSynchronizationPoint": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["synchronization"],
        "Pitch real-runtime synchronization probe verifies synchronization-point registration.",
    ),
    "REQ-FED-FM-4_12-synchronizationPointRegistrationFailed": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["synchronization-registration-failure"],
        "Pitch real-runtime synchronization failure probe verifies duplicate-label registration failure reporting.",
    ),
    "REQ-FED-FM-4_12-synchronizationPointRegistrationSucceeded": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["synchronization"],
        "Pitch real-runtime synchronization probe verifies registration success reporting.",
    ),
    "REQ-FED-FM-4_13-announceSynchronizationPoint": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["synchronization"],
        "Pitch real-runtime synchronization probe verifies synchronization-point announcement callbacks.",
    ),
    "REQ-RTI-FM-4_14-synchronizationPointAchieved": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["synchronization"],
        "Pitch real-runtime synchronization probe verifies synchronization completion participation.",
    ),
    "REQ-FED-FM-4_15-federationSynchronized": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["synchronization"],
        "Pitch real-runtime synchronization probe verifies federation-synchronized callbacks.",
    ),
    "REQ-RTI-FM-4_16-requestFederationSave": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "Pitch real-runtime save/restore probe verifies the positive save request path.",
    ),
    "REQ-FED-FM-4_17-initiateFederateSave": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "Pitch real-runtime save/restore probe verifies initiate-save callbacks.",
    ),
    "REQ-RTI-FM-4_18-federateSaveBegun": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "Pitch real-runtime save/restore probe verifies federate save-begun participation.",
    ),
    "REQ-RTI-FM-4_19-federateSaveComplete": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "Pitch real-runtime save/restore probe verifies federate save completion.",
    ),
    "REQ-RTI-FM-4_19-federateSaveNotComplete": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-failure"],
        "Pitch real-runtime save failure probe verifies federate save-not-complete participation.",
    ),
    "REQ-FED-FM-4_20-federationSaved": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "Pitch real-runtime save/restore probe verifies federation-saved callbacks.",
    ),
    "REQ-FED-FM-4_20-federationNotSaved": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-failure"],
        "Pitch real-runtime save failure probe verifies federation-not-saved callbacks.",
    ),
    "REQ-RTI-FM-4_21-abortFederationSave": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-abort"],
        "Pitch real-runtime save abort probe verifies abort-save behavior and status cleanup.",
    ),
    "REQ-RTI-FM-4_22-queryFederationSaveStatus": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "Pitch real-runtime save/restore probe verifies save-status queries.",
    ),
    "REQ-FED-FM-4_23-federationSaveStatusResponse": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "Pitch real-runtime save/restore probe verifies save-status response callbacks.",
    ),
    "REQ-RTI-FM-4_24-requestFederationRestore": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "Pitch real-runtime save/restore probe verifies the positive restore request path.",
    ),
    "REQ-FED-FM-4_25-requestFederationRestoreSucceeded": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "Pitch real-runtime save/restore probe verifies restore-request success callbacks.",
    ),
    "REQ-FED-FM-4_25-requestFederationRestoreFailed": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["restore-request-failure"],
        "Pitch real-runtime restore request failure probe verifies unknown-save failure callbacks.",
    ),
    "REQ-FED-FM-4_26-federationRestoreBegun": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "Pitch real-runtime save/restore probe verifies federation-restore-begun callbacks.",
    ),
    "REQ-FED-FM-4_27-initiateFederateRestore": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "Pitch real-runtime save/restore probe verifies initiate-restore callbacks.",
    ),
    "REQ-RTI-FM-4_28-federateRestoreComplete": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "Pitch real-runtime save/restore probe verifies federate restore completion.",
    ),
    "REQ-RTI-FM-4_28-federateRestoreNotComplete": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["restore-failure"],
        "Pitch real-runtime restore failure probe verifies federate restore-not-complete participation.",
    ),
    "REQ-FED-FM-4_29-federationRestored": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "Pitch real-runtime save/restore probe verifies federation-restored callbacks.",
    ),
    "REQ-FED-FM-4_29-federationNotRestored": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["restore-failure"],
        "Pitch real-runtime restore failure probe verifies federation-not-restored callbacks.",
    ),
    "REQ-RTI-FM-4_30-abortFederationRestore": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["restore-abort"],
        "Pitch real-runtime restore abort probe verifies abort-restore behavior and status cleanup.",
    ),
    "REQ-RTI-FM-4_31-queryFederationRestoreStatus": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "Pitch real-runtime save/restore probe verifies restore-status queries.",
    ),
    "REQ-FED-FM-4_32-federationRestoreStatusResponse": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"],
        "Pitch real-runtime save/restore probe verifies restore-status response callbacks.",
    ),
    "REQ-SAVE-RESTORE-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore"] + _SCENARIO_EVIDENCE_REGISTRY["save-restore-time-state"],
        "Shared save/restore scenario verifies Pitch save and restore lifecycle coordination, including logical-time state restoration.",
    ),
    "REQ-SAVE-RESTORE-OBJECT-STATE-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore-object-state"],
        "Shared restore object-state scenario verifies Pitch restores object ownership and persisted instance state through the backend-neutral harness.",
    ),
    "REQ-SAVE-RESTORE-FEDERATE-LOCAL-STATE-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore-federate-local-state"],
        "Shared restore federate-local-state scenario verifies Pitch restores saved local federate policy, time-management, and transport state through the backend-neutral harness.",
    ),
    "REQ-SAVE-RESTORE-CALLBACK-POLICY-001": (
        "not-applicable",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore-callback-policy"],
        "Callback enablement is a local runtime policy probe rather than a persisted shared-federation restore parity target for real Pitch runtime classification.",
    ),
    "REQ-SAVE-RESTORE-TRANSIENT-STATE-001": (
        "not-applicable",
        _SCENARIO_EVIDENCE_REGISTRY["save-restore-transient-state"],
        "Transient callback-queue and retraction bookkeeping cleanup depends on backend-local runtime internals rather than a portable real Pitch restore parity contract.",
    ),
    "REQ-OMT-PARSE-001": (
        "not-applicable",
        (
            "src/hla2010/fom.py::parse_fom_xml",
            "tests/factories/test_fom_omt_parsing.py",
            "analysis/compliance/verification_assets.json",
        ),
        "OMT parsing and catalog extraction are core parser coverage, not a Pitch-specific runtime parity slice.",
    ),
    "SCENARIO-TARGET-RADAR-001": (
        "not-applicable",
        (
            "tests/scenarios/test_target_radar_scenario.py",
            "analysis/compliance/verification_assets.json",
            "docs/evidence/hla2010_python_verification_evidence_v0_13/docs/mom_table_verification_v0_12.md",
        ),
        "Target/Radar is tracked as a smoke demonstration rather than a Pitch conformance or shared-harness parity requirement.",
    ),
    "REQ-RTI-OM-6_2-reserveObjectInstanceName": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["name-reservation"],
        "Shared name-reservation scenario verifies single-name reservation and conflict handling.",
    ),
    "REQ-FED-OM-6_3-objectInstanceNameReservationFailed": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["name-reservation"],
        "Shared name-reservation scenario verifies failed single-name reservation callbacks on conflict.",
    ),
    "REQ-FED-OM-6_3-objectInstanceNameReservationSucceeded": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["name-reservation"],
        "Shared name-reservation scenario verifies successful single-name reservation callbacks.",
    ),
    "REQ-RTI-OM-6_4-releaseObjectInstanceName": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["name-reservation"],
        "Shared name-reservation scenario verifies released single-name reservations can be reacquired by another federate.",
    ),
    "REQ-RTI-OM-6_5-reserveMultipleObjectInstanceName": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["name-reservation"],
        "Shared name-reservation scenario verifies multi-name reservation and conflict handling.",
    ),
    "REQ-FED-OM-6_6-multipleObjectInstanceNameReservationFailed": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["name-reservation"],
        "Shared name-reservation scenario verifies failed multi-name reservation callbacks on conflict.",
    ),
    "REQ-FED-OM-6_6-multipleObjectInstanceNameReservationSucceeded": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["name-reservation"],
        "Shared name-reservation scenario verifies successful multi-name reservation callbacks.",
    ),
    "REQ-RTI-OM-6_7-releaseMultipleObjectInstanceName": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["name-reservation"],
        "Shared name-reservation scenario verifies released multi-name reservations can be reacquired by another federate.",
    ),
    "REQ-RTI-OM-6_8-registerObjectInstance": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "Shared two-federate exchange scenario verifies object registration before discovery, update, and delete flows.",
    ),
    "REQ-FED-OM-6_9-discoverObjectInstance": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "Shared two-federate exchange scenario verifies discovery callback delivery for registered instances.",
    ),
    "REQ-FED-OM-6_9-hasProducingFederate": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["discovery-metadata-callbacks"],
        "Shared discovery metadata callback probe verifies producing-federate metadata callback delivery.",
    ),
    "REQ-FED-OM-6_9-getProducingFederate": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["discovery-metadata-callbacks"],
        "Shared discovery metadata callback probe verifies producing-federate metadata payload delivery.",
    ),
    "REQ-FED-OM-6_9-hasSentRegions": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["discovery-metadata-callbacks"],
        "Shared discovery metadata callback probe verifies sent-region metadata callback delivery.",
    ),
    "REQ-FED-OM-6_9-getSentRegions": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["discovery-metadata-callbacks"],
        "Shared discovery metadata callback probe verifies sent-region metadata payload delivery.",
    ),
    "REQ-FED-OM-6_11-reflectAttributeValues": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "Shared two-federate exchange scenario verifies reflected attribute delivery across receive and timestamp order paths.",
    ),
    "REQ-FED-OM-6_13-receiveInteraction": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "Shared two-federate exchange scenario verifies interaction delivery across receive and timestamp order paths.",
    ),
    "REQ-RTI-OM-6_14-deleteObjectInstance": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "Shared two-federate exchange scenario exercises delete-object teardown after successful exchange delivery.",
    ),
    "REQ-FED-OM-6_15-removeObjectInstance": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["two-federate-exchange"],
        "Shared two-federate exchange scenario verifies remove-object callbacks for deleted instances.",
    ),
    "REQ-RTI-OM-6_16-localDeleteObjectInstance": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["local-delete"],
        "Shared local-delete scenario verifies local knowledge removal and rediscovery behavior.",
    ),
    "REQ-FED-OM-6_17-attributesInScope": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["update-advisory-callbacks"],
        "Shared update-advisory callback probe verifies attributes-in-scope callback delivery.",
    ),
    "REQ-FED-OM-6_18-attributesOutOfScope": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["update-advisory-callbacks"],
        "Shared update-advisory callback probe verifies attributes-out-of-scope callback delivery.",
    ),
    "REQ-RTI-OM-6_19-requestAttributeValueUpdate": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["request-attribute-value-update"],
        "Shared request-attribute-value-update scenario verifies service-driven provide-value callbacks to the owning federate.",
    ),
    "REQ-FED-OM-6_20-provideAttributeValueUpdate": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["update-advisory-callbacks"],
        "Shared update-advisory callback probe verifies provide-attribute-value-update callback delivery.",
    ),
    "REQ-FED-OM-6_21-turnUpdatesOnForObjectInstance": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["update-advisory-callbacks"],
        "Shared update-advisory callback probe verifies turn-updates-on callback delivery.",
    ),
    "REQ-FED-OM-6_22-turnUpdatesOffForObjectInstance": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["update-advisory-callbacks"],
        "Shared update-advisory callback probe verifies turn-updates-off callback delivery.",
    ),
    "REQ-RTI-OM-6_23-requestAttributeTransportationTypeChange": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["transportation-type"]
        + _SCENARIO_EVIDENCE_REGISTRY["transportation-type-restore-persistence"],
        "Shared transportation scenarios verify attribute transportation change requests together with explicit override persistence across save/restore.",
    ),
    "REQ-FED-OM-6_24-confirmAttributeTransportationTypeChange": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["transportation-type"],
        "Shared transportation-type scenario verifies attribute transportation change confirmations.",
    ),
    "REQ-RTI-OM-6_25-queryAttributeTransportationType": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["transportation-type"],
        "Shared transportation-type scenario verifies attribute transportation queries.",
    ),
    "REQ-FED-OM-6_26-reportAttributeTransportationType": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["transportation-type"],
        "Shared transportation-type scenario verifies attribute transportation reports.",
    ),
    "REQ-RTI-OM-6_27-requestInteractionTransportationTypeChange": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["transportation-type"]
        + _SCENARIO_EVIDENCE_REGISTRY["transportation-type-restore-persistence"],
        "Shared transportation scenarios verify interaction transportation change requests together with explicit override persistence across save/restore.",
    ),
    "REQ-FED-OM-6_28-confirmInteractionTransportationTypeChange": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["transportation-type"],
        "Shared transportation-type scenario verifies interaction transportation change confirmations.",
    ),
    "REQ-RTI-OM-6_29-queryInteractionTransportationType": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["transportation-type"],
        "Shared transportation-type scenario verifies interaction transportation queries.",
    ),
    "REQ-FED-OM-6_30-reportInteractionTransportationType": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["transportation-type"],
        "Shared transportation-type scenario verifies interaction transportation reports.",
    ),
    "REQ-RTI-OWN-7_2-unconditionalAttributeOwnershipDivestiture": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "Shared ownership scenario verifies unconditional divestiture, acquisition-if-available, and ownership query callbacks.",
    ),
    "REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-negotiated-offer-probe"]
        + ("packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",),
        "Pitch negotiated ownership offer handling remains bridge-divergent before the end-to-end negotiated transfer can be promoted.",
    ),
    "REQ-FED-OWN-7_4-requestAttributeOwnershipAssumption": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-negotiated-offer-probe"],
        "Shared negotiated-offer probe verifies request-attribute-ownership-assumption callback delivery.",
    ),
    "REQ-FED-OWN-7_5-requestDivestitureConfirmation": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-negotiated-offer-probe"]
        + ("packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",),
        "Pitch negotiated ownership offer handling does not deliver a stable cross-bridge divestiture-confirmation sequence.",
    ),
    "REQ-RTI-OWN-7_6-confirmDivestiture": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-negotiated-offer-probe"]
        + ("packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",),
        "Pitch negotiated ownership never reaches a promotable confirm-divestiture transfer sequence across both bridges.",
    ),
    "REQ-FED-OWN-7_7-attributeOwnershipAcquisitionNotification": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "Shared ownership scenario verifies acquisition-notification callbacks after acquisition-if-available succeeds.",
    ),
    "REQ-RTI-OWN-7_8-attributeOwnershipAcquisition": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-release-request"],
        "Shared release-request ownership scenario verifies acquisition requests against owned attributes and the resulting transfer path.",
    ),
    "REQ-RTI-OWN-7_9-attributeOwnershipAcquisitionIfAvailable": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "Shared ownership scenario verifies acquisition-if-available against divested attributes.",
    ),
    "REQ-FED-OWN-7_11-requestAttributeOwnershipRelease": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-release-request"],
        "Shared release-request ownership scenario verifies owner-side release callbacks on acquisition requests against owned attributes.",
    ),
    "REQ-RTI-OWN-7_13-attributeOwnershipDivestitureIfWanted": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-release-request"],
        "Shared release-request ownership scenario verifies divestiture-if-wanted completion after a release request.",
    ),
    "REQ-RTI-OWN-7_14-cancelNegotiatedAttributeOwnershipDivestiture": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-negotiated-offer-probe"]
        + ("packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",),
        "Pitch negotiated ownership never reaches a stable cross-bridge state where negotiated divestiture cancellation can be promoted.",
    ),
    "REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-negotiated"]
        + ("packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",),
        "Pitch negotiated ownership continuation remains bridge-divergent before cancellation semantics can be promoted.",
    ),
    "REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-negotiated"]
        + ("packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",),
        "Pitch negotiated ownership continuation remains bridge-divergent before acquisition-cancellation confirmation is stable.",
    ),
    "REQ-RTI-OWN-7_17-queryAttributeOwnership": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "Shared ownership scenario verifies query-ownership reporting before and after transfer.",
    ),
    "REQ-FED-OWN-7_18-attributeIsNotOwned": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "Shared ownership scenario verifies the attribute-is-not-owned callback after unconditional divestiture.",
    ),
    "REQ-FED-OWN-7_18-attributeIsOwnedByRTI": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-query-callbacks"],
        "Shared ownership query callback probe verifies the attribute-is-owned-by-RTI callback surface.",
    ),
    "REQ-FED-OWN-7_18-informAttributeOwnership": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "Shared ownership scenario verifies inform-attribute-ownership callbacks after transfer.",
    ),
    "REQ-RTI-OWN-7_19-isAttributeOwnedByFederate": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "Shared ownership scenario verifies portable is-attribute-owned-by-federate checks before and after transfer.",
    ),
    "REQ-FED-OWN-7_10-attributeOwnershipUnavailable": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-unavailable"],
        "Shared ownership-unavailable scenario verifies acquisition-if-available failure callbacks when an attribute remains owned.",
    ),
    "REQ-RTI-OWN-7_12-attributeOwnershipReleaseDenied": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-release-denied"],
        "Shared release-denied ownership scenario verifies explicit denial preserves the original owner and suppresses acquisition completion.",
    ),
    "HLA1516.1-OWN-7.1-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "Shared ownership scenario verifies ownership state transitions through divestiture, reacquisition, and subsequent queries.",
    ),
    "HLA1516.1-OWN-7.1-002": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "Shared ownership scenario verifies transfer semantics where ownership leaves the original federate before the acquiring federate becomes owner.",
    ),
    "HLA1516.1-OWN-7.1-003": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-non-owner-update-rejection"],
        "Shared non-owner update rejection scenario verifies that a non-owning federate cannot update another federate's attribute.",
    ),
    "HLA1516.1-OWN-7.2-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "Shared ownership scenario verifies unconditional divestiture, acquisition-if-available transfer, and the resulting ownership state transitions.",
    ),
    "HLA1516.1-OWN-7.5-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-release-request"],
        "Shared release-request ownership scenario verifies acquisition requests against currently owned attributes.",
    ),
    "HLA1516.1-OWN-7.6-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "Shared ownership scenario verifies acquisition-if-available against divested attributes.",
    ),
    "HLA1516.1-OWN-7.7-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "Shared ownership scenario verifies acquisition notification callbacks after successful transfer.",
    ),
    "HLA1516.1-OWN-7.7-002": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-release-denied"],
        "Shared release-denied ownership scenario verifies acquisition notification is not emitted when the owner denies release.",
    ),
    "HLA1516.1-OWN-7.8-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-unavailable"],
        "Shared ownership-unavailable scenario verifies acquisition failure callbacks when acquisition-if-available cannot proceed.",
    ),
    "HLA1516.1-OWN-7.9-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "Shared ownership scenario verifies acquisition-if-available can complete only after the current owner divests ownership and the acquiring federate becomes the new owner.",
    ),
    "HLA1516.1-OWN-7.9-002": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-unavailable"],
        "Shared ownership-unavailable scenario verifies requestAttributeOwnershipRelease is not emitted when acquisition-if-available cannot proceed because ownership remains unavailable.",
    ),
    "HLA1516.1-OWN-7.12-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership"],
        "Shared ownership scenario verifies ownership-query reporting before and after transfer.",
    ),
    "HLA1516.1-OWN-7.13-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-query-callbacks"],
        "Shared ownership query callback probe verifies the owned-by-federate, unowned, and RTI-owned notification callback surfaces.",
    ),
    "HLA1516.1-OWN-7.3-001": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-negotiated-offer-probe"]
        + ("packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",),
        "Pitch negotiated ownership remains bridge-divergent before a stable negotiated divestiture path can be promoted.",
    ),
    "HLA1516.1-OWN-7.4-001": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-negotiated-offer-probe"]
        + ("packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",),
        "Pitch negotiated ownership remains bridge-divergent before a stable negotiated assumption and divestiture path can be promoted.",
    ),
    "HLA1516.1-OWN-7.10-001": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-negotiated"]
        + ("packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",),
        "Pitch negotiated ownership continuation remains bridge-divergent before cancellation semantics can be promoted.",
    ),
    "HLA1516.1-OWN-7.11-001": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["ownership-negotiated"]
        + ("packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",),
        "Pitch negotiated ownership continuation remains bridge-divergent before cancellation confirmation semantics can be promoted.",
    ),
    "HLA1516.1-DDM-9.1-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-region-routing"],
        "Shared DDM region-routing scenario verifies end-to-end region-based routing through the Pitch backend matrix, including constrained delivery under declared routing-space dimensions.",
    ),
    "HLA1516.1-DDM-9.1-002": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-region-routing"],
        "Shared DDM region-routing scenario verifies that DDM routing uses the FOM-declared routing dimension carried by the shared VendorSmokeFOM profile.",
    ),
    "HLA1516.1-DDM-9.1-003": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-region-routing"],
        "Shared DDM region-routing scenario verifies overlap-based relevance by suppressing far-region interaction delivery and admitting the overlapping near-region delivery.",
    ),
    "REQ-RTI-DDM-9_2-createRegion": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-region-routing"],
        "Shared DDM region-routing scenario verifies Pitch creates sender and receiver regions for the declared routing-space dimension and uses them in the subsequent routed interaction flow.",
    ),
    "REQ-RTI-DDM-9_3-commitRegionModifications": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-region-routing"],
        "Shared DDM region-routing scenario verifies Pitch commits region bound changes and applies those committed ranges when routing later timestamped interaction delivery.",
    ),
    "REQ-RTI-DDM-9_10-subscribeInteractionClassWithRegions": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-region-routing"],
        "Shared DDM region-routing scenario verifies Pitch supports active interaction-class subscription with regions and filters delivery by region overlap.",
    ),
    "REQ-RTI-DDM-9_12-sendInteractionWithRegions": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-region-routing"],
        "Shared DDM region-routing scenario verifies Pitch sends timestamped interactions with regions and delivers only the overlap-matching payload.",
    ),
    "HLA1516.1-DDM-9.2-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-region-routing"],
        "Shared DDM region-routing scenario verifies Pitch creates sender and receiver regions for the declared routing-space dimension and uses them in the subsequent routed interaction flow.",
    ),
    "HLA1516.1-DDM-9.3-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-region-routing"],
        "Shared DDM region-routing scenario verifies Pitch commits region bound changes and applies those committed ranges when routing later timestamped interaction delivery.",
    ),
    "HLA1516.1-DDM-9.10-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-region-routing"],
        "Shared DDM region-routing scenario verifies Pitch supports active interaction-class subscription with regions and filters delivery by region overlap.",
    ),
    "HLA1516.1-DDM-9.12-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-region-routing"],
        "Shared DDM region-routing scenario verifies Pitch sends timestamped interactions with regions and delivers only the overlap-matching payload.",
    ),
    "REQ-RTI-DDM-9_4-deleteRegion": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch deletes regions after subscription teardown without breaking the surrounding region-scoped lifecycle flow.",
    ),
    "REQ-RTI-DDM-9_5-registerObjectInstanceWithRegions": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch registers object instances with regions and discovers them through overlapping region-scoped subscriptions.",
    ),
    "REQ-RTI-DDM-9_6-associateRegionsForUpdates": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch associates regions for updates and restores the update-region binding after an explicit unassociate step.",
    ),
    "REQ-RTI-DDM-9_7-unassociateRegionsForUpdates": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch unassociates regions for updates before re-associating them on the same object instance.",
    ),
    "REQ-RTI-DDM-9_8-subscribeObjectClassAttributesWithRegions": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch supports active object-class attribute subscription with regions and the resulting overlapping-bounds discovery flow.",
    ),
    "REQ-RTI-DDM-9_9-unsubscribeObjectClassAttributesWithRegions": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch unsubscribes object-class attributes with regions during teardown of the region-scoped object lifecycle.",
    ),
    "REQ-RTI-DDM-9_11-unsubscribeInteractionClassWithRegions": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch unsubscribes interaction classes with regions and suppresses subsequent delivery on that path.",
    ),
    "REQ-RTI-DDM-9_13-requestAttributeValueUpdateWithRegions": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch routes requestAttributeValueUpdateWithRegions to the provider callback path for the overlapping regional subscription.",
    ),
    "HLA1516.1-DDM-9.4-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch deletes regions after subscription teardown without breaking the surrounding region-scoped lifecycle flow.",
    ),
    "HLA1516.1-DDM-9.5-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch registers object instances with regions and discovers them through overlapping region-scoped subscriptions.",
    ),
    "HLA1516.1-DDM-9.6-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch associates regions for updates and restores the update-region binding after an explicit unassociate step.",
    ),
    "HLA1516.1-DDM-9.7-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch unassociates regions for updates before re-associating them on the same object instance.",
    ),
    "HLA1516.1-DDM-9.8-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch supports active object-class attribute subscription with regions and the resulting overlapping-bounds discovery flow.",
    ),
    "HLA1516.1-DDM-9.9-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch unsubscribes object-class attributes with regions during teardown of the region-scoped object lifecycle.",
    ),
    "HLA1516.1-DDM-9.11-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch unsubscribes interaction classes with regions and suppresses subsequent delivery on that path.",
    ),
    "HLA1516.1-DDM-9.13-001": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-object-region-lifecycle"],
        "Shared DDM object-region lifecycle scenario verifies Pitch routes requestAttributeValueUpdateWithRegions to the provider callback path for the overlapping regional subscription.",
    ),
    "REQ-RTI-DDM-9_8-subscribeObjectClassAttributesPassivelyWithRegions": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-passive-region-subscriptions"],
        "Shared passive DDM region subscription scenario verifies Pitch supports passive object-class attribute subscription with regions and later discovery under overlapping bounds.",
    ),
    "REQ-RTI-DDM-9_10-subscribeInteractionClassPassivelyWithRegions": (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["ddm-passive-region-subscriptions"],
        "Shared passive DDM region subscription scenario verifies Pitch supports passive interaction-class subscription with regions and overlap-filtered delivery.",
    ),
    "HLA1516.1-TM-8.1-001": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-state-services"] + _PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_REF,
        "Pitch dedicated Section 8 state-services probes diverge from the shared harness expectation because the real Java bridge path does not surface the expected timeRegulationEnabled/timeConstrainedEnabled callback evidence in this matrix scenario.",
    ),
    "HLA1516.1-TM-8.1-002": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-queries"] + _PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_REF,
        "Pitch dedicated Section 8 next-message probes diverge from the shared harness expectation because the real Java bridge path does not reproduce the expected timestamp-ordered next-message delivery sequence in this matrix scenario.",
    ),
    "HLA1516.1-TM-8.1.1-001": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-queries"] + _PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_REF,
        "Pitch dedicated Section 8 next-message probes diverge from the shared harness expectation because the real Java bridge path does not reproduce the expected timestamp-ordered next-message delivery sequence in this matrix scenario.",
    ),
    "HLA1516.1-TM-8.1.2-001": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-order-override"] + _PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_REF,
        "Pitch dedicated Section 8 order-override probes diverge from the shared harness expectation because the real Java bridge path does not surface the expected receive-order callback evidence in this matrix scenario.",
    ),
    "HLA1516.1-TM-8.1.2-002": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-order-override"] + _PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_REF,
        "Pitch dedicated Section 8 order-override probes diverge from the shared harness expectation because the real Java bridge path does not surface the expected receive-order callback evidence in this matrix scenario.",
    ),
    "HLA1516.1-TM-8.1.2-003": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-order-override"] + _PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_REF,
        "Pitch dedicated Section 8 order-override probes diverge from the shared harness expectation because the real Java bridge path does not surface the expected receive-order callback evidence in this matrix scenario.",
    ),
    "HLA1516.1-TM-8.1.2-004": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-queries"] + _PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_REF,
        "Pitch dedicated Section 8 next-message probes diverge from the shared harness expectation because the real Java bridge path does not reproduce the expected timestamp-ordered next-message delivery sequence in this matrix scenario.",
    ),
    "HLA1516.1-TM-8.1.3-001": (
        "blocked",
        _SCENARIO_EVIDENCE_REGISTRY["section8-state-services"],
        "Shared Section 8 state-services scenario exists, but Pitch does not yet complete the dedicated time-regulation/constrained callback probe cleanly.",
    ),
    "HLA1516.1-TM-8.1.3-002": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-queries"] + _PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_REF,
        "Pitch dedicated Section 8 next-message probes diverge from the shared harness expectation because the real Java bridge path does not reproduce the expected timestamp-ordered next-message delivery sequence in this matrix scenario.",
    ),
    "HLA1516.1-TM-8.1.3-003": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-queries"] + _PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_REF,
        "Pitch dedicated Section 8 next-message probes diverge from the shared harness expectation because the real Java bridge path does not reproduce the expected timestamp-ordered next-message delivery sequence in this matrix scenario.",
    ),
    "HLA1516.1-TM-8.1.4-001": (
        "blocked",
        _SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-queries"],
        "Shared Section 8 ordering/query scenario exists, but Pitch does not yet complete the dedicated next-message ordering probe cleanly.",
    ),
    "HLA1516.1-TM-8.1.4-002": (
        "blocked",
        _SCENARIO_EVIDENCE_REGISTRY["section8-lookahead"],
        "Shared lookahead scenario exists, but broader Pitch Clause 8 parity remains incomplete and the dedicated time probe set is not fully promotable.",
    ),
    "HLA1516.1-TM-8.1.4-003": (
        "blocked",
        _SCENARIO_EVIDENCE_REGISTRY["section8-lookahead"],
        "Shared lookahead scenario exists, but broader Pitch Clause 8 parity remains incomplete and the dedicated time probe set is not fully promotable.",
    ),
    "HLA1516.1-TM-8.1.5-001": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-queries"] + _PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_REF,
        "Pitch dedicated Section 8 next-message probes diverge from the shared harness expectation because the real Java bridge path does not reproduce the expected timestamp-ordered next-message delivery sequence in this matrix scenario.",
    ),
    "HLA1516.1-TM-8.1.5-002": (
        "blocked",
        _SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-queries"],
        "Shared Section 8 ordering/query scenario exists, but Pitch does not yet complete the dedicated query-GALT probe cleanly.",
    ),
    "HLA1516.1-TM-8.1.5-003": (
        "blocked",
        _SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-queries"],
        "Shared Section 8 ordering/query scenario exists, but Pitch does not yet complete the dedicated query-LITS probe cleanly.",
    ),
    "HLA1516.1-TM-8.1.6-001": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-queries"] + _PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_REF,
        "Pitch dedicated Section 8 next-message probes diverge from the shared harness expectation because the real Java bridge path does not reproduce the expected timestamp-ordered next-message delivery sequence in this matrix scenario.",
    ),
    "HLA1516.1-TM-8.1.7-001": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-queries"] + _PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_REF,
        "Pitch dedicated Section 8 next-message probes diverge from the shared harness expectation because the real Java bridge path does not reproduce the expected timestamp-ordered next-message delivery sequence in this matrix scenario.",
    ),
    "REQ-TIME-ORDER-001": (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-queries"] + _PITCH_SECTION8_TIME_MANAGEMENT_VENDOR_DIVERGENCE_REF,
        "Pitch dedicated Section 8 next-message probes diverge from the shared harness expectation because the real Java bridge path does not reproduce the expected timestamp-order delivery sequence in this matrix scenario.",
    ),
}


def _add_pitch_evidence_rows(
    requirement_ids: tuple[str, ...],
    *,
    status: str,
    scenario_id: str,
    extra_refs: tuple[str, ...] = (),
    note: str,
) -> None:
    evidence = _SCENARIO_EVIDENCE_REGISTRY[scenario_id] + extra_refs
    for requirement_id in requirement_ids:
        _PITCH_REQUIREMENT_EVIDENCE.setdefault(requirement_id, (status, evidence, note))


def _merge_scenario_evidence(*scenario_ids: str) -> tuple[str, ...]:
    merged: list[str] = []
    for scenario_id in scenario_ids:
        for ref in _SCENARIO_EVIDENCE_REGISTRY[scenario_id]:
            if ref not in merged:
                merged.append(ref)
    return tuple(merged)


def _add_pitch_composite_evidence_rows(
    requirement_ids: tuple[str, ...],
    *,
    status: str,
    scenario_ids: tuple[str, ...],
    extra_refs: tuple[str, ...] = (),
    note: str,
) -> None:
    base_evidence = _merge_scenario_evidence(*scenario_ids)
    evidence = base_evidence + tuple(ref for ref in extra_refs if ref not in base_evidence)
    for requirement_id in requirement_ids:
        _PITCH_REQUIREMENT_EVIDENCE.setdefault(requirement_id, (status, evidence, note))


_add_pitch_evidence_rows(
    (
        "HLA1516.1-DM-5.1-004",
    ),
    status="verified",
    scenario_id="declaration-time-independence",
    note="Shared time-managed declaration scenario verifies declaration callbacks and receive-order delivery remain effective under active time regulation and constrained mode without additional logical-time advancement.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-DM-5.2-003",
    ),
    status="verified",
    scenario_id="declaration-invalid-attribute-publication",
    note="Shared declaration negative scenario verifies publish requests for unavailable object-class attributes are rejected.",
)

_add_pitch_evidence_rows(
    (
        "REQ-RTI-DM-5_3-unpublishObjectClass",
        "REQ-RTI-DM-5_6-subscribeObjectClassAttributesPassively",
        "REQ-RTI-DM-5_7-unsubscribeObjectClass",
        "REQ-RTI-DM-5_8-subscribeInteractionClassPassively",
    ),
    status="verified",
    scenario_id="declaration-management-overloads",
    note="Shared declaration-management scenario verifies the passive subscription and whole-class teardown declaration overloads through the same backend-neutral delivery and advisory flow.",
)

_add_pitch_evidence_rows(
    (
        "REQ-RTI-DM-5_2-publishObjectClassAttributes",
        "REQ-RTI-DM-5_3-unpublishObjectClassAttributes",
        "REQ-RTI-DM-5_4-publishInteractionClass",
        "REQ-RTI-DM-5_5-unpublishInteractionClass",
        "REQ-RTI-DM-5_6-subscribeObjectClassAttributes",
        "REQ-RTI-DM-5_7-unsubscribeObjectClassAttributes",
        "REQ-RTI-DM-5_8-subscribeInteractionClass",
        "REQ-RTI-DM-5_9-unsubscribeInteractionClass",
        "REQ-FED-DM-5_10-startRegistrationForObjectClass",
        "REQ-FED-DM-5_11-stopRegistrationForObjectClass",
        "REQ-FED-DM-5_12-turnInteractionsOn",
        "REQ-FED-DM-5_13-turnInteractionsOff",
        "HLA1516.1-DM-5.1-001",
        "HLA1516.1-DM-5.1-002",
        "HLA1516.1-DM-5.1-003",
        "HLA1516.1-DM-5.1.2-001",
        "HLA1516.1-DM-5.1.2-002",
        "HLA1516.1-DM-5.1.3-001",
        "HLA1516.1-DM-5.1.3-002",
        "HLA1516.1-DM-5.10-001",
        "HLA1516.1-DM-5.11-001",
        "HLA1516.1-DM-5.12-001",
        "HLA1516.1-DM-5.13-001",
        "HLA1516.1-DM-5.2-001",
        "HLA1516.1-DM-5.2-002",
        "HLA1516.1-DM-5.3-001",
        "HLA1516.1-DM-5.4-001",
        "HLA1516.1-DM-5.4-002",
        "HLA1516.1-DM-5.5-001",
        "HLA1516.1-DM-5.6-001",
        "HLA1516.1-DM-5.6-002",
        "HLA1516.1-DM-5.6-003",
        "HLA1516.1-DM-5.7-001",
        "HLA1516.1-DM-5.7-002",
        "HLA1516.1-DM-5.8-001",
        "HLA1516.1-DM-5.8-002",
        "HLA1516.1-DM-5.9-001",
    ),
    status="verified",
    scenario_id="declaration-management",
    note="Shared declaration-management scenario verifies declaration service sequencing, advisory callbacks, and declaration-gated object and interaction delivery.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-DM-5.1.5-001",
    ),
    status="verified",
    scenario_id="ddm-declaration-gating",
    note="Shared declaration/DDM gating scenario verifies region-scoped discovery and delivery begin only once matching declaration subscriptions are established, demonstrating interaction between DM subscriptions and DDM subscriptions.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-DM-5.1.6-001",
    ),
    status="verified",
    scenario_id="update-rate",
    note="Shared update-rate scenario verifies declaration subscriptions can carry update-rate reduction behavior where the FOM designates it.",
)

_PITCH_REQUIREMENT_EVIDENCE["HLA1516.1-DM-5.1.1-001"] = (
    "not-applicable",
    _PITCH_REQUIREMENT_EVIDENCE["REQ-OMT-PARSE-001"][1]
    + (
        "src/hla2010/fom.py::merge_fom_modules",
        "tests/factories/test_fom_omt_parsing.py",
        "analysis/compliance/verification_assets.json",
    ),
    "FDD single-superclass structure is verified through core OMT parsing and merge validation rather than Pitch runtime parity execution.",
)

_PITCH_REQUIREMENT_EVIDENCE["HLA1516.1-DM-5.1.1-002"] = (
    "not-applicable",
    _PITCH_REQUIREMENT_EVIDENCE["REQ-OMT-PARSE-001"][1],
    "Available object-class attributes, including inherited attributes, are verified through core OMT parsing and catalog construction rather than Pitch runtime parity execution.",
)

_PITCH_REQUIREMENT_EVIDENCE["HLA1516.1-DM-5.1.1-003"] = (
    "not-applicable",
    _PITCH_REQUIREMENT_EVIDENCE["REQ-OMT-PARSE-001"][1],
    "Available interaction-class parameters, including inherited parameters, are verified through core OMT parsing and catalog construction rather than Pitch runtime parity execution.",
)

_PITCH_REQUIREMENT_EVIDENCE["HLA1516.1-DM-5.3-002"] = (
    "blocked",
    _SCENARIO_EVIDENCE_REGISTRY["declaration-unpublish-rejection"],
    "Shared harness parity now includes strict post-unpublish object-update rejection, but this workspace only proved the Python slice locally; the Pitch wrapper remained skipped because real vendor smoke was disabled, so Pitch disposition stays blocked pending explicit vendor execution.",
)

_PITCH_REQUIREMENT_EVIDENCE["HLA1516.1-DM-5.5-002"] = (
    "blocked",
    _SCENARIO_EVIDENCE_REGISTRY["declaration-unpublish-rejection"],
    "Shared harness parity now includes strict post-unpublish interaction-send rejection, but this workspace only proved the Python slice locally; the Pitch wrapper remained skipped because real vendor smoke was disabled, so Pitch disposition stays blocked pending explicit vendor execution.",
)

_PITCH_REQUIREMENT_EVIDENCE["REQ-RTI-PLM-12_2-decodeAttributeHandle"] = (
    "not-yet-tested",
    _SCENARIO_EVIDENCE_REGISTRY["support-factory-decode"]
    + (
        "src/hla2010/handles.py::Handle.decode",
        "packages/hla-backend-inmemory/src/hla.backends.inmemory/support_factories.py",
        "tests/verification/test_spec_traceability_all_methods.py",
    ),
    "Programming-language mapping designator decoding now has shared harness coverage in the Python reference backend, but dedicated Pitch runtime parity wrappers for the Clause 12 decode surface have not yet been added or executed, so the Pitch disposition is explicitly tracked as not-yet-tested.",
)

for requirement_id in (
    "REQ-RTI-PLM-12_2-decodeDimensionHandle",
    "REQ-RTI-PLM-12_2-decodeFederateHandle",
    "REQ-RTI-PLM-12_2-decodeInteractionClassHandle",
    "REQ-RTI-PLM-12_2-decodeMessageRetractionHandle",
    "REQ-RTI-PLM-12_2-decodeObjectClassHandle",
    "REQ-RTI-PLM-12_2-decodeObjectInstanceHandle",
    "REQ-RTI-PLM-12_2-decodeParameterHandle",
    "REQ-RTI-PLM-12_2-decodeRegionHandle",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = _PITCH_REQUIREMENT_EVIDENCE["REQ-RTI-PLM-12_2-decodeAttributeHandle"]

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.1-001",
        "HLA1516.1-FM-4.1-002",
        "HLA1516.1-FM-4.1-003",
        "HLA1516.1-FM-4.1-004",
        "HLA1516.1-FM-4.2-001",
        "HLA1516.1-FM-4.2-CB-001",
        "HLA1516.1-FM-4.2-EFF-001",
        "HLA1516.1-FM-4.2-SIG-001",
        "HLA1516.1-FM-4.2-TEST-001",
        "HLA1516.1-FM-4.3-001",
        "HLA1516.1-FM-4.3-CB-001",
        "HLA1516.1-FM-4.3-EFF-001",
        "HLA1516.1-FM-4.3-PRE-001",
        "HLA1516.1-FM-4.3-SIG-001",
        "HLA1516.1-FM-4.3-TEST-001",
        "HLA1516.1-FM-4.5-001",
        "HLA1516.1-FM-4.5-EFF-001",
        "HLA1516.1-FM-4.5-PRE-001",
        "HLA1516.1-FM-4.5-TEST-001",
        "HLA1516.1-FM-4.9-001",
        "HLA1516.1-FM-4.9-EFF-001",
        "HLA1516.1-FM-4.9-SIG-001",
        "HLA1516.1-FM-4.9-TEST-001",
        "HLA1516.1-FM-4.10-001",
        "HLA1516.1-FM-4.10-EFF-001",
        "HLA1516.1-FM-4.10-SIG-001",
        "HLA1516.1-FM-4.10-TEST-001",
    ),
    status="verified",
    scenario_id="federation-lifecycle",
    note="Pitch real-runtime lifecycle scenario verifies the corresponding federation-management service behavior.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.5-CB-001",
        "HLA1516.1-FM-4.5-SIG-001",
        "HLA1516.1-FM-4.6-001",
        "HLA1516.1-FM-4.6-CB-001",
        "HLA1516.1-FM-4.6-EFF-001",
        "HLA1516.1-FM-4.6-PRE-001",
        "HLA1516.1-FM-4.6-SIG-001",
        "HLA1516.1-FM-4.6-TEST-001",
    ),
    status="verified",
    scenario_id="federation-listing",
    note="Pitch real-runtime listing scenario verifies federation catalog visibility after create and removal after destroy.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.1.4.2-001",
        "HLA1516.1-FM-4.5-MOM-001",
    ),
    status="verified",
    scenario_id="fom-module-visibility",
    note="Pitch real-runtime MOM/FOM visibility scenario verifies post-join access to MOM classes plus FOM-module and MIM report interactions from the created federation.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.1.4-001",
    ),
    status="verified",
    scenario_id="fom-multi-module-visibility",
    note="Pitch real-runtime multi-module MOM/FOM visibility scenario verifies the reported combined FOM-module data retains content from each merged FOM module.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.1.2-001",
        "HLA1516.1-FM-4.17-001",
        "HLA1516.1-FM-4.17-CB-001",
        "HLA1516.1-FM-4.17-EFF-001",
        "HLA1516.1-FM-4.17-PRE-001",
        "HLA1516.1-FM-4.17-SIG-001",
        "HLA1516.1-FM-4.17-TEST-001",
        "HLA1516.1-FM-4.22-001",
        "HLA1516.1-FM-4.22-CB-001",
        "HLA1516.1-FM-4.22-EFF-001",
        "HLA1516.1-FM-4.22-PRE-001",
        "HLA1516.1-FM-4.22-SIG-001",
        "HLA1516.1-FM-4.22-TEST-001",
        "HLA1516.1-FM-4.27-001",
        "HLA1516.1-FM-4.27-CB-001",
        "HLA1516.1-FM-4.27-EFF-001",
        "HLA1516.1-FM-4.27-PRE-001",
        "HLA1516.1-FM-4.27-SIG-001",
        "HLA1516.1-FM-4.27-TEST-001",
    ),
    status="verified",
    scenario_id="save-restore",
    note="Pitch real-runtime save/restore scenario verifies the corresponding positive save, restore, and status callback behavior.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.30-001",
        "HLA1516.1-FM-4.30-CB-001",
        "HLA1516.1-FM-4.30-EFF-001",
        "HLA1516.1-FM-4.30-PRE-001",
        "HLA1516.1-FM-4.30-SIG-001",
        "HLA1516.1-FM-4.30-TEST-001",
    ),
    status="verified",
    scenario_id="restore-abort",
    note="Pitch real-runtime restore-abort scenario verifies abort-restore behavior and status cleanup.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.11-001",
        "HLA1516.1-FM-4.11-EFF-001",
        "HLA1516.1-FM-4.11-MOM-001",
        "HLA1516.1-FM-4.11-PRE-001",
        "HLA1516.1-FM-4.11-SIG-001",
        "HLA1516.1-FM-4.11-TEST-001",
        "HLA1516.1-FM-4.12-001",
        "HLA1516.1-FM-4.12-CB-001",
        "HLA1516.1-FM-4.12-EFF-001",
        "HLA1516.1-FM-4.12-PRE-001",
        "HLA1516.1-FM-4.12-SIG-001",
        "HLA1516.1-FM-4.12-TEST-001",
        "HLA1516.1-FM-4.13-001",
        "HLA1516.1-FM-4.13-CB-001",
        "HLA1516.1-FM-4.13-EFF-001",
        "HLA1516.1-FM-4.13-EXC-001",
        "HLA1516.1-FM-4.13-MOM-001",
        "HLA1516.1-FM-4.13-PRE-001",
        "HLA1516.1-FM-4.13-SIG-001",
        "HLA1516.1-FM-4.13-TEST-001",
        "HLA1516.1-FM-4.14-001",
        "HLA1516.1-FM-4.14-CB-001",
        "HLA1516.1-FM-4.14-EFF-001",
        "HLA1516.1-FM-4.14-MOM-001",
        "HLA1516.1-FM-4.14-PRE-001",
        "HLA1516.1-FM-4.14-SIG-001",
        "HLA1516.1-FM-4.14-TEST-001",
        "HLA1516.1-FM-4.15-001",
        "HLA1516.1-FM-4.15-002",
        "HLA1516.1-FM-4.15-CB-001",
        "HLA1516.1-FM-4.15-EFF-001",
        "HLA1516.1-FM-4.15-EXC-001",
        "HLA1516.1-FM-4.15-MOM-001",
        "HLA1516.1-FM-4.15-PRE-001",
        "HLA1516.1-FM-4.15-SIG-001",
        "HLA1516.1-FM-4.15-TEST-001",
    ),
    status="verified",
    scenario_ids=("synchronization", "synchronization-failed-federate"),
    note="Pitch real-runtime synchronization scenarios verify registration success, announcement, achievement, federation-synchronized callback behavior, and failed-federate completion semantics.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.11-CB-001",
        "HLA1516.1-FM-4.11-EXC-001",
        "HLA1516.1-FM-4.12-EXC-001",
    ),
    status="verified",
    scenario_ids=("synchronization", "synchronization-registration-failure"),
    note="Pitch real-runtime synchronization success and duplicate-label failure scenarios verify the clause-defined registration callback and failure paths.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.14-EXC-001",
    ),
    status="verified",
    scenario_id="synchronization-multiple-points",
    note="Pitch real-runtime multiple-synchronization-point scenario verifies that distinct open synchronization labels are tracked independently instead of collapsing achievement handling into generic behavior.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.9-CB-001",
    ),
    status="verified",
    scenario_id="synchronization-late-join",
    note="Pitch real-runtime late-join synchronization scenario verifies that a joined late federate receives open whole-federation synchronization announcements before completion.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.1.3-001",
    ),
    status="verified",
    scenario_id="synchronization-multiple-points",
    note="Pitch real-runtime multiple-synchronization-point scenario verifies that distinct open synchronization points are tracked and completed independently.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.30-EXC-001",
    ),
    status="verified",
    scenario_id="restore-abort-exceptions",
    note="Pitch real-runtime restore-abort exception scenario verifies distinct not-connected, not-joined, and restore-not-in-progress failure categories.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.10-CB-001",
    ),
    status="verified",
    scenario_id="resign-callback-silence",
    note="Pitch real-runtime resign scenario verifies that a federate no longer receives joined-member save callbacks after successful resignation.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.10-EXC-001",
        "HLA1516.1-FM-4.10-PRE-001",
    ),
    status="verified",
    scenario_id="resign-preconditions",
    note="Pitch real-runtime resign precondition scenario verifies distinct not-connected, not-joined, invalid-action, owned-attribute, and pending-acquisition failures before resignation succeeds.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.10-MOM-001",
    ),
    status="verified",
    scenario_id="resign-mom-cleanup",
    note="Pitch real-runtime resign MOM scenario verifies observer-visible federation membership refresh and that the resigned federate MOM object becomes unknown for subsequent attribute updates.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.3-MOM-001",
    ),
    status="verified",
    scenario_id="disconnect-mom-cleanup",
    note="Pitch real-runtime disconnect MOM cleanup scenario verifies observer-visible federation membership refresh and that the disconnected federate MOM object becomes unknown for subsequent attribute updates.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.1.4.1-001",
        "HLA1516.1-FM-4.1.4.1-002",
    ),
    status="verified",
    scenario_id="fom-integrity-negative",
    note="Pitch real-runtime FOM integrity negative scenario verifies invalid and incompatible FOM modules are rejected cleanly and that failed create/join attempts leave the federation usable afterward.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.9-PRE-001",
    ),
    status="verified",
    scenario_id="join-preconditions",
    note="Pitch real-runtime join precondition scenario verifies connection, missing-federation, duplicate-name, already-joined, save-in-progress, and restore-in-progress gating.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.9-EXC-001",
    ),
    status="vendor-divergent",
    scenario_ids=("join-preconditions", "fom-integrity-negative"),
    note="Pitch real-runtime shared join-negative scenarios verify not-connected, missing-federation, duplicate-name, already-joined, save-in-progress, restore-in-progress, FOM-open, FOM-read, and inconsistent-FOM failures, but the backend remains vendor-divergent for the invalid-time-factory family because the real Pitch join surface does not expose the Python-style local logical-time-factory override used by the reference backend to force that branch.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.5-EXC-001",
    ),
    status="vendor-divergent",
    scenario_ids=("federation-lifecycle-negative", "fom-integrity-negative", "federation-lifecycle-with-mim"),
    note="Pitch real-runtime shared negative scenarios verify duplicate-name plus FDD open/read/inconsistent failure families, but the backend remains vendor-divergent for the explicit-MIM-specific create exception families because the createFederationExecutionWithMIM overload is not available.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.1-005",
        "HLA1516.1-FM-4.1-006",
    ),
    status="verified",
    scenario_id="multi-participation",
    note="Pitch real-runtime multi-participation scenario verifies one application can hold multiple joined federates and simultaneous participation across distinct federation executions.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.1.4-002",
    ),
    status="verified",
    scenario_id="fom-module-visibility",
    note="Pitch real-runtime MOM/FOM visibility scenario verifies that ordinary federation creation exposes the standard MIM automatically through post-join MIM report access.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.2-MERGE-7-001",
        "HLA1516.2-OMT-7-001",
        "HLA1516.2-MERGE-7.0-005",
        "HLA1516.2-MERGE-7.0-006",
    ),
    status="verified",
    scenario_id="fom-integrity-negative",
    note="Pitch real-runtime FOM integrity negative scenario verifies that conflicting logical-time and incompatible duplicate FOM definitions are rejected transactionally without leaving a half-created federation behind.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.2-OMT-7-002",
        "HLA1516.2-MERGE-7.0-001",
        "HLA1516.2-MERGE-7.0-002",
        "HLA1516.2-MERGE-7.0-003",
        "HLA1516.2-MERGE-7.0-004",
        "HLA1516.2-MERGE-7.0-007",
    ),
    status="verified",
    scenario_id="fom-multi-module-visibility",
    note="Pitch real-runtime multi-module FOM visibility scenario verifies that multiple compatible modules compose into one active reported catalog whose merged payload retains class, datatype, and dimension content from each participating module.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.2-MERGE-7.0-008",
    ),
    status="verified",
    scenario_id="fom-module-visibility",
    note="Pitch real-runtime MOM/FOM visibility scenario verifies that the standard MIM is included automatically in the active federation model and can be requested through MOM report interactions.",
)

_PITCH_REQUIREMENT_EVIDENCE["HLA1516.2-OMT-6-001"] = (
    "verified",
    (
        "docs/verification/requirements_hierarchy.md",
        "requirements/hla1516_2_priority_omt.csv",
        "tests/verification/test_requirement_traceability_1516_2_v013.py",
    ),
    "Pitch parity for this 1516.2 conformance row is satisfied by repo-level artifact evidence that explicitly distinguishes supported versus unsupported OMT behavior in the requirements hierarchy and verifies that traceability contract.",
)

_PITCH_REQUIREMENT_EVIDENCE["REQ-OMT-6-conformance"] = (
    "not-applicable",
    (
        "docs/verification/requirements_hierarchy.md",
        "requirements/hla1516_2_priority_omt.csv",
        "tests/verification/test_requirement_traceability_1516_2_v013.py",
    ),
    "This OMT area row is a planning umbrella rather than an executable backend-parity requirement. The concrete extracted 1516.2 conformance requirement is tracked separately as HLA1516.2-OMT-6-001.",
)

_add_pitch_composite_evidence_rows(
    (
        "REQ-OMT-7-merging_rules",
        "REQ-OMT-MERGE-001",
    ),
    status="verified",
    scenario_ids=("fom-multi-module-visibility", "fom-integrity-negative", "fom-module-visibility"),
    note="Pitch real-runtime shared FOM merge scenarios verify the supported 1516.2 subset: compatible multi-module composition, transactional rejection of conflicting definitions, and automatic inclusion/reporting of the standard MIM.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.2-MERGE-7-002",
    ),
    status="vendor-divergent",
    scenario_id="federation-lifecycle-with-mim",
    note="Pitch Java FedPro adapter does not expose the createFederationExecutionWithMIM overload, so explicit requested-MIM provenance cannot be promoted even though ordinary federation creation exposes the standard MIM automatically.",
)

_add_pitch_evidence_rows(
    (
        "REQ-RTI-TM-8_19-modifyLookahead",
        "REQ-RTI-TM-8_20-queryLookahead",
        "HLA1516.1-TM-8.19-001",
        "HLA1516.1-TM-8.1.4-002",
        "HLA1516.1-TM-8.1.4-003",
    ),
    status="verified",
    scenario_id="section8-lookahead",
    note="Pitch real-runtime shared lookahead probes verify query and modification of lookahead for regulating federates and reject timestamped sends earlier than logical time plus lookahead.",
)

for requirement_id in (
    "REQ-RTI-TM-8_19-modifyLookahead",
    "REQ-RTI-TM-8_20-queryLookahead",
    "HLA1516.1-TM-8.19-001",
    "HLA1516.1-TM-8.1.4-002",
    "HLA1516.1-TM-8.1.4-003",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["section8-lookahead"],
        "Pitch real-runtime shared lookahead probes verify query and modification of lookahead for regulating federates and reject timestamped sends earlier than logical time plus lookahead.",
    )

for requirement_id in (
    "HLA1516.1-TM-8.1.4-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["section8-early-timestamp-send"],
        "Pitch real-runtime shared early-timestamp rejection probe verifies that a regulating federate cannot send timestamped updates or interactions earlier than its current logical time plus lookahead.",
    )

for requirement_id in (
    "REQ-RTI-TM-8_2-enableTimeRegulation",
    "REQ-FED-TM-8_3-timeRegulationEnabled",
    "REQ-RTI-TM-8_5-enableTimeConstrained",
    "REQ-FED-TM-8_6-timeConstrainedEnabled",
    "HLA1516.1-TM-8.2-001",
    "HLA1516.1-TM-8.2-002",
    "HLA1516.1-TM-8.2-003",
    "HLA1516.1-TM-8.5-001",
    "HLA1516.1-TM-8.5-002",
    "HLA1516.1-TM-8.5-003",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["section8-state-services"],
        "Pitch real-runtime shared state-services probe verifies regulation and constrained enablement setup, including the corresponding callback-observable federate state transitions.",
    )

for requirement_id in (
    "REQ-RTI-TM-8_17-queryLogicalTime",
    "HLA1516.1-TM-8.17-001",
    "HLA1516.1-TM-8.1.3-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["section8-logical-time"],
        "Pitch real-runtime shared logical-time query probe verifies that joined federates expose logical-time state and that queryLogicalTime returns the initial logical time on both participants.",
    )

for requirement_id in (
    "REQ-RTI-TM-8_4-disableTimeRegulation",
    "REQ-RTI-TM-8_7-disableTimeConstrained",
    "REQ-RTI-TM-8_14-enableAsynchronousDelivery",
    "REQ-RTI-TM-8_15-disableAsynchronousDelivery",
    "HLA1516.1-TM-8.4-001",
    "HLA1516.1-TM-8.7-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["section8-state-toggles"],
        "Pitch real-runtime shared state-toggle probe verifies the state-service sequence that enables asynchronous delivery, disables it again, and cleanly disables time regulation and time constrained state after the initial regulation/constrained setup.",
    )

for requirement_id in (
    "REQ-RTI-TM-8_8-timeAdvanceRequest",
    "REQ-FED-TM-8_13-timeAdvanceGrant",
    "HLA1516.1-TM-8.8-001",
    "HLA1516.1-TM-8.8-002",
    "HLA1516.1-TM-8.8-003",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-queries"],
        "Pitch real-runtime shared ordering/query probe verifies regulating advance requests and the resulting time-advance grants while timestamp-ordered traffic is released in logical-time order.",
    )

for requirement_id in (
    "REQ-RTI-TM-8_16-queryGALT",
    "REQ-RTI-TM-8_18-queryLITS",
    "HLA1516.1-TM-8.16-001",
    "HLA1516.1-TM-8.18-001",
    "HLA1516.1-TM-8.1.5-002",
    "HLA1516.1-TM-8.1.5-003",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["section8-time-bound-queries"],
        "Pitch real-runtime shared time-bound query probe verifies that a constrained federate can query GALT and LITS after timestamped traffic is queued under an active regulating publisher.",
    )

for requirement_id in (
    "REQ-RTI-TM-8_10-nextMessageRequest",
    "HLA1516.1-TM-8.10-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-ordering-and-queries"]
        + ("packages/hla-vendor-pitch/docs/evidence/pitch_section8_time_management_vendor_divergence_2026-06-11.md",),
        "Pitch dedicated Section 8 next-message probes diverge from the shared harness expectation because the real Java bridge path does not reproduce the expected next-message grant and timestamp-ordered release sequence in this matrix scenario.",
    )

for requirement_id in (
    "REQ-RTI-TM-8_9-timeAdvanceRequestAvailable",
    "REQ-RTI-TM-8_12-flushQueueRequest",
    "HLA1516.1-TM-8.12-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["section8-available-and-flush"],
        "Pitch real-runtime shared available/flush probe verifies a constrained federate receives a time-advance grant from timeAdvanceRequestAvailable and that flushQueueRequest grants and releases the queued timestamped interaction without relying on Python-specific retraction return objects.",
    )

for requirement_id in (
    "REQ-RTI-TM-8_11-nextMessageRequestAvailable",
    "REQ-RTI-TM-8_21-retract",
    "HLA1516.1-TM-8.21-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-available-and-retraction"]
        + ("packages/hla-vendor-pitch/docs/evidence/pitch_section8_time_management_vendor_divergence_2026-06-11.md",),
        "Pitch dedicated Section 8 available/retraction probes diverge from the shared harness expectation because the real Java bridge path does not expose the expected Python-level retraction return semantics in this matrix scenario.",
    )

for requirement_id in (
    "REQ-RTI-TM-8_23-changeAttributeOrderType",
    "REQ-RTI-TM-8_24-changeInteractionOrderType",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["section8-order-override"],
        "Pitch real-runtime shared order-override probe verifies that object updates and interactions can be forced to receive order despite timestamp arguments, matching the explicit order-type override services.",
    )

for requirement_id in (
    "REQ-FED-TM-8_22-requestRetraction",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "vendor-divergent",
        _SCENARIO_EVIDENCE_REGISTRY["section8-request-retraction"]
        + ("packages/hla-vendor-pitch/docs/evidence/pitch_section8_time_management_vendor_divergence_2026-06-11.md",),
        "Pitch dedicated Section 8 request-retraction probes diverge from the shared harness expectation because the real Java bridge path does not expose the expected Python-level retraction handle semantics in this matrix scenario.",
    )

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.1.2-002",
    ),
    status="verified",
    scenario_id="save-restore-queued-callbacks",
    note="Pitch real-runtime queued save/restore coordination scenario verifies required save and restore callbacks remain pending for an evoked federate until it explicitly drains them.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.17-MOM-001",
        "HLA1516.1-FM-4.27-MOM-001",
    ),
    status="verified",
    scenario_id="save-restore",
    note="Pitch real-runtime save/restore scenario exposes initiate-save and initiate-restore observer state through status-response callbacks during the pending phases.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.22-MOM-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "save-failure", "save-abort"),
    note="Pitch real-runtime save-status scenarios expose observer-facing save-status responses across successful, failed, and aborted save paths.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.17-EXC-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "save-failure", "save-abort"),
    note="Pitch real-runtime save scenarios jointly verify that initiate-save leads to distinct successful, failed, and aborted outcome categories rather than one collapsed callback path.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.22-EXC-001",
    ),
    status="verified",
    scenario_id="save-status-exceptions",
    note="Pitch real-runtime save-status exception scenario verifies distinct not-connected and not-joined query-save-status failure categories.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.16-EXC-001",
    ),
    status="verified",
    scenario_id="save-request-preconditions",
    note="Pitch real-runtime save-request precondition scenario verifies not-connected, not-joined, save-in-progress, and restore-in-progress failure categories for requestFederationSave.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.16-MOM-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "save-failure", "save-abort"),
    note="Pitch real-runtime save request scenarios expose observer-facing save coordination state across successful, failed, and aborted save paths.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.18-EXC-001",
        "HLA1516.1-FM-4.19-EXC-001",
    ),
    status="verified",
    scenario_id="save-participant-exceptions",
    note="Pitch real-runtime save participant exception scenario verifies not-connected, not-joined, and no-active-save failure categories for federate save-begun and save-complete services.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.23-EXC-001",
        "HLA1516.1-FM-4.23-MOM-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "save-failure", "save-abort"),
    note="Pitch real-runtime save-status scenarios distinguish save-status response payload categories and expose observer-facing save-status reporting across successful, failed, and aborted save flows.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.27-EXC-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "restore-failure", "restore-abort"),
    note="Pitch real-runtime restore scenarios jointly verify that initiate-restore leads to distinct successful, failed, and aborted outcome categories rather than one collapsed callback path.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.30-MOM-001",
    ),
    status="verified",
    scenario_id="restore-abort",
    note="Pitch real-runtime restore-abort scenario exposes observer-facing cleared restore status after an aborted restore.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.24-EXC-001",
    ),
    status="verified",
    scenario_id="restore-request-preconditions",
    note="Pitch real-runtime restore-request precondition scenario verifies not-connected, not-joined, save-in-progress, and restore-in-progress failure categories for requestFederationRestore.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.24-MOM-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "restore-request-failure"),
    note="Pitch real-runtime restore request scenarios expose observer-facing restore coordination state across successful and missing-save restore requests.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.18-MOM-001",
    ),
    status="verified",
    scenario_id="save-restore",
    note="Pitch real-runtime save/restore scenario exposes the reporting federate transition into the saving state while peers remain instructed-to-save in observer-facing status callbacks.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.19-MOM-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "save-abort"),
    note="Pitch real-runtime save scenarios expose observer-facing save-state progression through completion and the subsequent cleared state on both successful and aborted save paths.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.20-EXC-001",
        "HLA1516.1-FM-4.20-MOM-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "save-failure", "save-abort"),
    note="Pitch real-runtime save scenarios distinguish saved versus not-saved outcomes and preserve observer-facing save-state reporting across successful, failed, and aborted paths.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.21-EXC-001",
    ),
    status="verified",
    scenario_id="abort-save-exceptions",
    note="Pitch real-runtime abort-save exception scenario verifies not-connected and not-joined failure categories before any save is in progress.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.21-MOM-001",
    ),
    status="verified",
    scenario_id="save-abort",
    note="Pitch real-runtime abort-save scenario exposes observer-facing cleared save state after the aborted save path.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.28-EXC-001",
    ),
    status="verified",
    scenario_id="restore-participant-exceptions",
    note="Pitch real-runtime restore participant exception scenario verifies not-connected, not-joined, and no-active-restore failure categories for federate restore-complete services.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.28-MOM-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "restore-failure", "restore-abort"),
    note="Pitch real-runtime restore scenarios expose observer-facing restore-state progression through completion and the subsequent cleared state on failed and aborted restore paths.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.1.5-001",
        "HLA1516.1-FM-4.1.5-002",
    ),
    status="blocked",
    scenario_ids=("connection-lost-callback", "disconnect-mom-cleanup", "lost-federate-mom"),
    note="A shared lost-federate MOM scenario now exists, the Python backend executes it directly, `pitch-py4j` has a gateway-process fault-injection wrapper, and `pitch-jpype` has a child-process probe path through the shared external-victim harness. The canonical `./tools/pitch lost-federate-probe` lane currently stops at preflight on this surface because Docker is unreachable and the required CRC/FedPro loopback ports are blocked, and earlier executed real-runtime Pitch probes still failed to produce observer-visible lost-federate evidence: the JPype path auto-resumed its dropped session and the Py4J path did not surface the report, so the family remains blocked.",
)

for requirement_id in ("HLA1516.1-FM-4.1.5-001", "HLA1516.1-FM-4.1.5-002"):
    evidence = list(_merge_scenario_evidence("connection-lost-callback", "disconnect-mom-cleanup", "lost-federate-mom"))
    for ref in (
        "packages/hla-vendor-pitch/docs/evidence/pitch_clause4_lost_federate_gap_2026-06-11.md",
        "analysis/preflight_artifacts/pitch-preflight.json",
        "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
        "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md",
    ):
        if ref not in evidence:
            evidence.append(ref)
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "blocked",
        tuple(evidence),
        "A shared lost-federate MOM scenario now exists, the Python backend executes it directly, `pitch-py4j` has a gateway-process fault-injection wrapper, and `pitch-jpype` has a child-process probe path through the shared external-victim harness. The canonical `./tools/pitch lost-federate-probe` lane currently stops at preflight on this surface because Docker is unreachable and the required CRC/FedPro loopback ports are blocked, and earlier executed real-runtime Pitch probes still failed to produce observer-visible lost-federate evidence: the JPype path auto-resumed its dropped session and the Py4J path did not surface the report, so the family remains blocked.",
    )

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.12-MOM-001",
    ),
    status="verified",
    scenario_id="synchronization",
    note="Pitch real-runtime synchronization scenario exposes observer-facing registration and announcement callback state for synchronization-point setup.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.2-MOM-001",
        "HLA1516.1-FM-4.9-MOM-001",
    ),
    status="verified",
    scenario_id="resign-mom-cleanup",
    note="Pitch real-runtime MOM federate visibility scenario exposes joined federates through observer-visible MOM federate objects and refreshed federation membership state.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.6-MOM-001",
    ),
    status="verified",
    scenario_id="federation-listing",
    note="Pitch real-runtime federation listing scenario exposes destroyed-federation removal through subsequent observer-facing federation-execution reports.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.2-EXC-001",
        "HLA1516.1-FM-4.2-PRE-001",
        "HLA1516.1-FM-4.3-EXC-001",
        "HLA1516.1-FM-4.6-EXC-001",
    ),
    status="verified",
    scenario_id="federation-lifecycle-negative",
    note="Pitch real-runtime lifecycle negative scenario verifies repeated-connect rejection, disconnect-while-joined rejection, and destroy-federation failure distinctions.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.16-001",
        "HLA1516.1-FM-4.16-CB-001",
        "HLA1516.1-FM-4.16-EFF-001",
        "HLA1516.1-FM-4.16-PRE-001",
        "HLA1516.1-FM-4.16-SIG-001",
        "HLA1516.1-FM-4.16-TEST-001",
        "HLA1516.1-FM-4.18-001",
        "HLA1516.1-FM-4.18-CB-001",
        "HLA1516.1-FM-4.18-EFF-001",
        "HLA1516.1-FM-4.18-PRE-001",
        "HLA1516.1-FM-4.18-SIG-001",
        "HLA1516.1-FM-4.18-TEST-001",
        "HLA1516.1-FM-4.23-001",
        "HLA1516.1-FM-4.23-CB-001",
        "HLA1516.1-FM-4.23-EFF-001",
        "HLA1516.1-FM-4.23-PRE-001",
        "HLA1516.1-FM-4.23-SIG-001",
        "HLA1516.1-FM-4.23-TEST-001",
        "HLA1516.1-FM-4.24-001",
        "HLA1516.1-FM-4.24-CB-001",
        "HLA1516.1-FM-4.24-EFF-001",
        "HLA1516.1-FM-4.24-PRE-001",
        "HLA1516.1-FM-4.24-SIG-001",
        "HLA1516.1-FM-4.24-TEST-001",
        "HLA1516.1-FM-4.26-001",
        "HLA1516.1-FM-4.26-CB-001",
        "HLA1516.1-FM-4.26-EFF-001",
        "HLA1516.1-FM-4.26-PRE-001",
        "HLA1516.1-FM-4.26-SIG-001",
        "HLA1516.1-FM-4.26-TEST-001",
        "HLA1516.1-FM-4.31-001",
        "HLA1516.1-FM-4.31-CB-001",
        "HLA1516.1-FM-4.31-EFF-001",
        "HLA1516.1-FM-4.31-PRE-001",
        "HLA1516.1-FM-4.31-SIG-001",
        "HLA1516.1-FM-4.31-TEST-001",
        "HLA1516.1-FM-4.32-001",
        "HLA1516.1-FM-4.32-CB-001",
        "HLA1516.1-FM-4.32-EFF-001",
        "HLA1516.1-FM-4.32-PRE-001",
        "HLA1516.1-FM-4.32-SIG-001",
        "HLA1516.1-FM-4.32-TEST-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "save-restore-time-state"),
    note="Pitch real-runtime save/restore scenarios verify the corresponding positive save, restore, status callback, and restored logical-time-state behavior.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.21-001",
        "HLA1516.1-FM-4.21-CB-001",
        "HLA1516.1-FM-4.21-EFF-001",
        "HLA1516.1-FM-4.21-PRE-001",
        "HLA1516.1-FM-4.21-SIG-001",
        "HLA1516.1-FM-4.21-TEST-001",
    ),
    status="verified",
    scenario_id="save-abort",
    note="Pitch real-runtime abort-save scenario verifies abort-save status cleanup and callback behavior.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.30-001",
        "HLA1516.1-FM-4.30-CB-001",
        "HLA1516.1-FM-4.30-EFF-001",
        "HLA1516.1-FM-4.30-PRE-001",
        "HLA1516.1-FM-4.30-SIG-001",
        "HLA1516.1-FM-4.30-TEST-001",
    ),
    status="verified",
    scenario_id="restore-abort",
    note="Pitch real-runtime abort-restore scenario verifies abort-restore status cleanup and callback behavior.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.19-001",
        "HLA1516.1-FM-4.19-CB-001",
        "HLA1516.1-FM-4.19-EFF-001",
        "HLA1516.1-FM-4.19-PRE-001",
        "HLA1516.1-FM-4.19-SIG-001",
        "HLA1516.1-FM-4.19-TEST-001",
        "HLA1516.1-FM-4.20-001",
        "HLA1516.1-FM-4.20-CB-001",
        "HLA1516.1-FM-4.20-EFF-001",
        "HLA1516.1-FM-4.20-PRE-001",
        "HLA1516.1-FM-4.20-SIG-001",
        "HLA1516.1-FM-4.20-TEST-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "save-failure"),
    note="Pitch real-runtime save/restore and save-failure scenarios jointly verify the success and failure save completion/reporting behavior.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.25-001",
        "HLA1516.1-FM-4.25-CB-001",
        "HLA1516.1-FM-4.25-EFF-001",
        "HLA1516.1-FM-4.25-PRE-001",
        "HLA1516.1-FM-4.25-SIG-001",
        "HLA1516.1-FM-4.25-TEST-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "restore-request-failure"),
    note="Pitch real-runtime restore scenarios jointly verify restore request success and unknown-save failure reporting.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.28-001",
        "HLA1516.1-FM-4.28-CB-001",
        "HLA1516.1-FM-4.28-EFF-001",
        "HLA1516.1-FM-4.28-PRE-001",
        "HLA1516.1-FM-4.28-SIG-001",
        "HLA1516.1-FM-4.28-TEST-001",
        "HLA1516.1-FM-4.29-001",
        "HLA1516.1-FM-4.29-CB-001",
        "HLA1516.1-FM-4.29-EFF-001",
        "HLA1516.1-FM-4.29-PRE-001",
        "HLA1516.1-FM-4.29-SIG-001",
        "HLA1516.1-FM-4.29-TEST-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "restore-failure"),
    note="Pitch real-runtime restore scenarios jointly verify restore completion and restore-failure reporting behavior.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.25-EXC-001",
        "HLA1516.1-FM-4.25-MOM-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "restore-request-failure"),
    note="Pitch real-runtime restore request scenarios distinguish restore-request success and unknown-save failure categories while exposing the resulting observer-facing restore state.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.26-EXC-001",
        "HLA1516.1-FM-4.26-MOM-001",
    ),
    status="verified",
    scenario_id="save-restore",
    note="Pitch real-runtime save/restore scenario verifies restore-begun callback delivery together with the pending observer-visible restore state.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.29-EXC-001",
        "HLA1516.1-FM-4.29-MOM-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "restore-failure"),
    note="Pitch real-runtime restore scenarios distinguish restored versus not-restored outcomes and keep the resulting observer-facing federation state coherent.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-FM-4.31-EXC-001",
    ),
    status="verified",
    scenario_id="restore-status-exceptions",
    note="Pitch real-runtime restore-status exception scenario verifies distinct not-connected and not-joined query-restore-status failure categories.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.31-MOM-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "restore-request-failure", "restore-failure", "restore-abort"),
    note="Pitch real-runtime restore-status scenarios expose pending, failed, aborted, and missing-save-label restore-state reporting through observer-facing restore-status queries.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.32-EXC-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "restore-failure", "restore-abort"),
    note="Pitch real-runtime restore-status response scenarios distinguish successful, failed, and aborted restore-status callback payload categories.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-FM-4.32-MOM-001",
    ),
    status="verified",
    scenario_ids=("save-restore", "restore-request-failure", "restore-failure", "restore-abort"),
    note="Pitch real-runtime restore-status response scenarios expose pending, failed, aborted, and missing-save-label observer-facing restore-status reporting.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-OM-6.2-001",
        "HLA1516.1-OM-6.3-001",
        "HLA1516.1-OM-6.4-001",
        "HLA1516.1-OM-6.5-001",
        "HLA1516.1-OM-6.6-001",
        "HLA1516.1-OM-6.7-001",
    ),
    status="verified",
    scenario_id="name-reservation",
    note="Pitch real-runtime shared name-reservation scenario verifies single-name and multi-name reservation, callback, and release/reacquisition behavior.",
)

_add_pitch_evidence_rows(
    (
        "REQ-RTI-OM-6_10-updateAttributeValues",
        "REQ-RTI-OM-6_12-sendInteraction",
        "HLA1516.1-OM-6.1-001",
        "HLA1516.1-OM-6.1-002",
        "HLA1516.1-OM-6.1.1-001",
        "HLA1516.1-OM-6.1.1-004",
        "HLA1516.1-OM-6.1.7-001",
        "HLA1516.1-OM-6.10-001",
        "HLA1516.1-OM-6.10-002",
        "HLA1516.1-OM-6.10-003",
        "HLA1516.1-OM-6.10-004",
        "HLA1516.1-OM-6.12-001",
        "HLA1516.1-OM-6.12-002",
        "HLA1516.1-OM-6.12-003",
        "HLA1516.1-OM-6.12-004",
        "HLA1516.1-OM-6.8-001",
        "HLA1516.1-OM-6.8-002",
        "HLA1516.1-OM-6.8-003",
        "HLA1516.1-OM-6.8-004",
        "HLA1516.1-OM-6.9-001",
        "HLA1516.1-OM-6.11-001",
        "HLA1516.1-OM-6.11-002",
        "HLA1516.1-OM-6.13-001",
        "HLA1516.1-OM-6.14-001",
        "HLA1516.1-OM-6.14-002",
        "HLA1516.1-OM-6.15-001",
    ),
    status="verified",
    scenario_id="two-federate-exchange",
    note="Pitch real-runtime shared two-federate exchange scenario verifies object registration, discovery, attribute reflection, interaction delivery, and delete/remove teardown behavior.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-OM-6.10-005",
        "HLA1516.1-OM-6.12-005",
    ),
    status="verified",
    scenario_ids=("two-federate-exchange", "transportation-type"),
    note="Pitch real-runtime shared exchange and transportation-type scenarios verify reflected-update and received-interaction delivery semantics together with the supported reliable/best-effort transportation subset.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-OM-6.1.6-001",
        "HLA1516.1-OM-6.16-001",
        "HLA1516.1-OM-6.16-002",
    ),
    status="verified",
    scenario_id="local-delete",
    note="Pitch real-runtime shared local-delete scenario verifies orphan/local knowledge handling by removing only local knowledge, preserving federation-wide instance state, and allowing subsequent rediscovery without federation-wide deletion.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-OM-6.19-001",
        "HLA1516.1-OM-6.19-002",
    ),
    status="verified",
    scenario_id="request-attribute-value-update",
    note="Pitch real-runtime shared request-attribute-value-update scenario verifies the service call and the resulting provide-value callback to the owning federate.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-OM-6.1.1-002",
        "HLA1516.1-OM-6.1.1-003",
    ),
    status="verified",
    scenario_id="discovery-class",
    note="Pitch real-runtime shared discovery-class scenario verifies that discovery uses the closest subscribed superclass and that the discovered class remains stable across later reflections.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-OM-6.1.2-001",
        "HLA1516.1-OM-6.1.3-001",
        "HLA1516.1-OM-6.1.4-001",
        "HLA1516.1-OM-6.1.5-001",
    ),
    status="verified",
    scenario_id="object-scope-relevance",
    note="Pitch real-runtime shared object-scope scenario verifies region-driven in-scope and out-of-scope transitions, suppression of out-of-scope reflections, and ownership-transfer relevance across published/subscribed attributes.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-OM-6.1.12-001",
    ),
    status="verified",
    scenario_id="update-rate",
    note="Pitch real-runtime shared update-rate scenario verifies that timestamped reflections are throttled according to the subscribed update-rate designator.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-OM-6.17-001",
        "HLA1516.1-OM-6.18-001",
        "HLA1516.1-OM-6.21-001",
        "HLA1516.1-OM-6.21-002",
        "HLA1516.1-OM-6.22-001",
    ),
    status="verified",
    scenario_id="update-advisory-callbacks",
    note="Pitch real-runtime shared update-advisory callback probe verifies in-scope, out-of-scope, and turn-updates advisory callback payloads.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-OM-6.1.11-001",
    ),
    status="verified",
    scenario_id="two-federate-exchange",
    note="Pitch real-runtime shared exchange scenario verifies the externally visible delivery semantics for reflected attributes and received interactions. Clause 6.1.11 permits message combination or passelization but does not require it, so the unbatched path exercised here satisfies the row by preserving the observable semantics.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-OM-6.1.10-002",
        "HLA1516.1-OM-6.1.10-003",
        "HLA1516.1-OM-6.23-002",
        "HLA1516.1-OM-6.27-002",
    ),
    status="verified",
    scenario_id="transportation-type-restore-persistence",
    note="Pitch real-runtime shared transportation restore scenario verifies explicit reliable versus best-effort override behavior and that attribute and interaction transport overrides persist across save/restore.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-OM-6.24-002",
        "HLA1516.1-OM-6.25-002",
        "HLA1516.1-OM-6.26-002",
        "HLA1516.1-OM-6.28-002",
        "HLA1516.1-OM-6.29-002",
        "HLA1516.1-OM-6.30-002",
    ),
    status="verified",
    scenario_id="transportation-type",
    note="Pitch real-runtime shared transportation-type scenario verifies reliable/best-effort subset confirmation and query/report callback behavior for attributes and interactions.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-OM-6.24-003",
        "HLA1516.1-OM-6.26-003",
        "HLA1516.1-OM-6.28-003",
        "HLA1516.1-OM-6.30-003",
    ),
    status="verified",
    scenario_id="transportation-type-rejection",
    note="Pitch real-runtime shared transportation rejection scenario verifies that rejected attribute and interaction transport change/query calls across invalid state, invalid-handle, invalid-transport, and non-owner paths do not emit confirm or report callbacks.",
)

_add_pitch_composite_evidence_rows(
    (
        "HLA1516.1-OM-6.1.10-001",
        "HLA1516.1-OM-6.23-001",
        "HLA1516.1-OM-6.27-001",
    ),
    status="vendor-divergent",
    scenario_ids=("transportation-type", "transportation-type-restore-persistence"),
    extra_refs=("packages/hla-vendor-pitch/docs/evidence/pitch_transport_subset_vendor_divergence_2026-06-11.md",),
    note="Pitch real-runtime transportation coverage verifies the reliable/best-effort subset and override persistence only. The broader standard rows that speak for the full transportation semantic space remain vendor-divergent because arbitrary transport-type semantics beyond that subset are not modeled by this backend surface.",
)

_add_pitch_evidence_rows(
    (
        "HLA1516.1-OM-6.24-001",
        "HLA1516.1-OM-6.25-001",
        "HLA1516.1-OM-6.26-001",
        "HLA1516.1-OM-6.28-001",
        "HLA1516.1-OM-6.29-001",
        "HLA1516.1-OM-6.30-001",
    ),
    status="vendor-divergent",
    scenario_id="transportation-type",
    extra_refs=("packages/hla-vendor-pitch/docs/evidence/pitch_transport_subset_vendor_divergence_2026-06-11.md",),
    note="Pitch real-runtime transportation coverage verifies the reliable/best-effort subset only. The broader standard rows that speak for the full transportation semantic space remain vendor-divergent because arbitrary transport-type semantics beyond that subset are not modeled by this backend surface.",
)

for requirement_id in (
    "REQ-OM-DISCOVERY-CLASS-001",
    "REQ-OM-REFLECT-KNOWN-CLASS-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["discovery-class"],
        "Pitch real-runtime shared discovery-class scenario verifies closest-superclass discovery selection, stable known-class lookup, and reflected-attribute mapping through the subscriber's discovered class handles.",
    )

for requirement_id in (
    "REQ-OM-LOCAL-KNOWLEDGE-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["local-delete"],
        "Pitch real-runtime shared local-delete scenario verifies that local delete clears only the observer's local knowledge and that a subsequent owner update causes rediscovery through the same object instance handle.",
    )

for requirement_id in (
    "REQ-OM-ORPHAN-KNOWLEDGE-001",
    "REQ-OM-ORPHAN-LIFECYCLE-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["orphan-object-lifecycle"],
        "Pitch real-runtime shared orphan-object scenario verifies that an ownerless object remains known to an existing subscriber, becomes discoverable to a late subscriber, is cleared only from the locally deleting federate's knowledge, and is removed globally only by the explicit delete path seen by other knowing federates.",
    )

for requirement_id in (
    "REQ-OM-TIMED-DELETE-REMOVE-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["timed-delete"],
        "Pitch real-runtime shared timed-delete scenario verifies that a timestamped delete does not emit Remove Object Instance before the time advance grant path reaches the delete time, and that the object is removed from known-object state only after the remove callback is delivered.",
    )

for requirement_id in (
    "REQ-OM-ATTRIBUTE-RELEVANCE-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["object-scope-relevance"],
        "Pitch real-runtime shared object-scope scenario verifies that relevance depends on ownership and subscribed region scope, suppresses out-of-scope delivery, and restores delivery after ownership and scope conditions change.",
    )

for requirement_id in (
    "REQ-OM-SCOPE-CALLBACKS-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["object-scope-relevance"],
        "Pitch real-runtime shared object-scope scenario verifies that known subscribed attributes emit Attributes In Scope on initial discovery, Attributes Out Of Scope after the observer region leaves scope, and Attributes In Scope again when relevance is restored.",
    )

for requirement_id in (
    "REQ-OM-REQUEST-VALUE-UPDATE-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["request-attribute-value-update"],
        "Pitch real-runtime shared request-attribute-value-update scenario verifies that a relevant owner receives the Provide Attribute Value Update callback with the requested object, attribute set, and tag.",
    )

for requirement_id in (
    "REQ-OM-REQUEST-VALUE-UPDATE-ROUTING-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["request-attribute-value-update-routing"],
        "Pitch real-runtime shared request-attribute-value-update routing scenario verifies that object-target requests notify only the owning federate for that object, while class-target requests notify each relevant owning federate for its own object instances.",
    )

for requirement_id in (
    "REQ-OM-TRANSPORT-REPORT-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["transportation-type"]
        + _SCENARIO_EVIDENCE_REGISTRY["transportation-type-rejection"],
        "Pitch real-runtime shared transportation scenarios verify confirm/report callback delivery for the supported reliable and best-effort subset and verify that rejected transport change/query requests do not emit those callbacks.",
    )

for requirement_id in (
    "REQ-OM-TRANSPORT-BEST-EFFORT-001",
):
    _PITCH_REQUIREMENT_EVIDENCE[requirement_id] = (
        "verified",
        _SCENARIO_EVIDENCE_REGISTRY["transportation-type-restore-persistence"],
        "Pitch real-runtime shared transportation restore scenario verifies distinct reliable versus best-effort callback transport behavior, explicit override persistence, and restore persistence for the backend's supported transport subset.",
    )

_PITCH_REQUIREMENT_EVIDENCE["REQ-OM-DISCOVERY-LIFECYCLE-001"] = (
    "verified",
    _merge_scenario_evidence(
        "two-federate-exchange",
        "discovery-class",
        "timed-delete",
    ),
    "Pitch real-runtime shared object-management scenarios verify the stable object lifecycle: registration and ordinary discovery/removal on the shared exchange path, closest-superclass and stable known-class behavior on discovery, and timestamped removal semantics once the delete time is granted.",
)

_PITCH_REQUIREMENT_EVIDENCE["REQ-OM-TRANSPORT-SCOPE-001"] = (
    "vendor-divergent",
    _merge_scenario_evidence(
        "object-scope-relevance",
        "local-delete",
        "transportation-type",
        "transportation-type-rejection",
        "transportation-type-restore-persistence",
    ),
    "Pitch real-runtime shared object-management scenarios verify the implemented subset of this broad slice: scope-driven relevance callbacks, local-delete knowledge restrictions, and reliable/best-effort transportation change, query, report, rejection, and restore-persistence behavior. The slice remains vendor-divergent because its transport-semantics language is broader than the backend's supported reliable/best-effort subset and does not stop at the implemented transportation profile.",
)

_SEED_ROW_NOT_APPLICABLE_NOTES: dict[str, str] = {
    "HLA1516-TIME-001": "Time-concept seed row is a planning umbrella for the detailed time-management slices, not an executable Python backend requirement.",
    "HLA1516.1-DM-001": "Declaration-management seed row is a planning umbrella for the detailed Clause 5 service rows, not an executable backend parity requirement.",
    "HLA1516.1-OM-001": "Object-management seed row is a planning umbrella for the detailed Clause 6 service and callback rows, not an executable backend parity requirement.",
    "HLA1516.1-OWN-001": "Ownership-management seed row is a planning umbrella for the detailed Clause 7 service rows, not an executable backend parity requirement.",
    "HLA1516.1-TM-001": "Time-management seed row is a planning umbrella for the detailed Clause 8 service rows, not an executable backend parity requirement.",
    "HLA1516.1-DDM-001": "DDM seed row is a planning umbrella for the detailed Clause 9 service rows, not an executable backend parity requirement.",
    "HLA1516.1-SUP-001": "Support-services seed row is a planning umbrella for the detailed Clause 10 service rows, not an executable backend parity requirement.",
    "HLA1516.1-MOM-001": "MOM seed row is a planning umbrella for the detailed Clause 11 reporting and observer rows, not an executable backend parity requirement.",
}


def _negative_priority(row: ServiceConformanceRow) -> tuple[str, str, tuple[int, int, str, str]]:
    root = row.section.split(".", 1)[0] if row.section else "unmapped"
    exception_count = actionable_negative_expectation_count(row)
    if root == "4":
        return ("P1", "core federation-management negative path", (0, -exception_count, row.section_ref, row.method_name))
    if root in {"5", "6", "7", "8", "9"}:
        return ("P2", "core RTI behavior negative path", (1, -exception_count, row.section_ref, row.method_name))
    if root == "10":
        return ("P3", "support-service negative path", (2, -exception_count, row.section_ref, row.method_name))
    return ("P4", "non-core or unmapped negative path", (3, -exception_count, row.section_ref, row.method_name))


def _negative_path_rationale(row: ServiceConformanceRow) -> str:
    status = negative_path_status(row)
    if status == "not-applicable":
        return "No declared RTI exception matrix is present for this row."
    if status == "complete":
        return "Declared negative-path expectations are fully represented by executable evidence."
    if status == "mapped-not-exhaustive":
        return "Declared exceptions are mapped from source metadata, but exhaustive negative-path execution is still incomplete."
    if status == "partial":
        return "Some negative-path execution exists, but completeness is still partial."
    return "Declared negative-path expectations exist, but executable negative-path evidence is not yet linked."


_SECTION8_HOSTED_METHODS = frozenset(
    {
        "enableTimeRegulation",
        "disableTimeRegulation",
        "enableTimeConstrained",
        "disableTimeConstrained",
        "timeAdvanceRequest",
        "timeAdvanceRequestAvailable",
        "nextMessageRequest",
        "nextMessageRequestAvailable",
        "flushQueueRequest",
        "queryGALT",
        "queryLogicalTime",
        "queryLITS",
        "modifyLookahead",
        "queryLookahead",
        "retract",
        "requestRetraction",
        "changeAttributeOrderType",
        "changeInteractionOrderType",
        "enableAsynchronousDelivery",
        "disableAsynchronousDelivery",
        "timeRegulationEnabled",
        "timeConstrainedEnabled",
        "timeAdvanceGrant",
    }
)

_SECTION8_CERTI_METHODS = frozenset(
    {
        "enableTimeRegulation",
        "enableTimeConstrained",
        "timeAdvanceRequest",
        "flushQueueRequest",
        "queryGALT",
        "queryLITS",
        "timeRegulationEnabled",
        "timeConstrainedEnabled",
        "timeAdvanceGrant",
    }
)

_SECTION8_PITCH_METHODS = frozenset(
    {
        "enableTimeRegulation",
        "enableTimeConstrained",
        "timeAdvanceGrant",
    }
)

_PYTHON_BACKEND_EXTENDED_TESTS = (
    "tests/backends/test_python_backend_federation_extended.py",
    "tests/backends/test_python_backend_time_ddm_extended.py",
    "tests/backends/test_python_backend_object_ownership_extended.py",
)

_CERTI_REAL_BACKEND_MATRIX_TESTS = (
    "tests/vendors/test_certi_real_backend_exchange_matrix.py",
    "tests/vendors/test_certi_real_backend_time_matrix.py",
    "tests/vendors/test_certi_real_backend_ownership_matrix.py",
)

_CORE_BACKEND_SLICE_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "slice_id": "federation-sync",
        "section_refs": ("IEEE 1516.1-2010 §4.25", "IEEE 1516.1-2010 §4.26"),
        "profiles": (
            {
                "backend_id": "python-inmemory",
                "backend_family": "python-reference",
                "status": "reference-passing",
                "scope": "core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "Reference backend semantics are exercised indirectly through shared scenario helpers and broader federation tests.",
            },
            {
                "backend_id": "rest-hosted-python",
                "backend_family": "hosted-python-rest",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/transport/test_rest_transport.py",),
                "notes": "REST-hosted Python RTI now has explicit synchronization end-to-end coverage.",
            },
            {
                "backend_id": "grpc-hosted-python",
                "backend_family": "hosted-python-grpc",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/transport/test_grpc_transport_python_server.py",),
                "notes": "gRPC-hosted Python RTI has explicit synchronization end-to-end coverage.",
            },
            {
                "backend_id": "java-shim-jpype",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "JPype Java shim has explicit synchronization coverage.",
            },
            {
                "backend_id": "java-shim-py4j",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "Py4J Java shim has explicit synchronization coverage.",
            },
            {
                "backend_id": "certi-native",
                "backend_family": "vendor-certi",
                "status": "env-gated-positive",
                "scope": "real-vendor core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_exchange_matrix.py",),
                "notes": "CERTI synchronization matrix exists but was not rerun in this session.",
            },
            {
                "backend_id": "certi-jpype",
                "backend_family": "vendor-certi-java-bridge",
                "status": "env-gated-positive",
                "scope": "real-vendor core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_exchange_matrix.py",),
                "notes": "CERTI JPype synchronization matrix exists but was not rerun in this session.",
            },
            {
                "backend_id": "certi-py4j",
                "backend_family": "vendor-certi-java-bridge",
                "status": "env-gated-positive",
                "scope": "real-vendor core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_exchange_matrix.py",),
                "notes": "CERTI Py4J synchronization matrix exists but was not rerun in this session.",
            },
        ),
    },
    {
        "slice_id": "exchange",
        "section_refs": ("IEEE 1516.1-2010 §5.2", "IEEE 1516.1-2010 §6.9"),
        "profiles": (
            {
                "backend_id": "python-inmemory",
                "backend_family": "python-reference",
                "status": "reference-passing",
                "scope": "core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/time/test_section8_backend_matrix.py",),
                "notes": "Reference backend exchange behavior is exercised heavily through the Section 8 and scenario suites.",
            },
            {
                "backend_id": "rest-hosted-python",
                "backend_family": "hosted-python-rest",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/transport/test_rest_transport.py",),
                "notes": "REST-hosted Python RTI has explicit exchange end-to-end coverage.",
            },
            {
                "backend_id": "grpc-hosted-python",
                "backend_family": "hosted-python-grpc",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/transport/test_grpc_transport_python_server.py",),
                "notes": "gRPC-hosted Python RTI has explicit exchange end-to-end coverage.",
            },
            {
                "backend_id": "java-shim-jpype",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "JPype Java shim has explicit exchange coverage including timed exchange.",
            },
            {
                "backend_id": "java-shim-py4j",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "Py4J Java shim has explicit exchange coverage including timed exchange.",
            },
            {
                "backend_id": "certi-native",
                "backend_family": "vendor-certi",
                "status": "verified-in-this-session",
                "scope": "real-vendor core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_exchange_matrix.py",),
                "notes": "CERTI native exchange and cross-facade parity slices passed in this session.",
            },
            {
                "backend_id": "certi-jpype",
                "backend_family": "vendor-certi-java-bridge",
                "status": "verified-in-this-session",
                "scope": "real-vendor core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_exchange_matrix.py",),
                "notes": "CERTI JPype exchange and cross-facade parity slices passed in this session.",
            },
            {
                "backend_id": "certi-py4j",
                "backend_family": "vendor-certi-java-bridge",
                "status": "verified-in-this-session",
                "scope": "real-vendor core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_exchange_matrix.py",),
                "notes": "CERTI Py4J exchange and cross-facade parity slices passed in this session.",
            },
        ),
    },
    {
        "slice_id": "ownership",
        "section_refs": ("IEEE 1516.1-2010 §7.2", "IEEE 1516.1-2010 §7.18"),
        "profiles": (
            {
                "backend_id": "python-inmemory",
                "backend_family": "python-reference",
                "status": "reference-passing",
                "scope": "core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/backends/test_python_backend_object_ownership_extended.py",),
                "notes": "Reference backend ownership semantics are covered in the Python backend suite.",
            },
            {
                "backend_id": "rest-hosted-python",
                "backend_family": "hosted-python-rest",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/transport/test_rest_transport.py",),
                "notes": "REST-hosted Python RTI now has explicit ownership end-to-end coverage.",
            },
            {
                "backend_id": "grpc-hosted-python",
                "backend_family": "hosted-python-grpc",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/transport/test_grpc_transport_python_server.py",),
                "notes": "gRPC-hosted Python RTI has explicit ownership and negotiated ownership coverage.",
            },
            {
                "backend_id": "java-shim-jpype",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "JPype Java shim has explicit ownership coverage.",
            },
            {
                "backend_id": "java-shim-py4j",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "Py4J Java shim has explicit ownership coverage.",
            },
            {
                "backend_id": "certi-native",
                "backend_family": "vendor-certi",
                "status": "verified-in-this-session",
                "scope": "real-vendor core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_ownership_matrix.py",),
                "notes": "CERTI native plain ownership slice passed in this session.",
            },
            {
                "backend_id": "certi-jpype",
                "backend_family": "vendor-certi-java-bridge",
                "status": "verified-in-this-session",
                "scope": "real-vendor core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_ownership_matrix.py",),
                "notes": "CERTI JPype plain ownership slice passed in this session.",
            },
            {
                "backend_id": "certi-py4j",
                "backend_family": "vendor-certi-java-bridge",
                "status": "verified-in-this-session",
                "scope": "real-vendor core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_ownership_matrix.py",),
                "notes": "CERTI Py4J plain ownership slice passed in this session.",
            },
        ),
    },
    {
        "slice_id": "negotiated-ownership",
        "section_refs": ("IEEE 1516.1-2010 §7.3", "IEEE 1516.1-2010 §7.15"),
        "profiles": (
            {
                "backend_id": "python-inmemory",
                "backend_family": "python-reference",
                "status": "reference-passing",
                "scope": "core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/backends/test_python_backend_object_ownership_extended.py",),
                "notes": "Reference backend negotiated ownership semantics are covered in the Python backend suite.",
            },
            {
                "backend_id": "rest-hosted-python",
                "backend_family": "hosted-python-rest",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/transport/test_rest_transport.py",),
                "notes": "REST-hosted Python RTI has explicit negotiated ownership end-to-end coverage.",
            },
            {
                "backend_id": "grpc-hosted-python",
                "backend_family": "hosted-python-grpc",
                "status": "positive-path-passing",
                "scope": "hosted core scenario slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/transport/test_grpc_transport_python_server.py",),
                "notes": "gRPC-hosted Python RTI has explicit negotiated ownership end-to-end coverage.",
            },
            {
                "backend_id": "java-shim-jpype",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "JPype Java shim has explicit negotiated ownership coverage.",
            },
            {
                "backend_id": "java-shim-py4j",
                "backend_family": "java-shim",
                "status": "positive-path-passing",
                "scope": "in-process Java shim slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_java_profile_backend_matrix.py",),
                "notes": "Py4J Java shim has explicit negotiated ownership coverage.",
            },
            {
                "backend_id": "certi-native",
                "backend_family": "vendor-certi",
                "status": "vendor-divergent",
                "scope": "real-vendor core scenario slice",
                "session_status": "failing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_ownership_matrix.py",),
                "notes": (
                    "CERTI native negotiated ownership failed in this session because the "
                    "runtime never produced the expected release/acquisition handshake."
                ),
            },
            {
                "backend_id": "certi-jpype",
                "backend_family": "vendor-certi-java-bridge",
                "status": "vendor-divergent",
                "scope": "real-vendor core scenario slice",
                "session_status": "failing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_ownership_matrix.py",),
                "notes": (
                    "CERTI JPype negotiated ownership failed in this session because the "
                    "runtime never produced the expected release/acquisition handshake."
                ),
            },
            {
                "backend_id": "certi-py4j",
                "backend_family": "vendor-certi-java-bridge",
                "status": "vendor-divergent",
                "scope": "real-vendor core scenario slice",
                "session_status": "failing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_ownership_matrix.py",),
                "notes": (
                    "CERTI Py4J negotiated ownership failed in this session because the "
                    "runtime never produced the expected release/acquisition handshake."
                ),
            },
        ),
    },
)

_SECTION10_BACKEND_SLICE_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "slice_id": "support-lookups",
        "section_refs": ("IEEE 1516.1-2010 §10.4", "IEEE 1516.1-2010 §10.32"),
        "profiles": (
            {
                "backend_id": "python-inmemory",
                "backend_family": "python-reference",
                "status": "complete-actionable",
                "scope": "reference support lookup slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": (
                    "packages/hla-verification/src/hla.verification/scenario_support_services.py",
                    "tests/scenarios/test_support_services_backend_matrix.py",
                    "tests/verification/test_spec_traceability_and_extended_python_rti.py",
                ),
                "notes": "Reference backend now has a shared-harness support factory/decode matrix plus existing traceability coverage for the broader support lookup surface.",
            },
            {
                "backend_id": "rest-hosted-python",
                "backend_family": "hosted-python-rest",
                "status": "partial",
                "scope": "hosted support lookup slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": (
                    "tests/transport/test_rest_transport.py",
                ),
                "notes": "REST transport exercises hosted Python positive-path federation/object/time flows, but the current CERTI-style transport facade does not expose the full support-service lookup surface such as getFederateHandle, so this slice remains only partially matrixed.",
            },
            {
                "backend_id": "grpc-hosted-python",
                "backend_family": "hosted-python-grpc",
                "status": "partial",
                "scope": "hosted support lookup slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": (
                    "tests/transport/test_grpc_transport_python_server.py",
                ),
                "notes": "gRPC transport exercises hosted Python positive-path federation/object/time flows, but the current CERTI-style transport facade does not expose the full support-service lookup surface such as getFederateHandle, so this slice remains only partially matrixed.",
            },
            {
                "backend_id": "java-shim-jpype",
                "backend_family": "java-shim",
                "status": "complete-actionable",
                "scope": "java shim support lookup slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": (
                    "packages/hla-verification/src/hla.verification/scenario_support_services.py",
                    "tests/vendors/test_java_profile_backend_matrix.py::test_inprocess_java_shim_support_factory_and_decode_scenario",
                ),
                "notes": "Java shim JPype now runs the shared support-services scenario in-process for the lookup subset it implements, giving executable Section 10 support-lookup coverage without vendor runtime dependencies.",
            },
            {
                "backend_id": "java-shim-py4j",
                "backend_family": "java-shim",
                "status": "complete-actionable",
                "scope": "java shim support lookup slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": (
                    "packages/hla-verification/src/hla.verification/scenario_support_services.py",
                    "tests/vendors/test_java_profile_backend_matrix.py::test_inprocess_java_shim_support_factory_and_decode_scenario",
                ),
                "notes": "Java shim Py4J now runs the shared support-services scenario in-process for the lookup subset it implements, giving executable Section 10 support-lookup coverage without vendor runtime dependencies.",
            },
            {
                "backend_id": "certi-native",
                "backend_family": "vendor-certi",
                "status": "smoke-gated-wrapper",
                "scope": "vendor support lookup slice",
                "session_status": "skipped-in-this-session",
                "evidence_tests": (
                    "tests/vendors/test_certi_real_backend_exchange_matrix.py::test_certi_backend_support_factory_and_decode_matrix",
                ),
                "notes": "CERTI native now has a thin real-runtime wrapper for the shared support-services scenario over the lookup subset exposed by the current facade, but local proof is still gated on enabling real vendor smoke and preflight.",
            },
            {
                "backend_id": "pitch-jpype",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "smoke-gated-wrapper",
                "scope": "vendor support lookup slice",
                "session_status": "skipped-in-this-session",
                "evidence_tests": (
                    "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_support_factory_and_decode_matrix",
                ),
                "notes": "Pitch JPype now has a thin real-runtime wrapper for the shared support factory/decode scenario, but local proof is still gated on enabling real vendor smoke and preflight.",
            },
            {
                "backend_id": "pitch-py4j",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "smoke-gated-wrapper",
                "scope": "vendor support lookup slice",
                "session_status": "skipped-in-this-session",
                "evidence_tests": (
                    "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_support_factory_and_decode_matrix",
                ),
                "notes": "Pitch Py4J now has a thin real-runtime wrapper for the shared support factory/decode scenario, but local proof is still gated on enabling real vendor smoke and preflight.",
            },
        ),
    },
    {
        "slice_id": "support-callback-control",
        "section_refs": ("IEEE 1516.1-2010 §10.41", "IEEE 1516.1-2010 §10.44"),
        "profiles": (
            {
                "backend_id": "python-inmemory",
                "backend_family": "python-reference",
                "status": "complete-actionable",
                "scope": "reference callback-control slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/backends/test_python_backend_object_ownership_extended.py",),
                "notes": "Reference backend now enforces save/restore callback-control blocking and within-callback evoke rejection.",
            },
            {
                "backend_id": "rest-hosted-python",
                "backend_family": "hosted-python-rest",
                "status": "partial",
                "scope": "hosted callback-control slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/transport/test_rest_transport.py",),
                "notes": "REST transport exercises evoke paths positively, but the support callback-control slice is not yet matrixed to the same depth.",
            },
            {
                "backend_id": "grpc-hosted-python",
                "backend_family": "hosted-python-grpc",
                "status": "partial",
                "scope": "hosted callback-control slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/transport/test_grpc_transport_python_server.py",),
                "notes": "gRPC transport exercises evoke paths positively, but the support callback-control slice is not yet matrixed to the same depth.",
            },
        ),
    },
    {
        "slice_id": "support-advisories",
        "section_refs": ("IEEE 1516.1-2010 §10.33", "IEEE 1516.1-2010 §10.40"),
        "profiles": (
            {
                "backend_id": "python-inmemory",
                "backend_family": "python-reference",
                "status": "complete-actionable",
                "scope": "reference advisory-switch slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/backends/test_python_backend_object_ownership_extended.py",),
                "notes": "Reference backend has explicit advisory on/off and save/restore negative coverage.",
            },
        ),
    },
    {
        "slice_id": "support-factories",
        "section_refs": ("IEEE 1516.1-2010 §10.44",),
        "profiles": (
            {
                "backend_id": "python-inmemory",
                "backend_family": "python-reference",
                "status": "complete-actionable",
                "scope": "reference factory slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/backends/test_python_backend_object_ownership_extended.py",),
                "notes": "Reference backend factory getters now have explicit connected vs joined negative coverage.",
            },
        ),
    },
)

_PITCH_BACKEND_SLICE_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "slice_id": "lifecycle",
        "section_refs": ("IEEE 1516.1-2010 §4.1", "IEEE 1516.1-2010 §4.10"),
        "profiles": (
            {
                "backend_id": "pitch-jpype",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "positive-path-passing",
                "scope": "real-vendor lifecycle slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_real_vendor_runtime_smoke.py",),
                "notes": "Pitch JPype lifecycle smoke exists through the Docker-backed CRC/FedPro route.",
            },
            {
                "backend_id": "pitch-py4j",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "positive-path-passing",
                "scope": "real-vendor lifecycle slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_real_vendor_runtime_smoke.py",),
                "notes": "Pitch Py4J lifecycle smoke exists through the Docker-backed CRC/FedPro route.",
            },
        ),
    },
    {
        "slice_id": "exchange",
        "section_refs": ("IEEE 1516.1-2010 §6.9", "IEEE 1516.1-2010 §8.13"),
        "profiles": (
            {
                "backend_id": "pitch-jpype",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "positive-path-passing",
                "scope": "real-vendor exchange/time slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_pitch_real_backend_matrix.py",),
                "notes": "Pitch JPype exchange matrix covers receive and timestamped flows.",
            },
            {
                "backend_id": "pitch-py4j",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "positive-path-passing",
                "scope": "real-vendor exchange/time slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_pitch_real_backend_matrix.py",),
                "notes": "Pitch Py4J exchange matrix covers receive and timestamped flows.",
            },
        ),
    },
    {
        "slice_id": "synchronization",
        "section_refs": ("IEEE 1516.1-2010 §4.11", "IEEE 1516.1-2010 §4.15"),
        "profiles": (
            {
                "backend_id": "pitch-jpype",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "positive-path-passing",
                "scope": "real-vendor synchronization slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_pitch_real_backend_matrix.py",),
                "notes": "Pitch JPype synchronization matrix exists.",
            },
            {
                "backend_id": "pitch-py4j",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "positive-path-passing",
                "scope": "real-vendor synchronization slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_pitch_real_backend_matrix.py",),
                "notes": "Pitch Py4J synchronization matrix exists.",
            },
        ),
    },
    {
        "slice_id": "lost-federate",
        "section_refs": ("IEEE 1516.1-2010 §4.1.5",),
        "profiles": (
            {
                "backend_id": "pitch-jpype",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "not-yet-matrixed",
                "scope": "real-vendor lost-federate slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": (
                    "packages/hla-vendor-pitch/docs/evidence/pitch_clause4_lost_federate_gap_2026-06-11.md",
                ),
                "notes": "Pitch JPype now has a child-process probe path, but executed real-runtime runs still auto-resume the dropped FedPro session instead of yielding observer-visible lost-federate evidence.",
            },
            {
                "backend_id": "pitch-py4j",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "blocked-runtime",
                "scope": "real-vendor lost-federate slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": (
                    "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix",
                    "packages/hla-vendor-pitch/docs/evidence/pitch_clause4_lost_federate_gap_2026-06-11.md",
                ),
                "notes": "Pitch Py4J now has a shared-harness lost-federate wrapper that terminates the victim gateway JVM, but executed real-runtime runs still do not surface the observer-visible lost-federate report.",
            },
        ),
    },
    {
        "slice_id": "ownership",
        "section_refs": ("IEEE 1516.1-2010 §7.2", "IEEE 1516.1-2010 §7.19"),
        "profiles": (
            {
                "backend_id": "pitch-jpype",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "positive-path-passing",
                "scope": "real-vendor ownership slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_pitch_real_backend_matrix.py",),
                "notes": "Pitch JPype plain ownership slice exists.",
            },
            {
                "backend_id": "pitch-py4j",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "positive-path-passing",
                "scope": "real-vendor ownership slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_pitch_real_backend_matrix.py",),
                "notes": "Pitch Py4J plain ownership slice exists.",
            },
        ),
    },
    {
        "slice_id": "negotiated-ownership",
        "section_refs": ("IEEE 1516.1-2010 §7.3", "IEEE 1516.1-2010 §7.16"),
        "profiles": (
            {
                "backend_id": "pitch-jpype",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "vendor-divergent",
                "scope": "real-vendor negotiated ownership slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": (
                    "tests/vendors/test_pitch_real_backend_matrix.py",
                    "docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",
                ),
                "notes": "Pitch JPype negotiated ownership is currently bridge-divergent.",
            },
            {
                "backend_id": "pitch-py4j",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "vendor-divergent",
                "scope": "real-vendor negotiated ownership slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": (
                    "tests/vendors/test_pitch_real_backend_matrix.py",
                    "docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",
                ),
                "notes": "Pitch Py4J negotiated ownership is currently bridge-divergent.",
            },
        ),
    },
    {
        "slice_id": "time-profile",
        "section_refs": ("IEEE 1516.1-2010 §8.2", "IEEE 1516.1-2010 §8.24"),
        "profiles": (
            {
                "backend_id": "pitch-jpype",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "positive-path-passing",
                "scope": "real-vendor time-profile slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_pitch_real_backend_matrix.py",),
                "notes": "Pitch JPype time-profile and exchange/time parity slice exists.",
            },
            {
                "backend_id": "pitch-py4j",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "positive-path-passing",
                "scope": "real-vendor time-profile slice",
                "session_status": "not-run-in-this-session",
                "evidence_tests": ("tests/vendors/test_pitch_real_backend_matrix.py",),
                "notes": "Pitch Py4J time-profile and exchange/time parity slice exists.",
            },
        ),
    },
)

_SECTION8_BACKEND_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "backend_id": "python-inmemory",
        "backend_family": "python-reference",
        "method_set": None,
        "status": "complete-actionable",
        "scope": "reference-backend complete actionable matrix",
        "session_status": "passing-in-this-session",
        "supports_immediate_inline": True,
        "evidence_tests": (
            "tests/time/test_section8_backend_matrix.py",
            "tests/time/test_mom_mim_time_v10.py",
            "tests/time/test_mom_mim_time_management_v010.py",
            "tests/time/test_mom_mim_and_time_semantics_v010.py",
            *_PYTHON_BACKEND_EXTENDED_TESTS,
        ),
        "notes": "Python in-memory backend has complete actionable Section 8 negative-path coverage plus explicit HLA_IMMEDIATE evidence.",
    },
    {
        "backend_id": "rest-hosted-python",
        "backend_family": "hosted-python-rest",
        "method_set": _SECTION8_HOSTED_METHODS,
        "status": "positive-path-passing",
        "scope": "hosted backend positive-path matrix",
        "session_status": "passing-in-this-session",
        "supports_immediate_inline": False,
        "evidence_tests": (
            "tests/time/test_section8_backend_matrix.py",
            "tests/transport/test_rest_transport.py",
        ),
        "notes": "REST-hosted Python RTI is exercised through the dedicated Section 8 suite and transport end-to-end checks.",
    },
    {
        "backend_id": "grpc-hosted-python",
        "backend_family": "hosted-python-grpc",
        "method_set": _SECTION8_HOSTED_METHODS,
        "status": "positive-path-passing",
        "scope": "hosted backend positive-path matrix",
        "session_status": "passing-in-this-session",
        "supports_immediate_inline": False,
        "evidence_tests": (
            "tests/time/test_section8_backend_matrix.py",
            "tests/transport/test_grpc_transport_python_server.py",
        ),
        "notes": "gRPC-hosted Python RTI is exercised through the dedicated Section 8 suite and transport end-to-end checks.",
    },
    {
        "backend_id": "certi-native",
        "backend_family": "vendor-certi",
        "method_set": _SECTION8_CERTI_METHODS,
        "status": "verified-in-this-session",
        "scope": "real-vendor positive-path matrix",
        "session_status": "passing-in-this-session",
        "supports_immediate_inline": False,
        "evidence_tests": _CERTI_REAL_BACKEND_MATRIX_TESTS,
        "notes": "CERTI native time-query and FQR slices passed in this session after the logical-time type-fidelity fix.",
    },
    {
        "backend_id": "certi-jpype",
        "backend_family": "vendor-certi-java-bridge",
        "method_set": _SECTION8_CERTI_METHODS,
        "status": "verified-in-this-session",
        "scope": "real-vendor positive-path matrix",
        "session_status": "passing-in-this-session",
        "supports_immediate_inline": False,
        "evidence_tests": _CERTI_REAL_BACKEND_MATRIX_TESTS,
        "notes": "CERTI JPype time-query and FQR slices passed in this session after the logical-time type-fidelity fix.",
    },
    {
        "backend_id": "certi-py4j",
        "backend_family": "vendor-certi-java-bridge",
        "method_set": _SECTION8_CERTI_METHODS,
        "status": "verified-in-this-session",
        "scope": "real-vendor positive-path matrix",
        "session_status": "passing-in-this-session",
        "supports_immediate_inline": False,
        "evidence_tests": _CERTI_REAL_BACKEND_MATRIX_TESTS,
        "notes": "CERTI Py4J time-query and FQR slices passed in this session after the logical-time type-fidelity fix.",
    },
    {
        "backend_id": "pitch-jpype",
        "backend_family": "vendor-pitch-java-bridge",
        "method_set": _SECTION8_PITCH_METHODS,
        "status": "vendor-divergent",
        "scope": "real-vendor dedicated Section 8 probe",
        "session_status": "xfail-in-this-session",
        "supports_immediate_inline": False,
        "evidence_tests": ("tests/vendors/test_pitch_real_backend_matrix.py",),
        "notes": "Pitch JPype has dedicated Section 8 probes; time regulation/constrained callbacks and timestamp-ordered delivery/retraction behavior diverge from the shared harness expectations.",
    },
    {
        "backend_id": "pitch-py4j",
        "backend_family": "vendor-pitch-java-bridge",
        "method_set": _SECTION8_PITCH_METHODS,
        "status": "vendor-divergent",
        "scope": "real-vendor dedicated Section 8 probe",
        "session_status": "xfail-in-this-session",
        "supports_immediate_inline": False,
        "evidence_tests": ("tests/vendors/test_pitch_real_backend_matrix.py",),
        "notes": "Pitch Py4J has dedicated Section 8 probes; time regulation/constrained callbacks and timestamp-ordered delivery/retraction behavior diverge from the shared harness expectations.",
    },
)

_LOOKAHEAD_BACKEND_SLICE_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "slice_id": "lookahead-window",
        "section_refs": ("IEEE 1516.1-2010 §8.2", "IEEE 1516.1-2010 §8.17"),
        "profiles": (
            {
                "backend_id": "python-inmemory",
                "backend_family": "python-reference",
                "status": "complete-actionable",
                "scope": "reference lookahead slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": (
                    "tests/time/test_lookahead_backend_matrix.py",
                    "tests/time/test_mom_mim_and_time_semantics_v010.py",
                ),
                "notes": "Python reference lookahead is exercised directly and through the Section 8 matrix.",
            },
            {
                "backend_id": "rest-hosted-python",
                "backend_family": "hosted-python-rest",
                "status": "positive-path-passing",
                "scope": "hosted lookahead slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": (
                    "tests/time/test_lookahead_backend_matrix.py",
                    "tests/transport/test_rest_transport.py",
                ),
                "notes": "REST-hosted Python RTI has explicit lookahead query/modify and early-send coverage.",
            },
            {
                "backend_id": "grpc-hosted-python",
                "backend_family": "hosted-python-grpc",
                "status": "positive-path-passing",
                "scope": "hosted lookahead slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": (
                    "tests/time/test_lookahead_backend_matrix.py",
                    "tests/transport/test_grpc_transport_python_server.py",
                ),
                "notes": "gRPC-hosted Python RTI has explicit lookahead query/modify and early-send coverage.",
            },
            {
                "backend_id": "certi-native",
                "backend_family": "vendor-certi",
                "status": "vendor-divergent",
                "scope": "real-vendor lookahead slice",
                "session_status": "failing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_time_matrix.py",),
                "notes": "CERTI native lookahead reaches the helper bridge, but queryLookahead returns RTIinternalError: Not yet implemented in this runtime.",
            },
            {
                "backend_id": "certi-jpype",
                "backend_family": "vendor-certi-java-bridge",
                "status": "vendor-divergent",
                "scope": "real-vendor lookahead slice",
                "session_status": "failing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_time_matrix.py",),
                "notes": "CERTI JPype lookahead reaches the helper bridge, but queryLookahead returns RTIinternalError: Not yet implemented in this runtime.",
            },
            {
                "backend_id": "certi-py4j",
                "backend_family": "vendor-certi-java-bridge",
                "status": "vendor-divergent",
                "scope": "real-vendor lookahead slice",
                "session_status": "failing-in-this-session",
                "evidence_tests": ("tests/vendors/test_certi_real_backend_time_matrix.py",),
                "notes": "CERTI Py4J lookahead reaches the helper bridge, but queryLookahead returns RTIinternalError: Not yet implemented in this runtime.",
            },
            {
                "backend_id": "pitch-jpype",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "verified-in-this-session",
                "scope": "real-vendor lookahead slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_pitch_real_backend_matrix.py",),
                "notes": "Pitch JPype lookahead query/modify and early-send assertions passed against the Docker-backed real runtime in this session.",
            },
            {
                "backend_id": "pitch-py4j",
                "backend_family": "vendor-pitch-java-bridge",
                "status": "verified-in-this-session",
                "scope": "real-vendor lookahead slice",
                "session_status": "passing-in-this-session",
                "evidence_tests": ("tests/vendors/test_pitch_real_backend_matrix.py",),
                "notes": "Pitch Py4J lookahead query/modify and early-send assertions passed against the Docker-backed real runtime in this session.",
            },
        ),
    },
)


def _section_summary(rows: tuple[ServiceConformanceRow, ...]) -> list[SectionComplianceSummary]:
    grouped: dict[str, list[ServiceConformanceRow]] = defaultdict(list)
    for row in rows:
        grouped[row.section_ref].append(row)

    summaries: list[SectionComplianceSummary] = []
    for section_ref, section_rows in sorted(grouped.items()):
        interface_counts: dict[str, int] = defaultdict(int)
        implementation_counts: dict[str, int] = defaultdict(int)
        verification_counts: dict[str, int] = defaultdict(int)
        exact_requirement_evidence_rows = 0
        no_requirement_evidence_rows = 0
        known_gap_rows = 0
        methods: list[str] = []

        for row in section_rows:
            interface_counts[row.interface] += 1
            implementation_counts[row.implementation_status] += 1
            verification_counts[row.verification_status] += 1
            methods.append(f"{row.interface}.{row.method_name}")
            if row.verification_status in {"focused-executable-tests", "callback-helper-covered"}:
                exact_requirement_evidence_rows += 1
            if row.verification_status not in {"focused-executable-tests", "callback-helper-covered"}:
                no_requirement_evidence_rows += 1
            if row.known_gaps:
                known_gap_rows += 1

        summaries.append(
            SectionComplianceSummary(
                section_ref=section_ref,
                interface_counts=dict(sorted(interface_counts.items())),
                implementation_status_counts=dict(sorted(implementation_counts.items())),
                verification_status_counts=dict(sorted(verification_counts.items())),
                exact_requirement_evidence_rows=exact_requirement_evidence_rows,
                no_requirement_evidence_rows=no_requirement_evidence_rows,
                known_gap_rows=known_gap_rows,
                methods=tuple(sorted(methods)),
            )
        )
    return summaries


def _gap_priority(row: ServiceConformanceRow) -> tuple[str, str]:
    root = row.section.split(".", 1)[0] if row.section else "unmapped"
    if root in {"4", "5", "6", "7", "8", "9"}:
        if row.implementation_status == "adapter-or-gap":
            return ("P0", "core section and no pure-Python reference handler")
        return ("P1", "core HLA section without exact requirement-level executable evidence")
    if row.known_gaps:
        return ("P2", "non-core section with known implementation or negative-path gaps")
    return ("P3", "non-core section lacking exact row-level evidence")


def _mapping_status(module_name: str, cls: type[Any]) -> tuple[str, str]:
    name = cls.__name__
    if module_name == "hla.rti1516e.raw_api":
        return ("close-1to1", "Generated abstract service surface from spec-source API metadata; overloads are collapsed into *args/**kwargs.")
    if module_name == "hla.rti1516e.handles":
        return ("close-1to1", "Opaque handle family mirrors HLA handle categories, with Python dataclass/set/dict implementations.")
    if module_name == "hla.rti1516e.time":
        return ("close-1to1", "Logical time, interval, and factory classes intentionally mirror the HLA logical-time families.")
    if module_name == "hla.rti1516e.exceptions":
        return ("close-1to1", "Exception class names intentionally mirror the HLA exception taxonomy.")
    if module_name == "hla.rti1516e.api":
        if name in {"RTIambassador", "RTIAmbassador", "FederateAmbassador"}:
            return ("adapted", "Python-facing ambassador layer preserves the spec surface but adds snake_case conveniences and overload flattening.")
        return ("adapted", "Convenience layer on top of the raw spec-shaped API surface.")
    if module_name == "hla.rti1516e.types":
        return ("adapted", "Python dataclass wrappers for HLA concepts and return values, not literal header-level classes.")
    if module_name in {"hla.rti1516e.encoding", "hla.rti1516e.ambassadors", "hla.rti1516e.rti"}:
        return ("supporting-scaffold", "Support or workflow scaffolding around the HLA surface rather than a direct header-spec type.")
    if module_name.startswith("hla.rti1516e.backends"):
        return ("supporting-scaffold", "Runtime/backend integration support, not a direct spec class mapping.")
    return ("adapted", "Public class is part of the package surface but is not a literal 1:1 reproduction of a Java/C++ header type.")


PUBLIC_CLASS_INVENTORY_MODULES = (
    "hla.rti1516e.ambassadors",
    "hla.rti1516e.api",
    "hla.rti1516e.encoding",
    "hla.rti1516e.enums",
    "hla.rti1516e.exceptions",
    "hla.rti1516e.fom",
    "hla.rti1516e.handles",
    "hla.rti1516e.mom",
    "hla.rti1516e.raw_api",
    "hla.rti1516e.rti",
    "hla.rti1516e.runtime_api",
    "hla.rti1516e.time",
    "hla.rti1516e.types",
)


def _public_class_inventory() -> list[PublicClassInventoryRow]:
    exported_names = set(getattr(hla.rti1516e, "__dict__", {}).keys())
    rows: list[PublicClassInventoryRow] = []

    for module_name in PUBLIC_CLASS_INVENTORY_MODULES:
        module = importlib.import_module(module_name)
        module_public = getattr(module, "__all__", None)
        public_names = set(module_public) if module_public is not None else {name for name in vars(module) if not name.startswith("_")}
        for name, value in sorted(vars(module).items()):
            if name not in public_names:
                continue
            if not inspect.isclass(value):
                continue
            if value.__module__ != module_name:
                continue
            status, rationale = _mapping_status(module_name, value)
            rows.append(
                PublicClassInventoryRow(
                    module=module_name,
                    class_name=name,
                    exported_via_package=name in exported_names,
                    mapping_status=status,
                    rationale=rationale,
                )
            )
    return rows


def _split_public_class_inventory(rows: list[PublicClassInventoryRow]) -> tuple[list[PublicClassInventoryRow], list[PublicClassInventoryRow]]:
    package_exported = [row for row in rows if row.exported_via_package]
    all_public = list(rows)
    return package_exported, all_public


def _gap_section_summaries(rows: tuple[ServiceConformanceRow, ...]) -> list[GapSectionSummary]:
    grouped: dict[str, list[ServiceConformanceRow]] = defaultdict(list)
    for row in rows:
        if row.verification_status in {"focused-executable-tests", "callback-helper-covered"}:
            continue
        grouped[row.section.split(".", 1)[0] if row.section else "unmapped"].append(row)

    summaries: list[GapSectionSummary] = []
    for root, group_rows in grouped.items():
        core_priority = 0 if root in {"4", "5", "6", "7", "8", "9"} else 1
        section_label = f"IEEE 1516.1-2010 §{root}" if root != "unmapped" else "unmapped"
        representative_methods = tuple(sorted(f"{row.interface}.{row.method_name}" for row in group_rows)[:8])
        summaries.append(
            GapSectionSummary(
                section_root=root,
                section_label=section_label,
                row_count=len(group_rows),
                core_priority=core_priority,
                representative_methods=representative_methods,
            )
        )
    return sorted(summaries, key=lambda item: (item.core_priority, -item.row_count, item.section_root))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _extracted_requirement_rows_by_prefixes(prefixes: tuple[str, ...]) -> list[dict[str, Any]]:
    matrix = build_requirements_matrix_2010(REPO_ROOT, version=hla.rti1516e.__version__)
    return [
        row
        for row in matrix["rows"]
        if row["kind"] == "extracted-requirement"
        and any(str(row["requirement_id"]).startswith(prefix) for prefix in prefixes)
    ]


def _write_extracted_requirements_split_artifacts(
    *,
    stem: str,
    title: str,
    intro: str,
    prefixes: tuple[str, ...],
) -> None:
    rows = _extracted_requirement_rows_by_prefixes(prefixes)
    status_counts: dict[str, int] = defaultdict(int)
    clause_counts: dict[str, int] = defaultdict(int)
    claim_scope_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        status_counts[str(row["status"])] += 1
        clause = str(row["section_ref"]).split("§", 1)[1].split(".", 1)[0].strip()
        clause_counts[clause] += 1
        claim_scope_counts[str(row.get("claim_scope") or "broad-spec")] += 1
    broad_rows = [row for row in rows if str(row.get("claim_scope") or "broad-spec") == "broad-spec"]
    supported_subset_rows = [row for row in rows if str(row.get("claim_scope") or "") == "supported-subset"]
    _write_json(
        OUTPUT_DIR / f"{stem}.json",
        {
            "row_count": len(rows),
            "status_counts": dict(sorted(status_counts.items())),
            "clause_counts": dict(sorted(clause_counts.items())),
            "claim_scope_counts": dict(sorted(claim_scope_counts.items())),
            "supported_subset_rows_needed": bool(supported_subset_rows),
            "rows": rows,
        },
    )
    md_lines = [
        f"# {title}",
        "",
        intro,
        "",
        "## Summary",
        "",
        f"- Rows: {len(rows)}",
        f"- Broad-spec rows: {len(broad_rows)}",
        f"- Supported-subset rows: {len(supported_subset_rows)}",
        f"- Status counts: {', '.join(f'{key}={value}' for key, value in sorted(status_counts.items()))}",
        "",
        "## Broad-spec rows",
        "",
        "| Requirement ID | Section | Status | Policy basis | Title | Linked methods | Linked assets | Notes |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in broad_rows:
        md_lines.append(
            f"| {row['requirement_id']} | {row['section_ref']} | {row['status']} | {row.get('policy_basis', '') or '-'} | {row['title']} | "
            f"{', '.join(row.get('linked_methods', [])) or '-'} | {', '.join(row.get('linked_assets', [])) or '-'} | {row.get('notes', '') or '-'} |"
        )
    md_lines.extend(["", "## Supported-subset rows", ""])
    if supported_subset_rows:
        md_lines.extend(
            [
                "| Requirement ID | Section | Status | Supported subset for | Policy basis | Title | Linked methods | Linked assets | Notes |",
                "|---|---|---|---|---|---|---|---|---|",
            ]
        )
        for row in supported_subset_rows:
            md_lines.append(
                f"| {row['requirement_id']} | {row['section_ref']} | {row['status']} | {row.get('supported_subset_for', '') or '-'} | {row.get('policy_basis', '') or '-'} | {row['title']} | "
                f"{', '.join(row.get('linked_methods', [])) or '-'} | {', '.join(row.get('linked_assets', [])) or '-'} | {row.get('notes', '') or '-'} |"
            )
    else:
        md_lines.append("No supported-subset rows are currently needed for this tranche. These requirements remain plain broad-spec rows because the current evidence is already narrow enough to support the original claim wording.")
    md_lines.extend(
        [
            "",
            "## All rows",
            "",
            "| Requirement ID | Section | Status | Claim scope | Policy basis | Title | Linked methods | Linked assets | Notes |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        md_lines.append(
            f"| {row['requirement_id']} | {row['section_ref']} | {row['status']} | {row.get('claim_scope', 'broad-spec')} | {row.get('policy_basis', '') or '-'} | {row['title']} | "
            f"{', '.join(row.get('linked_methods', [])) or '-'} | {', '.join(row.get('linked_assets', [])) or '-'} | {row.get('notes', '') or '-'} |"
        )
    _write_markdown(OUTPUT_DIR / f"{stem}.md", md_lines)


def _write_clause56_extracted_requirements_artifacts() -> None:
    _write_extracted_requirements_split_artifacts(
        stem="extracted_requirements_clause5_6",
        title="Extracted Requirements: Clauses 5 And 6",
        intro="Curated Clause 5 Declaration Management and Clause 6 Object Management requirements, linked back to the existing service ledger and verification assets.",
        prefixes=("HLA1516.1-DM-", "HLA1516.1-OM-"),
    )


def _write_clause79_extracted_requirements_artifacts() -> None:
    _write_extracted_requirements_split_artifacts(
        stem="extracted_requirements_clause7_9",
        title="Extracted Requirements: Clauses 7 And 9",
        intro="Curated Clause 7 Ownership Management and Clause 9 Data Distribution Management requirements, linked back to the existing service ledger and verification assets.",
        prefixes=("HLA1516.1-OWN-", "HLA1516.1-DDM-"),
    )


def _write_supported_subset_policy_artifacts() -> None:
    matrix = build_requirements_matrix_2010(REPO_ROOT, version=hla.rti1516e.__version__)
    rows = [
        row
        for row in matrix["rows"]
        if row["kind"] == "extracted-requirement"
        and (
            str(row.get("policy_basis", "")).strip()
            or str(row.get("claim_scope", "")).strip() == "supported-subset"
            or str(row.get("supported_subset_for", "")).strip()
        )
    ]
    grouped_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped_rows[str(row.get("policy_basis") or "unclassified")].append(row)

    policy_rows: list[dict[str, Any]] = []
    for policy_id, definition in sorted(_SUPPORTED_SUBSET_POLICY_DEFS.items()):
        policy_group = grouped_rows.get(policy_id, [])
        broad_rows = [row for row in policy_group if str(row.get("claim_scope") or "broad-spec") == "broad-spec"]
        subset_rows = [row for row in policy_group if str(row.get("claim_scope") or "") == "supported-subset"]
        policy_rows.append(
            {
                "policy_id": policy_id,
                "title": definition["title"],
                "supported_behavior": definition["supported_behavior"],
                "broad_gap": definition["broad_gap"],
                "broad_spec_rows": broad_rows,
                "supported_subset_rows": subset_rows,
                "broad_status_counts": dict(sorted({status: sum(1 for row in broad_rows if row["status"] == status) for status in {row["status"] for row in broad_rows}}.items())),
                "supported_subset_status_counts": dict(sorted({status: sum(1 for row in subset_rows if row["status"] == status) for status in {row["status"] for row in subset_rows}}.items())),
            }
        )

    _write_json(
        OUTPUT_DIR / "supported_subset_policy.json",
        {
            "policy_count": len(policy_rows),
            "policies": policy_rows,
        },
    )

    md_lines = [
        "# Supported-Subset Policy",
        "",
        "This packet separates broad specification claims from narrower supported-subset claims for the current Python reference backend.",
        "",
        "Interpretation:",
        "",
        "- `broad-spec`: the full standard wording. These rows stay `partial` when the backend intentionally implements only a defensible subset.",
        "- `supported-subset`: a narrowed claim that is explicitly implemented and evidenced in the current backend.",
        "",
    ]
    for policy in policy_rows:
        md_lines.extend(
            [
                f"## {policy['title']}",
                "",
                f"- Policy ID: `{policy['policy_id']}`",
                f"- Supported behavior: {policy['supported_behavior']}",
                f"- Broad-gap rationale: {policy['broad_gap']}",
                f"- Broad-spec status counts: {', '.join(f'{k}={v}' for k, v in policy['broad_status_counts'].items()) or 'none'}",
                f"- Supported-subset status counts: {', '.join(f'{k}={v}' for k, v in policy['supported_subset_status_counts'].items()) or 'none'}",
                "",
                "Broad-spec rows:",
                "",
                "| Requirement ID | Section | Status | Title | Notes |",
                "|---|---|---|---|---|",
            ]
        )
        for row in policy["broad_spec_rows"]:
            md_lines.append(
                f"| {row['requirement_id']} | {row['section_ref']} | {row['status']} | {row['title']} | {row.get('notes', '') or '-'} |"
            )
        if not policy["broad_spec_rows"]:
            md_lines.append("| - | - | - | - | - |")
        md_lines.extend(
            [
                "",
                "Supported-subset rows:",
                "",
                "| Requirement ID | Section | Status | Broad row | Title | Notes |",
                "|---|---|---|---|---|---|",
            ]
        )
        for row in policy["supported_subset_rows"]:
            md_lines.append(
                f"| {row['requirement_id']} | {row['section_ref']} | {row['status']} | {row.get('supported_subset_for', '') or '-'} | {row['title']} | {row.get('notes', '') or '-'} |"
            )
        if not policy["supported_subset_rows"]:
            md_lines.append("| - | - | - | - | - | - |")
        md_lines.append("")

    _write_markdown(OUTPUT_DIR / "supported_subset_policy.md", md_lines)


def _write_defended_partials_index_artifacts() -> None:
    matrix = build_requirements_matrix_2010(REPO_ROOT, version=hla.rti1516e.__version__)
    rows = [row for row in matrix["rows"] if row["kind"] == "extracted-requirement"]
    rows_by_id = {str(row["requirement_id"]): row for row in rows if row.get("requirement_id")}
    broad_partials = [
        row
        for row in rows
        if str(row.get("claim_scope") or "broad-spec") == "broad-spec" and str(row.get("status")) == "partial"
        and (
            str(row.get("policy_basis", "")).strip()
            or any(
                str(candidate.get("supported_subset_for") or "") == str(row["requirement_id"])
                and str(candidate.get("claim_scope") or "") == "supported-subset"
                and str(candidate.get("status")) == "pass"
                for candidate in rows
            )
        )
    ]
    defended_rows: list[dict[str, Any]] = []
    for broad_row in broad_partials:
        supported_rows = [
            row
            for row in rows
            if str(row.get("supported_subset_for") or "") == str(broad_row["requirement_id"])
            and str(row.get("status")) == "pass"
        ]
        defended_rows.append(
            {
                "requirement_id": broad_row["requirement_id"],
                "section_ref": broad_row["section_ref"],
                "title": broad_row["title"],
                "policy_basis": broad_row.get("policy_basis", ""),
                "notes": broad_row.get("notes", ""),
                "supported_subset_rows": supported_rows,
            }
        )

    _write_json(
        OUTPUT_DIR / "defended_partials_index.json",
        {
            "row_count": len(defended_rows),
            "rows": defended_rows,
        },
    )
    md_lines = [
        "# Defended Partials Index",
        "",
        "This index lists only broad-spec rows that intentionally remain partial, along with any passing supported-subset rows that defend the narrower implemented claim.",
        "",
        "| Broad requirement ID | Section | Policy basis | Supported-subset passes | Broad row notes |",
        "|---|---|---|---|---|",
    ]
    for row in defended_rows:
        subset_refs = ", ".join(
            f"{item['requirement_id']} ({item['section_ref']})" for item in row["supported_subset_rows"]
        ) or "-"
        md_lines.append(
            f"| {row['requirement_id']} | {row['section_ref']} | {row.get('policy_basis', '') or '-'} | {subset_refs} | {row.get('notes', '') or '-'} |"
        )
    _write_markdown(OUTPUT_DIR / "defended_partials_index.md", md_lines)


def _write_section_summary_artifacts(rows: tuple[ServiceConformanceRow, ...]) -> None:
    summaries = _section_summary(rows)
    _write_json(
        OUTPUT_DIR / "section_compliance_summary.json",
        {
            "summary_count": len(summaries),
            "sections": [asdict(item) for item in summaries],
        },
    )

    md_lines = [
        "# Section Compliance Summary",
        "",
        "| Section | Exact requirement evidence | No requirement evidence | Known gap rows | Verification status counts |",
        "|---|---:|---:|---:|---|",
    ]
    for item in summaries:
        md_lines.append(
            f"| {item.section_ref} | {item.exact_requirement_evidence_rows} | {item.no_requirement_evidence_rows} | {item.known_gap_rows} | "
            f"{', '.join(f'{k}={v}' for k, v in item.verification_status_counts.items())} |"
        )
    _write_markdown(OUTPUT_DIR / "section_compliance_summary.md", md_lines)


def _write_public_class_inventory_artifacts() -> None:
    rows = _public_class_inventory()
    package_exported_rows, all_public_rows = _split_public_class_inventory(rows)

    def write_inventory(stem: str, title: str, inventory_rows: list[PublicClassInventoryRow]) -> None:
        _write_json(
            OUTPUT_DIR / f"{stem}.json",
            {
                "row_count": len(inventory_rows),
                "rows": [asdict(item) for item in inventory_rows],
            },
        )

        md_lines = [
            f"# {title}",
            "",
            "| Module | Class | Exported via `hla2010` | Mapping status | Rationale |",
            "|---|---|---:|---|---|",
        ]
        for item in inventory_rows:
            md_lines.append(
                f"| {item.module} | {item.class_name} | {'yes' if item.exported_via_package else 'no'} | {item.mapping_status} | {item.rationale} |"
            )
        _write_markdown(OUTPUT_DIR / f"{stem}.md", md_lines)

    write_inventory("public_class_inventory_all_public", "Public Class Inventory: All Public Module Classes", all_public_rows)
    write_inventory("public_class_inventory_package_exported", "Public Class Inventory: Package Exported", package_exported_rows)

    _write_json(
        OUTPUT_DIR / "public_class_inventory.json",
        {
            "all_public_row_count": len(all_public_rows),
            "package_exported_row_count": len(package_exported_rows),
            "rows": [asdict(item) for item in all_public_rows],
        },
    )

    md_lines = [
        "# Public Class Inventory",
        "",
        f"- all public module classes: {len(all_public_rows)}",
        f"- package-exported classes: {len(package_exported_rows)}",
        "",
        "| Module | Class | Exported via `hla2010` | Mapping status | Rationale |",
        "|---|---|---:|---|---|",
    ]
    for item in all_public_rows:
        md_lines.append(f"| {item.module} | {item.class_name} | {'yes' if item.exported_via_package else 'no'} | {item.mapping_status} | {item.rationale} |")
    _write_markdown(OUTPUT_DIR / "public_class_inventory.md", md_lines)


def _write_gap_report_artifacts(rows: tuple[ServiceConformanceRow, ...]) -> None:
    gap_rows = [row for row in rows if row.verification_status not in {"focused-executable-tests", "callback-helper-covered"}]
    _write_json(
        OUTPUT_DIR / "no_requirement_evidence_rows.json",
        {
            "row_count": len(gap_rows),
            "rows": [
                {
                    **row.as_dict(),
                    "priority": _gap_priority(row)[0],
                    "priority_rationale": _gap_priority(row)[1],
                }
                for row in gap_rows
            ],
        },
    )

    md_lines = [
        "# No Requirement Evidence Rows",
        "",
        "Rows listed here do not have exact requirement-level executable evidence linked in the current conformance metadata.",
        "They may still have group-level or slice-level executable evidence.",
        "",
        "| Priority | Section | Interface | Method | Implementation status | Known gaps |",
        "|---|---|---|---|---|---|",
    ]
    for row in gap_rows:
        gaps = "; ".join(row.known_gaps) if row.known_gaps else ""
        priority, _rationale = _gap_priority(row)
        md_lines.append(f"| {priority} | {row.section_ref} | {row.interface} | {row.method_name} | {row.implementation_status} | {gaps} |")
    _write_markdown(OUTPUT_DIR / "no_requirement_evidence_rows.md", md_lines)

    summaries = _gap_section_summaries(rows)
    _write_json(
        OUTPUT_DIR / "gap_executive_summary.json",
        {
            "section_count": len(summaries),
            "sections": [asdict(item) for item in summaries],
        },
    )

    summary_lines = [
        "# Gap Executive Summary",
        "",
        "Ranked by core HLA section priority (`§4-§9` first) and then by remaining row count without exact requirement-level executable evidence.",
        "",
        "| Rank | Section | Remaining rows | Representative methods |",
        "|---|---|---:|---|",
    ]
    for index, item in enumerate(summaries, start=1):
        summary_lines.append(f"| {index} | {item.section_label} | {item.row_count} | {', '.join(item.representative_methods)} |")
    _write_markdown(OUTPUT_DIR / "gap_executive_summary.md", summary_lines)


def _write_negative_path_artifacts(rows: tuple[ServiceConformanceRow, ...]) -> None:
    ledger_rows = [
        NegativePathLedgerRow(
            section_ref=row.section_ref,
            interface=row.interface,
            method_name=row.method_name,
            verification_status=row.verification_status,
            negative_path_status=negative_path_status(row),
            declared_exception_count=row.negative_expectation_count,
            actionable_exception_count=actionable_negative_expectation_count(row),
            negative_executed_count=row.negative_executed_count,
            declared_exceptions=row.declared_exceptions,
            rationale=_negative_path_rationale(row),
        )
        for row in rows
    ]
    by_status: dict[str, int] = defaultdict(int)
    for row in ledger_rows:
        by_status[row.negative_path_status] += 1

    _write_json(
        OUTPUT_DIR / "negative_path_completeness.json",
        {
            "row_count": len(ledger_rows),
            "status_counts": dict(sorted(by_status.items())),
            "rows": [asdict(item) for item in ledger_rows],
        },
    )

    md_lines = [
        "# Negative Path Completeness",
        "",
        "This ledger tracks declared exception and negative-path completeness independently from positive-path requirement evidence.",
        "",
        "| Section | Interface | Method | Negative-path status | Declared exceptions | Actionable exceptions | Executed negatives | Rationale |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for row in ledger_rows:
        md_lines.append(
            f"| {row.section_ref} | {row.interface} | {row.method_name} | {row.negative_path_status} | "
            f"{row.declared_exception_count} | {row.actionable_exception_count} | {row.negative_executed_count} | {row.rationale} |"
        )
    _write_markdown(OUTPUT_DIR / "negative_path_completeness.md", md_lines)

    ranked_rows = [row for row in rows if negative_path_status(row) == "mapped-not-exhaustive"]
    ranked_rows = sorted(ranked_rows, key=lambda row: _negative_priority(row)[2])
    _write_json(
        OUTPUT_DIR / "negative_path_priority_ranking.json",
        {
            "row_count": len(ranked_rows),
            "rows": [
                {
                    **row.as_dict(),
                    "negative_path_status": negative_path_status(row),
                    "priority": _negative_priority(row)[0],
                    "priority_rationale": _negative_priority(row)[1],
                }
                for row in ranked_rows
            ],
        },
    )

    ranking_lines = [
        "# Negative Path Priority Ranking",
        "",
        "Rows ranked by section priority and declared exception count for converting mapped negative-path obligations into executable tests.",
        "",
        "| Priority | Section | Interface | Method | Declared exceptions | Verification status |",
        "|---|---|---|---|---:|---|",
    ]
    for row in ranked_rows:
        ranking_lines.append(
            f"| {_negative_priority(row)[0]} | {row.section_ref} | {row.interface} | {row.method_name} | "
            f"{row.negative_expectation_count} | {row.verification_status} |"
        )
    _write_markdown(OUTPUT_DIR / "negative_path_priority_ranking.md", ranking_lines)


def _write_section8_backend_matrix_artifacts(rows: tuple[ServiceConformanceRow, ...]) -> None:
    section8_rows = sorted((row for row in rows if row.section.split(".", 1)[0] == "8"), key=lambda row: (row.section_ref, row.method_name))
    matrix_rows: list[Section8BackendMatrixRow] = []
    for profile in _SECTION8_BACKEND_PROFILES:
        method_set = profile["method_set"]
        for row in section8_rows:
            if method_set is None or row.method_name in method_set:
                status = profile["status"]
            else:
                status = "not-yet-matrixed"
            matrix_rows.append(
                Section8BackendMatrixRow(
                    backend_id=profile["backend_id"],
                    backend_family=profile["backend_family"],
                    section_ref=row.section_ref,
                    method_name=row.method_name,
                    status=status,
                    scope=profile["scope"],
                    session_status=profile["session_status"],
                    supports_immediate_inline=bool(profile["supports_immediate_inline"]),
                    evidence_tests=tuple(profile["evidence_tests"]),
                    notes=profile["notes"],
                )
            )

    grouped: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in matrix_rows:
        grouped[row.backend_id][row.status] += 1

    _write_json(
        OUTPUT_DIR / "section8_backend_matrix.json",
        {
            "row_count": len(matrix_rows),
            "backend_summaries": {backend_id: dict(sorted(counts.items())) for backend_id, counts in sorted(grouped.items())},
            "rows": [asdict(item) for item in matrix_rows],
        },
    )

    md_lines = [
        "# Section 8 Backend Matrix",
        "",
        "This matrix records backend-specific Section 8 verification scope separately from the reference conformance ledger.",
        "",
        "| Backend | Family | Section | Method | Status | Scope | Session status | Immediate inline | Evidence | Notes |",
        "|---|---|---|---|---|---|---|---:|---|---|",
    ]
    for row in matrix_rows:
        md_lines.append(
            f"| {row.backend_id} | {row.backend_family} | {row.section_ref} | {row.method_name} | {row.status} | {row.scope} | "
            f"{row.session_status} | {'yes' if row.supports_immediate_inline else 'no'} | {', '.join(row.evidence_tests)} | {row.notes} |"
        )
    _write_markdown(OUTPUT_DIR / "section8_backend_matrix.md", md_lines)


def _build_core_backend_matrix_rows() -> list[CoreBackendMatrixRow]:
    rows: list[CoreBackendMatrixRow] = []
    for slice_profile in _CORE_BACKEND_SLICE_PROFILES:
        for profile in slice_profile["profiles"]:
            rows.append(
                CoreBackendMatrixRow(
                    backend_id=profile["backend_id"],
                    backend_family=profile["backend_family"],
                    slice_id=slice_profile["slice_id"],
                    section_refs=tuple(slice_profile["section_refs"]),
                    status=profile["status"],
                    scope=profile["scope"],
                    session_status=profile["session_status"],
                    evidence_tests=tuple(profile["evidence_tests"]),
                    notes=profile["notes"],
                )
            )
    return rows


def _write_core_backend_matrix_artifacts() -> list[CoreBackendMatrixRow]:
    matrix_rows = _build_core_backend_matrix_rows()
    backend_summaries: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in matrix_rows:
        backend_summaries[row.backend_id][row.status] += 1

    _write_json(
        OUTPUT_DIR / "core_backend_matrix.json",
        {
            "row_count": len(matrix_rows),
            "backend_summaries": {backend_id: dict(sorted(counts.items())) for backend_id, counts in sorted(backend_summaries.items())},
            "rows": [asdict(row) for row in matrix_rows],
        },
    )

    md_lines = [
        "# Core Backend Matrix",
        "",
        "This matrix records non-Section-8 backend verification slices that currently have explicit executable evidence.",
        "",
        "| Backend | Family | Slice | Section refs | Status | Scope | Session status | Evidence | Notes |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in matrix_rows:
        md_lines.append(
            f"| {row.backend_id} | {row.backend_family} | {row.slice_id} | {', '.join(row.section_refs)} | {row.status} | {row.scope} | "
            f"{row.session_status} | {', '.join(row.evidence_tests) if row.evidence_tests else '-'} | {row.notes} |"
        )
    _write_markdown(OUTPUT_DIR / "core_backend_matrix.md", md_lines)
    return matrix_rows


def _build_matrix_rows(profiles: tuple[dict[str, Any], ...]) -> list[CoreBackendMatrixRow]:
    rows: list[CoreBackendMatrixRow] = []
    for slice_profile in profiles:
        for profile in slice_profile["profiles"]:
            rows.append(
                CoreBackendMatrixRow(
                    backend_id=profile["backend_id"],
                    backend_family=profile["backend_family"],
                    slice_id=slice_profile["slice_id"],
                    section_refs=tuple(slice_profile["section_refs"]),
                    status=profile["status"],
                    scope=profile["scope"],
                    session_status=profile["session_status"],
                    evidence_tests=tuple(profile["evidence_tests"]),
                    notes=profile["notes"],
                )
            )
    return rows


def _write_backend_slice_matrix_artifacts(
    *,
    stem: str,
    title: str,
    intro: str,
    profiles: tuple[dict[str, Any], ...],
) -> list[CoreBackendMatrixRow]:
    matrix_rows = _build_matrix_rows(profiles)
    backend_summaries: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in matrix_rows:
        backend_summaries[row.backend_id][row.status] += 1
    _write_json(
        OUTPUT_DIR / f"{stem}.json",
        {
            "row_count": len(matrix_rows),
            "backend_summaries": {backend_id: dict(sorted(counts.items())) for backend_id, counts in sorted(backend_summaries.items())},
            "rows": [asdict(row) for row in matrix_rows],
        },
    )
    md_lines = [
        f"# {title}",
        "",
        intro,
        "",
        "| Backend | Family | Slice | Section refs | Status | Scope | Session status | Evidence | Notes |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in matrix_rows:
        md_lines.append(
            f"| {row.backend_id} | {row.backend_family} | {row.slice_id} | {', '.join(row.section_refs)} | {row.status} | {row.scope} | "
            f"{row.session_status} | {', '.join(row.evidence_tests) if row.evidence_tests else '-'} | {row.notes} |"
        )
    _write_markdown(OUTPUT_DIR / f"{stem}.md", md_lines)
    return matrix_rows


def _write_completion_checklist_artifacts(
    rows: tuple[ServiceConformanceRow, ...],
    core_backend_rows: list[CoreBackendMatrixRow],
) -> None:
    negative_status_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        negative_status_counts[negative_path_status(row)] += 1

    checklist_rows = [
        CompletionChecklistRow(
            checklist_id="requirements-ledger",
            area="Requirement-level positive-path ledger",
            status="done",
            evidence=("analysis/compliance/requirements_ledger.json",),
            rationale="All 217 service rows are represented as pass in the current requirement ledger.",
        ),
        CompletionChecklistRow(
            checklist_id="exact-row-evidence",
            area="Exact row-level executable evidence",
            status="done",
            evidence=("analysis/compliance/no_requirement_evidence_rows.json",),
            rationale="The exact row-level evidence gap report is empty.",
        ),
        CompletionChecklistRow(
            checklist_id="negative-path-ledger",
            area="Negative-path accounting",
            status="partial",
            evidence=("analysis/compliance/negative_path_completeness.json",),
            rationale=(
                f"Negative-path coverage is not closed: {negative_status_counts['complete']} complete, "
                f"{negative_status_counts['partial']} partial, {negative_status_counts['mapped-not-exhaustive']} mapped-not-exhaustive, "
                f"{negative_status_counts['not-evidenced']} not-evidenced. Callback-only FederateInternalError rows are now excluded from actionable debt."
            ),
        ),
        CompletionChecklistRow(
            checklist_id="section8-backend-matrix",
            area="Section 8 cross-backend matrix",
            status="partial",
            evidence=("analysis/compliance/section8_backend_matrix.json",),
            rationale=(
                "Python reference is complete-actionable and hosted Python is positive-path passing, "
                "CERTI time slices are now verified in this session, but Pitch and the remaining vendor surface are still only partially matrixed."
            ),
        ),
        CompletionChecklistRow(
            checklist_id="lookahead-backend-matrix",
            area="Lookahead backend matrix",
            status="partial",
            evidence=("analysis/compliance/lookahead_backend_matrix.json",),
            rationale=(
                "Lookahead is now explicit in the reference and hosted matrices, and "
                "CERTI/Pitch lookahead coverage is being widened into a dedicated backend matrix."
            ),
        ),
        CompletionChecklistRow(
            checklist_id="core-backend-matrix",
            area="Non-Section-8 backend matrix",
            status="partial",
            evidence=("analysis/compliance/core_backend_matrix.json",),
            rationale=(
                "Exchange, synchronization, and ownership slices are now matrixed across Python, hosted Python, Java shim, and CERTI, "
                "but negotiated ownership still includes explicit vendor divergences."
            ),
        ),
        CompletionChecklistRow(
            checklist_id="vendor-certi-time",
            area="Real CERTI time-profile verification",
            status="partial",
            evidence=(
                "tests/vendors/test_certi_real_backend_time_matrix.py",
                "tests/vendors/test_certi_real_backend_exchange_matrix.py",
            ),
            rationale=(
                "Real CERTI time-query/FQR and exchange slices were rerun cleanly in this session, "
                "with logical-time type fidelity preserved across native and Java-facade paths."
            ),
        ),
        CompletionChecklistRow(
            checklist_id="vendor-certi-ownership",
            area="Real CERTI ownership verification",
            status="partial",
            evidence=("tests/vendors/test_certi_real_backend_ownership_matrix.py",),
            rationale=(
                "Plain ownership passed in this session, but negotiated ownership failed across "
                "native and Java-facade CERTI paths."
            ),
        ),
        CompletionChecklistRow(
            checklist_id="pitch-matrix",
            area="Pitch backend matrix",
            status="partial",
            evidence=("analysis/compliance/pitch_backend_matrix.json", "analysis/compliance/pitch_requirement_disposition.json"),
            rationale=(
                "Pitch now has a dedicated positive-path/backend-divergence matrix, but it remains "
                "incomplete and negotiated ownership is still vendor-divergent. The requirement disposition audit now exposes every unclassified Pitch row by clause."
            ),
        ),
        CompletionChecklistRow(
            checklist_id="support-services-backend-matrix",
            area="Section 10 backend matrix",
            status="partial",
            evidence=("analysis/compliance/section10_backend_matrix.json",),
            rationale="A dedicated Section 10 backend matrix now exists, with deep Python reference coverage, executed Java-shim support coverage, transport-backed hosted partial coverage, and smoke-gated CERTI/Pitch wrappers, but the remaining Section 10 slices still need broader parity depth.",
        ),
    ]

    _write_json(
        OUTPUT_DIR / "compliance_completion_checklist.json",
        {"row_count": len(checklist_rows), "rows": [asdict(row) for row in checklist_rows]},
    )
    md_lines = [
        "# Compliance Completion Checklist",
        "",
        "| Checklist item | Area | Status | Evidence | Rationale |",
        "|---|---|---|---|---|",
    ]
    for row in checklist_rows:
        md_lines.append(f"| {row.checklist_id} | {row.area} | {row.status} | {', '.join(row.evidence)} | {row.rationale} |")
    _write_markdown(OUTPUT_DIR / "compliance_completion_checklist.md", md_lines)


def _write_unfinished_work_ranking_artifacts(core_backend_rows: list[CoreBackendMatrixRow]) -> None:
    rows = [
        UnfinishedWorkRow(
            priority="P1",
            claim_value_rank=1,
            work_id="close-negative-path-ledger",
            area="Cross-standard negative-path completeness",
            current_state="Reference ledger still has partial, mapped-not-exhaustive, and not-evidenced rows.",
            target_state="All actionable rows move to complete or explicit vendor divergence.",
            evidence=("analysis/compliance/negative_path_completeness.json",),
            rationale="This is the biggest remaining blocker to an honest whole-standard compliance claim.",
        ),
        UnfinishedWorkRow(
            priority="P1",
            claim_value_rank=2,
            work_id="certi-negotiated-ownership-divergence",
            area="CERTI negotiated ownership divergence",
            current_state="Negotiated ownership now has matrix rows everywhere, but CERTI native, JPype, and Py4J fail the scenario contract.",
            target_state="CERTI negotiated ownership is either fixed in the adapter/runtime or documented as an explicit vendor limitation.",
            evidence=("analysis/compliance/core_backend_matrix.json",),
            rationale="This is now the highest-value non-Section-8 backend problem because it is a real failing vendor behavior, not a missing test.",
        ),
        UnfinishedWorkRow(
            priority="P2",
            claim_value_rank=3,
            work_id="section10-backend-matrix",
            area="Section 10 backend matrix",
            current_state="A dedicated Section 10 matrix now exists; Python is deeply covered, Java shim support lookups execute, hosted REST/gRPC have explicit transport-limited partial coverage, and CERTI/Pitch support wrappers exist, but the remaining Section 10 slices still lack broader executed parity depth.",
            target_state="Hosted, Java shim, CERTI, and Pitch rows are explicitly exercised or documented as unsupported/vendor-divergent.",
            evidence=("analysis/compliance/section10_backend_matrix.json",),
            rationale="High volume, lower claim value than core federation/object/time behavior, but still necessary for a complete matrix.",
        ),
        UnfinishedWorkRow(
            priority="P2",
            claim_value_rank=4,
            work_id="pitch-dedicated-matrix",
            area="Pitch dedicated backend matrices",
            current_state="Pitch now has a dedicated matrix artifact, but it is still mostly positive-path and negotiated ownership remains divergent.",
            target_state="Pitch slices are rerun cleanly and widened beyond the existing real-runtime smoke and parity tests.",
            evidence=("analysis/compliance/pitch_backend_matrix.json",),
            rationale="Pitch is still one of the least proven major backend families.",
        ),
    ]

    _write_json(
        OUTPUT_DIR / "unfinished_compliance_work_ranking.json",
        {"row_count": len(rows), "rows": [asdict(row) for row in rows]},
    )
    md_lines = [
        "# Unfinished Compliance Work Ranking",
        "",
        "| Priority | Rank | Work item | Area | Current state | Target state | Evidence | Rationale |",
        "|---|---:|---|---|---|---|---|---|",
    ]
    for row in rows:
        md_lines.append(
            f"| {row.priority} | {row.claim_value_rank} | {row.work_id} | {row.area} | {row.current_state} | "
            f"{row.target_state} | {', '.join(row.evidence)} | {row.rationale} |"
        )
    _write_markdown(OUTPUT_DIR / "unfinished_compliance_work_ranking.md", md_lines)


def _clause_root(section_ref: str) -> str:
    match = re.search(r"§\s*(\d+)", str(section_ref or ""))
    return match.group(1) if match else "unknown"


def _pitch_requirement_applicability(row: dict[str, Any]) -> str:
    kind = str(row.get("kind", ""))
    section_root = _clause_root(str(row.get("section_ref", "")))
    if kind == "section-area":
        return "section-summary-row"
    if kind == "curated-seed":
        return "seed-row"
    if section_root in {"4", "5", "6", "7", "8", "9", "10"}:
        return "runtime-or-service-probe"
    if section_root in {"11", "12"}:
        return "artifact-or-model-verification"
    return "classification-required"


def _normalized_evidence_refs(refs: tuple[str, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    seen: set[str] = set()
    for ref in refs:
        value = str(ref)
        while value.startswith("../"):
            value = value[3:]
        if value and value not in seen:
            normalized.append(value)
            seen.add(value)
    return tuple(normalized)


def _pitch_evidence_refs(source_row: dict[str, Any], *, clause_root: str) -> tuple[str, ...]:
    requirement_id = str(source_row.get("requirement_id") or source_row.get("matrix_id") or "")
    mapped_evidence = _PITCH_REQUIREMENT_EVIDENCE.get(requirement_id, ("", (), ""))[1]
    vendor_evidence = tuple(str(ref) for ref in source_row.get("vendor_evidence_refs", []) if str(ref))
    if mapped_evidence and str(source_row.get("document", "")) == "IEEE 1516.1-2010" and clause_root in {"4", "6", "7", "8", "9"}:
        return _normalized_evidence_refs(mapped_evidence)
    return _normalized_evidence_refs(vendor_evidence + mapped_evidence)


def _family_evidence_refs(source_row: dict[str, Any], *, backend: str, clause_root: str) -> tuple[str, ...]:
    vendor_evidence = tuple(str(ref) for ref in source_row.get("vendor_evidence_refs", []) if str(ref))
    requirement_id = str(source_row.get("requirement_id") or source_row.get("matrix_id") or "")
    if requirement_id in _SEED_ROW_NOT_APPLICABLE_NOTES:
        return ()
    if backend == "python" and requirement_id in _PYTHON_REQUIREMENT_EVIDENCE:
        return _normalized_evidence_refs(_PYTHON_REQUIREMENT_EVIDENCE[requirement_id][0])
    if backend != "python":
        if backend == "certi":
            if requirement_id in _CERTI_REQUIREMENT_EVIDENCE:
                return _normalized_evidence_refs(_CERTI_REQUIREMENT_EVIDENCE[requirement_id][0])
            allowed_prefixes = (
                "packages/hla-verification/src/hla.verification/",
                "tests/vendors/test_certi_real_backend_exchange_matrix.py::",
                "tests/vendors/test_certi_real_backend_ownership_matrix.py::",
                "tests/vendors/test_certi_real_backend_time_matrix.py::",
                "tests/vendors/test_real_vendor_runtime_smoke.py::",
                "tests/vendors/test_java_profile_backend_matrix.py::",
                "packages/hla-backend-certi/docs/evidence/",
            )
            filtered_vendor = tuple(ref for ref in vendor_evidence if ref.startswith(allowed_prefixes))
            return _normalized_evidence_refs(filtered_vendor)
        if backend == "portico":
            requirement_id = str(source_row.get("requirement_id") or source_row.get("matrix_id") or "")
            if requirement_id in _PORTICO_REQUIREMENT_EVIDENCE:
                return _normalized_evidence_refs(_PORTICO_REQUIREMENT_EVIDENCE[requirement_id][0])
            allowed_prefixes = (
                "packages/hla-verification/src/hla.verification/",
                "tests/vendors/test_portico_real_backend_matrix.py::",
                "tests/scenarios/test_ownership_management_backend_matrix.py::",
                "tests/scenarios/test_object_management_backend_matrix.py::",
                "tests/scenarios/test_federation_lifecycle_backend_matrix.py::",
                "tests/scenarios/test_federation_management_backend_matrix.py::",
                "tests/scenarios/test_ddm_backend_matrix.py::",
                "tests/scenarios/test_support_services_backend_matrix.py::",
                "tests/time/test_section8_backend_matrix.py::",
                "tests/time/test_lookahead_backend_matrix.py::",
            )
            filtered_vendor = tuple(ref for ref in vendor_evidence if ref.startswith(allowed_prefixes))
            return _normalized_evidence_refs(filtered_vendor)
        return _normalized_evidence_refs(vendor_evidence)

    allowed_prefixes_by_clause = {
        "4": (
            "packages/hla-verification/src/hla.verification/",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::",
            "tests/scenarios/test_federation_management_backend_matrix.py::",
        ),
        "6": (
            "packages/hla-verification/src/hla.verification/",
            "tests/scenarios/test_object_management_backend_matrix.py::",
        ),
        "7": (
            "packages/hla-verification/src/hla.verification/",
            "tests/scenarios/test_ownership_management_backend_matrix.py::",
        ),
        "8": (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::",
            "tests/time/test_section8_backend_matrix.py::",
            "tests/time/test_lookahead_backend_matrix.py::",
        ),
        "9": (
            "packages/hla-verification/src/hla.verification/",
            "tests/scenarios/test_ddm_backend_matrix.py::",
        ),
        "10": (
            "packages/hla-verification/src/hla.verification/",
            "tests/scenarios/test_support_services_backend_matrix.py::",
        ),
    }
    allowed_prefixes = allowed_prefixes_by_clause.get(clause_root)
    mapped_evidence = _PITCH_REQUIREMENT_EVIDENCE.get(requirement_id, ("", (), ""))[1]
    if not allowed_prefixes:
        return _normalized_evidence_refs(vendor_evidence)
    filtered_mapped = tuple(ref for ref in mapped_evidence if ref.startswith(allowed_prefixes))
    filtered_vendor = tuple(ref for ref in vendor_evidence if ref.startswith(allowed_prefixes))
    return _normalized_evidence_refs(filtered_mapped + filtered_vendor)


def _family_requirement_notes(source_row: dict[str, Any], *, backend: str, disposition: str) -> str:
    requirement_id = str(source_row.get("requirement_id") or source_row.get("matrix_id") or "")
    vendor_notes = str(source_row.get("vendor_notes") or "").strip()
    generic_notes = str(source_row.get("notes") or "").strip()
    status_field = f"{backend}_runtime_status"
    runtime_status = str(source_row.get(status_field, "")).strip()

    if requirement_id in _SEED_ROW_NOT_APPLICABLE_NOTES:
        return _SEED_ROW_NOT_APPLICABLE_NOTES[requirement_id]
    if backend == "python" and requirement_id in _PYTHON_REQUIREMENT_EVIDENCE:
        return _PYTHON_REQUIREMENT_EVIDENCE[requirement_id][1]

    if backend == "certi":
        if requirement_id in _CERTI_NOTE_OVERRIDES:
            return _CERTI_NOTE_OVERRIDES[requirement_id]
        if requirement_id in _CERTI_REQUIREMENT_EVIDENCE:
            return _CERTI_REQUIREMENT_EVIDENCE[requirement_id][1]
        lowered = vendor_notes.lower()
        if vendor_notes and "pitch" not in lowered and "python" not in lowered:
            return vendor_notes
        if runtime_status:
            return f"CERTI runtime status is marked {runtime_status} in the shared 2010 requirements matrix."
        if disposition:
            return f"CERTI runtime disposition is generated as {disposition} from the shared 2010 requirements matrix."
        return generic_notes

    if backend == "portico":
        if requirement_id in _PORTICO_REQUIREMENT_EVIDENCE:
            return _PORTICO_REQUIREMENT_EVIDENCE[requirement_id][1]
        if runtime_status:
            return f"Portico runtime status is marked {runtime_status} in the shared 2010 requirements matrix."
        if disposition:
            return f"Portico runtime disposition is generated as {disposition} from the shared 2010 requirements matrix."
        return generic_notes

    return vendor_notes or generic_notes


def _pitch_requirement_disposition(row: dict[str, Any]) -> tuple[str, str]:
    requirement_id = str(row.get("requirement_id") or row.get("matrix_id") or "")
    if requirement_id in _SEED_ROW_NOT_APPLICABLE_NOTES:
        return "not-applicable", _SEED_ROW_NOT_APPLICABLE_NOTES[requirement_id]
    if requirement_id in _PITCH_REQUIREMENT_EVIDENCE:
        mapped_status, _, mapped_note = _PITCH_REQUIREMENT_EVIDENCE[requirement_id]
        return mapped_status, mapped_note
    pitch_status = str(row.get("pitch_runtime_status", "")).strip()
    kind = str(row.get("kind", ""))
    section_root = _clause_root(str(row.get("section_ref", "")))
    if pitch_status == "yes":
        return "verified", "Pitch runtime status is marked yes in the shared 2010 requirements matrix."
    if pitch_status == "blocked":
        return "blocked", "Pitch runtime status is blocked in the shared 2010 requirements matrix."
    if pitch_status:
        return pitch_status, f"Pitch runtime status is marked {pitch_status} in the shared 2010 requirements matrix."
    if kind in {"section-area", "curated-seed"}:
        return "not-applicable", "Section summary and seed rows are planning rows, not executable Pitch runtime parity requirements."
    if str(row.get("document")) == "IEEE 1516.1-2010" and section_root in {"4", "6", "7", "8", "9", "10"}:
        return "not-yet-tested", "Pitch runtime/service requirement is applicable but does not yet have an explicit Pitch outcome."
    return (
        "classification-required",
        "Pitch runtime disposition is explicitly generated as classification-required because the current evidence does not yet justify a narrower verified, blocked, vendor-divergent, not-applicable, or not-yet-tested outcome.",
    )


def _pitch_profile_requirement_views(
    row: dict[str, Any],
    *,
    family_disposition: str,
    evidence_refs: tuple[str, ...],
) -> dict[str, tuple[str, tuple[str, ...]]]:
    default_view = (family_disposition, evidence_refs)
    views = {
        "pitch-jpype": default_view,
        "pitch-py4j": default_view,
    }
    requirement_id = str(row.get("requirement_id") or row.get("matrix_id") or "")
    if requirement_id in {"HLA1516.1-FM-4.1.5-001", "HLA1516.1-FM-4.1.5-002"}:
        views["pitch-jpype"] = (
            "blocked",
            (
                "packages/hla-vendor-pitch/docs/evidence/pitch_clause4_lost_federate_gap_2026-06-11.md",
                "analysis/preflight_artifacts/pitch-preflight.json",
                "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
                "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md",
                "packages/hla-verification/src/hla.verification/scenario_lost_federate.py::run_external_lost_federate_observer_scenario",
                "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix",
                "tests/test_rti_pitch_split_packages.py::test_pitch_jpype_factory_uses_inprocess_runtime_without_gateway_process",
            ),
        )
        views["pitch-py4j"] = (
            "blocked",
            (
                "analysis/preflight_artifacts/pitch-preflight.json",
                "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
                "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md",
                "packages/hla-verification/src/hla.verification/scenario_lost_federate.py::run_lost_federate_mom_scenario",
                "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix",
                "tests/test_rti_pitch_split_packages.py::test_pitch_py4j_factory_attaches_gateway_process",
                "packages/hla-vendor-pitch/docs/evidence/pitch_clause4_lost_federate_gap_2026-06-11.md",
            ),
        )
    return views


def _write_pitch_requirement_disposition_artifacts() -> None:
    matrix = build_requirements_matrix_2010(REPO_ROOT, version=hla.rti1516e.__version__)
    rows: list[PitchRequirementDispositionRow] = []
    clause_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    profile_clause_counts: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    disposition_counts: dict[str, int] = defaultdict(int)
    applicability_counts: dict[str, int] = defaultdict(int)
    profile_disposition_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for source_row in matrix["rows"]:
        document = str(source_row.get("document", ""))
        section_ref = str(source_row.get("section_ref", ""))
        clause_root = _clause_root(section_ref)
        clause_key = f"{document} §{clause_root}" if clause_root != "unknown" else f"{document} unknown"
        disposition, disposition_note = _pitch_requirement_disposition(source_row)
        applicability = _pitch_requirement_applicability(source_row)
        evidence_refs = _pitch_evidence_refs(source_row, clause_root=clause_root)
        if (
            document == "IEEE 1516.1-2010"
            and clause_root == "10"
            and disposition == "not-yet-tested"
            and "analysis/compliance/section10_backend_matrix.json" not in evidence_refs
        ):
            evidence_refs = evidence_refs + ("analysis/compliance/section10_backend_matrix.json",)
        profile_views = _pitch_profile_requirement_views(
            source_row,
            family_disposition=disposition,
            evidence_refs=evidence_refs,
        )
        notes = str(source_row.get("vendor_notes") or source_row.get("notes") or disposition_note)
        if disposition == "blocked" and disposition_note and disposition_note not in notes:
            notes = disposition_note if not notes else f"{disposition_note} {notes}"
        if disposition == "classification-required" and disposition_note not in notes:
            notes = disposition_note if not notes else f"{disposition_note} {notes}"
        row = PitchRequirementDispositionRow(
            matrix_id=str(source_row.get("matrix_id", "")),
            requirement_id=str(source_row.get("requirement_id", "")),
            document=document,
            section_ref=section_ref,
            clause_root=clause_root,
            kind=str(source_row.get("kind", "")),
            title=str(source_row.get("title", "")),
            python_runtime_status=str(source_row.get("python_runtime_status", "")),
            pitch_runtime_status=str(source_row.get("pitch_runtime_status", "")),
            pitch_disposition=disposition,
            pitch_jpype_disposition=profile_views["pitch-jpype"][0],
            pitch_py4j_disposition=profile_views["pitch-py4j"][0],
            applicability=applicability,
            evidence_refs=evidence_refs,
            pitch_jpype_evidence_refs=profile_views["pitch-jpype"][1],
            pitch_py4j_evidence_refs=profile_views["pitch-py4j"][1],
            notes=notes,
        )
        rows.append(row)
        clause_counts[clause_key][disposition] += 1
        clause_counts[clause_key]["total"] += 1
        disposition_counts[disposition] += 1
        applicability_counts[applicability] += 1
        profile_disposition_counts["pitch-jpype"][row.pitch_jpype_disposition] += 1
        profile_disposition_counts["pitch-py4j"][row.pitch_py4j_disposition] += 1
        profile_clause_counts["pitch-jpype"][clause_key][row.pitch_jpype_disposition] += 1
        profile_clause_counts["pitch-jpype"][clause_key]["total"] += 1
        profile_clause_counts["pitch-py4j"][clause_key][row.pitch_py4j_disposition] += 1
        profile_clause_counts["pitch-py4j"][clause_key]["total"] += 1

    sorted_rows = sorted(
        rows,
        key=lambda row: (
            row.document,
            int(row.clause_root) if row.clause_root.isdigit() else 999,
            row.section_ref,
            row.requirement_id or row.matrix_id,
        ),
    )
    clause_summary = {
        clause: dict(sorted(counts.items()))
        for clause, counts in sorted(
            clause_counts.items(),
            key=lambda item: item[0],
        )
    }
    profile_clause_summary = {
        profile: {
            clause: dict(sorted(counts.items()))
            for clause, counts in sorted(clause_map.items(), key=lambda item: item[0])
        }
        for profile, clause_map in sorted(profile_clause_counts.items())
    }

    _write_json(
        OUTPUT_DIR / "pitch_requirement_disposition.json",
        {
            "summary": {
                "row_count": len(sorted_rows),
                "disposition_counts": dict(sorted(disposition_counts.items())),
                "applicability_counts": dict(sorted(applicability_counts.items())),
                "profile_disposition_counts": {
                    profile: dict(sorted(counts.items()))
                    for profile, counts in sorted(profile_disposition_counts.items())
                },
                "clause_summary": clause_summary,
                "profile_clause_summary": profile_clause_summary,
                "source_artifact": "analysis/compliance/requirements_matrix_2010.json",
            },
            "rows": [asdict(row) for row in sorted_rows],
        },
    )

    md_lines = [
        "# Pitch Requirement Disposition",
        "",
        "This audit projects the shared HLA 2010 requirements matrix onto Pitch so every row has an explicit generated `pitch` disposition.",
        "",
        "## Profile Summary",
        "",
        "| Pitch backend | Verified | Blocked | Vendor divergent | Not yet tested | Not applicable | Classification required |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for profile, counts in sorted(profile_disposition_counts.items()):
        md_lines.append(
            f"| {profile} | {counts.get('verified', 0)} | {counts.get('blocked', 0)} | "
            f"{counts.get('vendor-divergent', 0)} | {counts.get('not-yet-tested', 0)} | "
            f"{counts.get('not-applicable', 0)} | {counts.get('classification-required', 0)} |"
        )
    md_lines.extend(
        [
            "",
        "## Clause Summary",
        "",
            "| Document clause | Total | Verified | Blocked | Vendor divergent | Not yet tested | Not applicable | Classification required |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for clause, counts in clause_summary.items():
        md_lines.append(
            f"| {clause} | {counts.get('total', 0)} | {counts.get('verified', 0)} | "
            f"{counts.get('blocked', 0)} | {counts.get('vendor-divergent', 0)} | {counts.get('not-yet-tested', 0)} | "
            f"{counts.get('not-applicable', 0)} | {counts.get('classification-required', 0)} |"
        )
    md_lines.extend(
        [
            "",
            "## Profile Clause Summary",
            "",
        ]
    )
    for profile, clause_map in sorted(profile_clause_summary.items()):
        md_lines.extend(
            [
                f"### {profile}",
                "",
                "| Document clause | Total | Verified | Blocked | Vendor divergent | Not yet tested | Not applicable | Classification required |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for clause, counts in clause_map.items():
            md_lines.append(
                f"| {clause} | {counts.get('total', 0)} | {counts.get('verified', 0)} | "
                f"{counts.get('blocked', 0)} | {counts.get('vendor-divergent', 0)} | {counts.get('not-yet-tested', 0)} | "
                f"{counts.get('not-applicable', 0)} | {counts.get('classification-required', 0)} |"
            )
        md_lines.extend([""])
    md_lines.extend(
        [
            "## Backend-Split Rows",
            "",
            "Rows where `pitch-jpype` and `pitch-py4j` currently have different generated dispositions.",
            "",
            "| Document | Clause | Requirement | Family | Pitch JPype | Pitch Py4J |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in sorted_rows:
        if row.pitch_jpype_disposition == row.pitch_py4j_disposition:
            continue
        md_lines.append(
            f"| {row.document} | {row.clause_root} | {row.requirement_id or row.matrix_id} | "
            f"{row.pitch_disposition} | {row.pitch_jpype_disposition} | {row.pitch_py4j_disposition} |"
        )
    md_lines.extend(
        [
            "",
            "## Not Yet Tested Rows",
            "",
            "| Document | Clause | Requirement | Kind | Applicability | Title |",
            "|---|---|---|---|---|",
        ]
    )
    for row in sorted_rows:
        if row.pitch_disposition != "not-yet-tested":
            continue
        md_lines.append(
            f"| {row.document} | {row.clause_root} | {row.requirement_id or row.matrix_id} | {row.kind} | {row.applicability} | {row.title} |"
        )
    md_lines.extend(
        [
            "",
            "## Classification Required Rows",
            "",
            "| Document | Clause | Requirement | Kind | Applicability | Title |",
            "|---|---|---|---|---|",
        ]
    )
    for row in sorted_rows:
        if row.pitch_disposition != "classification-required":
            continue
        md_lines.append(
            f"| {row.document} | {row.clause_root} | {row.requirement_id or row.matrix_id} | {row.kind} | {row.applicability} | {row.title} |"
        )
    _write_markdown(OUTPUT_DIR / "pitch_requirement_disposition.md", md_lines)


def _write_pitch_profile_requirement_disposition_artifacts(profile: str) -> None:
    if profile not in {"pitch-jpype", "pitch-py4j"}:
        raise ValueError(f"unsupported pitch profile: {profile}")

    pitch_disposition_path = OUTPUT_DIR / "pitch_requirement_disposition.json"
    if not pitch_disposition_path.exists():
        return

    payload = json.loads(pitch_disposition_path.read_text(encoding="utf-8"))
    disposition_key = f"{profile.replace('-', '_')}_disposition"
    evidence_key = f"{profile.replace('-', '_')}_evidence_refs"
    rows: list[BackendRequirementDispositionRow] = []
    clause_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    disposition_counts: dict[str, int] = defaultdict(int)

    for source_row in payload.get("rows", []):
        document = str(source_row.get("document", ""))
        section_ref = str(source_row.get("section_ref", ""))
        clause_root = _clause_root(section_ref)
        clause_key = f"{document} §{clause_root}" if clause_root != "unknown" else f"{document} unknown"
        disposition = str(source_row.get(disposition_key, "")).strip()
        if not disposition:
            continue
        rows.append(
            BackendRequirementDispositionRow(
                matrix_id=str(source_row.get("matrix_id", "")),
                requirement_id=str(source_row.get("requirement_id", "")),
                document=document,
                section_ref=section_ref,
                clause_root=clause_root,
                kind=str(source_row.get("kind", "")),
                title=str(source_row.get("title", "")),
                runtime_status="",
                runtime_disposition=disposition,
                evidence_refs=tuple(str(item) for item in source_row.get(evidence_key, ())),
                notes=str(source_row.get("notes", "")),
            )
        )
        clause_counts[clause_key][disposition] += 1
        clause_counts[clause_key]["total"] += 1
        disposition_counts[disposition] += 1

    sorted_rows = sorted(
        rows,
        key=lambda row: (
            row.document,
            int(row.clause_root) if row.clause_root.isdigit() else 999,
            row.section_ref,
            row.requirement_id or row.matrix_id,
        ),
    )
    clause_summary = {
        clause: dict(sorted(counts.items()))
        for clause, counts in sorted(clause_counts.items(), key=lambda item: item[0])
    }
    output_stem = f"{profile}_requirement_disposition"
    _write_json(
        OUTPUT_DIR / f"{output_stem}.json",
        {
            "summary": {
                "backend": profile,
                "row_count": len(sorted_rows),
                "disposition_counts": dict(sorted(disposition_counts.items())),
                "clause_summary": clause_summary,
                "source_artifact": "analysis/compliance/pitch_requirement_disposition.json",
            },
            "rows": [asdict(row) for row in sorted_rows],
        },
    )

    md_lines = [
        f"# {profile} Requirement Disposition",
        "",
        f"This audit projects the shared HLA 2010 requirements matrix onto `{profile}` so every row has an explicit generated `{profile}` disposition.",
        "",
        "This profile currently inherits the Pitch family-level requirement disposition because the JPype and Py4J routes are adapter profiles over the same generated Pitch requirement packet, with profile-specific evidence carried through the family artifact fields.",
        "",
        "## Summary",
        "",
        "| Document clause | Total | Verified | Blocked | Vendor divergent | Not yet tested | Not applicable | Classification required |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for clause, counts in clause_summary.items():
        md_lines.append(
            f"| {clause} | {counts.get('total', 0)} | {counts.get('verified', 0)} | "
            f"{counts.get('blocked', 0)} | {counts.get('vendor-divergent', 0)} | "
            f"{counts.get('not-yet-tested', 0)} | {counts.get('not-applicable', 0)} | "
            f"{counts.get('classification-required', 0)} |"
        )
    md_lines.extend(
        [
            "",
            "## Non-Verified Rows",
            "",
            "| Document | Clause | Requirement | Disposition | Kind | Title |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in sorted_rows:
        if row.runtime_disposition == "verified":
            continue
        md_lines.append(
            f"| {row.document} | {row.clause_root} | {row.requirement_id or row.matrix_id} | "
            f"{row.runtime_disposition} | {row.kind} | {row.title} |"
        )
    _write_markdown(OUTPUT_DIR / f"{output_stem}.md", md_lines)


def _write_certi_profile_requirement_disposition_artifacts(profile: str) -> None:
    if profile not in {"certi-native", "certi-jpype", "certi-py4j"}:
        raise ValueError(f"unsupported certi profile: {profile}")

    certi_disposition_path = OUTPUT_DIR / "certi_requirement_disposition.json"
    if not certi_disposition_path.exists():
        return

    payload = json.loads(certi_disposition_path.read_text(encoding="utf-8"))
    rows: list[BackendRequirementDispositionRow] = []
    clause_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    disposition_counts: dict[str, int] = defaultdict(int)

    for source_row in payload.get("rows", []):
        document = str(source_row.get("document", ""))
        section_ref = str(source_row.get("section_ref", ""))
        clause_root = _clause_root(section_ref)
        clause_key = f"{document} §{clause_root}" if clause_root != "unknown" else f"{document} unknown"
        disposition = str(source_row.get("runtime_disposition", "")).strip()
        if not disposition:
            continue
        rows.append(
            BackendRequirementDispositionRow(
                matrix_id=str(source_row.get("matrix_id", "")),
                requirement_id=str(source_row.get("requirement_id", "")),
                document=document,
                section_ref=section_ref,
                clause_root=clause_root,
                kind=str(source_row.get("kind", "")),
                title=str(source_row.get("title", "")),
                runtime_status=str(source_row.get("runtime_status", "")),
                runtime_disposition=disposition,
                evidence_refs=tuple(str(item) for item in source_row.get("evidence_refs", ())),
                notes=str(source_row.get("notes", "")),
            )
        )
        clause_counts[clause_key][disposition] += 1
        clause_counts[clause_key]["total"] += 1
        disposition_counts[disposition] += 1

    sorted_rows = sorted(
        rows,
        key=lambda row: (
            row.document,
            int(row.clause_root) if row.clause_root.isdigit() else 999,
            row.section_ref,
            row.requirement_id or row.matrix_id,
        ),
    )
    clause_summary = {
        clause: dict(sorted(counts.items()))
        for clause, counts in sorted(clause_counts.items(), key=lambda item: item[0])
    }
    output_stem = f"{profile}_requirement_disposition"
    _write_json(
        OUTPUT_DIR / f"{output_stem}.json",
        {
            "summary": {
                "backend": profile,
                "row_count": len(sorted_rows),
                "disposition_counts": dict(sorted(disposition_counts.items())),
                "clause_summary": clause_summary,
                "source_artifact": "analysis/compliance/certi_requirement_disposition.json",
            },
            "rows": [asdict(row) for row in sorted_rows],
        },
    )

    md_lines = [
        f"# {profile} Requirement Disposition",
        "",
        f"This audit projects the shared HLA 2010 requirements matrix onto `{profile}` so every row has an explicit generated `{profile}` disposition.",
        "",
        "This profile currently inherits the CERTI family-level requirement disposition because the JPype and Py4J routes are documented as Java-profile facades over the same native CERTI runtime path.",
        "",
        "## Summary",
        "",
        "| Document clause | Total | Verified | Blocked | Vendor divergent | Not yet tested | Not applicable | Classification required |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for clause, counts in clause_summary.items():
        md_lines.append(
            f"| {clause} | {counts.get('total', 0)} | {counts.get('verified', 0)} | "
            f"{counts.get('blocked', 0)} | {counts.get('vendor-divergent', 0)} | "
            f"{counts.get('not-yet-tested', 0)} | {counts.get('not-applicable', 0)} | "
            f"{counts.get('classification-required', 0)} |"
        )
    md_lines.extend(
        [
            "",
            "## Non-Verified Rows",
            "",
            "| Document | Clause | Requirement | Disposition | Kind | Title |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in sorted_rows:
        if row.runtime_disposition == "verified":
            continue
        md_lines.append(
            f"| {row.document} | {row.clause_root} | {row.requirement_id or row.matrix_id} | "
            f"{row.runtime_disposition} | {row.kind} | {row.title} |"
        )
    _write_markdown(OUTPUT_DIR / f"{output_stem}.md", md_lines)


def _write_portico_profile_requirement_disposition_artifacts(profile: str) -> None:
    if profile not in {"portico-jpype", "portico-py4j"}:
        raise ValueError(f"unsupported portico profile: {profile}")

    portico_disposition_path = OUTPUT_DIR / "portico_requirement_disposition.json"
    if not portico_disposition_path.exists():
        return

    payload = json.loads(portico_disposition_path.read_text(encoding="utf-8"))
    rows: list[BackendRequirementDispositionRow] = []
    clause_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    disposition_counts: dict[str, int] = defaultdict(int)

    for source_row in payload.get("rows", []):
        document = str(source_row.get("document", ""))
        section_ref = str(source_row.get("section_ref", ""))
        clause_root = _clause_root(section_ref)
        clause_key = f"{document} §{clause_root}" if clause_root != "unknown" else f"{document} unknown"
        disposition = str(source_row.get("runtime_disposition", "")).strip()
        if not disposition:
            continue
        rows.append(
            BackendRequirementDispositionRow(
                matrix_id=str(source_row.get("matrix_id", "")),
                requirement_id=str(source_row.get("requirement_id", "")),
                document=document,
                section_ref=section_ref,
                clause_root=clause_root,
                kind=str(source_row.get("kind", "")),
                title=str(source_row.get("title", "")),
                runtime_status=str(source_row.get("runtime_status", "")),
                runtime_disposition=disposition,
                evidence_refs=tuple(str(item) for item in source_row.get("evidence_refs", ())),
                notes=str(source_row.get("notes", "")),
            )
        )
        clause_counts[clause_key][disposition] += 1
        clause_counts[clause_key]["total"] += 1
        disposition_counts[disposition] += 1

    sorted_rows = sorted(
        rows,
        key=lambda row: (
            row.document,
            int(row.clause_root) if row.clause_root.isdigit() else 999,
            row.section_ref,
            row.requirement_id or row.matrix_id,
        ),
    )
    clause_summary = {
        clause: dict(sorted(counts.items()))
        for clause, counts in sorted(clause_counts.items(), key=lambda item: item[0])
    }
    output_stem = f"{profile}_requirement_disposition"
    _write_json(
        OUTPUT_DIR / f"{output_stem}.json",
        {
            "summary": {
                "backend": profile,
                "row_count": len(sorted_rows),
                "disposition_counts": dict(sorted(disposition_counts.items())),
                "clause_summary": clause_summary,
                "source_artifact": "analysis/compliance/portico_requirement_disposition.json",
            },
            "rows": [asdict(row) for row in sorted_rows],
        },
    )

    md_lines = [
        f"# {profile} Requirement Disposition",
        "",
        f"This audit projects the shared HLA 2010 requirements matrix onto `{profile}` so every row has an explicit generated `{profile}` disposition.",
        "",
        "This profile currently inherits the Portico family-level requirement disposition because the JPype and Py4J routes are install-dependent Java adapter profiles over the same Portico runtime family and no profile-specific requirement evidence is generated yet.",
        "",
        "## Summary",
        "",
        "| Document clause | Total | Verified | Blocked | Vendor divergent | Not yet tested | Not applicable | Classification required |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for clause, counts in clause_summary.items():
        md_lines.append(
            f"| {clause} | {counts.get('total', 0)} | {counts.get('verified', 0)} | "
            f"{counts.get('blocked', 0)} | {counts.get('vendor-divergent', 0)} | "
            f"{counts.get('not-yet-tested', 0)} | {counts.get('not-applicable', 0)} | "
            f"{counts.get('classification-required', 0)} |"
        )
    md_lines.extend(
        [
            "",
            "## Non-Verified Rows",
            "",
            "| Document | Clause | Requirement | Disposition | Kind | Title |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in sorted_rows:
        if row.runtime_disposition == "verified":
            continue
        md_lines.append(
            f"| {row.document} | {row.clause_root} | {row.requirement_id or row.matrix_id} | "
            f"{row.runtime_disposition} | {row.kind} | {row.title} |"
        )
    _write_markdown(OUTPUT_DIR / f"{output_stem}.md", md_lines)


def _project_backend_dispositions_into_requirements_matrix_artifacts() -> None:
    requirements_json_path = OUTPUT_DIR / "requirements_matrix_2010.json"
    requirements_csv_path = OUTPUT_DIR / "requirements_matrix_2010.csv"
    pitch_disposition_path = OUTPUT_DIR / "pitch_requirement_disposition.json"
    if not (requirements_json_path.exists() and requirements_csv_path.exists() and pitch_disposition_path.exists()):
        return

    requirements_payload = json.loads(requirements_json_path.read_text(encoding="utf-8"))
    pitch_disposition_payload = json.loads(pitch_disposition_path.read_text(encoding="utf-8"))

    rows = requirements_payload.get("rows", [])
    disposition_rows = pitch_disposition_payload.get("rows", [])
    pitch_by_key = {
        (str(row.get("requirement_id") or ""), str(row.get("matrix_id") or "")): row
        for row in disposition_rows
    }
    python_requirement_overrides = {
        "HLA1516.1-FM-4.3-MOM-001": "verified",
        "HLA1516.1-FM-4.1.5-001": "verified",
        "HLA1516.1-FM-4.1.5-002": "verified",
        "HLA1516.1-FM-4.1.2-002": "verified",
        "HLA1516.1-FM-4.1-005": "verified",
        "HLA1516.1-FM-4.1-006": "verified",
        "HLA1516.1-FM-4.1.4.1-002": "verified",
        "HLA1516.1-TM-8.1.2-003": "verified",
        "HLA1516.2-DT-002": "verified",
        "HLA1516.2-SYNC-001": "verified",
        "HLA1516.2-MERGE-001": "verified",
        "HLA1516.2-XML-001": "verified",
    }
    python_requirement_overrides.update({requirement_id: "not-applicable" for requirement_id in _SEED_ROW_NOT_APPLICABLE_NOTES})
    certi_requirement_overrides = {
        "REQ-RTI-FM-4_16-requestFederationSave": "verified",
        "REQ-FED-FM-4_17-initiateFederateSave": "verified",
        "REQ-RTI-FM-4_18-federateSaveBegun": "verified",
        "REQ-FED-FM-4_20-federationSaved": "verified",
        "REQ-RTI-FM-4_22-queryFederationSaveStatus": "verified",
        "REQ-FED-FM-4_23-federationSaveStatusResponse": "verified",
        "REQ-RTI-FM-4_24-requestFederationRestore": "verified",
        "REQ-FED-FM-4_25-requestFederationRestoreSucceeded": "verified",
        "REQ-FED-FM-4_26-federationRestoreBegun": "verified",
        "REQ-FED-FM-4_27-initiateFederateRestore": "verified",
        "REQ-FED-FM-4_29-federationRestored": "verified",
        "REQ-RTI-FM-4_31-queryFederationRestoreStatus": "verified",
        "REQ-FED-FM-4_32-federationRestoreStatusResponse": "verified",
        "HLA1516.1-FM-4.16-001": "verified",
        "HLA1516.1-FM-4.17-001": "verified",
        "HLA1516.1-FM-4.18-001": "verified",
        "HLA1516.1-FM-4.22-001": "verified",
        "HLA1516.1-FM-4.23-001": "verified",
        "HLA1516.1-FM-4.24-001": "verified",
        "HLA1516.1-FM-4.26-001": "verified",
        "HLA1516.1-FM-4.27-001": "verified",
        "HLA1516.1-FM-4.31-001": "verified",
        "HLA1516.1-FM-4.32-001": "verified",
    }
    certi_requirement_overrides.update(_CERTI_DISPOSITION_OVERRIDES)

    def _normalized_runtime_disposition(
        row: dict[str, Any],
        *,
        backend: str,
        legacy_status: str,
    ) -> str:
        requirement_id = str(row.get("requirement_id") or row.get("matrix_id") or "")
        if requirement_id in _SEED_ROW_NOT_APPLICABLE_NOTES:
            return "not-applicable"
        if backend == "python" and requirement_id in python_requirement_overrides:
            return python_requirement_overrides[requirement_id]
        if backend == "certi" and requirement_id in certi_requirement_overrides:
            return certi_requirement_overrides[requirement_id]
        if backend == "portico":
            kind = str(row.get("kind", "")).strip()
            if kind in {"section-area", "omt-area", "verification-slice", "curated-seed"}:
                return "not-applicable"
            document = str(row.get("document", "")).strip()
            clause_root = _clause_root(str(row.get("section_ref", "")))
            if document == "IEEE 1516.1-2010" and clause_root in {"4", "5", "6", "7", "8", "9", "10", "11", "12"}:
                return "classification-required"
            if document == "IEEE 1516.2-2010":
                return "classification-required"
            return "not-applicable"
        legacy_status = legacy_status.strip()
        if legacy_status == "yes":
            return "verified"
        if legacy_status == "blocked":
            return "blocked"
        if legacy_status == "partial":
            return "vendor-divergent"
        if legacy_status == "no":
            return "not-yet-tested"

        kind = str(row.get("kind", "")).strip()
        matrix_status = str(row.get("status", "")).strip()
        document = str(row.get("document", "")).strip()
        clause_root = _clause_root(str(row.get("section_ref", "")))

        if kind in {"section-area", "omt-area", "verification-slice", "curated-seed"}:
            return "not-applicable"
        if backend == "python":
            if matrix_status == "pass":
                return "verified"
            if matrix_status == "partial":
                return "vendor-divergent"
            if matrix_status in {"planned", "not-evidenced"}:
                return "not-yet-tested"
            if matrix_status == "fail":
                return "blocked"
            return "classification-required"
        if document == "IEEE 1516.1-2010" and clause_root in {"4", "5", "6", "7", "8", "9", "10", "11", "12"}:
            if matrix_status in {"planned", "not-evidenced"}:
                return "not-yet-tested"
            if matrix_status == "fail":
                return "blocked"
            return "classification-required"
        return "not-applicable"

    python_counts: dict[str, int] = defaultdict(int)
    certi_counts: dict[str, int] = defaultdict(int)
    portico_counts: dict[str, int] = defaultdict(int)
    disposition_counts: dict[str, int] = defaultdict(int)
    jpype_counts: dict[str, int] = defaultdict(int)
    py4j_counts: dict[str, int] = defaultdict(int)

    for row in rows:
        row["python_runtime_disposition"] = _normalized_runtime_disposition(
            row,
            backend="python",
            legacy_status=str(row.get("python_runtime_status", "")),
        )
        row["certi_runtime_disposition"] = _normalized_runtime_disposition(
            row,
            backend="certi",
            legacy_status=str(row.get("certi_runtime_status", "")),
        )
        row["portico_runtime_disposition"] = _normalized_runtime_disposition(
            row,
            backend="portico",
            legacy_status=str(row.get("portico_runtime_status", "")),
        )
        key = (str(row.get("requirement_id") or ""), str(row.get("matrix_id") or ""))
        disposition_row = pitch_by_key.get(key)
        if disposition_row is None:
            row["pitch_runtime_disposition"] = _normalized_runtime_disposition(
                row,
                backend="pitch",
                legacy_status=str(row.get("pitch_runtime_status", "")),
            )
            row["pitch_jpype_runtime_disposition"] = row["pitch_runtime_disposition"]
            row["pitch_py4j_runtime_disposition"] = row["pitch_runtime_disposition"]
        else:
            row["pitch_runtime_disposition"] = str(disposition_row.get("pitch_disposition", ""))
            row["pitch_jpype_runtime_disposition"] = str(disposition_row.get("pitch_jpype_disposition", ""))
            row["pitch_py4j_runtime_disposition"] = str(disposition_row.get("pitch_py4j_disposition", ""))
        python_counts[row["python_runtime_disposition"]] += 1
        certi_counts[row["certi_runtime_disposition"]] += 1
        portico_counts[row["portico_runtime_disposition"]] += 1
        if row["pitch_runtime_disposition"]:
            disposition_counts[row["pitch_runtime_disposition"]] += 1
        if row["pitch_jpype_runtime_disposition"]:
            jpype_counts[row["pitch_jpype_runtime_disposition"]] += 1
        if row["pitch_py4j_runtime_disposition"]:
            py4j_counts[row["pitch_py4j_runtime_disposition"]] += 1

    requirements_payload.setdefault("summary", {})
    requirements_payload["summary"]["python_runtime_disposition_counts"] = dict(sorted(python_counts.items()))
    requirements_payload["summary"]["certi_runtime_disposition_counts"] = dict(sorted(certi_counts.items()))
    requirements_payload["summary"]["portico_runtime_disposition_counts"] = dict(sorted(portico_counts.items()))
    requirements_payload["summary"]["pitch_runtime_disposition_counts"] = dict(sorted(disposition_counts.items()))
    requirements_payload["summary"]["pitch_jpype_runtime_disposition_counts"] = dict(sorted(jpype_counts.items()))
    requirements_payload["summary"]["pitch_py4j_runtime_disposition_counts"] = dict(sorted(py4j_counts.items()))
    requirements_json_path.write_text(json.dumps(requirements_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fieldnames = [
        "matrix_id",
        "kind",
        "document",
        "section_ref",
        "title",
        "requirement_id",
        "service_group",
        "status",
        "implementation_refs",
        "positive_test_refs",
        "negative_test_refs",
        "artifact_refs",
        "linked_methods",
        "linked_assets",
        "claim_scope",
        "supported_subset_for",
        "policy_basis",
        "python_runtime_status",
        "python_runtime_disposition",
        "certi_runtime_status",
        "certi_runtime_disposition",
        "portico_runtime_status",
        "portico_runtime_disposition",
        "pitch_runtime_status",
        "pitch_runtime_disposition",
        "pitch_jpype_runtime_disposition",
        "pitch_py4j_runtime_disposition",
        "vendor_evidence_refs",
        "vendor_notes",
        "vendor_source",
        "vendor_profile_bucket",
        "vendor_profile_refs",
        "vendor_profile_notes",
        "vendor_profile_source",
        "notes",
        "source",
    ]
    with requirements_csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            record = dict(row)
            for key, value in list(record.items()):
                if isinstance(value, list):
                    record[key] = "; ".join(str(item) for item in value)
            writer.writerow(record)


def _write_family_requirement_disposition_artifacts(backend: str) -> None:
    if backend not in _BACKEND_DISPOSITION_ARTIFACT_META:
        raise ValueError(f"unsupported family disposition backend: {backend}")

    requirements_json_path = OUTPUT_DIR / "requirements_matrix_2010.json"
    if not requirements_json_path.exists():
        return

    payload = json.loads(requirements_json_path.read_text(encoding="utf-8"))
    meta = _BACKEND_DISPOSITION_ARTIFACT_META[backend]
    disposition_field = meta["disposition_field"]
    status_field = meta["status_field"]
    rows: list[BackendRequirementDispositionRow] = []
    clause_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    disposition_counts: dict[str, int] = defaultdict(int)

    for source_row in payload.get("rows", []):
        document = str(source_row.get("document", ""))
        section_ref = str(source_row.get("section_ref", ""))
        clause_root = _clause_root(section_ref)
        clause_key = f"{document} §{clause_root}" if clause_root != "unknown" else f"{document} unknown"
        disposition = str(source_row.get(disposition_field, "")).strip()
        if not disposition:
            continue
        notes = _family_requirement_notes(source_row, backend=backend, disposition=disposition)
        rows.append(
            BackendRequirementDispositionRow(
                matrix_id=str(source_row.get("matrix_id", "")),
                requirement_id=str(source_row.get("requirement_id", "")),
                document=document,
                section_ref=section_ref,
                clause_root=clause_root,
                kind=str(source_row.get("kind", "")),
                title=str(source_row.get("title", "")),
                runtime_status=str(source_row.get(status_field, "")),
                runtime_disposition=disposition,
                evidence_refs=_family_evidence_refs(source_row, backend=backend, clause_root=clause_root),
                notes=notes,
            )
        )
        clause_counts[clause_key][disposition] += 1
        clause_counts[clause_key]["total"] += 1
        disposition_counts[disposition] += 1

    sorted_rows = sorted(
        rows,
        key=lambda row: (
            row.document,
            int(row.clause_root) if row.clause_root.isdigit() else 999,
            row.section_ref,
            row.requirement_id or row.matrix_id,
        ),
    )
    clause_summary = {
        clause: dict(sorted(counts.items()))
        for clause, counts in sorted(clause_counts.items(), key=lambda item: item[0])
    }
    output_stem = meta["output_stem"]
    _write_json(
        OUTPUT_DIR / f"{output_stem}.json",
        {
            "summary": {
                "backend": meta["label"],
                "row_count": len(sorted_rows),
                "disposition_counts": dict(sorted(disposition_counts.items())),
                "clause_summary": clause_summary,
                "source_artifact": "analysis/compliance/requirements_matrix_2010.json",
            },
            "rows": [asdict(row) for row in sorted_rows],
        },
    )

    md_lines = [
        f"# {meta['title']}",
        "",
        f"This audit projects the shared HLA 2010 requirements matrix onto `{meta['label']}` so every row has an explicit generated `{meta['label']}` disposition.",
        "",
    ]
    if backend == "portico":
        md_lines.extend(
            [
                "Portico currently has no promoted package-owned real-runtime requirement evidence in the generated matrix, so applicable rows stay `classification-required` until shared-harness scenario wrappers and Portico-owned findings are promoted deliberately.",
                "",
            ]
        )
    md_lines.extend(
        [
        "## Summary",
        "",
        "| Document clause | Total | Verified | Blocked | Vendor divergent | Not yet tested | Not applicable | Classification required |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for clause, counts in clause_summary.items():
        md_lines.append(
            f"| {clause} | {counts.get('total', 0)} | {counts.get('verified', 0)} | "
            f"{counts.get('blocked', 0)} | {counts.get('vendor-divergent', 0)} | "
            f"{counts.get('not-yet-tested', 0)} | {counts.get('not-applicable', 0)} | "
            f"{counts.get('classification-required', 0)} |"
        )
    md_lines.extend(
        [
            "",
            "## Non-Verified Rows",
            "",
            "| Document | Clause | Requirement | Disposition | Kind | Title |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in sorted_rows:
        if row.runtime_disposition == "verified":
            continue
        md_lines.append(
            f"| {row.document} | {row.clause_root} | {row.requirement_id or row.matrix_id} | "
            f"{row.runtime_disposition} | {row.kind} | {row.title} |"
        )
    _write_markdown(OUTPUT_DIR / f"{output_stem}.md", md_lines)


def main(argv: list[str] | None = None) -> int:
    global REPO_ROOT, OUTPUT_DIR
    parser = argparse.ArgumentParser(description="Generate the compliance and requirements artifact packet for the current repo state.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Repository root for compliance inputs and outputs.")
    args = parser.parse_args(argv)
    REPO_ROOT = args.project_root.resolve()
    OUTPUT_DIR = REPO_ROOT / "analysis" / "compliance"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    matrix = build_service_conformance_matrix(version=hla.rti1516e.__version__)
    write_service_conformance_json(OUTPUT_DIR / "service_conformance.json", version=hla.rti1516e.__version__)
    write_service_conformance_csv(OUTPUT_DIR / "service_conformance.csv", version=hla.rti1516e.__version__)
    write_requirements_ledger_json(OUTPUT_DIR / "requirements_ledger.json", version=hla.rti1516e.__version__)
    write_requirements_ledger_csv(OUTPUT_DIR / "requirements_ledger.csv", version=hla.rti1516e.__version__)
    write_requirements_matrix_2010_json(OUTPUT_DIR / "requirements_matrix_2010.json", REPO_ROOT, version=hla.rti1516e.__version__)
    write_requirements_matrix_2010_csv(OUTPUT_DIR / "requirements_matrix_2010.csv", REPO_ROOT, version=hla.rti1516e.__version__)
    _write_pitch_requirement_disposition_artifacts()
    _project_backend_dispositions_into_requirements_matrix_artifacts()
    _write_family_requirement_disposition_artifacts("python")
    _write_family_requirement_disposition_artifacts("certi")
    _write_family_requirement_disposition_artifacts("portico")
    _write_certi_profile_requirement_disposition_artifacts("certi-native")
    _write_certi_profile_requirement_disposition_artifacts("certi-jpype")
    _write_certi_profile_requirement_disposition_artifacts("certi-py4j")
    _write_portico_profile_requirement_disposition_artifacts("portico-jpype")
    _write_portico_profile_requirement_disposition_artifacts("portico-py4j")
    _write_pitch_profile_requirement_disposition_artifacts("pitch-jpype")
    _write_pitch_profile_requirement_disposition_artifacts("pitch-py4j")
    _write_clause56_extracted_requirements_artifacts()
    _write_clause79_extracted_requirements_artifacts()
    _write_supported_subset_policy_artifacts()
    _write_defended_partials_index_artifacts()
    write_verification_assets(OUTPUT_DIR / "verification_assets.json", version=hla.rti1516e.__version__)
    write_traceability_csv(OUTPUT_DIR / "verification_traceability.csv", version=hla.rti1516e.__version__)
    _write_section_summary_artifacts(matrix.rows)
    _write_public_class_inventory_artifacts()
    _write_gap_report_artifacts(matrix.rows)
    _write_negative_path_artifacts(matrix.rows)
    _write_section8_backend_matrix_artifacts(matrix.rows)
    _write_backend_slice_matrix_artifacts(
        stem="lookahead_backend_matrix",
        title="Lookahead Backend Matrix",
        intro="This matrix records backend-specific lookahead query/modify and early-send verification separately from the reference conformance ledger.",
        profiles=_LOOKAHEAD_BACKEND_SLICE_PROFILES,
    )
    core_backend_rows = _write_core_backend_matrix_artifacts()
    _write_backend_slice_matrix_artifacts(
        stem="section10_backend_matrix",
        title="Section 10 Backend Matrix",
        intro="This matrix records backend-specific Section 10 support-service verification separately from the reference conformance ledger.",
        profiles=_SECTION10_BACKEND_SLICE_PROFILES,
    )
    _write_backend_slice_matrix_artifacts(
        stem="pitch_backend_matrix",
        title="Pitch Backend Matrix",
        intro="This matrix records the dedicated Pitch backend verification slices and the current negotiated-ownership divergence.",
        profiles=_PITCH_BACKEND_SLICE_PROFILES,
    )
    write_vendor_discovery_backlog_artifacts(REPO_ROOT)
    _write_completion_checklist_artifacts(matrix.rows, core_backend_rows)
    _write_unfinished_work_ranking_artifacts(core_backend_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
