"""Repo-internal verification asset plan helpers."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def _edition_qualified_section(section: str) -> str:
    return (
        section.replace("1516.1-2010 §", "IEEE 1516.1-2010 (2010 edition) §")
        .replace("1516.2-2010 §", "IEEE 1516.2-2010 (2010 edition) §")
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
            "sections": sorted({_edition_qualified_section(section) for section in self.by_section()}),
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
            ("packages/hla-backend-python1516e/src/hla.backends.python1516e/mom_actions.py::_run_mom_service_action", "verification/mom_negative_matrix_v0_12.json"),
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
            "Annex E schema-family conformance validation is executable for the carried standard schemas and round-trip witnesses",
            ("1516.2-2010 §Annex E",),
            "implemented-slice",
            (
                "hla2010/fom.py::validate_fom_xml_schema",
                "tests/factories/test_fom_omt_parsing.py::test_parse_fom_xml_with_omt_schema_validation_accepts_restaurant_reference_module_and_rejects_invalid_document",
                "tests/factories/test_fom_omt_parsing.py::test_parse_fom_xml_rejects_unknown_object_model_namespace",
                "tests/factories/test_fom_omt_parsing.py::test_serialize_fom_module_emits_schema_valid_xml_and_preserves_identification",
                "tests/factories/test_fom_omt_parsing.py::test_serialize_fom_module_preserves_metadata_subset_across_round_trip",
            ),
            gaps=(
                "The repo proves Annex E schema-family validation and round-trip behavior, but it does not yet maintain one curated executable witness per imported schema element or schema type.",
            ),
            notes="This slice captures the repo's executable Annex E family proof without overstating it as per-element or full generic-schema closure.",
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
                "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_future_exclusion_scenario",
                "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_output_delivery_scenario",
                "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_consumer_order_scenario",
                "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_pipeline_scenario",
                "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_receive_order_poison_scenario",
                "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_future_exclusion",
                "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_output_delivery",
                "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_consumer_order",
                "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_pipeline",
                "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_receive_order_poison",
                "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_future_exclusion_oracle_rejects_mismatched_lits_boundary",
                "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_output_delivery_oracle_rejects_output_before_window_close",
                "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_consumer_order_oracle_rejects_reversed_delivery_order",
                "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_pipeline_oracle_rejects_cross_window_payload_contamination",
                "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_receive_order_poison_oracle_rejects_closed_window_mutation",
            ),
            gaps=("The distributed-time algorithm remains a local-process approximation, not a proven multi-process LBTS algorithm.",),
            notes=(
                "The bounded radar time harness now proves future-exclusion blocking, closed-window output delivery, "
                "downstream consumer ordering, pipeline overlap isolation, and receive-order poison rejection under "
                "timestamp order, with spec-lane negative oracle guards for mismatched LITS, premature output, "
                "reversed consumer order, cross-window contamination, and closed-window mutation."
            ),
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
                "packages/hla-backend-python1516e/src/hla.backends.python1516e/save_restore.py",
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
                "packages/hla-backend-python1516e/src/hla.backends.python1516e/save_restore.py",
                "tests/verification/test_compliance_slice_v011.py::test_restore_reinstates_saved_federate_runtime_flags_and_lookahead_state",
                "tests/verification/test_compliance_slice_v011.py::test_restore_reinstates_saved_federate_policy_reporting_and_conveyance_switches",
                "tests/verification/test_compliance_slice_v011.py::test_restore_reinstates_saved_attribute_and_interaction_order_overrides",
                "tests/verification/test_compliance_slice_v011.py::test_restore_reinstates_saved_attribute_and_interaction_transportation_overrides",
                "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_restore_state_scenario",
                "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_restore_output_scenario",
                "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_pipeline_restore_scenario",
                "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_restore_state",
                "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_restore_output",
                "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_pipeline_restore",
                "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_restore_window_state_oracle_rejects_dirty_post_close_callback_leak",
                "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_restore_output_oracle_rejects_dirty_output_replay_after_restore",
                "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_pipeline_restore_oracle_rejects_dirty_pipeline_output_replay",
            ),
            notes=(
                "The bounded 2025 restore ladder now covers open-window restore, closed-window restore, output resume, "
                "and pipeline resume, with spec-lane negative oracle guards for dirty post-close callback leakage, "
                "dirty output replay, and dirty pipeline output replay."
            ),
        ),
        VerificationAsset(
            "REQ-SAVE-RESTORE-CALLBACK-POLICY-001",
            "requirement",
            "Save/restore treats callback enablement as local runtime policy rather than persisted federation state",
            ("1516-2010 §12.2", "1516.1-2010 §4.24-§4.29"),
            "implemented-slice",
            (
                "packages/hla-backend-python1516e/src/hla.backends.python1516e/save_restore.py",
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
                "packages/hla-backend-python1516e/src/hla.backends.python1516e/save_restore.py",
                "tests/verification/test_compliance_slice_v011.py::test_restore_discards_pre_restore_callback_queue_and_retraction_bookkeeping",
                "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_stale_directed_tso_cleanup_scenario",
                "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_restore_output_scenario",
                "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_pipeline_restore_scenario",
                "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_restore_output",
                "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_pipeline_restore",
                "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_restore_clears_stale_directed_tso_and_preserves_post_restore_routing",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_clears_stale_directed_tso_and_preserves_post_restore_routing_over_fedpro_schema",
                "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_restore_output_oracle_rejects_dirty_output_replay_after_restore",
                "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_pipeline_restore_oracle_rejects_dirty_pipeline_output_replay",
            ),
            notes=(
                "This slice specifies transient post-restore quiescence rather than persistence of queued callback or "
                "message-retraction state, including bounded 2025 restore-output and pipeline-resume checks that dirty "
                "replayed outputs do not survive restore."
            ),
        ),
        VerificationAsset(
            "REQ-SAVE-RESTORE-ROUTING-STATE-001",
            "requirement",
            "Save/restore reinstates saved object and interaction subscription-routing state rather than preserving dirty post-save declaration mutations",
            ("1516-2010 §12.2", "1516.1-2010 §4.24-§4.29", "1516.1-2010 §5", "1516.1-2010 §6"),
            "implemented-slice",
            (
                "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_plain_object_subscriber_routing_scenario",
                "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_plain_interaction_subscriber_routing_scenario",
                "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_directed_ddm_subscriber_routing_scenario",
                "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_restore_recovers_plain_object_subscriber_routing",
                "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_restore_recovers_plain_interaction_subscriber_routing",
                "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_restore_recovers_directed_ddm_subscriber_routing",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_plain_object_subscriber_routing_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_plain_interaction_subscriber_routing_over_fedpro_schema",
                "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_directed_ddm_subscriber_routing_over_fedpro_schema",
            ),
            notes=(
                "This slice isolates declaration-routing rollback as saved RTI state: subscriber A owns the saved "
                "route, subscriber B owns the dirty post-save route, and restore must reinstate the saved delivery "
                "visibility for object reflections, plain interaction receipt, and directed DDM interaction routing."
            ),
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
                "artifacts/two_federate_suite/two_federate_callbacks.csv",
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
                "packages/hla-backend-python1516e/src/hla.backends.python1516e/subscriptions.py",
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
                "artifacts/two_federate_suite/two_federate_callbacks.csv",
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
                "hla.verification.repo_internal/verification/asset_plan.py::write_verification_assets",
                "hla.verification.repo_internal/verification/asset_plan.py::write_traceability_csv",
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

__all__ = [
    "VerificationAsset",
    "VerificationPlan",
    "build_verification_plan",
    "write_traceability_csv",
    "write_verification_assets",
]
