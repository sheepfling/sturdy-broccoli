from __future__ import annotations

import json
from pathlib import Path

import pytest
from hla.verification.repo_internal.spec2025_finish_line import (
    build_spec2025_finish_line_markdown,
    build_spec2025_finish_line_snapshot,
    write_spec2025_finish_line,
)

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-TRACE-001", "HLA2025-TRACE-002")
def test_2025_finish_line_snapshot_keeps_scope_counts_and_open_work_honest() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)

    assert snapshot["scope"] == "IEEE 1516-2025 requirements finish-line inventory, not a conformance claim"
    assert snapshot["registry"]["initial_tranche_requirements"] == 28
    assert "hla-2025-executable-test-requirements-v3" in snapshot["registry"]["imported_packets"]

    executable = snapshot["executable_test_backlog"]
    assert executable["row_count"] == 1117
    assert executable["source_rows"] == 398
    assert executable["by_test_kind"]["surface_contract"] == 196
    assert executable["by_test_kind"]["validator_positive_fixture"] == 158
    assert executable["by_test_kind"]["validator_negative_fixture"] == 158
    depth = snapshot["requirement_depth_expansion"]
    assert depth["status"] == "imported-harmonization-candidate"
    assert depth["row_count"] == 691
    assert depth["row_count_from_csv"] == 691
    assert depth["by_area"]["Federate Interface service catalog"] == 196
    assert depth["by_area"]["SOM/FOM service-usage requirements"] == 196
    assert depth["by_area"]["OMT component-level conformance"] == 224
    assert depth["by_area"]["OMT validator-negative conformance"] == 29
    assert depth["by_delta_type"]["carry-forward"] == 328
    assert depth["by_delta_type"]["modified"] == 237
    assert depth["by_delta_type"]["new"] == 71
    assert depth["by_delta_type"]["retired"] == 24
    disposition = snapshot["requirement_coverage_disposition"]
    assert disposition["status"] == "repo-reconciled-disposition"
    assert disposition["row_count"] == 691
    assert disposition["row_count_from_csv"] == 691
    assert disposition["covered_row_count"] == 564
    assert disposition["by_disposition"] == {
        "duplicate/umbrella": 22,
        "covered": 564,
        "retired/legacy-only": 24,
        "unsupported-boundary": 81,
    }
    assert disposition["by_priority"] == {"P0": 89, "P1": 430, "P2": 172}
    assert disposition["by_closure_wave"]["1-fi-service-and-binding-disposition"] == 208
    assert disposition["by_closure_wave"]["2-omt-field-and-validator-fixtures"] == 253
    assert disposition["fi_binding_surface"]["fi_rows"] == 196
    assert disposition["fi_binding_surface"]["java_present"] == 196
    assert disposition["fi_binding_surface"]["cpp_present"] == 196
    assert disposition["fi_binding_surface"]["fedpro_route_boundary_or_missing_review"] == 4

    backlog = snapshot["completion_backlog"]
    assert backlog["by_bucket"]["new-2025-requirements"] == 7
    assert backlog["by_current_status"]["implemented-slice"] >= 20
    assert backlog["by_current_status"].get("partial", 0) == 0
    assert "planned" not in backlog["by_current_status"]
    assert backlog["by_current_status"].get("unsupported-boundary", 0) == 0
    assert backlog["by_current_status"]["legacy-only"] == 1
    assert backlog["high_priority_open_count"] == 0

    open_ids = {row["id"] for row in backlog["high_priority_open"]}
    assert not open_ids
    for row_id in (
        "HLA2025-BLG-001",
        "HLA2025-BLG-002",
        "HLA2025-BND-001",
        "HLA2025-BND-002",
        "HLA2025-BND-003",
        "HLA2025-MOD-005",
        "HLA2025-MOD-007",
        "HLA2025-MOD-009",
        "HLA2025-MOD-010",
        "HLA2025-NEW-004",
        "HLA2025-NEW-007",
        "HLA2025-RET-003",
    ):
        assert row_id not in open_ids
    assert "HLA2025-NEW-001" not in open_ids
    assert "HLA2025-NEW-002" not in open_ids
    assert "HLA2025-NEW-005" not in open_ids
    assert "HLA2025-NEW-006" not in open_ids
    assert "HLA2025-MOD-004" not in open_ids
    assert "HLA2025-MOD-008" not in open_ids
    assert "HLA2025-RET-001" not in open_ids
    assert "HLA2025-MOD-002" not in open_ids
    assert "HLA2025-MOD-003" not in open_ids
    assert "HLA2025-MOD-006" not in open_ids

    matrix = snapshot["verification_matrix"]
    assert matrix["row_count"] == backlog["row_count"]
    assert matrix["high_priority_missing_anchor_count"] == 0
    assert matrix["high_priority_missing_anchors"] == []
    route_matrix = snapshot["route_parity_matrix"]
    assert route_matrix["scenario_count"] >= 8
    assert "python-2025-fedpro-grpc" in route_matrix["routes"]
    assert route_matrix["by_route"]["java-standard-2025-jpype"]["parity-covered"] == 8
    assert route_matrix["by_route"]["cpp-standard-2025-grpc"]["parity-covered"] == 8


@pytest.mark.requirements("HLA2025-REQ-002", "HLA2025-TRACE-001")
def test_2025_finish_line_snapshot_names_only_implemented_slices_with_evidence() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)
    slices = {row["id"]: row for row in snapshot["implemented_evidence_slices"]}

    assert slices["2025-auth-connect"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-001" in slices["2025-auth-connect"]["requirements"]
    assert any(path.endswith("test_rti1516_2025_encoding_auth_contexts.py") for path in slices["2025-auth-connect"]["evidence"])

    assert slices["2025-logical-time"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-112" in slices["2025-logical-time"]["requirements"]
    assert "HLA2025-FI-SVC-101" in slices["2025-logical-time"]["requirements"]
    assert "HLA2025-FI-SVC-122" in slices["2025-logical-time"]["requirements"]
    assert "HLA2025-FI-SVC-125" in slices["2025-logical-time"]["requirements"]
    assert "flushQueueRequest" in slices["2025-logical-time"]["supported_scope"]
    assert "queued timestamped object updates/interactions" in slices["2025-logical-time"]["supported_scope"]
    assert "message retraction before delivery" in slices["2025-logical-time"]["supported_scope"]
    assert "Cross-binding parity" in slices["2025-logical-time"]["supported_scope"]
    assert slices["2025-save-restore-lifecycle"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-018" in slices["2025-save-restore-lifecycle"]["requirements"]
    assert "HLA2025-FI-SVC-034" in slices["2025-save-restore-lifecycle"]["requirements"]
    assert "federation save/restore lifecycle callbacks" in slices["2025-save-restore-lifecycle"]["supported_scope"]
    assert "requestFederationSave and requestFederationRestore" in slices["2025-save-restore-lifecycle"]["supported_scope"]
    assert "object registry rollback" in slices["2025-save-restore-lifecycle"]["supported_scope"]
    assert "joined-federate logical-time rollback" in slices["2025-save-restore-lifecycle"]["supported_scope"]
    assert slices["2025-switch-inquiry-control"]["status"] == "implemented-slice"
    assert "HLA2025-RET-001" in slices["2025-switch-inquiry-control"]["requirements"]
    assert slices["2025-fom-mim-error-taxonomy"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-003" in slices["2025-fom-mim-error-taxonomy"]["requirements"]
    assert slices["2025-callback-context-parameters"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-004" in slices["2025-callback-context-parameters"]["requirements"]
    assert slices["2025-directed-interaction-boundary"]["status"] == "implemented-slice"
    assert "HLA2025-NEW-001" in slices["2025-directed-interaction-boundary"]["requirements"]
    assert {
        "HLA2025-FI-SVC-039",
        "HLA2025-FI-SVC-040",
        "HLA2025-FI-SVC-045",
        "HLA2025-FI-SVC-046",
        "HLA2025-FI-SVC-063",
        "HLA2025-FI-SVC-064",
    } <= set(slices["2025-directed-interaction-boundary"]["requirements"])
    assert "receiveDirectedInteraction callback delivery" in slices["2025-directed-interaction-boundary"]["supported_scope"]
    assert "Java/C++/FedPro route parity remain later behavior work" in slices["2025-directed-interaction-boundary"]["supported_scope"]
    assert slices["2025-omt-reference-value-required"]["status"] == "implemented-slice"
    assert "HLA2025-NEW-006" in slices["2025-omt-reference-value-required"]["requirements"]
    assert slices["2025-omt-component-metadata-roundtrip"]["status"] == "implemented-slice"
    assert "HLA2025-OMT-COMP-004" in slices["2025-omt-component-metadata-roundtrip"]["requirements"]
    assert "HLA2025-OMT-COMP-215" in slices["2025-omt-component-metadata-roundtrip"]["requirements"]
    assert "array encodings" in slices["2025-omt-component-metadata-roundtrip"]["supported_scope"]
    assert "logicalTime/logicalTimeInterval names and dataType bindings" in slices["2025-omt-component-metadata-roundtrip"]["supported_scope"]
    assert slices["2025-omt-switch-and-transport-subset"]["status"] == "implemented-slice"
    assert "HLA2025-OMT-COMP-078" in slices["2025-omt-switch-and-transport-subset"]["requirements"]
    assert "HLA2025-OMT-COMP-167" in slices["2025-omt-switch-and-transport-subset"]["requirements"]
    assert "conveyProducingFederate default" in slices["2025-omt-switch-and-transport-subset"]["supported_scope"]
    assert slices["2025-omt-extended-supported-subset"]["status"] == "implemented-slice"
    assert "HLA2025-OMT-COMP-001" in slices["2025-omt-extended-supported-subset"]["requirements"]
    assert "HLA2025-OMT-COMP-223" in slices["2025-omt-extended-supported-subset"]["requirements"]
    assert "supported model-identification scalar and reference/POC metadata subset" in slices["2025-omt-extended-supported-subset"]["supported_scope"]
    assert "supported basic/simple/enumerated/array/fixed-record/variant-record datatype tables" in slices["2025-omt-extended-supported-subset"]["supported_scope"]
    assert slices["2025-omt-unsupported-component-boundaries"]["status"] == "unsupported-boundary"
    assert "HLA2025-OMT-COMP-037" in slices["2025-omt-unsupported-component-boundaries"]["requirements"]
    assert "HLA2025-OMT-COMP-197" in slices["2025-omt-unsupported-component-boundaries"]["requirements"]
    assert "not modeled in the shared parser/serializer surface" in slices["2025-omt-unsupported-component-boundaries"]["supported_scope"]
    assert slices["2025-omt-unmodeled-component-boundaries-expanded"]["status"] == "unsupported-boundary"
    assert "HLA2025-OMT-COMP-006" in slices["2025-omt-unmodeled-component-boundaries-expanded"]["requirements"]
    assert "HLA2025-OMT-COMP-224" in slices["2025-omt-unmodeled-component-boundaries-expanded"]["requirements"]
    assert "keyword taxonomy attributes" in slices["2025-omt-unmodeled-component-boundaries-expanded"]["supported_scope"]
    assert "transportation reliable/semantics detail rows" in slices["2025-omt-unmodeled-component-boundaries-expanded"]["supported_scope"]
    assert slices["2025-carry-forward-cleanup"]["status"] == "implemented-slice"
    assert "HLA2025-BLG-001" in slices["2025-carry-forward-cleanup"]["requirements"]
    assert slices["2025-service-utilization-crosscheck"]["status"] == "implemented-slice"
    assert "HLA2025-OMT-SU-001" in slices["2025-service-utilization-crosscheck"]["requirements"]
    assert "HLA2025-OMT-SU-196" in slices["2025-service-utilization-crosscheck"]["requirements"]
    assert "optional serviceUtilization tables from SOM, FOM, and MIM modules" in slices["2025-service-utilization-crosscheck"]["supported_scope"]
    assert "treats table absence as an empty mapping" in slices["2025-service-utilization-crosscheck"]["supported_scope"]
    assert "preserves service-usage attributes through parse/serialize roundtrip" in slices["2025-service-utilization-crosscheck"]["supported_scope"]
    assert slices["2025-exception-and-logical-time-deltas"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-010" in slices["2025-exception-and-logical-time-deltas"]["requirements"]
    assert slices["2025-java-binding-source-trace"]["status"] == "implemented-slice"
    assert "full Java behavior conformance" in slices["2025-java-binding-source-trace"]["supported_scope"]
    assert slices["2025-cpp-binding-source-trace"]["status"] == "implemented-slice"
    assert "full C++ RTI behavior pass" in slices["2025-cpp-binding-source-trace"]["supported_scope"]
    assert slices["2025-standard-route-runtime-capability"]["status"] == "implemented-slice"
    assert "HLA2025-BND-001" in slices["2025-standard-route-runtime-capability"]["requirements"]
    assert "HLA2025-BND-002" in slices["2025-standard-route-runtime-capability"]["requirements"]
    assert "C++ artifacts exercise this locally" in slices["2025-standard-route-runtime-capability"]["supported_scope"]
    assert "Java runtime evidence runs when the Java 2025 shim jar is built" in slices["2025-standard-route-runtime-capability"]["supported_scope"]
    assert "not full Java/C++ behavior conformance or object exchange" in slices["2025-standard-route-runtime-capability"]["supported_scope"]
    assert slices["2025-fedpro-transport-contract"]["status"] == "implemented-slice"
    assert "hosted loopback runtime session" in slices["2025-fedpro-transport-contract"]["supported_scope"]
    assert "basic ownership divest/acquire callbacks" in slices["2025-fedpro-transport-contract"]["supported_scope"]
    assert "time-regulation/time-constrained/time-advance callbacks" in slices["2025-fedpro-transport-contract"]["supported_scope"]
    assert "queued timestamped attribute reflection/interaction receipt" in slices["2025-fedpro-transport-contract"]["supported_scope"]
    assert "pre-delivery retract" in slices["2025-fedpro-transport-contract"]["supported_scope"]
    assert "object discovery, attribute reflection, interaction receipt" in slices["2025-fedpro-transport-contract"]["supported_scope"]
    assert "basic DDM region-overlap filtering for object attributes" in slices["2025-fedpro-transport-contract"]["supported_scope"]
    assert "MOM service-invocation report callbacks over FedPro" in slices["2025-fedpro-transport-contract"]["supported_scope"]
    assert "synchronization point/status MOM reports over FedPro" in slices["2025-fedpro-transport-contract"]["supported_scope"]
    assert "Full MOM action/request routing" in slices["2025-fedpro-transport-contract"]["supported_scope"]
    assert "full RTI semantics remain outside this slice" in slices["2025-fedpro-transport-contract"]["supported_scope"]
    assert slices["2025-basic-object-exchange"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-057" in slices["2025-basic-object-exchange"]["requirements"]
    assert "HLA2025-FI-SVC-062" in slices["2025-basic-object-exchange"]["requirements"]
    assert "discoverObjectInstance delivery" in slices["2025-basic-object-exchange"]["supported_scope"]
    assert "interaction publication gating" in slices["2025-basic-object-exchange"]["supported_scope"]
    assert slices["2025-ddm-default-attribute-policy"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-007" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-076" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-124" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-126" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-136" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-157" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-128" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-129" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-131" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-133" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-137" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-159" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "HLA2025-FI-SVC-164" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "createRegion/commitRegionModifications/deleteRegion/setRangeBounds" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert "registerObjectInstanceWithRegions/subscribeObjectClassAttributesWithRegions" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert "unassociateRegionsForUpdates/requestAttributeValueUpdateWithRegions" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert "subscribeInteractionClassWithRegions/unsubscribeInteractionClassWithRegions/sendInteractionWithRegions" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert "Attribute scope advisory callbacks" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert "in-scope and out-of-scope transitions" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert slices["2025-omt-schema-constraint-validation"]["status"] == "implemented-slice"
    assert "HLA2025-OMT-CV-001" in slices["2025-omt-schema-constraint-validation"]["requirements"]
    assert "HLA2025-OMT-CV-029" in slices["2025-omt-schema-constraint-validation"]["requirements"]
    assert "lxml-backed IEEE1516-OMT-2025 XML Schema validation path" in slices["2025-omt-schema-constraint-validation"]["supported_scope"]
    assert "strict domain checks" in slices["2025-omt-schema-constraint-validation"]["supported_scope"]
    assert "union-backed fields" in slices["2025-omt-schema-constraint-validation"]["supported_scope"]
    assert slices["2025-object-management-support-callbacks"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-065" in slices["2025-object-management-support-callbacks"]["requirements"]
    assert "HLA2025-FI-SVC-071" in slices["2025-object-management-support-callbacks"]["requirements"]
    assert "HLA2025-FI-SVC-072" in slices["2025-object-management-support-callbacks"]["requirements"]
    assert "HLA2025-FI-SVC-073" in slices["2025-object-management-support-callbacks"]["requirements"]
    assert "HLA2025-FI-SVC-074" in slices["2025-object-management-support-callbacks"]["requirements"]
    assert "HLA2025-FI-SVC-082" in slices["2025-object-management-support-callbacks"]["requirements"]
    assert "deleteObjectInstance/removeObjectInstance callbacks" in slices["2025-object-management-support-callbacks"]["supported_scope"]
    assert "requestAttributeValueUpdate callbacks" in slices["2025-object-management-support-callbacks"]["supported_scope"]
    assert "transportation type change/query callbacks" in slices["2025-object-management-support-callbacks"]["supported_scope"]
    assert "attributesInScope and attributesOutOfScope transitions" in slices["2025-object-management-support-callbacks"]["supported_scope"]
    assert slices["2025-single-name-reservation-services"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-051" in slices["2025-single-name-reservation-services"]["requirements"]
    assert "HLA2025-FI-SVC-052" in slices["2025-single-name-reservation-services"]["requirements"]
    assert "HLA2025-FI-SVC-053" in slices["2025-single-name-reservation-services"]["requirements"]
    assert "single-name reservation success and failure callbacks" in slices["2025-single-name-reservation-services"]["supported_scope"]
    assert "ObjectInstanceNameNotReserved on invalid single-name release" in slices["2025-single-name-reservation-services"]["supported_scope"]
    assert slices["2025-multi-name-reservation-services"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-054" in slices["2025-multi-name-reservation-services"]["requirements"]
    assert "HLA2025-FI-SVC-055" in slices["2025-multi-name-reservation-services"]["requirements"]
    assert "HLA2025-FI-SVC-056" in slices["2025-multi-name-reservation-services"]["requirements"]
    assert "set-wide success/failure callbacks" in slices["2025-multi-name-reservation-services"]["supported_scope"]
    assert "reservation preservation through save/restore snapshots" in slices["2025-multi-name-reservation-services"]["supported_scope"]
    assert slices["2025-connection-lifecycle-services"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-002" in slices["2025-connection-lifecycle-services"]["requirements"]
    assert "HLA2025-FI-SVC-003" in slices["2025-connection-lifecycle-services"]["requirements"]
    assert "orderly disconnect state teardown" in slices["2025-connection-lifecycle-services"]["supported_scope"]
    assert "connectionLost callback" in slices["2025-connection-lifecycle-services"]["supported_scope"]
    assert slices["2025-federation-lifecycle-services"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-001" in slices["2025-federation-lifecycle-services"]["requirements"]
    assert "HLA2025-FI-SVC-006" in slices["2025-federation-lifecycle-services"]["requirements"]
    assert "HLA2025-FI-SVC-005" in slices["2025-federation-lifecycle-services"]["requirements"]
    assert "HLA2025-FI-SVC-017" in slices["2025-federation-lifecycle-services"]["requirements"]
    assert "HLA2025-FI-SVC-012" in slices["2025-federation-lifecycle-services"]["requirements"]
    assert "creates federation executions with resolved FOM modules" in slices["2025-federation-lifecycle-services"]["supported_scope"]
    assert "lists federation executions" in slices["2025-federation-lifecycle-services"]["supported_scope"]
    assert "registers synchronization points" in slices["2025-federation-lifecycle-services"]["supported_scope"]
    assert "reports federation execution members" in slices["2025-federation-lifecycle-services"]["supported_scope"]
    assert "federateResigned callback" in slices["2025-federation-lifecycle-services"]["supported_scope"]
    assert slices["2025-basic-declaration-services"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-047" in slices["2025-basic-declaration-services"]["requirements"]
    assert "HLA2025-FI-SVC-050" in slices["2025-basic-declaration-services"]["requirements"]
    assert "HLA2025-FI-SVC-035" in slices["2025-basic-declaration-services"]["requirements"]
    assert "HLA2025-FI-SVC-044" in slices["2025-basic-declaration-services"]["requirements"]
    assert "publish and unpublish for object class attributes and interaction classes" in slices["2025-basic-declaration-services"]["supported_scope"]
    assert "startRegistrationForObjectClass" in slices["2025-basic-declaration-services"]["supported_scope"]
    assert "turnInteractionsOff" in slices["2025-basic-declaration-services"]["supported_scope"]
    assert "unsubscribe state stops subsequent reflectAttributeValues and receiveInteraction callbacks" in slices["2025-basic-declaration-services"]["supported_scope"]
    assert slices["2025-support-handle-normalization-and-switches"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-162" in slices["2025-support-handle-normalization-and-switches"]["requirements"]
    assert "HLA2025-FI-SVC-165" in slices["2025-support-handle-normalization-and-switches"]["requirements"]
    assert "HLA2025-FI-SVC-166" in slices["2025-support-handle-normalization-and-switches"]["requirements"]
    assert "HLA2025-FI-SVC-167" in slices["2025-support-handle-normalization-and-switches"]["requirements"]
    assert "HLA2025-FI-SVC-181" in slices["2025-support-handle-normalization-and-switches"]["requirements"]
    assert "HLA2025-FI-SVC-192" in slices["2025-support-handle-normalization-and-switches"]["requirements"]
    assert "normalizes object class, interaction class, object instance, and federate handles" in slices["2025-support-handle-normalization-and-switches"]["supported_scope"]
    assert "returns dimension handle sets for joined regions" in slices["2025-support-handle-normalization-and-switches"]["supported_scope"]
    assert "automatic resign directive" in slices["2025-support-handle-normalization-and-switches"]["supported_scope"]
    assert "service reporting, exception reporting" in slices["2025-support-handle-normalization-and-switches"]["supported_scope"]
    assert "allow-relaxed-DDM, and non-regulated-grant controls" in slices["2025-support-handle-normalization-and-switches"]["supported_scope"]
    assert slices["2025-callback-control-services"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-193" in slices["2025-callback-control-services"]["requirements"]
    assert "HLA2025-FI-SVC-194" in slices["2025-callback-control-services"]["requirements"]
    assert "HLA2025-FI-SVC-195" in slices["2025-callback-control-services"]["requirements"]
    assert "HLA2025-FI-SVC-196" in slices["2025-callback-control-services"]["requirements"]
    assert "disableCallbacks queues local and target federate callbacks" in slices["2025-callback-control-services"]["supported_scope"]
    assert "evokeMultipleCallbacks drains the pending callback queue" in slices["2025-callback-control-services"]["supported_scope"]
    assert slices["2025-ownership-basic-tag-callbacks"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-083" in slices["2025-ownership-basic-tag-callbacks"]["requirements"]
    assert "HLA2025-FI-SVC-084" in slices["2025-ownership-basic-tag-callbacks"]["requirements"]
    assert "HLA2025-FI-SVC-087" in slices["2025-ownership-basic-tag-callbacks"]["requirements"]
    assert "HLA2025-FI-SVC-093" in slices["2025-ownership-basic-tag-callbacks"]["requirements"]
    assert "HLA2025-FI-SVC-100" in slices["2025-ownership-basic-tag-callbacks"]["requirements"]
    assert "HLA2025-MOD-005" in slices["2025-ownership-basic-tag-callbacks"]["requirements"]
    assert "negotiated ownership offers" in slices["2025-ownership-basic-tag-callbacks"]["supported_scope"]
    assert "requestAttributeOwnershipAssumption" in slices["2025-ownership-basic-tag-callbacks"]["supported_scope"]
    assert "confirmAttributeOwnershipAcquisitionCancellation" in slices["2025-ownership-basic-tag-callbacks"]["supported_scope"]
    assert "resign-time ownership policies" in slices["2025-ownership-basic-tag-callbacks"]["supported_scope"]
    assert "divest/transfer owned attributes" in slices["2025-ownership-basic-tag-callbacks"]["supported_scope"]
    assert slices["2025-support-query-lookups"]["status"] == "implemented-slice"
    assert "HLA2025-FI-SVC-138" in slices["2025-support-query-lookups"]["requirements"]
    assert "HLA2025-FI-SVC-144" in slices["2025-support-query-lookups"]["requirements"]
    assert "HLA2025-FI-SVC-147" in slices["2025-support-query-lookups"]["requirements"]
    assert "HLA2025-FI-SVC-158" in slices["2025-support-query-lookups"]["requirements"]
    assert "HLA2025-FI-SVC-163" in slices["2025-support-query-lookups"]["requirements"]
    assert "HLA2025-FI-SVC-140" in slices["2025-support-query-lookups"]["requirements"]
    assert "HLA2025-FI-SVC-156" in slices["2025-support-query-lookups"]["requirements"]
    assert "federate, object-class, known-object-class, object-instance" in slices["2025-support-query-lookups"]["supported_scope"]
    assert "order, update-rate, transportation, available-dimension, and range-bounds" in slices["2025-support-query-lookups"]["supported_scope"]
    assert slices["2025-mom-service-report-serialization"]["status"] == "implemented-slice"
    assert "HLA2025-NEW-007" in slices["2025-mom-service-report-serialization"]["requirements"]
    assert "service-report callback delivery" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert (
        "Python 2025 shim also routes MIM data, FOM module data, synchronization point MOM request/report interactions, "
        "and service/exception reporting MOM adjust interactions plus exposed HLAsetSwitches, HLAsetTiming, and "
        "HLAmodifyAttributeState adjust interactions"
        in slices["2025-mom-service-report-serialization"]["supported_scope"]
    )
    assert "declaration-management MOM service actions" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert (
        "federate-level FOM module data, publication/subscription, and object-instance information MOM reports"
        in slices["2025-mom-service-report-serialization"]["supported_scope"]
    )
    assert "federation-management MOM service actions" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert "supported time-management MOM service actions" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert "disable, asynchronous-delivery, TARA, NMR, and NMRA paths" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert "supported object-management and ownership MOM service actions" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert "order-type-change" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert "activity/count MOM reports for updates, reflections, interactions" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert "HLAreportMOMexception interactions" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert "reports standard MIM data for HLArequestMIMdata" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert "FOM module data for HLArequestFOMmoduleData" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert "object publication/subscription state" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert "object instance information for HLArequestObjectInstanceInformation" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert "object-instance counts for deletable/updated/reflected objects" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert "activity counts for updates, reflections, interactions sent" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert "synchronization point/status reports" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert "not full MOM manager interaction routing" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert slices["2025-wsdl-legacy-only"]["status"] == "legacy-only"
    assert "HLA2025-RET-003" in slices["2025-wsdl-legacy-only"]["requirements"]
    assert slices["2025-verification-anchor-matrix"]["status"] == "implemented-slice"
    assert "HLA2025-VER-001" in slices["2025-verification-anchor-matrix"]["requirements"]

    matrix_rows = {row["id"]: row for row in snapshot["verification_matrix"]["rows"]}
    assert matrix_rows["HLA2025-NEW-001"]["explicit_disposition_anchor"] is False
    assert "2025-directed-interaction-boundary" in matrix_rows["HLA2025-NEW-001"]["evidence_slices"]
    assert matrix_rows["HLA2025-RET-003"]["explicit_disposition_anchor"] is True
    assert "2025-verification-anchor-matrix" in matrix_rows["HLA2025-VER-001"]["evidence_slices"]

    markdown = "\n".join(build_spec2025_finish_line_markdown(ROOT))
    assert "HLA conformance" in markdown
    assert "Highest-Priority Open Work" in markdown
    assert "2025-wsdl-legacy-only" in markdown
    assert "Do not promote `partial` rows" in markdown


@pytest.mark.requirements("HLA2025-TRACE-001")
def test_2025_finish_line_writer_emits_reviewable_json_and_markdown(tmp_path: Path) -> None:
    paths = write_spec2025_finish_line(tmp_path, ROOT)

    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert payload["executable_test_backlog"]["row_count"] == 1117
    assert payload["requirement_depth_expansion"]["row_count"] == 691
    assert payload["requirement_coverage_disposition"]["covered_row_count"] == 564
    assert payload["verification_matrix"]["high_priority_missing_anchor_count"] == 0
    assert payload["route_parity_matrix"]["by_status"]["missing"] == 0

    markdown = paths["markdown"].read_text(encoding="utf-8")
    assert markdown.startswith("# IEEE 1516-2025 Requirements Finish Line")
    assert "Imported requirement-depth rows: 691" in markdown
    assert "Imported provisional disposition rows: 691" in markdown
    assert "Implemented Evidence Slices" in markdown
    matrix = paths["verification_matrix"].read_text(encoding="utf-8")
    assert "HLA2025-VER-001" in matrix
    assert "2025-verification-anchor-matrix" in matrix
    route_matrix = paths["route_parity_matrix"].read_text(encoding="utf-8")
    assert "object_exchange,java-standard-2025-jpype,parity-covered,scenario-parity" in route_matrix
    assert "federation_lifecycle,java-standard-2025-jpype,parity-covered,scenario-parity" in route_matrix
    assert "federation_lifecycle,cpp-standard-2025-grpc,parity-covered,scenario-parity" in route_matrix
