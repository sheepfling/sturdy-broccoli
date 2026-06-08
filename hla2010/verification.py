"""Verification asset planning for the HLA 1516.1/1516.2 Python RTI.

This module deliberately separates implementation progress from conformance
claims.  It emits versioned, machine-readable planning artifacts that link
feature slices to specification sections, executable tests, scenarios, known
assumptions, and remaining gaps.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .spec_refs import FOM_REFERENCES, SERVICE_AREAS


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _split_semicolon_list(value: Any) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    return [item.strip() for item in text.split(";") if item.strip()]


def _split_scalar_list(value: Any) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    if ";" in text:
        return [item.strip() for item in text.split(";") if item.strip()]
    if "," in text:
        return [item.strip() for item in text.split(",") if item.strip()]
    return [text]


def _looks_like_artifact_ref(value: str) -> bool:
    text = str(value or "").strip()
    return any(token in text for token in ("/", ".py", ".md", ".csv", ".json", ".yaml", ".yml"))


def _path_like_refs(value: Any) -> list[str]:
    return [item for item in _split_semicolon_list(value) if _looks_like_artifact_ref(item)]


def _extract_markdown_link_targets(value: Any) -> list[str]:
    text = str(value or "")
    return [match.strip() for match in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text) if match.strip()]


_CURATED_REQUIREMENT_DIRECT_REFS: dict[str, dict[str, tuple[str, ...]]] = {
    "HLA1516.1-FM-4.15-001": {
        "implementation_refs": ("hla2010/backends/python/federation_sync.py",),
        "positive_test_refs": (
            "tests/scenarios/test_startup_sync_fom_java_translation_v09.py::test_whole_federation_synchronization_announces_late_joiner_before_completion",
            "tests/verification/test_compliance_slice_v011.py::test_core_time_and_sync_compliance_smoke_covers_late_join_sync_and_time_controls",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-FM-4.15-002": {
        "implementation_refs": ("hla2010/backends/python/federation_sync.py",),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/verification/test_compliance_slice_v011.py::test_core_time_and_sync_compliance_smoke_covers_late_join_sync_and_time_controls",
        ),
    },
    "HLA1516.1-FM-4.17-001": {
        "implementation_refs": ("hla2010/backends/python/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_synchronization_points_and_save_status_callbacks",
            "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        ),
        "negative_test_refs": (
            "tests/verification/test_compliance_slice_v011.py::test_scheduled_save_waits_for_time_and_restore_reinstates_time_state",
        ),
    },
    "HLA1516.1-FM-4.20-001": {
        "implementation_refs": ("hla2010/backends/python/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_synchronization_points_and_save_status_callbacks",
            "tests/backends/test_python_backend_federation_extended.py::test_save_failure_reports_federation_not_saved_and_clears_status",
            "tests/backends/test_python_backend_federation_extended.py::test_abort_federation_save_reports_aborted_and_clears_status",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-FM-4.23-001": {
        "implementation_refs": ("hla2010/backends/python/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_synchronization_points_and_save_status_callbacks",
            "tests/backends/test_python_backend_federation_extended.py::test_save_failure_reports_federation_not_saved_and_clears_status",
            "tests/backends/test_python_backend_federation_extended.py::test_abort_federation_save_reports_aborted_and_clears_status",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-FM-4.25-001": {
        "implementation_refs": ("hla2010/backends/python/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_request_federation_restore_failed_is_reported_for_unknown_save_label",
            "tests/backends/test_python_backend_federation_extended.py::test_restore_status_response_and_failure_callback_paths",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-FM-4.26-001": {
        "implementation_refs": ("hla2010/backends/python/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-FM-4.27-001": {
        "implementation_refs": ("hla2010/backends/python/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_restore_status_response_and_failure_callback_paths",
            "tests/backends/test_python_backend_federation_extended.py::test_save_restore_lifecycle_states_are_visible_in_mom_summary",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-FM-4.29-001": {
        "implementation_refs": ("hla2010/backends/python/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_restore_status_response_and_failure_callback_paths",
            "tests/backends/test_python_backend_federation_extended.py::test_abort_federation_restore_reports_aborted_and_clears_status",
            "tests/backends/test_python_backend_federation_extended.py::test_save_restore_mom_federate_objects_persist_across_restore_cycles",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-FM-4.31-001": {
        "implementation_refs": ("hla2010/backends/python/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_restore_status_response_and_failure_callback_paths",
            "tests/backends/test_python_backend_federation_extended.py::test_abort_federation_restore_reports_aborted_and_clears_status",
            "tests/backends/test_python_backend_federation_extended.py::test_request_federation_restore_failed_is_reported_for_unknown_save_label",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_query_federation_restore_status_rejects_not_connected_and_not_joined",
        ),
    },
    "HLA1516.1-FM-4.32-001": {
        "implementation_refs": ("hla2010/backends/python/save_restore.py",),
        "positive_test_refs": (
            "tests/backends/test_python_backend_federation_extended.py::test_restore_status_response_and_failure_callback_paths",
            "tests/backends/test_python_backend_federation_extended.py::test_abort_federation_restore_reports_aborted_and_clears_status",
            "tests/backends/test_python_backend_federation_extended.py::test_request_federation_restore_failed_is_reported_for_unknown_save_label",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-MOM-11.3-003": {
        "implementation_refs": ("hla2010/backends/python/mom_reporting.py",),
        "positive_test_refs": (
            "tests/verification/test_mom_observer_slice_v013.py::test_mom_observer_slice_reconstructs_mim_request_report_exchange",
        ),
        "negative_test_refs": (
            "tests/mom/test_mom_catalog_validation_v012.py::test_rejected_mom_report_request_does_not_emit_positive_mim_report",
        ),
    },
    "HLA1516.1-MOM-11.3-004": {
        "implementation_refs": ("hla2010/backends/python/mom_reporting.py",),
        "positive_test_refs": (
            "tests/mom/test_mom_catalog_validation_v012.py::test_mom_report_payload_uses_exact_mim_catalog_parameters",
        ),
        "negative_test_refs": (
            "tests/mom/test_mom_catalog_validation_v012.py::test_rejected_mom_report_request_does_not_emit_positive_mim_report",
        ),
    },
    "HLA1516.1-MOM-11.3-006": {
        "implementation_refs": ("hla2010/backends/python/mom_actions.py", "hla2010/backends/python/mom_reporting.py"),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/mom/test_mom_catalog_validation_v012.py::test_rejected_mom_report_request_does_not_emit_positive_mim_report",
            "tests/mom/test_mom_catalog_validation_v012.py::test_rejected_mom_adjustment_emits_exception_but_not_service_invocation_report",
            "tests/mom/test_mom_catalog_validation_v012.py::test_strict_mom_rejects_federate_sent_report_interaction",
        ),
    },
    "HLA1516.1-MOM-11.5-001": {
        "implementation_refs": ("hla2010/service_reporting.py", "hla2010/backends/python/mom_reporting.py"),
        "positive_test_refs": (
            "tests/verification/test_mom_observer_slice_v013.py::test_mom_observer_slice_reconstructs_service_invocation_reporting",
        ),
        "negative_test_refs": (
            "tests/mom/test_mom_catalog_validation_v012.py::test_rejected_mom_adjustment_emits_exception_but_not_service_invocation_report",
        ),
    },
    "HLA1516.1-MOM-11.5-003": {
        "implementation_refs": ("hla2010/service_reporting.py", "hla2010/backends/python/mom_actions.py", "hla2010/backends/python/mom_reporting.py"),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/mom/test_mom_catalog_validation_v012.py::test_rejected_mom_adjustment_emits_exception_but_not_service_invocation_report",
        ),
    },
    "HLA1516.1-OWN-7.7-002": {
        "implementation_refs": ("hla2010/backends/python/ownership.py",),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/backends/test_python_backend_object_ownership_extended.py::test_python_rti_release_denied_preserves_owner_and_no_acquisition_grant",
        ),
    },
    "HLA1516.1-OWN-7.9-002": {
        "implementation_refs": ("hla2010/backends/python/ownership.py",),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/backends/test_python_backend_object_ownership_extended.py::test_python_rti_acquisition_if_available_reports_unavailable_without_transfer",
        ),
    },
    "HLA1516.1-TM-8.2-001": {
        "implementation_refs": ("hla2010/backends/python/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_section8_core_time_management_surface_covers_callbacks_states_and_grants",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_object_ownership_extended.py::test_enable_time_regulation_rejects_not_connected_not_joined_invalid_lookahead_duplicate_save_restore_and_time_advancing",
        ),
    },
    "HLA1516.1-TM-8.2-002": {
        "implementation_refs": ("hla2010/backends/python/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_section8_core_time_management_surface_covers_callbacks_states_and_grants",
            "tests/backends/test_python_backend_time_ddm_extended.py::test_hla_immediate_time_enable_callbacks_expose_pending_request_exceptions",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-TM-8.2-003": {
        "implementation_refs": ("hla2010/backends/python/time_services.py",),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/backends/test_python_backend_object_ownership_extended.py::test_time_enable_callbacks_are_not_emitted_on_failed_requests",
        ),
    },
    "HLA1516.1-TM-8.5-001": {
        "implementation_refs": ("hla2010/backends/python/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_section8_core_time_management_surface_covers_callbacks_states_and_grants",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_object_ownership_extended.py::test_modify_lookahead_retract_change_attribute_order_type_and_enable_time_constrained_reject_core_negative_paths",
        ),
    },
    "HLA1516.1-TM-8.5-002": {
        "implementation_refs": ("hla2010/backends/python/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_section8_core_time_management_surface_covers_callbacks_states_and_grants",
            "tests/backends/test_python_backend_time_ddm_extended.py::test_hla_immediate_time_enable_callbacks_expose_pending_request_exceptions",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-TM-8.5-003": {
        "implementation_refs": ("hla2010/backends/python/time_services.py",),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/backends/test_python_backend_object_ownership_extended.py::test_time_enable_callbacks_are_not_emitted_on_failed_requests",
        ),
    },
    "HLA1516.1-TM-8.8-001": {
        "implementation_refs": ("hla2010/backends/python/time_services.py", "hla2010/backends/python/time_queue.py"),
        "positive_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_section8_core_time_management_surface_covers_callbacks_states_and_grants",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_advance_services_reject_not_connected_not_joined_invalid_and_past_time",
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_advance_services_reject_save_restore_and_outstanding_advance",
        ),
    },
    "HLA1516.1-TM-8.8-002": {
        "implementation_refs": ("hla2010/backends/python/time_queue.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_section8_core_time_management_surface_covers_callbacks_states_and_grants",
        ),
        "negative_test_refs": (),
    },
    "HLA1516.1-TM-8.8-003": {
        "implementation_refs": ("hla2010/backends/python/time_queue.py",),
        "positive_test_refs": (),
        "negative_test_refs": (
            "tests/time/test_mom_mim_time_v10.py::test_time_advance_request_waits_at_galt_boundary_but_available_request_can_grant_equal_galt",
        ),
    },
    "HLA1516.1-TM-8.10-001": {
        "implementation_refs": ("hla2010/backends/python/time_services.py", "hla2010/backends/python/time_queue.py"),
        "positive_test_refs": (
            "tests/time/test_mom_mim_time_v10.py::test_timestamp_order_next_message_requests_deliver_in_time_order_and_query_galt_lits",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_advance_services_reject_not_connected_not_joined_invalid_and_past_time",
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_advance_services_reject_save_restore_and_outstanding_advance",
        ),
    },
    "HLA1516.1-TM-8.12-001": {
        "implementation_refs": ("hla2010/backends/python/time_services.py", "hla2010/backends/python/time_queue.py"),
        "positive_test_refs": (
            "tests/backends/test_python_backend_time_ddm_extended.py::test_flush_queue_request_delivers_all_queued_tso_messages_and_grants_earliest_tso",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_advance_services_reject_not_connected_not_joined_invalid_and_past_time",
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_advance_services_reject_save_restore_and_outstanding_advance",
        ),
    },
    "HLA1516.1-TM-8.16-001": {
        "implementation_refs": ("hla2010/backends/python/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_time_v10.py::test_timestamp_order_next_message_requests_deliver_in_time_order_and_query_galt_lits",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_query_tail_rejects_not_connected_not_joined_and_save_restore",
        ),
    },
    "HLA1516.1-TM-8.17-001": {
        "implementation_refs": ("hla2010/backends/python/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_section8_core_time_management_surface_covers_callbacks_states_and_grants",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_query_tail_rejects_not_connected_not_joined_and_save_restore",
        ),
    },
    "HLA1516.1-TM-8.18-001": {
        "implementation_refs": ("hla2010/backends/python/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_mom_mim_time_v10.py::test_timestamp_order_next_message_requests_deliver_in_time_order_and_query_galt_lits",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_time_ddm_extended.py::test_time_query_tail_rejects_not_connected_not_joined_and_save_restore",
        ),
    },
    "HLA1516.1-TM-8.19-001": {
        "implementation_refs": ("hla2010/backends/python/time_services.py",),
        "positive_test_refs": (
            "tests/time/test_lookahead_backend_matrix.py::test_lookahead_backend_matrix_state_services",
        ),
        "negative_test_refs": (
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_query_lookahead_requires_time_regulation_and_modify_lookahead_rejects_pending_advance",
            "tests/time/test_mom_mim_and_time_semantics_v010.py::test_negative_lookahead_is_rejected_for_regulation_and_modification",
        ),
    },
    "HLA1516.1-TM-8.21-001": {
        "implementation_refs": ("hla2010/backends/python/time_services.py", "hla2010/backends/python/time_queue.py"),
        "positive_test_refs": (
            "tests/time/test_mom_mim_time_management_v010.py::test_tso_message_retraction_prevents_later_delivery",
        ),
        "negative_test_refs": (
            "tests/backends/test_python_backend_object_ownership_extended.py::test_modify_lookahead_retract_change_attribute_order_type_and_enable_time_constrained_reject_core_negative_paths",
        ),
    },
}


def _section_ref(document: str, clause: str) -> str:
    normalized = str(clause).strip()
    if normalized.lower().startswith("clause "):
        normalized = normalized.split(" ", 1)[1].strip()
    if normalized in {"Framework concepts", "Federation and federate rules", "Object model concepts", "Time concept rules"}:
        return f"{document} {normalized}"
    return f"{document} §{normalized}"


def _curated_row_kind(row: dict[str, Any]) -> str:
    status = str(row.get("status", "")).strip().lower()
    seed_markers = {
        status,
        str(row.get("source_type", "")).strip().lower(),
        str(row.get("normative_keyword", "")).strip().lower(),
    }
    return "curated-seed" if {"seed", "seeded"} & seed_markers else "extracted-requirement"


def _curated_service_group(row: dict[str, Any]) -> str:
    family = str(row.get("family", "")).strip()
    service_group = str(row.get("service_group", "")).strip()
    topic = str(row.get("topic", "")).strip()
    decomposition_kind = str(row.get("decomposition_kind", "")).strip()
    if family and decomposition_kind:
        return f"{family}/{decomposition_kind}"
    if family:
        return family
    if service_group and decomposition_kind:
        return f"{service_group}/{decomposition_kind}"
    if service_group:
        return service_group
    if topic:
        return topic
    return "requirement"


def _load_curated_requirement_rows() -> list[dict[str, Any]]:
    repo_root = _repo_root()
    traceability_path = repo_root / "requirements" / "traceability_matrix.csv"
    requirements_dir = repo_root / "requirements"
    if not requirements_dir.exists() or not traceability_path.exists():
        return []
    excluded_sources = {
        "hla1516_1_clause_5_declaration_management.csv",
        "hla1516_1_clause_6_object_management.csv",
    }
    excluded_requirement_ids: set[str] = set()
    for source_name in excluded_sources:
        source_path = requirements_dir / source_name
        if not source_path.exists():
            continue
        with source_path.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                requirement_id = str(row.get("requirement_id", "")).strip()
                if requirement_id:
                    excluded_requirement_ids.add(requirement_id)

    with traceability_path.open(newline="", encoding="utf-8") as fh:
        trace_rows = list(csv.DictReader(fh))
    trace_by_requirement = {row["requirement_id"]: row for row in trace_rows if row.get("requirement_id")}

    curated_rows_by_id: dict[str, dict[str, Any]] = {}
    seen: set[str] = set()

    for source_path in sorted(requirements_dir.glob("*.csv")):
        if source_path.name == "traceability_matrix.csv":
            continue
        if source_path.name in excluded_sources:
            continue
        with source_path.open(newline="", encoding="utf-8") as fh:
            source_rows = list(csv.DictReader(fh))
        for row in source_rows:
            requirement_id = str(row.get("requirement_id", "")).strip()
            if not requirement_id or requirement_id in seen or requirement_id in excluded_requirement_ids:
                continue
            trace = trace_by_requirement.get(requirement_id, {})
            document = str(row.get("standard") or row.get("source_document") or trace.get("source_document") or "").strip()
            clause = str(row.get("clause") or trace.get("clause") or "").strip()
            title = str(row.get("requirement_text") or row.get("topic") or row.get("canonical_topic") or requirement_id).strip()
            test_refs = _split_semicolon_list(trace.get("test_refs")) or _split_scalar_list(row.get("test_id"))
            implementation_refs = (
                _split_semicolon_list(trace.get("implementation_refs"))
                or _path_like_refs(row.get("implementation_target"))
                or _path_like_refs(row.get("derived_interpretation"))
            )
            linked_assets = [item for item in [str(trace.get("current_artifact_id", "")).strip(), str(row.get("parent_requirement_id", "")).strip()] if item]
            note_parts = [
                f"verification_method={row['verification_method']}" if row.get("verification_method") else "",
                str(row.get("notes", "")).strip(),
                str(trace.get("notes", "")).strip(),
            ]
            direct_refs = _CURATED_REQUIREMENT_DIRECT_REFS.get(requirement_id, {})
            curated_rows_by_id[requirement_id] = {
                "matrix_id": requirement_id,
                "kind": _curated_row_kind(row),
                "document": document,
                "section_ref": _section_ref(document, clause) if document and clause else document or clause,
                "title": title,
                "requirement_id": requirement_id,
                "service_group": _curated_service_group(row),
                "status": trace.get("status") or row.get("status", "planned"),
                "implementation_refs": list(direct_refs.get("implementation_refs", implementation_refs)),
                "positive_test_refs": list(direct_refs.get("positive_test_refs", test_refs)),
                "negative_test_refs": list(direct_refs.get("negative_test_refs", ())),
                "artifact_refs": sorted(
                    set(_split_semicolon_list(trace.get("artifact_refs"))) | {f"requirements/{source_path.name}"}
                ),
                "linked_methods": _split_scalar_list(row.get("linked_methods")),
                "linked_assets": linked_assets,
                "notes": "; ".join(part for part in note_parts if part),
                "source": f"requirements/{source_path.name}",
            }
            seen.add(requirement_id)

    for requirement_id, trace in sorted(trace_by_requirement.items()):
        if requirement_id in seen or requirement_id in excluded_requirement_ids:
            continue
        curated_rows_by_id[requirement_id] = {
                "matrix_id": requirement_id,
                "kind": "curated-seed",
                "document": trace["source_document"],
                "section_ref": _section_ref(trace["source_document"], trace["clause"]),
                "title": trace["canonical_topic"],
                "requirement_id": requirement_id,
                "service_group": "seed",
                "status": trace["status"],
                "implementation_refs": _split_semicolon_list(trace.get("implementation_refs")),
                "positive_test_refs": _split_semicolon_list(trace.get("test_refs")),
                "negative_test_refs": [],
                "artifact_refs": _split_semicolon_list(trace.get("artifact_refs")),
                "linked_assets": [item for item in [trace.get("current_artifact_id", "").strip()] if item],
                "notes": trace.get("notes", "").strip(),
                "source": "requirements/traceability_matrix.csv",
            }
    return [curated_rows_by_id[key] for key in sorted(curated_rows_by_id)]


def _load_backend_conformance_vendor_rows() -> dict[str, dict[str, Any]]:
    matrix_path = _repo_root() / "docs" / "backend_conformance_matrix.md"
    if not matrix_path.exists():
        return {}

    rows_by_clause: dict[str, dict[str, Any]] = {}
    for raw_line in matrix_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) < 7:
            continue
        if parts[0] in {"Clause", "---"}:
            continue
        clause = parts[0]
        if not re.fullmatch(r"\d+(?:\.\d+)?", clause):
            continue
        rows_by_clause[clause] = {
            "python_runtime_status": parts[2],
            "certi_runtime_status": parts[3],
            "pitch_runtime_status": parts[4],
            "vendor_evidence_refs": _extract_markdown_link_targets(parts[5]),
            "vendor_notes": "|".join(parts[6:]).strip(),
            "vendor_source": "docs/backend_conformance_matrix.md",
        }
    return rows_by_clause


def _load_operational_vendor_profiles() -> dict[str, list[dict[str, Any]]]:
    matrix_path = _repo_root() / "docs" / "rti_options_and_test_matrix.md"
    if not matrix_path.exists():
        return {}

    rows: list[dict[str, Any]] = []
    in_table = False
    for raw_line in matrix_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("| Backend family | Bridge model | Transport | Exchange | Timed | Sync | Ownership | Negotiated Ownership | Real runtime |"):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            break
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) != 9:
            continue
        if parts[0] == "---":
            continue
        rows.append(
            {
                "backend_family": parts[0],
                "bridge_model": parts[1],
                "transport": parts[2],
                "exchange": parts[3],
                "timed": parts[4],
                "sync": parts[5],
                "ownership": parts[6],
                "negotiated ownership": parts[7],
                "real runtime": parts[8],
            }
        )
    return {"rows": rows, "source": "docs/rti_options_and_test_matrix.md"}


def _extract_numeric_clause(section_ref: Any) -> str:
    match = re.search(r"§\s*(\d+(?:\.\d+)?)", str(section_ref or ""))
    return match.group(1) if match else ""


def _section_root(section_ref: Any) -> str:
    clause = _extract_numeric_clause(section_ref)
    return clause.split(".", 1)[0] if clause else ""


def _operational_capability_bucket(row: dict[str, Any]) -> str:
    if str(row.get("document")) != "IEEE 1516.1-2010":
        return ""
    clause = _extract_numeric_clause(row.get("section_ref"))
    root = clause.split(".", 1)[0] if clause else ""
    title = str(row.get("title", "")).lower()
    if root == "8":
        return "Timed"
    if root == "6":
        return "Exchange"
    if root == "7":
        negotiated_tokens = ("negotiated", "acquisition", "divestiture", "release", "cancel", "assumption")
        if any(token in title for token in negotiated_tokens):
            return "Negotiated Ownership"
        return "Ownership"
    if root == "4" and clause in {"4.11", "4.12", "4.13", "4.14", "4.15"}:
        return "Sync"
    return ""


def _operational_vendor_note(
    row: dict[str, Any],
    *,
    profile_rows: dict[str, Any],
) -> dict[str, Any]:
    augmented = dict(row)
    bucket = _operational_capability_bucket(augmented)
    augmented.setdefault("vendor_profile_bucket", bucket)
    if not bucket or not profile_rows:
        augmented.setdefault("vendor_profile_refs", [])
        augmented.setdefault("vendor_profile_notes", "")
        augmented.setdefault("vendor_profile_source", "")
        return augmented

    matching: list[str] = []
    for profile in profile_rows.get("rows", []):
        value = profile.get(bucket.lower(), "")
        matching.append(
            f"{profile['backend_family']} ({profile['bridge_model']}, {profile['transport']}): {value}"
        )
    augmented.setdefault("vendor_profile_refs", [profile_rows.get("source", "")] if profile_rows.get("source") else [])
    augmented.setdefault("vendor_profile_notes", "; ".join(matching))
    augmented.setdefault("vendor_profile_source", profile_rows.get("source", ""))
    return augmented


def _with_vendor_parity(
    row: dict[str, Any],
    *,
    vendor_rows_by_clause: dict[str, dict[str, Any]],
    operational_vendor_profiles: dict[str, Any] | None = None,
) -> dict[str, Any]:
    augmented = dict(row)
    clause = _extract_numeric_clause(augmented.get("section_ref"))
    vendor = vendor_rows_by_clause.get(clause, {}) if str(augmented.get("document")) == "IEEE 1516.1-2010" else {}
    augmented.setdefault("python_runtime_status", vendor.get("python_runtime_status", ""))
    augmented.setdefault("certi_runtime_status", vendor.get("certi_runtime_status", ""))
    augmented.setdefault("pitch_runtime_status", vendor.get("pitch_runtime_status", ""))
    augmented.setdefault("vendor_evidence_refs", list(vendor.get("vendor_evidence_refs", ())))
    augmented.setdefault("vendor_notes", vendor.get("vendor_notes", ""))
    augmented.setdefault("vendor_source", vendor.get("vendor_source", ""))
    return _operational_vendor_note(
        augmented,
        profile_rows=operational_vendor_profiles or {},
    )


@dataclass(frozen=True)
class VerificationAsset:
    """One traceable verification artifact or planned artifact."""

    asset_id: str
    asset_type: str
    title: str
    section_refs: tuple[str, ...]
    status: str
    evidence: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VerificationPlan:
    """Versioned verification plan for this development RTI."""

    version: str
    scope: str
    assets: tuple[VerificationAsset, ...] = field(default_factory=tuple)

    def by_status(self) -> dict[str, list[VerificationAsset]]:
        grouped: dict[str, list[VerificationAsset]] = {}
        for asset in self.assets:
            grouped.setdefault(asset.status, []).append(asset)
        return grouped

    def by_section(self) -> dict[str, list[VerificationAsset]]:
        grouped: dict[str, list[VerificationAsset]] = {}
        for asset in self.assets:
            for section in asset.section_refs:
                grouped.setdefault(section, []).append(asset)
        return grouped

    def coverage_summary(self) -> dict[str, Any]:
        grouped = self.by_status()
        return {
            "version": self.version,
            "scope": self.scope,
            "asset_count": len(self.assets),
            "status_counts": {status: len(items) for status, items in sorted(grouped.items())},
            "sections": sorted(self.by_section()),
            "gap_asset_ids": [asset.asset_id for asset in self.assets if asset.status in {"gap", "planned"} or asset.gaps],
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "scope": self.scope,
            "summary": self.coverage_summary(),
            "assets": [asset.as_dict() for asset in self.assets],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.as_dict(), indent=indent, sort_keys=True)


def build_verification_plan(version: str = "0.13.0") -> VerificationPlan:
    """Return the current honest verification plan.

    Status vocabulary:
    ``implemented-slice`` means focused tests exist for the present subset;
    ``implemented-smoke`` means scenario/parity smoke evidence exists;
    ``planned`` means the asset is identified but not yet implemented;
    ``gap`` means the behavior is known incomplete or externally blocked.
    """

    assets = (
        VerificationAsset(
            "REQ-MOM-TABLE-001",
            "requirement",
            "MOM object and interaction exposure is derived from the active MIM/FOM catalog",
            ("1516.1-2010 §11.2", "1516.1-2010 §11.3", "1516.1-2010 Annex G"),
            "implemented-slice",
            (
                "hla2010/mom_catalog.py::build_mom_exposure_model",
                "tests/mom/test_mom_catalog_validation_v012.py::test_mom_catalog_is_derived_from_standard_mim_and_exposes_validation_matrix",
            ),
            notes="The active catalog now drives MOM object attributes, interaction parameters, request/report pairs, direction, and matrix output.",
        ),
        VerificationAsset(
            "REQ-MOM-NEG-001",
            "requirement",
            "Strict MOM decoding reports and raises through generated parameterized negative-path tests",
            ("1516.1-2010 §11.4.1", "1516.1-2010 §11.5"),
            "implemented-slice",
            (
                "hla2010/mom_negative_testing.py::build_mom_negative_test_cases",
                "tests/verification/test_mom_negative_matrix_executable_v013.py::test_generated_mom_negative_matrix_case_executes",
                "tests/test_mom_negative_matrix_parametrized_v013.py::test_generated_mom_negative_matrix_case_executes",
                "verification/mom_negative_matrix_v0_13.json",
            ),
            gaps=("Semantic HLAservice precondition-negative rows remain planned separately because they require service-specific federation setup.",),
        ),
        VerificationAsset(
            "REQ-MOM-REPORT-001",
            "requirement",
            "MOM reports use the exact parameter names declared in the active MIM catalog",
            ("1516.1-2010 §11.3", "1516.1-2010 §11.4.1", "1516.1-2010 Annex G"),
            "implemented-slice",
            ("tests/mom/test_mom_catalog_validation_v012.py::test_mom_report_payload_uses_exact_mim_catalog_parameters",),
            gaps=("Report payload values are still local-process diagnostics for several specialized report classes.",),
        ),
        VerificationAsset(
            "REQ-MOM-SERVICE-001",
            "requirement",
            "MOM HLAservice interactions are modeled as RTI-received actions with negative-path service failure reporting",
            ("1516.1-2010 §11.3", "1516.1-2010 §11.4.1"),
            "implemented-slice",
            ("hla2010/backends/python/mom_actions.py::_run_mom_service_action", "verification/mom_negative_matrix_v0_12.json"),
            gaps=("Not every Annex G service action has a complete semantic implementation yet.",),
        ),
        VerificationAsset(
            "REQ-MOM-OBSERVER-001",
            "requirement",
            "A MOM observer witness can reconstruct federation-visible MOM objects, reports, and service invocation traffic",
            ("1516.1-2010 §11.2", "1516.1-2010 §11.3", "1516.1-2010 §11.5"),
            "implemented-slice",
            (
                "tests/verification/test_mom_observer_slice_v013.py::test_mom_observer_slice_reconstructs_federate_object_discovery_and_reflection",
                "tests/verification/test_mom_observer_slice_v013.py::test_mom_observer_slice_reconstructs_mim_request_report_exchange",
                "tests/verification/test_mom_observer_slice_v013.py::test_mom_observer_slice_reconstructs_service_invocation_reporting",
                "analysis/compliance/verification_traceability.csv",
            ),
            gaps=("The observer proof is currently a focused local-process slice, not yet a standalone reusable monitor federate package.",),
            notes="This slice treats MOM traffic as an independent witness for visible federation state and service reporting.",
        ),
        VerificationAsset(
            "REQ-OMT-PARSE-001",
            "requirement",
            (
                "FOM/MIM XML parsing and name-bearing OMT catalog extraction cover the active "
                "1516.2 object, interaction, attribute, parameter, dimension, and time tables"
            ),
            (
                "1516.2-2010 §4",
                "1516.2-2010 §4.2",
                "1516.2-2010 §4.3",
                "1516.2-2010 §4.4",
                "1516.2-2010 §4.5",
                "1516.2-2010 §4.6",
                "1516.2-2010 §4.7",
                "1516.2-2010 Annex D",
            ),
            "implemented-slice",
            (
                "hla2010/fom.py::parse_fom_xml",
                "tests/factories/test_fom_time_factories.py::test_python_rti_resolves_fom_path_and_uses_requested_time_factory",
                "tests/scenarios/test_startup_sync_fom_java_translation_v09.py::test_strict_fom_lookup_rejects_unknown_names",
                "tests/time/test_mom_mim_and_time_semantics_v010.py::test_mom_fom_module_request_reports_requested_module_payload",
            ),
            notes="This slice proves the repo consumes active FOM/MIM XML into a usable catalog and surfaces the expected names and module payloads.",
        ),
        VerificationAsset(
            "REQ-OMT-MERGE-001",
            "requirement",
            "FOM module merge and MIM/FOM combination rules are enforced for the supported 1516.2 subset",
            ("1516.2-2010 §7",),
            "implemented-slice",
            (
                "hla2010/fom.py::merge_fom_modules",
                "tests/scenarios/test_startup_sync_fom_java_translation_v09.py::test_conflicting_time_implementations_are_rejected",
                "tests/backends/test_python_backend_federation_extended.py::test_create_federation_execution_with_explicit_mim_overrides_default_mim",
                "tests/backends/test_python_backend_federation_extended.py::test_join_federation_execution_with_additional_modules_updates_catalog",
            ),
            gaps=("The merge policy is a supported subset of IEEE 1516.2-2010 §7 rather than a complete schema-level implementation.",),
        ),
        VerificationAsset(
            "REQ-OMT-SCHEMA-001",
            "requirement",
            "Annex E schema-level conformance checking is identified explicitly and remains planned",
            ("1516.2-2010 Annex E",),
            "planned",
            ("hla2010/fom.py",),
            gaps=("The parser is intentionally not a full XML Schema validator, so Annex E conformance is not yet executable.",),
        ),
        VerificationAsset(
            "REQ-SERVICE-FILE-001",
            "requirement",
            "Service-report file output contains initial and per-service records with section anchors",
            ("1516.1-2010 §11.5",),
            "implemented-slice",
            ("hla2010/service_reporting.py", "tests/verification/test_compliance_slice_v011.py::test_mom_service_reports_to_file_and_global_report_file"),
            gaps=("The current format is JSONL for auditability; exact vendor/report-file formatting is not claimed.",),
        ),
        VerificationAsset(
            "REQ-TIME-ORDER-001",
            "requirement",
            "Timestamp-order queues respect local GALT/LITS-style lower-bound rules and DDM filtering before delivery",
            ("1516.1-2010 §8.1", "1516.1-2010 §8.13", "1516.1-2010 §8.16", "1516.1-2010 §8.18", "1516.1-2010 §9"),
            "implemented-slice",
            (
                "hla2010/time_management.py",
                "tests/verification/test_compliance_slice_v011.py::test_ddm_region_filtering_applies_before_timestamp_order_delivery",
            ),
            gaps=("The distributed-time algorithm remains a local-process approximation, not a proven multi-process LBTS algorithm.",),
        ),
        VerificationAsset(
            "REQ-SAVE-RESTORE-001",
            "requirement",
            "Save/restore coordinates with time-state and restores logical-time state",
            ("1516.1-2010 §4.16-§4.25", "1516.1-2010 §8"),
            "implemented-slice",
            ("tests/verification/test_compliance_slice_v011.py::test_scheduled_save_waits_for_time_and_restore_reinstates_time_state",),
            gaps=("External persistent save-file interchange is not implemented.",),
        ),
        VerificationAsset(
            "REQ-SAVE-RESTORE-OBJECT-STATE-001",
            "requirement",
            "Save/restore reinstates saved object existence, name mapping, attribute values, and ownership state",
            ("1516-2010 §12.2", "1516.1-2010 §4.24-§4.29", "1516.1-2010 §6", "1516.1-2010 §7"),
            "implemented-slice",
            (
                "hla2010/backends/python/save_restore.py",
                "tests/verification/test_compliance_slice_v011.py::test_restore_reinstates_saved_object_values_names_and_ownership_state",
            ),
            gaps=("External persistent save-file interchange is not implemented.",),
        ),
        VerificationAsset(
            "REQ-SAVE-RESTORE-FEDERATE-LOCAL-STATE-001",
            "requirement",
            "Save/restore reinstates saved federate runtime flags, policy switches, reporting switches, conveyance state, order-override state, and transportation-override state",
            ("1516-2010 §12.2", "1516.1-2010 §4.24-§4.29", "1516.1-2010 §8"),
            "implemented-slice",
            (
                "hla2010/backends/python/save_restore.py",
                "tests/verification/test_compliance_slice_v011.py::test_restore_reinstates_saved_federate_runtime_flags_and_lookahead_state",
                "tests/verification/test_compliance_slice_v011.py::test_restore_reinstates_saved_federate_policy_reporting_and_conveyance_switches",
                "tests/verification/test_compliance_slice_v011.py::test_restore_reinstates_saved_attribute_and_interaction_order_overrides",
                "tests/verification/test_compliance_slice_v011.py::test_restore_reinstates_saved_attribute_and_interaction_transportation_overrides",
            ),
        ),
        VerificationAsset(
            "REQ-SAVE-RESTORE-CALLBACK-POLICY-001",
            "requirement",
            "Save/restore treats callback enablement as local runtime policy rather than persisted federation state",
            ("1516-2010 §12.2", "1516.1-2010 §4.24-§4.29"),
            "implemented-slice",
            (
                "hla2010/backends/python/save_restore.py",
                "tests/verification/test_compliance_slice_v011.py::test_restore_treats_callback_enablement_as_runtime_policy_not_saved_state",
            ),
            notes="This is an explicit implementation contract: callback dispatch enablement is process-local delivery policy, while persisted restore state covers federation-visible ordering and reporting semantics.",
        ),
        VerificationAsset(
            "REQ-SAVE-RESTORE-TRANSIENT-STATE-001",
            "requirement",
            "Save/restore discards stale pre-restore callback-queue and message-retraction bookkeeping state",
            ("1516-2010 §12.2", "1516.1-2010 §4.24-§4.29", "1516.1-2010 §8.21"),
            "implemented-slice",
            (
                "hla2010/backends/python/save_restore.py",
                "tests/verification/test_compliance_slice_v011.py::test_restore_discards_pre_restore_callback_queue_and_retraction_bookkeeping",
            ),
            notes="This slice specifies transient post-restore quiescence rather than persistence of queued callback or message-retraction state.",
        ),
        VerificationAsset(
            "REQ-DM-DECLARATION-STATE-001",
            "requirement",
            "Declaration-management state gates registration, update, and interaction send behavior",
            ("1516.1-2010 §5.1", "1516.1-2010 §5.1.2", "1516.1-2010 §5.1.3", "1516.1-2010 §5.2", "1516.1-2010 §5.3", "1516.1-2010 §5.4", "1516.1-2010 §5.5"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend.py",
                "tests/backends/test_python_backend_time_ddm_extended.py::test_strict_publication_gates_registration_update_and_interaction_sends",
                "tests/scenarios/test_target_radar_scenario.py",
            ),
            notes="This is narrower than the end-to-end Target/Radar smoke because it explicitly exercises publication state as a precondition for later object and interaction flow.",
        ),
        VerificationAsset(
            "REQ-DM-SUBSCRIPTION-DELIVERY-001",
            "requirement",
            "Declaration subscriptions drive discover/reflect/receive delivery visibility",
            ("1516.1-2010 §5.6", "1516.1-2010 §5.7", "1516.1-2010 §5.8", "1516.1-2010 §5.9", "1516.1-2010 §6.9", "1516.1-2010 §6.11", "1516.1-2010 §6.13", "1516.1-2010 §6.17", "1516.1-2010 §6.18"),
            "implemented-slice",
            (
                "tests/scenarios/test_target_radar_scenario.py",
                "tests/backends/test_python_backend_time_ddm_extended.py",
                "analysis/two_federate_suite/two_federate_callbacks.csv",
            ),
            notes="This slice ties object/interaction subscriptions directly to the visible callback traffic instead of relying only on service-level existence.",
        ),
        VerificationAsset(
            "REQ-DM-DDM-INTERPLAY-001",
            "requirement",
            "DM subscriptions and DDM scope filtering compose before delivery",
            ("1516.1-2010 §5.1.5", "1516.1-2010 §6.1.2", "1516.1-2010 §6.1.3", "1516.1-2010 §6.1.4", "1516.1-2010 §9"),
            "implemented-slice",
            (
                "tests/verification/test_compliance_slice_v011.py::test_ddm_region_filtering_applies_before_timestamp_order_delivery",
                "tests/backends/test_python_backend_time_ddm_extended.py",
            ),
            notes="This is the narrowest current proof that routing/scope decisions happen before reflect/receive delivery.",
        ),
        VerificationAsset(
            "REQ-DM-DDM-OBJECT-SCOPE-001",
            "requirement",
            "Object attribute routing is suppressed while regions are out of scope and resumes when regions overlap",
            ("1516.1-2010 §5.1.5", "1516.1-2010 §6.1.2", "1516.1-2010 §6.1.3", "1516.1-2010 §6.1.4", "1516.1-2010 §9"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_time_ddm_extended.py::test_ddm_object_scope_filter_blocks_out_of_scope_reflects_until_regions_overlap",
            ),
            notes="This slice is narrower than the generic DDM routing asset because it proves both the blocked and restored reflect path for a region-scoped object attribute.",
        ),
        VerificationAsset(
            "REQ-DM-DDM-GATING-001",
            "requirement",
            "DM or DDM subscription declarations are required before object discovery, attribute reflection, or interaction receipt occurs",
            ("1516.1-2010 §5.1", "1516.1-2010 §5.1.5", "1516.1-2010 §6.1.1", "1516.1-2010 §6.1.3", "1516.1-2010 §6.1.7"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_time_ddm_extended.py::test_dm_ddm_subscriptions_gate_discovery_reflect_and_receive_until_declared",
            ),
            notes="This slice proves no discovery, reflect, or receive occurs before subscription declaration, and that all three become possible after the matching DDM subscriptions are declared.",
        ),
        VerificationAsset(
            "REQ-OM-SCOPE-CALLBACKS-001",
            "requirement",
            "Object-scope transitions emit Attributes In Scope and Attributes Out Of Scope callbacks for known subscribed attributes",
            ("1516.1-2010 §6.17", "1516.1-2010 §6.18", "1516.1-2010 §9"),
            "implemented-slice",
            (
                "hla2010/backends/python/subscriptions.py",
                "tests/backends/test_python_backend_time_ddm_extended.py::test_attributes_in_scope_and_out_of_scope_callbacks_track_region_scope_transitions",
            ),
            notes="This slice proves both the gained-scope and lost-scope callback transitions on the same known object instance under DDM region changes.",
        ),
        VerificationAsset(
            "REQ-OM-DISCOVERY-LIFECYCLE-001",
            "requirement",
            "Object registration, discovery, known-class behavior, and removal form a stable object lifecycle",
            ("1516.1-2010 §6.1.1", "1516.1-2010 §6.8", "1516.1-2010 §6.9", "1516.1-2010 §6.15"),
            "implemented-slice",
            (
                "tests/scenarios/test_target_radar_scenario.py",
                "analysis/two_federate_suite/two_federate_callbacks.csv",
                "tests/verification/test_compliance_slice_v011.py",
            ),
            gaps=("Closest-subscribed-superclass and immutable discovered-class semantics are still broader than the present scenario proofs.",),
        ),
        VerificationAsset(
            "REQ-OM-DISCOVERY-CLASS-001",
            "requirement",
            "Discovery chooses the closest subscribed superclass and the discovered class remains stable for later lookups",
            ("1516.1-2010 §6.1.1", "1516.1-2010 §6.9"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_support_services.py::test_discovery_uses_closest_subscribed_superclass_and_known_class_stays_stable",
            ),
            notes="This slice specifically proves discovered-class selection and stability instead of only proving that a discovery callback occurs.",
        ),
        VerificationAsset(
            "REQ-OM-REQUEST-VALUE-UPDATE-001",
            "requirement",
            "Attribute-value update requests trigger Provide Attribute Value Update at relevant owners",
            ("1516.1-2010 §6.19", "1516.1-2010 §6.20"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_time_ddm_extended.py::test_request_attribute_value_update_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore",
                "tests/backends/test_python_backend_time_ddm_extended.py",
            ),
            gaps=("The extracted Clause 6 matrix currently tracks §6.19 explicitly; §6.20 remains linked as callback evidence rather than its own extracted row.",),
        ),
        VerificationAsset(
            "REQ-OM-REQUEST-VALUE-UPDATE-ROUTING-001",
            "requirement",
            "Request Attribute Value Update routes object-target and class-target requests only to relevant owning federates",
            ("1516.1-2010 §6.19", "1516.1-2010 §6.20"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_time_ddm_extended.py::test_request_attribute_value_update_routes_only_to_relevant_object_owners",
            ),
            notes="This slice is narrower than the generic request-value-update asset because it proves owner-specific routing for both object-handle and class-handle requests.",
        ),
        VerificationAsset(
            "REQ-OM-TRANSPORT-SCOPE-001",
            "requirement",
            "Object-management routing semantics cover transport choice, scope, and local-delete restrictions",
            ("1516.1-2010 §6.1.2", "1516.1-2010 §6.1.10", "1516.1-2010 §6.1.12", "1516.1-2010 §6.14", "1516.1-2010 §6.16", "1516.1-2010 §6.23", "1516.1-2010 §6.25", "1516.1-2010 §6.27", "1516.1-2010 §6.29"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_time_ddm_extended.py",
                "tests/time/test_mom_mim_time_v10.py",
            ),
            gaps=("Transport-type semantics, update-rate reduction, and local-delete/orphan rules still have broader specification language than the current focused runtime slices.",),
        ),
        VerificationAsset(
            "REQ-OM-LOCAL-KNOWLEDGE-001",
            "requirement",
            "Local delete clears only the invoking federate's object knowledge and allows later rediscovery",
            ("1516.1-2010 §6.1.6", "1516.1-2010 §6.16"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_support_services.py::test_local_delete_clears_only_local_knowledge_and_object_can_be_rediscovered",
            ),
            gaps=("The broader orphan-instance narrative remains larger than this focused local-delete knowledge slice.",),
        ),
        VerificationAsset(
            "REQ-OM-ORPHAN-KNOWLEDGE-001",
            "requirement",
            "An ownerless object instance remains discoverable to a joined federate until that federate locally deletes it",
            ("1516.1-2010 §6.1.6", "1516.1-2010 §6.16"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_support_services.py::test_orphan_object_remains_discovered_until_local_delete_clears_only_local_knowledge",
            ),
            gaps=("This slice covers known-object behavior for orphaned instances, not the entire orphan-object lifecycle narrative.",),
        ),
        VerificationAsset(
            "REQ-OM-ORPHAN-LIFECYCLE-001",
            "requirement",
            "An orphaned object remains discoverable to existing and late subscribers, supports local-delete knowledge clearing, and is removed globally only by explicit delete",
            ("1516.1-2010 §6.1.6", "1516.1-2010 §6.14", "1516.1-2010 §6.15", "1516.1-2010 §6.16"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_support_services.py::test_orphan_object_lifecycle_supports_late_discovery_local_delete_and_global_remove",
            ),
            notes="This slice proves an ownerless object persists in federation state, remains discoverable to a late subscriber, can be locally deleted at one federate without affecting others, and is removed globally only when the registrar explicitly deletes it.",
        ),
        VerificationAsset(
            "REQ-OM-ATTRIBUTE-RELEVANCE-001",
            "requirement",
            "Attribute relevance is determined from the combination of publication, subscription, ownership, and DDM scope on a single object instance",
            ("1516.1-2010 §6.1.5",),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_support_services.py::test_attribute_relevance_combines_publication_subscription_ownership_and_scope",
            ),
            notes="This slice proves that an in-scope subscribed observer reflects updates from the current owner, suppresses out-of-scope updates, and stops accepting stale updates from the previous owner after transfer.",
        ),
        VerificationAsset(
            "REQ-OM-TIMED-DELETE-REMOVE-001",
            "requirement",
            "A timestamped delete removes the object from federation knowledge only after the time-managed remove callback is delivered",
            ("1516.1-2010 §6.14", "1516.1-2010 §6.15", "1516.1-2010 §8"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_support_services.py::test_time_managed_delete_defers_remove_until_grant_and_then_clears_known_object",
            ),
            notes="This slice proves the time-managed delete/remove path: no early removal before grant, TSO remove delivery after grant, and known-object cleanup after callback delivery.",
        ),
        VerificationAsset(
            "REQ-OM-UPDATE-RATE-001",
            "requirement",
            "Subscribed and FOM-declared update-rate settings throttle eligible reflected updates across direct, inherited, and regioned subscriptions without suppressing receive-order delivery that has no logical-time basis",
            ("1516.1-2010 §5.1.6", "1516.1-2010 §6.1.12"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_support_services.py::test_update_rate_designator_throttles_timed_reflects",
                "tests/backends/test_python_backend_support_services.py::test_update_rate_designator_does_not_suppress_receive_order_updates",
                "tests/backends/test_python_backend_support_services.py::test_fom_declared_update_rate_defaults_apply_to_inherited_and_regioned_subscriptions",
            ),
            gaps=("Current proof covers explicit designators plus FOM-declared defaults for direct, inherited, and regioned subscriptions, along with explicit receive-order non-suppression when no logical-time basis exists. Broader vendor-style policies outside this backend's logical-time-driven model remain out of scope.",),
        ),
        VerificationAsset(
            "REQ-OM-REFLECT-KNOWN-CLASS-001",
            "requirement",
            "Reflected attributes are reported using the subscriber's known discovered class handles",
            ("1516.1-2010 §6.11",),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_support_services.py::test_reflect_attributes_are_mapped_to_known_discovered_class_handles",
            ),
            notes="This slice proves handle-space normalization for reflect callbacks after discovery at a subscribed superclass.",
        ),
        VerificationAsset(
            "REQ-DM-TIME-INDEPENDENCE-001",
            "requirement",
            "Declaration-management publication and subscription state takes effect even while federates are time managed",
            ("1516.1-2010 §5.1", "1516.1-2010 §8"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_object_ownership_extended.py::test_declaration_management_effects_apply_while_time_managed",
            ),
            notes="This slice proves that DM state changes remain effective while one federate is time regulating and another is time constrained.",
        ),
        VerificationAsset(
            "REQ-DM-UNPUBLISH-OBJECT-001",
            "requirement",
            "Unpublishing object-class attributes removes the federate's ability to perform strict updates for those attributes",
            ("1516.1-2010 §5.3", "1516.1-2010 §6.10"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_object_ownership_extended.py::test_unpublishing_object_class_attributes_prevents_strict_updates",
            ),
        ),
        VerificationAsset(
            "REQ-DM-UNPUBLISH-INTERACTION-001",
            "requirement",
            "Unpublishing an interaction class removes the federate's ability to perform strict sends for that class",
            ("1516.1-2010 §5.5", "1516.1-2010 §6.12"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_object_ownership_extended.py::test_unpublishing_interaction_class_prevents_strict_sends",
            ),
        ),
        VerificationAsset(
            "REQ-DM-UNSUBSCRIBE-OBJECT-001",
            "requirement",
            "Unsubscribing object-class attributes removes interest in later reflected updates for those attributes",
            ("1516.1-2010 §5.7", "1516.1-2010 §6.11"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_time_ddm_extended.py::test_unsubscribe_object_class_attributes_removes_interest_in_future_reflections",
            ),
        ),
        VerificationAsset(
            "REQ-OM-TRANSPORT-REPORT-001",
            "requirement",
            "Transportation-type change, query, and report services emit confirm/report callbacks for the backend's supported reliable and best-effort subset",
            ("1516.1-2010 §6.1.10", "1516.1-2010 §6.23", "1516.1-2010 §6.24", "1516.1-2010 §6.25", "1516.1-2010 §6.26", "1516.1-2010 §6.27", "1516.1-2010 §6.28", "1516.1-2010 §6.29", "1516.1-2010 §6.30"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_object_ownership_extended.py::test_transportation_type_services_emit_confirm_and_report_callbacks",
                "tests/backends/test_python_backend_object_ownership_extended.py::test_request_attribute_transportation_type_change_rejects_not_connected_not_joined_and_unknown_object",
                "tests/backends/test_python_backend_object_ownership_extended.py::test_request_interaction_transportation_type_change_rejects_not_connected_not_joined_and_save_restore",
                "tests/backends/test_python_backend_object_ownership_extended.py::test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore",
                "tests/backends/test_python_backend_object_ownership_extended.py::test_query_interaction_transportation_type_rejects_not_connected_not_joined_invalid_handle_and_save_restore",
            ),
            gaps=("This asset proves the implemented reliable plus best-effort service-argument subset. The broader standards rows remain partial because FDD-driven and wider transport semantic space behavior is still narrower than the full specification.",),
        ),
        VerificationAsset(
            "REQ-OM-TRANSPORT-BEST-EFFORT-001",
            "requirement",
            "Best-effort transportation semantics, including FOM-defined defaults and explicit overrides, are implemented distinctly from reliable transport and persist across restore",
            ("1516.1-2010 §6.1.10", "1516.1-2010 §6.23", "1516.1-2010 §6.27", "1516-2010 §12.2"),
            "implemented-slice",
            (
                "tests/backends/test_python_backend_object_ownership_extended.py::test_best_effort_transport_changes_callback_transport_and_splits_mixed_attribute_updates",
                "tests/backends/test_python_backend_support_services.py::test_fom_declared_transport_defaults_apply_to_attributes_and_interactions",
                "tests/verification/test_compliance_slice_v011.py::test_restore_reinstates_saved_attribute_and_interaction_transportation_overrides",
            ),
            gaps=("This asset proves distinct callback transport semantics for both FOM-defined defaults and explicit service-selected overrides, plus restore persistence for the implemented best-effort subset. Custom transport names or wider non-standard transport semantics remain outside the supported model.",),
            notes="The backend now executes distinct best-effort versus reliable callback transport behavior for both FOM-defined defaults and explicit service-selected overrides, and persists that non-reliable transport state across restore.",
        ),
        VerificationAsset(
            "SCENARIO-TARGET-RADAR-001",
            "scenario",
            "Two-federate Target/Radar simulation runs over Python RTI and Java shim profiles",
            ("1516.1-2010 §4", "1516.1-2010 §5", "1516.1-2010 §6", "1516.1-2010 §8"),
            "implemented-smoke",
            ("examples/target_radar_simulation.py", "tests/scenarios/test_target_radar_scenario.py", "test_run_summary.txt"),
            gaps=("Scenario is a smoke demonstration, not a conformance test.",),
        ),
        VerificationAsset(
            "ASSET-CONFORMANCE-MATRIX-001",
            "verification-artifact",
            "Service-by-service conformance matrix covering RTIambassador services and MOM receive interactions",
            ("1516.1-2010 §4-§11", "1516.1-2010 Annex G"),
            "implemented-slice",
            (
                "hla2010/conformance.py::build_service_conformance_matrix",
                "analysis/service_conformance_matrix_v0_13.json",
                "analysis/service_conformance_matrix_v0_13.csv",
                "tests/verification/test_service_conformance_matrix_v013.py",
            ),
            gaps=("Rows identify handlers and current evidence; several handler-only rows still need service-specific behavior/exception tests.",),
        ),
        VerificationAsset(
            "ASSET-REQUIREMENTS-LEDGER-001",
            "verification-artifact",
            "Strict requirements ledger classifying each mapped service row as pass, partial, fail, or not-evidenced",
            ("1516.1-2010 §4-§11", "1516.1-2010 Annex G"),
            "implemented-slice",
            (
                "hla2010/conformance.py::build_requirements_ledger",
                "analysis/requirements_ledger_v0_13.json",
                "analysis/requirements_ledger_v0_13.csv",
                "tests/verification/test_requirements_ledger_v013.py",
            ),
            gaps=("The ledger is only as strong as the linked executable evidence; rows marked partial and not-evidenced remain open engineering work.",),
        ),
        VerificationAsset(
            "ASSET-VERIFICATION-TRACEABILITY-001",
            "verification-artifact",
            "Verification-plan asset packet and flat section-to-asset traceability export",
            ("1516.1-2010 §4-§11", "1516.1-2010 Annex G"),
            "implemented-slice",
            (
                "hla2010/verification.py::write_verification_assets",
                "hla2010/verification.py::write_traceability_csv",
                "analysis/compliance/verification_assets.json",
                "analysis/compliance/verification_traceability.csv",
            ),
            gaps=("This packet traces verification assets and requirement slices, but it does not replace the service-level conformance ledger.",),
        ),
        VerificationAsset(
            "ASSET-VENDOR-PARITY-PACKET-001",
            "verification-artifact",
            "Harmonized vendor parity packet indexing runtime smoke commands, vendor matrix tests, findings notes, and optional preflight snapshots",
            ("1516.1-2010 §4-§10", "operational vendor parity"),
            "implemented-slice",
            (
                "hla2010/testing/vendor_parity_artifacts.py::write_vendor_parity_artifacts",
                "scripts/run_vendor_parity_artifacts.py",
                "docs/vendor_parity_artifacts.md",
                "tests/scenarios/test_vendor_parity_artifacts.py",
            ),
            gaps=("This packet harmonizes the current artifact surface, but it does not itself execute real vendor smoke or certify vendor behavior.",),
            notes="Use this asset to normalize CERTI and Pitch parity evidence around a stable manifest before attaching session-specific preflight or runtime outputs.",
        ),
        VerificationAsset(
            "ASSET-MOM-SERVICE-SEMANTIC-NEG-001",
            "planned-artifact",
            "Bespoke semantic negative-path harnesses for every MOM HLAservice action",
            ("1516.1-2010 §11.4.1", "1516.1-2010 Annex G"),
            "planned",
            ("analysis/service_conformance_matrix_v0_13.json", "verification/mom_negative_matrix_v0_13.json"),
            gaps=(
                "The generated parameter-validation rows are executable; service-action rows still "
                "need per-service precondition setup so success paths are not misreported as "
                "negative evidence.",
            ),
        ),
        VerificationAsset(
            "ASSET-CROSS-RTI-BRIDGE-001",
            "planned-artifact",
            "Cross-run verification against at least one real Java RTI via JPype and Py4J",
            ("1516.1-2010 Java binding", "1516.1-2010 §4-§10"),
            "gap",
            ("tests/runtime/test_optional_real_java_bridges.py",),
            gaps=("No vendor RTI, jpype1, or py4j package is available in this sandbox.",),
        ),
        VerificationAsset(
            "ASSET-NEGATIVE-MOM-MATRIX-001",
            "verification-artifact",
            "Generated MOM negative-path matrix with executable parameter-validation rows",
            ("1516.1-2010 §11.4.1", "1516.1-2010 Annex G"),
            "implemented-slice",
            (
                "verification/mom_negative_matrix_v0_13.json",
                "analysis/mom_negative_matrix_v0_13.json",
                "hla2010/mom_negative_testing.py::mom_negative_case_report",
                "tests/verification/test_mom_negative_matrix_executable_v013.py",
            ),
            gaps=("Service-action semantic negative cases remain visible as planned rows until each has a bespoke precondition harness.",),
        ),
    )
    return VerificationPlan(version=version, scope="Pure Python RTI plus Java adapter/shim compatibility layer", assets=assets)


def write_verification_assets(path: str | Path, *, version: str = "0.13.0") -> Path:
    """Write the current plan as JSON and return the output path."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_verification_plan(version).to_json(indent=2) + "\n", encoding="utf-8")
    return target


def write_traceability_csv(path: str | Path, *, version: str = "0.13.0") -> Path:
    """Write a flat section-to-asset traceability CSV."""

    plan = build_verification_plan(version)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["asset_id", "asset_type", "title", "section_ref", "status", "evidence", "gaps"])
        for asset in plan.assets:
            for section in asset.section_refs:
                writer.writerow(
                    [
                        asset.asset_id,
                        asset.asset_type,
                        asset.title,
                        section,
                        asset.status,
                        "; ".join(asset.evidence),
                        "; ".join(asset.gaps),
                    ]
                )
    return target


_EXTRACTED_REQUIREMENTS_1516_1_CLAUSES_5_6: tuple[dict[str, Any], ...] = (
    {"requirement_id": "HLA1516.1-DM-5.1-001", "section_ref": "IEEE 1516.1-2010 §5.1", "title": "Joined federates shall use DM services to declare intent to generate information.", "service_group": "Declaration management", "linked_methods": ("publishObjectClassAttributes", "publishInteractionClass"), "linked_assets": ("REQ-DM-DECLARATION-STATE-001",)},
    {"requirement_id": "HLA1516.1-DM-5.1-002", "section_ref": "IEEE 1516.1-2010 §5.1", "title": "A joined federate shall invoke appropriate DM services before registering objects, updating attributes, or sending interactions.", "service_group": "Declaration management", "linked_methods": ("publishObjectClassAttributes", "publishInteractionClass", "registerObjectInstance", "updateAttributeValues", "sendInteraction"), "linked_assets": ("REQ-DM-DECLARATION-STATE-001",)},
    {"requirement_id": "HLA1516.1-DM-5.1-003", "section_ref": "IEEE 1516.1-2010 §5.1", "title": "Joined federates shall use DM or DDM services before discovering objects, reflecting attributes, or receiving interactions.", "service_group": "Declaration management", "linked_methods": ("subscribeObjectClassAttributes", "subscribeInteractionClass", "discoverObjectInstance", "reflectAttributeValues", "receiveInteraction", "subscribeObjectClassAttributesWithRegions", "subscribeInteractionClassWithRegions"), "linked_assets": ("REQ-DM-SUBSCRIPTION-DELIVERY-001", "REQ-DM-DDM-INTERPLAY-001", "REQ-DM-DDM-GATING-001")},
    {"requirement_id": "HLA1516.1-DM-5.1-004", "section_ref": "IEEE 1516.1-2010 §5.1", "title": "DM effects shall be independent of federate logical time.", "service_group": "Declaration management", "linked_methods": ("publishObjectClassAttributes", "subscribeObjectClassAttributes", "publishInteractionClass", "subscribeInteractionClass"), "linked_assets": ("REQ-TIME-ORDER-001", "REQ-DM-DECLARATION-STATE-001", "REQ-DM-TIME-INDEPENDENCE-001")},
    {"requirement_id": "HLA1516.1-DM-5.1.1-001", "section_ref": "IEEE 1516.1-2010 §5.1.1", "title": "Each FDD class shall have at most one immediate superclass.", "service_group": "Declaration management", "linked_methods": (), "linked_assets": ("REQ-OMT-PARSE-001", "REQ-OMT-MERGE-001")},
    {"requirement_id": "HLA1516.1-DM-5.1.1-002", "section_ref": "IEEE 1516.1-2010 §5.1.1", "title": "Object classes shall expose declared and inherited available attributes.", "service_group": "Declaration management", "linked_methods": ("publishObjectClassAttributes", "subscribeObjectClassAttributes"), "linked_assets": ("REQ-OMT-PARSE-001",)},
    {"requirement_id": "HLA1516.1-DM-5.1.1-003", "section_ref": "IEEE 1516.1-2010 §5.1.1", "title": "Interaction classes shall expose declared and inherited available parameters.", "service_group": "Declaration management", "linked_methods": ("publishInteractionClass", "subscribeInteractionClass"), "linked_assets": ("REQ-OMT-PARSE-001",)},
    {"requirement_id": "HLA1516.1-DM-5.1.2-001", "section_ref": "IEEE 1516.1-2010 §5.1.2", "title": "RTI shall track published object-class attributes per joined federate.", "service_group": "Declaration management", "linked_methods": ("publishObjectClassAttributes", "unpublishObjectClassAttributes", "unpublishObjectClass"), "linked_assets": ("REQ-DM-DECLARATION-STATE-001",)},
    {"requirement_id": "HLA1516.1-DM-5.1.2-002", "section_ref": "IEEE 1516.1-2010 §5.1.2", "title": "RTI shall track subscribed object-class attributes per joined federate.", "service_group": "Declaration management", "linked_methods": ("subscribeObjectClassAttributes", "subscribeObjectClassAttributesPassively", "unsubscribeObjectClassAttributes", "unsubscribeObjectClass"), "linked_assets": ("REQ-DM-SUBSCRIPTION-DELIVERY-001",)},
    {"requirement_id": "HLA1516.1-DM-5.1.3-001", "section_ref": "IEEE 1516.1-2010 §5.1.3", "title": "RTI shall track published interaction classes per joined federate.", "service_group": "Declaration management", "linked_methods": ("publishInteractionClass", "unpublishInteractionClass"), "linked_assets": ("REQ-DM-DECLARATION-STATE-001",)},
    {"requirement_id": "HLA1516.1-DM-5.1.3-002", "section_ref": "IEEE 1516.1-2010 §5.1.3", "title": "RTI shall track subscribed interaction classes per joined federate.", "service_group": "Declaration management", "linked_methods": ("subscribeInteractionClass", "subscribeInteractionClassPassively", "unsubscribeInteractionClass"), "linked_assets": ("REQ-DM-SUBSCRIPTION-DELIVERY-001",)},
    {"requirement_id": "HLA1516.1-DM-5.1.5-001", "section_ref": "IEEE 1516.1-2010 §5.1.5", "title": "RTI shall support interaction between DM subscriptions and DDM subscriptions.", "service_group": "Declaration management", "linked_methods": ("subscribeObjectClassAttributes", "subscribeObjectClassAttributesWithRegions", "subscribeInteractionClass", "subscribeInteractionClassWithRegions"), "linked_assets": ("REQ-DM-DDM-INTERPLAY-001", "REQ-DM-DDM-OBJECT-SCOPE-001")},
    {"requirement_id": "HLA1516.1-DM-5.1.6-001", "section_ref": "IEEE 1516.1-2010 §5.1.6", "title": "RTI shall support subscribing with update rate reduction where applicable.", "service_group": "Declaration management", "linked_methods": ("subscribeObjectClassAttributes", "subscribeObjectClassAttributesPassively", "subscribeObjectClassAttributesWithRegions", "subscribeObjectClassAttributesPassivelyWithRegions"), "linked_assets": ("REQ-OM-UPDATE-RATE-001",), "claim_scope": "broad-spec", "policy_basis": "logical-time-update-rate-only", "status_override": "partial", "notes": "The backend now proves explicit and FOM-declared update-rate defaults across direct, inherited, and regioned subscriptions, plus receive-order non-suppression when no logical-time basis exists. Broader vendor-style update-rate policies remain outside the current model."},
    {"requirement_id": "HLA1516.1-DM-5.2-001", "section_ref": "IEEE 1516.1-2010 §5.2", "title": "RTI shall provide Publish Object Class Attributes.", "service_group": "Declaration management", "linked_methods": ("publishObjectClassAttributes",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-DM-5.2-002", "section_ref": "IEEE 1516.1-2010 §5.2", "title": "Publish Object Class Attributes shall declare attributes a federate may update for instances of an object class.", "service_group": "Declaration management", "linked_methods": ("publishObjectClassAttributes", "updateAttributeValues"), "linked_assets": ("REQ-DM-DECLARATION-STATE-001",)},
    {"requirement_id": "HLA1516.1-DM-5.2-003", "section_ref": "IEEE 1516.1-2010 §5.2", "title": "RTI shall reject publication requests for unavailable attributes.", "service_group": "Declaration management", "linked_methods": ("publishObjectClassAttributes",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-DM-5.3-001", "section_ref": "IEEE 1516.1-2010 §5.3", "title": "RTI shall provide Unpublish Object Class Attributes.", "service_group": "Declaration management", "linked_methods": ("unpublishObjectClassAttributes", "unpublishObjectClass"), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-DM-5.3-002", "section_ref": "IEEE 1516.1-2010 §5.3", "title": "Unpublishing shall remove the federate’s ability to update the specified attributes.", "service_group": "Declaration management", "linked_methods": ("unpublishObjectClassAttributes", "unpublishObjectClass", "updateAttributeValues"), "linked_assets": ("REQ-DM-UNPUBLISH-OBJECT-001",)},
    {"requirement_id": "HLA1516.1-DM-5.4-001", "section_ref": "IEEE 1516.1-2010 §5.4", "title": "RTI shall provide Publish Interaction Class.", "service_group": "Declaration management", "linked_methods": ("publishInteractionClass",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-DM-5.4-002", "section_ref": "IEEE 1516.1-2010 §5.4", "title": "Publication of an interaction class shall permit the federate to send interactions of that class.", "service_group": "Declaration management", "linked_methods": ("publishInteractionClass", "sendInteraction"), "linked_assets": ("REQ-DM-DECLARATION-STATE-001",)},
    {"requirement_id": "HLA1516.1-DM-5.5-001", "section_ref": "IEEE 1516.1-2010 §5.5", "title": "RTI shall provide Unpublish Interaction Class.", "service_group": "Declaration management", "linked_methods": ("unpublishInteractionClass",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-DM-5.5-002", "section_ref": "IEEE 1516.1-2010 §5.5", "title": "Unpublishing an interaction class shall remove the federate’s ability to send interactions of that class.", "service_group": "Declaration management", "linked_methods": ("unpublishInteractionClass", "sendInteraction"), "linked_assets": ("REQ-DM-UNPUBLISH-INTERACTION-001",)},
    {"requirement_id": "HLA1516.1-DM-5.6-001", "section_ref": "IEEE 1516.1-2010 §5.6", "title": "RTI shall provide Subscribe Object Class Attributes.", "service_group": "Declaration management", "linked_methods": ("subscribeObjectClassAttributes", "subscribeObjectClassAttributesPassively"), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-DM-5.6-002", "section_ref": "IEEE 1516.1-2010 §5.6", "title": "Subscribing to object-class attributes shall make matching object instances discoverable when discovery conditions are met.", "service_group": "Declaration management", "linked_methods": ("subscribeObjectClassAttributes", "discoverObjectInstance"), "linked_assets": ("REQ-DM-SUBSCRIPTION-DELIVERY-001", "REQ-OM-DISCOVERY-LIFECYCLE-001")},
    {"requirement_id": "HLA1516.1-DM-5.6-003", "section_ref": "IEEE 1516.1-2010 §5.6", "title": "Subscribing to object-class attributes shall make matching in-scope attribute updates reflectable.", "service_group": "Declaration management", "linked_methods": ("subscribeObjectClassAttributes", "reflectAttributeValues", "attributesInScope"), "linked_assets": ("REQ-DM-SUBSCRIPTION-DELIVERY-001", "REQ-DM-DDM-INTERPLAY-001")},
    {"requirement_id": "HLA1516.1-DM-5.7-001", "section_ref": "IEEE 1516.1-2010 §5.7", "title": "RTI shall provide Unsubscribe Object Class Attributes.", "service_group": "Declaration management", "linked_methods": ("unsubscribeObjectClassAttributes", "unsubscribeObjectClass"), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-DM-5.7-002", "section_ref": "IEEE 1516.1-2010 §5.7", "title": "Unsubscribing shall remove the federate’s interest in the specified object-class attributes.", "service_group": "Declaration management", "linked_methods": ("unsubscribeObjectClassAttributes", "unsubscribeObjectClass", "attributesOutOfScope"), "linked_assets": ("REQ-DM-UNSUBSCRIBE-OBJECT-001",)},
    {"requirement_id": "HLA1516.1-DM-5.8-001", "section_ref": "IEEE 1516.1-2010 §5.8", "title": "RTI shall provide Subscribe Interaction Class.", "service_group": "Declaration management", "linked_methods": ("subscribeInteractionClass", "subscribeInteractionClassPassively"), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-DM-5.8-002", "section_ref": "IEEE 1516.1-2010 §5.8", "title": "Subscribing to an interaction class shall make matching interactions receivable.", "service_group": "Declaration management", "linked_methods": ("subscribeInteractionClass", "receiveInteraction"), "linked_assets": ("REQ-DM-SUBSCRIPTION-DELIVERY-001",)},
    {"requirement_id": "HLA1516.1-DM-5.9-001", "section_ref": "IEEE 1516.1-2010 §5.9", "title": "RTI shall provide Unsubscribe Interaction Class.", "service_group": "Declaration management", "linked_methods": ("unsubscribeInteractionClass",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-DM-5.10-001", "section_ref": "IEEE 1516.1-2010 §5.10", "title": "RTI shall invoke Start Registration For Object Class when registration becomes useful for subscribed federates.", "service_group": "Declaration management", "linked_methods": ("startRegistrationForObjectClass",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-DM-5.11-001", "section_ref": "IEEE 1516.1-2010 §5.11", "title": "RTI shall invoke Stop Registration For Object Class when registration is no longer useful for subscribed federates.", "service_group": "Declaration management", "linked_methods": ("stopRegistrationForObjectClass",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-DM-5.12-001", "section_ref": "IEEE 1516.1-2010 §5.12", "title": "RTI shall invoke Turn Interactions On when a published interaction class has matching subscribers.", "service_group": "Declaration management", "linked_methods": ("turnInteractionsOn",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-DM-5.13-001", "section_ref": "IEEE 1516.1-2010 §5.13", "title": "RTI shall invoke Turn Interactions Off when a published interaction class no longer has matching subscribers.", "service_group": "Declaration management", "linked_methods": ("turnInteractionsOff",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.1-001", "section_ref": "IEEE 1516.1-2010 §6.1", "title": "RTI shall support registration, modification, and deletion of object instances.", "service_group": "Object management", "linked_methods": ("registerObjectInstance", "updateAttributeValues", "deleteObjectInstance", "localDeleteObjectInstance"), "linked_assets": ("REQ-OM-DISCOVERY-LIFECYCLE-001", "REQ-OM-TRANSPORT-SCOPE-001")},
    {"requirement_id": "HLA1516.1-OM-6.1-002", "section_ref": "IEEE 1516.1-2010 §6.1", "title": "RTI shall support sending and receiving interactions.", "service_group": "Object management", "linked_methods": ("sendInteraction", "receiveInteraction"), "linked_assets": ("REQ-DM-SUBSCRIPTION-DELIVERY-001",)},
    {"requirement_id": "HLA1516.1-OM-6.1.1-001", "section_ref": "IEEE 1516.1-2010 §6.1.1", "title": "RTI shall discover object instances at subscribed federates when discovery conditions are satisfied.", "service_group": "Object management", "linked_methods": ("registerObjectInstance", "discoverObjectInstance", "subscribeObjectClassAttributes"), "linked_assets": ("REQ-OM-DISCOVERY-LIFECYCLE-001",)},
    {"requirement_id": "HLA1516.1-OM-6.1.1-002", "section_ref": "IEEE 1516.1-2010 §6.1.1", "title": "RTI shall determine a candidate discovery class from the registered class or closest subscribed superclass.", "service_group": "Object management", "linked_methods": ("registerObjectInstance", "discoverObjectInstance"), "linked_assets": ("REQ-OM-DISCOVERY-LIFECYCLE-001", "REQ-OM-DISCOVERY-CLASS-001")},
    {"requirement_id": "HLA1516.1-OM-6.1.1-003", "section_ref": "IEEE 1516.1-2010 §6.1.1", "title": "Once discovered, an object instance’s discovered class shall not change.", "service_group": "Object management", "linked_methods": ("discoverObjectInstance",), "linked_assets": ("REQ-OM-DISCOVERY-LIFECYCLE-001", "REQ-OM-DISCOVERY-CLASS-001")},
    {"requirement_id": "HLA1516.1-OM-6.1.1-004", "section_ref": "IEEE 1516.1-2010 §6.1.1", "title": "A registered or discovered object instance shall become known to the joined federate.", "service_group": "Object management", "linked_methods": ("registerObjectInstance", "discoverObjectInstance"), "linked_assets": ("REQ-OM-DISCOVERY-LIFECYCLE-001",)},
    {"requirement_id": "HLA1516.1-OM-6.1.2-001", "section_ref": "IEEE 1516.1-2010 §6.1.2", "title": "RTI shall determine whether an instance attribute is in scope for each joined federate.", "service_group": "Object management", "linked_methods": ("attributesInScope", "attributesOutOfScope", "subscribeObjectClassAttributesWithRegions"), "linked_assets": ("REQ-DM-DDM-INTERPLAY-001", "REQ-DM-DDM-OBJECT-SCOPE-001")},
    {"requirement_id": "HLA1516.1-OM-6.1.3-001", "section_ref": "IEEE 1516.1-2010 §6.1.3", "title": "RTI shall reflect attribute updates only when attributes are in scope and subscribed.", "service_group": "Object management", "linked_methods": ("updateAttributeValues", "reflectAttributeValues", "attributesInScope", "subscribeObjectClassAttributes"), "linked_assets": ("REQ-DM-DDM-INTERPLAY-001", "REQ-DM-SUBSCRIPTION-DELIVERY-001")},
    {"requirement_id": "HLA1516.1-OM-6.1.4-001", "section_ref": "IEEE 1516.1-2010 §6.1.4", "title": "RTI shall not reflect out-of-scope attribute updates except where required by service semantics.", "service_group": "Object management", "linked_methods": ("reflectAttributeValues", "attributesOutOfScope"), "linked_assets": ("REQ-DM-DDM-INTERPLAY-001", "REQ-DM-DDM-OBJECT-SCOPE-001")},
    {"requirement_id": "HLA1516.1-OM-6.1.5-001", "section_ref": "IEEE 1516.1-2010 §6.1.5", "title": "RTI shall determine attribute relevance from publication, subscription, ownership, and scope.", "service_group": "Object management", "linked_methods": ("publishObjectClassAttributes", "subscribeObjectClassAttributes", "attributeOwnershipAcquisition", "attributeOwnershipAcquisitionIfAvailable", "attributesInScope", "attributesOutOfScope"), "linked_assets": ("REQ-OM-ATTRIBUTE-RELEVANCE-001",)},
    {"requirement_id": "HLA1516.1-OM-6.1.6-001", "section_ref": "IEEE 1516.1-2010 §6.1.6", "title": "RTI shall handle orphan object instances according to ownership and discovery rules.", "service_group": "Object management", "linked_methods": ("deleteObjectInstance", "localDeleteObjectInstance", "removeObjectInstance"), "linked_assets": ("REQ-OM-LOCAL-KNOWLEDGE-001", "REQ-OM-ORPHAN-KNOWLEDGE-001", "REQ-OM-ORPHAN-LIFECYCLE-001")},
    {"requirement_id": "HLA1516.1-OM-6.1.7-001", "section_ref": "IEEE 1516.1-2010 §6.1.7", "title": "RTI shall deliver interactions to joined federates subscribed to the relevant interaction class.", "service_group": "Object management", "linked_methods": ("sendInteraction", "receiveInteraction", "subscribeInteractionClass"), "linked_assets": ("REQ-DM-SUBSCRIPTION-DELIVERY-001",)},
    {"requirement_id": "HLA1516.1-OM-6.1.10-001", "section_ref": "IEEE 1516.1-2010 §6.1.10", "title": "RTI shall use transportation types for object updates and interactions as defined by the FDD and service arguments.", "service_group": "Object management", "linked_methods": ("updateAttributeValues", "sendInteraction", "requestAttributeTransportationTypeChange", "queryAttributeTransportationType", "requestInteractionTransportationTypeChange", "queryInteractionTransportationType"), "linked_assets": ("REQ-OM-TRANSPORT-SCOPE-001", "REQ-OM-TRANSPORT-REPORT-001", "REQ-OM-TRANSPORT-BEST-EFFORT-001"), "claim_scope": "broad-spec", "policy_basis": "reliable-best-effort-transport-only", "status_override": "partial", "notes": "This broad standards row remains partial. The backend now proves distinct reliable versus best-effort callback transport behavior for both FOM-defined defaults and explicit service-selected overrides, plus restore persistence for the supported subset, but it still does not model the full custom transportation semantic space described by the standard."},
    {"requirement_id": "HLA1516.1-OM-6.1.10-002", "section_ref": "IEEE 1516.1-2010 §6.1.10", "title": "RTI shall support explicit reliable transportation type selection, query reporting, and restore persistence for object updates and interactions in the currently supported transport subset.", "service_group": "Object management", "linked_methods": ("requestAttributeTransportationTypeChange", "queryAttributeTransportationType", "requestInteractionTransportationTypeChange", "queryInteractionTransportationType"), "linked_assets": ("REQ-OM-TRANSPORT-REPORT-001", "REQ-SAVE-RESTORE-FEDERATE-LOCAL-STATE-001"), "claim_scope": "supported-subset", "supported_subset_for": "HLA1516.1-OM-6.1.10-001", "policy_basis": "reliable-best-effort-transport-only", "status_override": "pass", "notes": "This narrow supported-subset row covers explicit reliable transport selection, report/query callbacks, and restore persistence for object and interaction transport state."},
    {"requirement_id": "HLA1516.1-OM-6.1.10-003", "section_ref": "IEEE 1516.1-2010 §6.1.10", "title": "RTI shall support distinct best-effort versus reliable delivery semantics for object updates and interactions when explicit transportation selections differ.", "service_group": "Object management", "linked_methods": ("updateAttributeValues", "sendInteraction", "requestAttributeTransportationTypeChange", "queryAttributeTransportationType", "requestInteractionTransportationTypeChange", "queryInteractionTransportationType"), "linked_assets": ("REQ-OM-TRANSPORT-BEST-EFFORT-001", "REQ-SAVE-RESTORE-FEDERATE-LOCAL-STATE-001"), "claim_scope": "supported-subset", "supported_subset_for": "HLA1516.1-OM-6.1.10-001", "policy_basis": "reliable-best-effort-transport-only", "status_override": "pass", "positive_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_best_effort_transport_changes_callback_transport_and_splits_mixed_attribute_updates", "tests/verification/test_compliance_slice_v011.py::test_restore_reinstates_saved_attribute_and_interaction_transportation_overrides"), "implementation_refs": ("hla2010/backends/python/object_delivery.py", "hla2010/backends/python/ddm.py", "hla2010/backends/python/save_restore.py", "hla2010/backends/python/state.py"), "notes": "This supported-subset row is now implemented: explicit reliable versus best-effort transport overrides produce distinct callback transport handles for object updates and interactions, and that non-reliable override state survives restore."},
    {"requirement_id": "HLA1516.1-OM-6.1.11-001", "section_ref": "IEEE 1516.1-2010 §6.1.11", "title": "RTI may combine, package, or passelize messages without changing externally visible semantics.", "service_group": "Object management", "linked_methods": ("reflectAttributeValues", "receiveInteraction"), "linked_assets": ("REQ-DM-SUBSCRIPTION-DELIVERY-001",), "claim_scope": "broad-spec", "policy_basis": "unbatched-callback-delivery-only", "status_override": "partial", "notes": "This backend proves externally visible delivery semantics for unbatched callbacks. It does not explicitly model message combination, packaging, or passelization, so this row remains partial by policy until those semantics are modeled or separately justified."},
    {"requirement_id": "HLA1516.1-OM-6.1.12-001", "section_ref": "IEEE 1516.1-2010 §6.1.12", "title": "RTI shall honor update-rate reduction when reflecting attribute updates.", "service_group": "Object management", "linked_methods": ("reflectAttributeValues", "subscribeObjectClassAttributes", "subscribeObjectClassAttributesWithRegions"), "linked_assets": ("REQ-OM-UPDATE-RATE-001",), "claim_scope": "broad-spec", "policy_basis": "logical-time-update-rate-only", "status_override": "partial", "notes": "The backend proves explicit and FOM-declared update-rate throttling for direct, inherited, and regioned subscriptions, plus receive-order non-suppression when no logical-time basis exists. Broader vendor-style update-rate policies remain outside the current model, so this row remains partial."},
    {"requirement_id": "HLA1516.1-OM-6.2-001", "section_ref": "IEEE 1516.1-2010 §6.2", "title": "RTI shall provide Reserve Object Instance Name.", "service_group": "Object management", "linked_methods": ("reserveObjectInstanceName",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.3-001", "section_ref": "IEEE 1516.1-2010 §6.3", "title": "RTI shall invoke Object Instance Name Reserved when a reservation succeeds.", "service_group": "Object management", "linked_methods": ("objectInstanceNameReservationSucceeded",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.4-001", "section_ref": "IEEE 1516.1-2010 §6.4", "title": "RTI shall provide Release Object Instance Name.", "service_group": "Object management", "linked_methods": ("releaseObjectInstanceName",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.5-001", "section_ref": "IEEE 1516.1-2010 §6.5", "title": "RTI shall provide Reserve Multiple Object Instance Names.", "service_group": "Object management", "linked_methods": ("reserveMultipleObjectInstanceName",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.6-001", "section_ref": "IEEE 1516.1-2010 §6.6", "title": "RTI shall invoke Multiple Object Instance Names Reserved when multiple-name reservation succeeds.", "service_group": "Object management", "linked_methods": ("multipleObjectInstanceNameReservationSucceeded",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.7-001", "section_ref": "IEEE 1516.1-2010 §6.7", "title": "RTI shall provide Release Multiple Object Instance Names.", "service_group": "Object management", "linked_methods": ("releaseMultipleObjectInstanceName",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.8-001", "section_ref": "IEEE 1516.1-2010 §6.8", "title": "RTI shall provide Register Object Instance.", "service_group": "Object management", "linked_methods": ("registerObjectInstance",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.8-002", "section_ref": "IEEE 1516.1-2010 §6.8", "title": "Register Object Instance shall create an object instance of a published object class.", "service_group": "Object management", "linked_methods": ("registerObjectInstance", "publishObjectClassAttributes"), "linked_assets": ("REQ-DM-DECLARATION-STATE-001", "REQ-OM-DISCOVERY-LIFECYCLE-001")},
    {"requirement_id": "HLA1516.1-OM-6.8-003", "section_ref": "IEEE 1516.1-2010 §6.8", "title": "RTI shall assign a unique object instance handle to each registered object instance.", "service_group": "Object management", "linked_methods": ("registerObjectInstance",), "linked_assets": ("REQ-OM-DISCOVERY-LIFECYCLE-001",)},
    {"requirement_id": "HLA1516.1-OM-6.8-004", "section_ref": "IEEE 1516.1-2010 §6.8", "title": "RTI shall support registration with RTI-assigned or federate-supplied object instance names.", "service_group": "Object management", "linked_methods": ("registerObjectInstance", "reserveObjectInstanceName"), "linked_assets": ("REQ-OM-DISCOVERY-LIFECYCLE-001",)},
    {"requirement_id": "HLA1516.1-OM-6.9-001", "section_ref": "IEEE 1516.1-2010 §6.9", "title": "RTI shall invoke Discover Object Instance at federates satisfying discovery conditions.", "service_group": "Object management", "linked_methods": ("discoverObjectInstance",), "linked_assets": ("REQ-OM-DISCOVERY-LIFECYCLE-001",)},
    {"requirement_id": "HLA1516.1-OM-6.10-001", "section_ref": "IEEE 1516.1-2010 §6.10", "title": "RTI shall provide Update Attribute Values.", "service_group": "Object management", "linked_methods": ("updateAttributeValues",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.10-002", "section_ref": "IEEE 1516.1-2010 §6.10", "title": "A federate shall update only attributes it owns and is permitted to publish.", "service_group": "Object management", "linked_methods": ("updateAttributeValues", "publishObjectClassAttributes"), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.10-003", "section_ref": "IEEE 1516.1-2010 §6.10", "title": "RTI shall route attribute updates to joined federates with relevant subscriptions and scope.", "service_group": "Object management", "linked_methods": ("updateAttributeValues", "reflectAttributeValues", "subscribeObjectClassAttributes", "attributesInScope"), "linked_assets": ("REQ-DM-DDM-INTERPLAY-001", "REQ-DM-SUBSCRIPTION-DELIVERY-001")},
    {"requirement_id": "HLA1516.1-OM-6.10-004", "section_ref": "IEEE 1516.1-2010 §6.10", "title": "RTI shall support RO and TSO attribute updates according to time-management rules.", "service_group": "Object management", "linked_methods": ("updateAttributeValues", "reflectAttributeValues"), "linked_assets": ("REQ-TIME-ORDER-001",)},
    {"requirement_id": "HLA1516.1-OM-6.10-005", "section_ref": "IEEE 1516.1-2010 §6.10", "title": "RTI shall deliver reflected attribute updates with transportation metadata that matches the currently implemented reliable and best-effort transport subset.", "service_group": "Object management", "linked_methods": ("updateAttributeValues", "reflectAttributeValues", "requestAttributeTransportationTypeChange"), "linked_assets": ("REQ-OM-TRANSPORT-BEST-EFFORT-001", "REQ-OM-TRANSPORT-REPORT-001"), "claim_scope": "supported-subset", "policy_basis": "reliable-best-effort-transport-only", "positive_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_best_effort_transport_changes_callback_transport_and_splits_mixed_attribute_updates",), "negative_test_refs": (), "implementation_refs": ("hla2010/backends/python/object_delivery.py", "hla2010/backends/python/state.py")},
    {"requirement_id": "HLA1516.1-OM-6.11-001", "section_ref": "IEEE 1516.1-2010 §6.11", "title": "RTI shall invoke Reflect Attribute Values to deliver attribute updates.", "service_group": "Object management", "linked_methods": ("reflectAttributeValues",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.11-002", "section_ref": "IEEE 1516.1-2010 §6.11", "title": "Reflected attributes shall correspond to attributes available at the object instance’s known class.", "service_group": "Object management", "linked_methods": ("reflectAttributeValues", "discoverObjectInstance"), "linked_assets": ("REQ-OMT-PARSE-001", "REQ-OM-REFLECT-KNOWN-CLASS-001")},
    {"requirement_id": "HLA1516.1-OM-6.12-001", "section_ref": "IEEE 1516.1-2010 §6.12", "title": "RTI shall provide Send Interaction.", "service_group": "Object management", "linked_methods": ("sendInteraction",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.12-002", "section_ref": "IEEE 1516.1-2010 §6.12", "title": "A federate shall send only interaction classes it has published.", "service_group": "Object management", "linked_methods": ("sendInteraction", "publishInteractionClass"), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.12-003", "section_ref": "IEEE 1516.1-2010 §6.12", "title": "Sent interaction parameters shall be available parameters of the interaction class.", "service_group": "Object management", "linked_methods": ("sendInteraction",), "linked_assets": ("REQ-OMT-PARSE-001",)},
    {"requirement_id": "HLA1516.1-OM-6.12-004", "section_ref": "IEEE 1516.1-2010 §6.12", "title": "RTI shall support RO and TSO interactions according to time-management rules.", "service_group": "Object management", "linked_methods": ("sendInteraction", "receiveInteraction"), "linked_assets": ("REQ-TIME-ORDER-001",)},
    {"requirement_id": "HLA1516.1-OM-6.12-005", "section_ref": "IEEE 1516.1-2010 §6.12", "title": "RTI shall deliver received interactions with transportation metadata that matches the currently implemented reliable and best-effort transport subset.", "service_group": "Object management", "linked_methods": ("sendInteraction", "receiveInteraction", "requestInteractionTransportationTypeChange"), "linked_assets": ("REQ-OM-TRANSPORT-BEST-EFFORT-001", "REQ-OM-TRANSPORT-REPORT-001"), "claim_scope": "supported-subset", "policy_basis": "reliable-best-effort-transport-only", "positive_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_best_effort_transport_changes_callback_transport_and_splits_mixed_attribute_updates",), "negative_test_refs": (), "implementation_refs": ("hla2010/backends/python/object_delivery.py", "hla2010/backends/python/ddm.py", "hla2010/backends/python/state.py")},
    {"requirement_id": "HLA1516.1-OM-6.13-001", "section_ref": "IEEE 1516.1-2010 §6.13", "title": "RTI shall invoke Receive Interaction for matching subscribed federates.", "service_group": "Object management", "linked_methods": ("receiveInteraction", "subscribeInteractionClass"), "linked_assets": ("REQ-DM-SUBSCRIPTION-DELIVERY-001",)},
    {"requirement_id": "HLA1516.1-OM-6.14-001", "section_ref": "IEEE 1516.1-2010 §6.14", "title": "RTI shall provide Delete Object Instance.", "service_group": "Object management", "linked_methods": ("deleteObjectInstance",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.14-002", "section_ref": "IEEE 1516.1-2010 §6.14", "title": "Delete Object Instance shall remove an object instance from the federation execution according to ownership and time rules.", "service_group": "Object management", "linked_methods": ("deleteObjectInstance", "removeObjectInstance"), "linked_assets": ("REQ-TIME-ORDER-001", "REQ-OM-TIMED-DELETE-REMOVE-001")},
    {"requirement_id": "HLA1516.1-OM-6.15-001", "section_ref": "IEEE 1516.1-2010 §6.15", "title": "RTI shall invoke Remove Object Instance at federates that know the deleted object instance.", "service_group": "Object management", "linked_methods": ("removeObjectInstance",), "linked_assets": ("REQ-OM-DISCOVERY-LIFECYCLE-001",)},
    {"requirement_id": "HLA1516.1-OM-6.16-001", "section_ref": "IEEE 1516.1-2010 §6.16", "title": "RTI shall provide Local Delete Object Instance.", "service_group": "Object management", "linked_methods": ("localDeleteObjectInstance",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.16-002", "section_ref": "IEEE 1516.1-2010 §6.16", "title": "Local Delete Object Instance shall remove knowledge of the object instance only at the invoking federate.", "service_group": "Object management", "linked_methods": ("localDeleteObjectInstance",), "linked_assets": ("REQ-OM-LOCAL-KNOWLEDGE-001",)},
    {"requirement_id": "HLA1516.1-OM-6.17-001", "section_ref": "IEEE 1516.1-2010 §6.17", "title": "RTI shall invoke Attributes In Scope when subscribed attributes become in scope.", "service_group": "Object management", "linked_methods": ("attributesInScope",), "linked_assets": ("REQ-OM-SCOPE-CALLBACKS-001",)},
    {"requirement_id": "HLA1516.1-OM-6.18-001", "section_ref": "IEEE 1516.1-2010 §6.18", "title": "RTI shall invoke Attributes Out Of Scope when subscribed attributes go out of scope.", "service_group": "Object management", "linked_methods": ("attributesOutOfScope",), "linked_assets": ("REQ-OM-SCOPE-CALLBACKS-001",)},
    {"requirement_id": "HLA1516.1-OM-6.19-001", "section_ref": "IEEE 1516.1-2010 §6.19", "title": "RTI shall provide Request Attribute Value Update.", "service_group": "Object management", "linked_methods": ("requestAttributeValueUpdate",), "linked_assets": ()},
    {"requirement_id": "HLA1516.1-OM-6.19-002", "section_ref": "IEEE 1516.1-2010 §6.19", "title": "Request Attribute Value Update shall cause relevant owning federates to receive a request to provide current values.", "service_group": "Object management", "linked_methods": ("requestAttributeValueUpdate", "provideAttributeValueUpdate"), "linked_assets": ("REQ-OM-REQUEST-VALUE-UPDATE-001", "REQ-OM-REQUEST-VALUE-UPDATE-ROUTING-001")},
    {"requirement_id": "HLA1516.1-OM-6.23-001", "section_ref": "IEEE 1516.1-2010 §6.23", "title": "RTI shall provide Request Attribute Transportation Type Change across the full transportation semantic space defined by the standard.", "service_group": "Object management", "linked_methods": ("requestAttributeTransportationTypeChange",), "linked_assets": ("REQ-OM-TRANSPORT-SCOPE-001",), "claim_scope": "broad-spec", "policy_basis": "reliable-best-effort-transport-only", "status_override": "partial", "notes": "The backend exposes this service but the broad standards row remains partial because only the supported reliable plus best-effort subset is modeled directly."},
    {"requirement_id": "HLA1516.1-OM-6.23-002", "section_ref": "IEEE 1516.1-2010 §6.23", "title": "RTI shall support Request Attribute Transportation Type Change for the currently implemented reliable and best-effort transport subset and persist that selected attribute transport state across restore.", "service_group": "Object management", "linked_methods": ("requestAttributeTransportationTypeChange", "queryAttributeTransportationType"), "linked_assets": ("REQ-OM-TRANSPORT-REPORT-001", "REQ-OM-TRANSPORT-BEST-EFFORT-001", "REQ-SAVE-RESTORE-FEDERATE-LOCAL-STATE-001"), "claim_scope": "supported-subset", "supported_subset_for": "HLA1516.1-OM-6.23-001", "policy_basis": "reliable-best-effort-transport-only", "positive_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_transportation_type_services_emit_confirm_and_report_callbacks", "tests/backends/test_python_backend_object_ownership_extended.py::test_best_effort_transport_changes_callback_transport_and_splits_mixed_attribute_updates", "tests/verification/test_compliance_slice_v011.py::test_restore_reinstates_saved_attribute_and_interaction_transportation_overrides"), "negative_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_request_attribute_transportation_type_change_rejects_not_connected_not_joined_and_unknown_object",), "implementation_refs": ("hla2010/backends/python/object_delivery.py", "hla2010/backends/python/save_restore.py", "hla2010/backends/python/state.py")},
    {"requirement_id": "HLA1516.1-OM-6.24-001", "section_ref": "IEEE 1516.1-2010 §6.24", "title": "RTI shall invoke Confirm Attribute Transportation Type Change across the full transportation semantic space.", "service_group": "Object management", "linked_methods": ("confirmAttributeTransportationTypeChange",), "linked_assets": ("REQ-OM-TRANSPORT-SCOPE-001",), "claim_scope": "broad-spec", "policy_basis": "reliable-best-effort-transport-only", "status_override": "partial", "notes": "The backend proves confirm callbacks for the supported reliable plus best-effort subset, not the full broader transport semantic space."},
    {"requirement_id": "HLA1516.1-OM-6.24-002", "section_ref": "IEEE 1516.1-2010 §6.24", "title": "RTI shall invoke Confirm Attribute Transportation Type Change for the currently implemented reliable and best-effort transport subset.", "service_group": "Object management", "linked_methods": ("confirmAttributeTransportationTypeChange",), "linked_assets": ("REQ-OM-TRANSPORT-REPORT-001",), "claim_scope": "supported-subset", "supported_subset_for": "HLA1516.1-OM-6.24-001", "policy_basis": "reliable-best-effort-transport-only", "positive_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_transportation_type_services_emit_confirm_and_report_callbacks",), "negative_test_refs": (), "implementation_refs": ("hla2010/backends/python/object_delivery.py", "hla2010/ambassadors.py")},
    {"requirement_id": "HLA1516.1-OM-6.24-003", "section_ref": "IEEE 1516.1-2010 §6.24", "title": "RTI shall not emit Confirm Attribute Transportation Type Change when the corresponding change request is rejected for invalid state, handle, ownership, publication, or transport inputs.", "service_group": "Object management", "linked_methods": ("confirmAttributeTransportationTypeChange", "requestAttributeTransportationTypeChange"), "linked_assets": ("REQ-OM-TRANSPORT-REPORT-001",), "claim_scope": "supported-subset", "supported_subset_for": "HLA1516.1-OM-6.24-001", "policy_basis": "reliable-best-effort-transport-only", "positive_test_refs": (), "negative_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_request_attribute_transportation_type_change_rejects_not_connected_not_joined_and_unknown_object",), "implementation_refs": ("hla2010/backends/python/object_delivery.py", "hla2010/ambassadors.py")},
    {"requirement_id": "HLA1516.1-OM-6.25-001", "section_ref": "IEEE 1516.1-2010 §6.25", "title": "RTI shall provide Query Attribute Transportation Type across the full transportation semantic space defined by the standard.", "service_group": "Object management", "linked_methods": ("queryAttributeTransportationType",), "linked_assets": ("REQ-OM-TRANSPORT-SCOPE-001",), "claim_scope": "broad-spec", "policy_basis": "reliable-best-effort-transport-only", "status_override": "partial", "notes": "The backend proves query/report behavior for the supported reliable plus best-effort subset, not the full broader transport semantic space."},
    {"requirement_id": "HLA1516.1-OM-6.25-002", "section_ref": "IEEE 1516.1-2010 §6.25", "title": "RTI shall report stored attribute transportation overrides for the currently implemented reliable and best-effort transport subset.", "service_group": "Object management", "linked_methods": ("queryAttributeTransportationType", "reportAttributeTransportationType"), "linked_assets": ("REQ-OM-TRANSPORT-REPORT-001",), "claim_scope": "supported-subset", "supported_subset_for": "HLA1516.1-OM-6.25-001", "policy_basis": "reliable-best-effort-transport-only", "positive_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_transportation_type_services_emit_confirm_and_report_callbacks",), "negative_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore",), "implementation_refs": ("hla2010/backends/python/object_delivery.py", "hla2010/ambassadors.py")},
    {"requirement_id": "HLA1516.1-OM-6.26-001", "section_ref": "IEEE 1516.1-2010 §6.26", "title": "RTI shall invoke Report Attribute Transportation Type across the full transportation semantic space.", "service_group": "Object management", "linked_methods": ("reportAttributeTransportationType",), "linked_assets": ("REQ-OM-TRANSPORT-SCOPE-001",), "claim_scope": "broad-spec", "policy_basis": "reliable-best-effort-transport-only", "status_override": "partial", "notes": "The backend proves report callbacks for the supported reliable plus best-effort subset, not the full broader transport semantic space."},
    {"requirement_id": "HLA1516.1-OM-6.26-002", "section_ref": "IEEE 1516.1-2010 §6.26", "title": "RTI shall invoke Report Attribute Transportation Type for the currently implemented reliable and best-effort transport subset.", "service_group": "Object management", "linked_methods": ("reportAttributeTransportationType",), "linked_assets": ("REQ-OM-TRANSPORT-REPORT-001",), "claim_scope": "supported-subset", "supported_subset_for": "HLA1516.1-OM-6.26-001", "policy_basis": "reliable-best-effort-transport-only", "positive_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_transportation_type_services_emit_confirm_and_report_callbacks",), "negative_test_refs": (), "implementation_refs": ("hla2010/backends/python/object_delivery.py", "hla2010/ambassadors.py")},
    {"requirement_id": "HLA1516.1-OM-6.26-003", "section_ref": "IEEE 1516.1-2010 §6.26", "title": "RTI shall not emit Report Attribute Transportation Type when the corresponding query is rejected for invalid state, object, or attribute inputs.", "service_group": "Object management", "linked_methods": ("reportAttributeTransportationType", "queryAttributeTransportationType"), "linked_assets": ("REQ-OM-TRANSPORT-REPORT-001",), "claim_scope": "supported-subset", "supported_subset_for": "HLA1516.1-OM-6.26-001", "policy_basis": "reliable-best-effort-transport-only", "positive_test_refs": (), "negative_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore",), "implementation_refs": ("hla2010/backends/python/object_delivery.py", "hla2010/ambassadors.py")},
    {"requirement_id": "HLA1516.1-OM-6.27-001", "section_ref": "IEEE 1516.1-2010 §6.27", "title": "RTI shall provide Request Interaction Transportation Type Change across the full transportation semantic space defined by the standard.", "service_group": "Object management", "linked_methods": ("requestInteractionTransportationTypeChange",), "linked_assets": ("REQ-OM-TRANSPORT-SCOPE-001",), "claim_scope": "broad-spec", "policy_basis": "reliable-best-effort-transport-only", "status_override": "partial", "notes": "The backend exposes this service but the broad standards row remains partial because only the supported reliable plus best-effort subset is modeled directly."},
    {"requirement_id": "HLA1516.1-OM-6.27-002", "section_ref": "IEEE 1516.1-2010 §6.27", "title": "RTI shall support Request Interaction Transportation Type Change for the currently implemented reliable and best-effort transport subset and persist that selected interaction transport state across restore.", "service_group": "Object management", "linked_methods": ("requestInteractionTransportationTypeChange", "queryInteractionTransportationType"), "linked_assets": ("REQ-OM-TRANSPORT-REPORT-001", "REQ-OM-TRANSPORT-BEST-EFFORT-001", "REQ-SAVE-RESTORE-FEDERATE-LOCAL-STATE-001"), "claim_scope": "supported-subset", "supported_subset_for": "HLA1516.1-OM-6.27-001", "policy_basis": "reliable-best-effort-transport-only", "positive_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_transportation_type_services_emit_confirm_and_report_callbacks", "tests/backends/test_python_backend_object_ownership_extended.py::test_best_effort_transport_changes_callback_transport_and_splits_mixed_attribute_updates", "tests/verification/test_compliance_slice_v011.py::test_restore_reinstates_saved_attribute_and_interaction_transportation_overrides"), "negative_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_request_interaction_transportation_type_change_rejects_not_connected_not_joined_and_save_restore",), "implementation_refs": ("hla2010/backends/python/object_delivery.py", "hla2010/backends/python/ddm.py", "hla2010/backends/python/save_restore.py", "hla2010/backends/python/state.py")},
    {"requirement_id": "HLA1516.1-OM-6.28-001", "section_ref": "IEEE 1516.1-2010 §6.28", "title": "RTI shall invoke Confirm Interaction Transportation Type Change across the full transportation semantic space.", "service_group": "Object management", "linked_methods": ("confirmInteractionTransportationTypeChange",), "linked_assets": ("REQ-OM-TRANSPORT-SCOPE-001",), "claim_scope": "broad-spec", "policy_basis": "reliable-best-effort-transport-only", "status_override": "partial", "notes": "The backend proves confirm callbacks for the supported reliable plus best-effort subset, not the full broader transport semantic space."},
    {"requirement_id": "HLA1516.1-OM-6.28-002", "section_ref": "IEEE 1516.1-2010 §6.28", "title": "RTI shall invoke Confirm Interaction Transportation Type Change for the currently implemented reliable and best-effort transport subset.", "service_group": "Object management", "linked_methods": ("confirmInteractionTransportationTypeChange",), "linked_assets": ("REQ-OM-TRANSPORT-REPORT-001",), "claim_scope": "supported-subset", "supported_subset_for": "HLA1516.1-OM-6.28-001", "policy_basis": "reliable-best-effort-transport-only", "positive_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_transportation_type_services_emit_confirm_and_report_callbacks",), "negative_test_refs": (), "implementation_refs": ("hla2010/backends/python/object_delivery.py", "hla2010/ambassadors.py")},
    {"requirement_id": "HLA1516.1-OM-6.28-003", "section_ref": "IEEE 1516.1-2010 §6.28", "title": "RTI shall not emit Confirm Interaction Transportation Type Change when the corresponding change request is rejected for invalid state, class, publication, or transport inputs.", "service_group": "Object management", "linked_methods": ("confirmInteractionTransportationTypeChange", "requestInteractionTransportationTypeChange"), "linked_assets": ("REQ-OM-TRANSPORT-REPORT-001",), "claim_scope": "supported-subset", "supported_subset_for": "HLA1516.1-OM-6.28-001", "policy_basis": "reliable-best-effort-transport-only", "positive_test_refs": (), "negative_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_request_interaction_transportation_type_change_rejects_not_connected_not_joined_and_save_restore",), "implementation_refs": ("hla2010/backends/python/object_delivery.py", "hla2010/ambassadors.py")},
    {"requirement_id": "HLA1516.1-OM-6.29-001", "section_ref": "IEEE 1516.1-2010 §6.29", "title": "RTI shall provide Query Interaction Transportation Type across the full transportation semantic space defined by the standard.", "service_group": "Object management", "linked_methods": ("queryInteractionTransportationType",), "linked_assets": ("REQ-OM-TRANSPORT-SCOPE-001",), "claim_scope": "broad-spec", "policy_basis": "reliable-best-effort-transport-only", "status_override": "partial", "notes": "The backend proves query/report behavior for the supported reliable plus best-effort subset, not the full broader transport semantic space."},
    {"requirement_id": "HLA1516.1-OM-6.29-002", "section_ref": "IEEE 1516.1-2010 §6.29", "title": "RTI shall report stored interaction transportation overrides for the currently implemented reliable and best-effort transport subset.", "service_group": "Object management", "linked_methods": ("queryInteractionTransportationType", "reportInteractionTransportationType"), "linked_assets": ("REQ-OM-TRANSPORT-REPORT-001",), "claim_scope": "supported-subset", "supported_subset_for": "HLA1516.1-OM-6.29-001", "policy_basis": "reliable-best-effort-transport-only", "positive_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_transportation_type_services_emit_confirm_and_report_callbacks",), "negative_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_query_interaction_transportation_type_rejects_not_connected_not_joined_invalid_handle_and_save_restore",), "implementation_refs": ("hla2010/backends/python/object_delivery.py", "hla2010/ambassadors.py")},
    {"requirement_id": "HLA1516.1-OM-6.30-001", "section_ref": "IEEE 1516.1-2010 §6.30", "title": "RTI shall invoke Report Interaction Transportation Type across the full transportation semantic space.", "service_group": "Object management", "linked_methods": ("reportInteractionTransportationType",), "linked_assets": ("REQ-OM-TRANSPORT-SCOPE-001",), "claim_scope": "broad-spec", "policy_basis": "reliable-best-effort-transport-only", "status_override": "partial", "notes": "The backend proves report callbacks for the supported reliable plus best-effort subset, not the full broader transport semantic space."},
    {"requirement_id": "HLA1516.1-OM-6.30-002", "section_ref": "IEEE 1516.1-2010 §6.30", "title": "RTI shall invoke Report Interaction Transportation Type for the currently implemented reliable and best-effort transport subset.", "service_group": "Object management", "linked_methods": ("reportInteractionTransportationType",), "linked_assets": ("REQ-OM-TRANSPORT-REPORT-001",), "claim_scope": "supported-subset", "supported_subset_for": "HLA1516.1-OM-6.30-001", "policy_basis": "reliable-best-effort-transport-only", "positive_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_transportation_type_services_emit_confirm_and_report_callbacks",), "negative_test_refs": (), "implementation_refs": ("hla2010/backends/python/object_delivery.py", "hla2010/ambassadors.py")},
    {"requirement_id": "HLA1516.1-OM-6.30-003", "section_ref": "IEEE 1516.1-2010 §6.30", "title": "RTI shall not emit Report Interaction Transportation Type when the corresponding query is rejected for invalid state or invalid interaction inputs.", "service_group": "Object management", "linked_methods": ("reportInteractionTransportationType", "queryInteractionTransportationType"), "linked_assets": ("REQ-OM-TRANSPORT-REPORT-001",), "claim_scope": "supported-subset", "supported_subset_for": "HLA1516.1-OM-6.30-001", "policy_basis": "reliable-best-effort-transport-only", "positive_test_refs": (), "negative_test_refs": ("tests/backends/test_python_backend_object_ownership_extended.py::test_query_interaction_transportation_type_rejects_not_connected_not_joined_invalid_handle_and_save_restore",), "implementation_refs": ("hla2010/backends/python/object_delivery.py", "hla2010/ambassadors.py")},
)


def build_requirements_matrix_2010(project_root: str | Path | None = None, *, version: str = "0.13.0") -> dict[str, Any]:
    """Return a whole-spec requirements matrix spanning section areas, service rows, and verification slices."""
    del project_root
    ledger = build_requirements_ledger(version=version)
    plan = build_verification_plan(version)
    vendor_rows_by_clause = _load_backend_conformance_vendor_rows()
    operational_vendor_profiles = _load_operational_vendor_profiles()

    rows: list[dict[str, Any]] = []
    verification_slice_rows: list[dict[str, Any]] = []
    service_rows_by_method: dict[str, list[dict[str, Any]]] = {}
    for row in ledger["rows"]:
        service_rows_by_method.setdefault(str(row["method"]), []).append(row)
    assets_by_id = {asset.asset_id: asset for asset in plan.assets}
    extracted_specs_by_id = {spec["requirement_id"]: spec for spec in _EXTRACTED_REQUIREMENTS_1516_1_CLAUSES_5_6}

    def _normalize_requirement_status(status: str) -> str:
        mapping = {
            "implemented-slice": "pass",
            "implemented-smoke": "partial",
            "pass": "pass",
            "mapped": "pass",
            "partial": "partial",
            "planned": "planned",
            "seeded": "planned",
            "not-evidenced": "not-evidenced",
            "gap": "fail",
            "fail": "fail",
        }
        return mapping.get(status, "planned")

    def _aggregate_status(statuses: list[str]) -> str:
        normalized = [_normalize_requirement_status(item) for item in statuses if item]
        if not normalized:
            return "planned"
        if any(item == "fail" for item in normalized):
            return "fail"
        if any(item == "not-evidenced" for item in normalized):
            return "not-evidenced"
        if any(item == "partial" for item in normalized):
            return "partial"
        if any(item == "pass" for item in normalized):
            return "pass"
        return "planned"

    section_area_inputs: dict[str, list[str]] = {}
    omt_area_inputs: dict[str, list[str]] = {}
    for row in ledger["rows"]:
        raw_section = str(row["section"])
        section = raw_section.split("§", 1)[-1].split(".", 1)[0].strip()
        section_area_inputs.setdefault(section, []).append(row["outcome"])

    for key, ref in SERVICE_AREAS.items():
        section_status = _aggregate_status(section_area_inputs.get(ref.section, []))
        rows.append(
            _with_vendor_parity(
                {
                    "matrix_id": f"AREA-1516.1-{ref.section}",
                    "kind": "section-area",
                    "document": ref.document,
                    "section_ref": f"{ref.document} §{ref.section}",
                    "title": ref.title,
                    "requirement_id": "",
                    "service_group": ref.title,
                    "status": section_status,
                    "implementation_refs": [],
                    "positive_test_refs": [],
                    "negative_test_refs": [],
                    "artifact_refs": [],
                    "source": key,
                },
                vendor_rows_by_clause=vendor_rows_by_clause,
                operational_vendor_profiles=operational_vendor_profiles,
            )
        )

    def _omt_requirement_id(section: str, source_key: str) -> str:
        token = section.replace(" ", "_").replace(".", "_").replace("-", "_").replace("/", "_")
        return f"REQ-OMT-{token}-{source_key}"

    for key, ref in FOM_REFERENCES.items():
        requirement_id = _omt_requirement_id(ref.section, key)
        rows.append(
            _with_vendor_parity(
                {
                    "matrix_id": requirement_id,
                    "kind": "omt-area",
                    "document": ref.document,
                    "section_ref": f"{ref.document} §{ref.section}",
                    "title": ref.title,
                    "requirement_id": requirement_id,
                    "service_group": "OMT/FOM",
                    "status": "planned",
                    "implementation_refs": [],
                    "positive_test_refs": [],
                    "negative_test_refs": [],
                    "artifact_refs": [],
                    "source": key,
                },
                vendor_rows_by_clause=vendor_rows_by_clause,
                operational_vendor_profiles=operational_vendor_profiles,
            )
        )

    curated_requirement_ids: set[str] = set()
    for row in _load_curated_requirement_rows():
        normalized = dict(row)
        extracted_spec = extracted_specs_by_id.get(str(normalized.get("requirement_id", "")))
        if extracted_spec is not None:
            if not normalized.get("linked_methods"):
                normalized["linked_methods"] = list(extracted_spec.get("linked_methods", ()))
            if not normalized.get("linked_assets"):
                normalized["linked_assets"] = list(extracted_spec.get("linked_assets", ()))
        normalized["status"] = _normalize_requirement_status(str(row["status"]))
        rows.append(
            _with_vendor_parity(
                normalized,
                vendor_rows_by_clause=vendor_rows_by_clause,
                operational_vendor_profiles=operational_vendor_profiles,
            )
        )
        curated_requirement_ids.add(str(normalized["requirement_id"]))
        section_ref = str(normalized["section_ref"])
    for row in ledger["rows"]:
        rows.append(
            _with_vendor_parity(
                {
                    "matrix_id": row["requirement_id"],
                    "kind": "service-requirement",
                    "document": "IEEE 1516.1-2010",
                    "section_ref": row["section"],
                    "title": row["title"],
                    "requirement_id": row["requirement_id"],
                    "service_group": row["service_group"],
                    "status": row["outcome"],
                    "implementation_refs": row["implementation_refs"],
                    "positive_test_refs": row["positive_test_refs"],
                    "negative_test_refs": row["negative_test_refs"],
                    "artifact_refs": row["artifact_refs"],
                    "source": row["method"],
                },
                vendor_rows_by_clause=vendor_rows_by_clause,
                operational_vendor_profiles=operational_vendor_profiles,
            )
        )

    for spec in _EXTRACTED_REQUIREMENTS_1516_1_CLAUSES_5_6:
        if spec["requirement_id"] in curated_requirement_ids:
            continue
        linked_service_rows = [item for method_name in spec.get("linked_methods", ()) for item in service_rows_by_method.get(method_name, ())]
        linked_assets = [assets_by_id[asset_id] for asset_id in spec.get("linked_assets", ()) if asset_id in assets_by_id]
        statuses = [item["outcome"] for item in linked_service_rows] + [asset.status for asset in linked_assets]
        status = spec.get("status_override") or _aggregate_status(statuses)
        implementation_refs = (
            list(spec["implementation_refs"])
            if "implementation_refs" in spec
            else sorted(
            {
                ref
                for item in linked_service_rows
                for ref in item["implementation_refs"]
            }
            | {
                ref
                for asset in linked_assets
                for ref in asset.evidence
                if ref.startswith("hla2010/")
            }
        )
        )
        positive_test_refs = (
            list(spec["positive_test_refs"])
            if "positive_test_refs" in spec
            else sorted(
            {
                ref
                for item in linked_service_rows
                for ref in item["positive_test_refs"]
            }
            | {
                ref
                for asset in linked_assets
                for ref in asset.evidence
                if ref.startswith("tests/")
            }
        )
        )
        negative_test_refs = (
            list(spec["negative_test_refs"])
            if "negative_test_refs" in spec
            else sorted(
            {
                ref
                for item in linked_service_rows
                for ref in item["negative_test_refs"]
            }
            | {
                ref
                for asset in linked_assets
                for ref in asset.evidence
                if ref.startswith("tests/") and "negative" in ref.lower()
            }
        )
        )
        artifact_refs = (
            list(spec["artifact_refs"])
            if "artifact_refs" in spec
            else sorted(
            {
                ref
                for item in linked_service_rows
                for ref in item["artifact_refs"]
            }
            | {
                ref
                for asset in linked_assets
                for ref in asset.evidence
                if ref.startswith("analysis/") or ref.startswith("verification/")
            }
        )
        )
        rows.append(
            _with_vendor_parity(
                {
                    "matrix_id": spec["requirement_id"],
                    "kind": "extracted-requirement",
                    "document": "IEEE 1516.1-2010",
                    "section_ref": spec["section_ref"],
                    "title": spec["title"],
                    "requirement_id": spec["requirement_id"],
                    "service_group": spec["service_group"],
                    "status": status,
                    "implementation_refs": implementation_refs,
                    "positive_test_refs": positive_test_refs,
                    "negative_test_refs": negative_test_refs,
                    "artifact_refs": artifact_refs,
                    "linked_methods": list(spec.get("linked_methods", ())),
                    "linked_assets": list(spec.get("linked_assets", ())),
                    "claim_scope": spec.get("claim_scope", "broad-spec"),
                    "supported_subset_for": spec.get("supported_subset_for", ""),
                    "policy_basis": spec.get("policy_basis", ""),
                    "notes": spec.get("notes", ""),
                    "source": "curated-clause5-6",
                },
                vendor_rows_by_clause=vendor_rows_by_clause,
                operational_vendor_profiles=operational_vendor_profiles,
            )
        )
        if spec["section_ref"].startswith("IEEE 1516.1-2010 §"):
            section = spec["section_ref"].split("§", 1)[1].split(".", 1)[0].strip()
            section_area_inputs.setdefault(section, []).append(status)

    for asset in plan.assets:
        if asset.asset_type not in {"requirement", "scenario"}:
            continue
        asset_row = (
            {
                "matrix_id": asset.asset_id,
                "kind": "verification-slice",
                "document": "multi-section",
                "section_ref": "; ".join(asset.section_refs),
                "title": asset.title,
                "requirement_id": asset.asset_id,
                "service_group": asset.asset_type,
                "status": asset.status,
                "implementation_refs": [item for item in asset.evidence if item.startswith("hla2010/")],
                "positive_test_refs": [item for item in asset.evidence if item.startswith("tests/")],
                "negative_test_refs": [item for item in asset.evidence if "negative" in item.lower()],
                "artifact_refs": [item for item in asset.evidence if item.startswith("analysis/") or item.startswith("verification/")],
                "source": asset.asset_id,
            }
        )
        asset_row = _with_vendor_parity(
            asset_row,
            vendor_rows_by_clause=vendor_rows_by_clause,
            operational_vendor_profiles=operational_vendor_profiles,
        )
        verification_slice_rows.append(asset_row)
        rows.append(asset_row)
        for section_ref in asset.section_refs:
            if section_ref.startswith("1516.1-2010 §"):
                section = section_ref.split("§", 1)[1].split(".", 1)[0].strip()
                section_area_inputs.setdefault(section, []).append(asset.status)
            elif section_ref.startswith("1516.2-2010 §"):
                section = section_ref.split("§", 1)[1].strip()
                omt_area_inputs.setdefault(section, []).append(asset.status)

    for row in rows:
        if row["kind"] == "section-area":
            section = row["section_ref"].split("§", 1)[1].strip()
            row["status"] = _aggregate_status(section_area_inputs.get(section, []))
        elif row["kind"] == "omt-area":
            section = row["section_ref"].split("§", 1)[1].strip()
            source_key = row["source"]
            matching_assets = [
                item for item in verification_slice_rows
                if f"1516.2-2010 §{section}" in item["section_ref"].split("; ")
            ]
            row["status"] = _aggregate_status(omt_area_inputs.get(section, []))
            row["implementation_refs"] = [item for asset in matching_assets for item in asset["implementation_refs"]]
            row["positive_test_refs"] = [item for asset in matching_assets for item in asset["positive_test_refs"]]
            row["negative_test_refs"] = [item for asset in matching_assets for item in asset["negative_test_refs"]]
            row["artifact_refs"] = [item for asset in matching_assets for item in asset["artifact_refs"]]
            row["source"] = source_key

    kind_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    for row in rows:
        kind_counts[row["kind"]] = kind_counts.get(row["kind"], 0) + 1
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1

    return {
        "summary": {
            "version": version,
            "row_count": len(rows),
            "kind_counts": dict(sorted(kind_counts.items())),
            "status_counts": dict(sorted(status_counts.items())),
            "documents": sorted({row["document"] for row in rows}),
        },
        "rows": rows,
    }


def write_requirements_matrix_2010_json(
    path: str | Path,
    project_root: str | Path | None = None,
    *,
    version: str = "0.13.0",
) -> Path:
    del project_root
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_requirements_matrix_2010(version=version), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def write_requirements_matrix_2010_csv(
    path: str | Path,
    project_root: str | Path | None = None,
    *,
    version: str = "0.13.0",
) -> Path:
    del project_root
    matrix = build_requirements_matrix_2010(version=version)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
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
        "certi_runtime_status",
        "pitch_runtime_status",
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
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in matrix["rows"]:
            record = dict(row)
            for key, value in list(record.items()):
                if isinstance(value, list):
                    record[key] = "; ".join(str(item) for item in value)
            writer.writerow(record)
    return target


__all__ = [
    "VerificationAsset",
    "VerificationPlan",
    "build_verification_plan",
    "write_verification_assets",
    "write_traceability_csv",
]

# Compatibility helpers for repo-seed tests.  The canonical implementation lives
# in hla2010.conformance; these wrappers produce the flatter dictionary/CSV/MD
# shape used by the current pytest suite without requiring generated analysis
# assets to be committed to the repository seed.


def build_service_conformance_matrix(project_root: str | Path | None = None, *, version: str = "0.13.0") -> dict[str, Any]:
    """Return a flat service-by-service conformance matrix dictionary.

    ``project_root`` is accepted for compatibility with earlier asset-writer
    call sites; the matrix is generated from package source, not from generated
    verification files.
    """
    from .conformance import build_service_conformance_matrix as _build

    canonical = _build(version=version)
    rows: list[dict[str, Any]] = []
    status_counts: dict[str, int] = {}
    interface_counts: dict[str, int] = {}

    for index, row in enumerate(canonical.rows, start=1):
        has_backend = row.python_entry_point.startswith("PythonRTIBackend.")
        has_evidence = bool(row.evidence) or row.negative_executed_count > 0
        if row.interface == "FederateAmbassador" and row.implementation_status == "callback-helper":
            status = "callback-helper-tested" if has_evidence else "callback-helper-untested"
        elif has_backend and row.verification_status == "focused-executable-tests":
            status = "reference-implemented-tested"
        elif has_backend:
            status = "reference-implemented-untested"
        else:
            status = "planned-or-adapter-gap"

        status_counts[status] = status_counts.get(status, 0) + 1
        interface_counts[row.interface] = interface_counts.get(row.interface, 0) + 1
        rows.append(
            {
                "row_id": f"SCM-{index:04d}",
                "requirement_id": row.requirement_id,
                "interface": row.interface,
                "method": row.method_name,
                "python_name": row.python_name,
                "section": row.section_ref.replace("IEEE ", ""),
                "title": row.title,
                "service_group": row.service_group,
                "status": status,
                "source_languages": list(row.source_languages),
                "source_overload_count": row.source_overload_count,
                "declared_exceptions": list(row.declared_exceptions),
                "python_entry_point": row.python_entry_point,
                "implementation_refs": list(row.implementation_refs),
                "positive_test_refs": list(row.positive_test_refs),
                "negative_test_refs": list(row.negative_test_refs),
                "artifact_refs": list(row.artifact_refs),
                "python_backend_entrypoint": has_backend,
                "callback_helper": row.implementation_status == "callback-helper",
                "evidence": list(row.evidence),
                "negative_expectation_count": row.negative_expectation_count,
                "negative_executed_count": row.negative_executed_count,
                "negative_evidence": row.negative_executed_count > 0,
                "known_gaps": list(row.known_gaps),
            }
        )

    return {
        "summary": {
            "version": version,
            "row_count": len(rows),
            "interface_counts": dict(sorted(interface_counts.items())),
            "status_counts": dict(sorted(status_counts.items())),
            "source": "generated-from-package-source",
        },
        "rows": rows,
    }


def build_requirements_ledger(project_root: str | Path | None = None, *, version: str = "0.13.0") -> dict[str, Any]:
    """Return a flat requirements ledger dictionary compatible with artifact writers."""
    from .conformance import build_requirements_ledger as _build

    del project_root
    canonical = _build(version=version)
    rows: list[dict[str, Any]] = []
    for row in canonical.rows:
        rows.append(
            {
                "requirement_id": row.requirement_id,
                "interface": row.interface,
                "method": row.method_name,
                "python_name": row.python_name,
                "section": row.section_ref.replace("IEEE ", ""),
                "title": row.title,
                "service_group": row.service_group,
                "outcome": row.outcome,
                "implementation_status": row.implementation_status,
                "verification_status": row.verification_status,
                "implementation_refs": list(row.implementation_refs),
                "positive_test_refs": list(row.positive_test_refs),
                "negative_test_refs": list(row.negative_test_refs),
                "artifact_refs": list(row.artifact_refs),
                "verification_asset_id": row.verification_asset_id,
                "rationale": row.rationale,
                "evidence": list(row.evidence),
                "known_gaps": list(row.known_gaps),
            }
        )
    return {
        "summary": canonical.summary(),
        "rows": rows,
    }


def write_service_conformance_matrix_json(
    path: str | Path,
    project_root: str | Path | None = None,
    *,
    version: str = "0.13.0",
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_service_conformance_matrix(project_root, version=version), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def write_service_conformance_matrix_csv(
    path: str | Path,
    project_root: str | Path | None = None,
    *,
    version: str = "0.13.0",
) -> Path:
    matrix = build_service_conformance_matrix(project_root, version=version)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "row_id",
        "requirement_id",
        "interface",
        "method",
        "python_name",
        "section",
        "title",
        "service_group",
        "status",
        "python_backend_entrypoint",
        "callback_helper",
        "negative_evidence",
    ]
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in matrix["rows"]:
            record = dict(row)
            for key, value in list(record.items()):
                if isinstance(value, list):
                    record[key] = "; ".join(str(item) for item in value)
            writer.writerow(record)
    return target


def write_service_conformance_summary_markdown(
    path: str | Path,
    project_root: str | Path | None = None,
    *,
    version: str = "0.13.0",
) -> Path:
    matrix = build_service_conformance_matrix(project_root, version=version)
    summary = matrix["summary"]
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Service-by-service conformance matrix v{version}",
        "",
        f"Rows: {summary['row_count']}",
        "",
        "## Interface counts",
        "",
    ]
    for key, value in summary["interface_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Status counts", ""])
    for key, value in summary["status_counts"].items():
        lines.append(f"- {key}: {value}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def write_requirements_ledger_json(
    path: str | Path,
    project_root: str | Path | None = None,
    *,
    version: str = "0.13.0",
) -> Path:
    del project_root
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_requirements_ledger(version=version), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def write_requirements_ledger_csv(
    path: str | Path,
    project_root: str | Path | None = None,
    *,
    version: str = "0.13.0",
) -> Path:
    del project_root
    ledger = build_requirements_ledger(version=version)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "requirement_id",
        "interface",
        "method",
        "python_name",
        "section",
        "title",
        "service_group",
        "outcome",
        "implementation_status",
        "verification_status",
        "implementation_refs",
        "positive_test_refs",
        "negative_test_refs",
        "artifact_refs",
        "verification_asset_id",
        "rationale",
    ]
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in ledger["rows"]:
            record = dict(row)
            for key, value in list(record.items()):
                if isinstance(value, list):
                    record[key] = "; ".join(str(item) for item in value)
            writer.writerow(record)
    return target


__all__ = tuple(
    dict.fromkeys(
        __all__
        + [
            "build_requirements_matrix_2010",
            "build_requirements_ledger",
            "build_service_conformance_matrix",
            "write_requirements_matrix_2010_csv",
            "write_requirements_matrix_2010_json",
            "write_requirements_ledger_csv",
            "write_requirements_ledger_json",
            "write_service_conformance_matrix_json",
            "write_service_conformance_matrix_csv",
            "write_service_conformance_summary_markdown",
        ]
    )
)
