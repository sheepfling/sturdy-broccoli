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
    assert route_matrix["by_route"]["java-standard-2025-jpype"]["parity-covered"] == 0
    assert route_matrix["by_route"]["cpp-standard-2025-grpc"]["parity-covered"] == 0


@pytest.mark.requirements("HLA2025-REQ-002", "HLA2025-TRACE-001")
def test_2025_finish_line_snapshot_names_only_implemented_slices_with_evidence() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)
    slices = {row["id"]: row for row in snapshot["implemented_evidence_slices"]}

    assert slices["2025-auth-connect"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-001" in slices["2025-auth-connect"]["requirements"]
    assert any(path.endswith("test_rti1516_2025_encoding_auth_contexts.py") for path in slices["2025-auth-connect"]["evidence"])

    assert slices["2025-logical-time"]["status"] == "implemented-slice"
    assert "flushQueueRequest" in slices["2025-logical-time"]["supported_scope"]
    assert "queued timestamped object updates/interactions" in slices["2025-logical-time"]["supported_scope"]
    assert "message retraction before delivery" in slices["2025-logical-time"]["supported_scope"]
    assert "Cross-binding parity" in slices["2025-logical-time"]["supported_scope"]
    assert slices["2025-save-restore-lifecycle"]["status"] == "implemented-slice"
    assert "federation save/restore lifecycle callbacks" in slices["2025-save-restore-lifecycle"]["supported_scope"]
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
    assert "receiveDirectedInteraction callback delivery" in slices["2025-directed-interaction-boundary"]["supported_scope"]
    assert "Java/C++/FedPro route parity remain later behavior work" in slices["2025-directed-interaction-boundary"]["supported_scope"]
    assert slices["2025-omt-reference-value-required"]["status"] == "implemented-slice"
    assert "HLA2025-NEW-006" in slices["2025-omt-reference-value-required"]["requirements"]
    assert slices["2025-carry-forward-cleanup"]["status"] == "implemented-slice"
    assert "HLA2025-BLG-001" in slices["2025-carry-forward-cleanup"]["requirements"]
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
    assert slices["2025-ddm-default-attribute-policy"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-007" in slices["2025-ddm-default-attribute-policy"]["requirements"]
    assert "basic createRegion/setRangeBounds/subscribeObjectClassAttributesWithRegions" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert "subscribeInteractionClassWithRegions/sendInteractionWithRegions" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert "Attribute scope advisory callbacks" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert "in-scope and out-of-scope transitions" in slices["2025-ddm-default-attribute-policy"]["supported_scope"]
    assert slices["2025-object-management-support-callbacks"]["status"] == "implemented-slice"
    assert "deleteObjectInstance/removeObjectInstance callbacks" in slices["2025-object-management-support-callbacks"]["supported_scope"]
    assert "requestAttributeValueUpdate callbacks" in slices["2025-object-management-support-callbacks"]["supported_scope"]
    assert "transportation type change/query callbacks" in slices["2025-object-management-support-callbacks"]["supported_scope"]
    assert slices["2025-ownership-basic-tag-callbacks"]["status"] == "implemented-slice"
    assert "HLA2025-MOD-005" in slices["2025-ownership-basic-tag-callbacks"]["requirements"]
    assert "negotiated ownership offers" in slices["2025-ownership-basic-tag-callbacks"]["supported_scope"]
    assert "resign-time ownership policies" in slices["2025-ownership-basic-tag-callbacks"]["supported_scope"]
    assert "divest/transfer owned attributes" in slices["2025-ownership-basic-tag-callbacks"]["supported_scope"]
    assert slices["2025-mom-service-report-serialization"]["status"] == "implemented-slice"
    assert "HLA2025-NEW-007" in slices["2025-mom-service-report-serialization"]["requirements"]
    assert "service-report callback delivery" in slices["2025-mom-service-report-serialization"]["supported_scope"]
    assert (
        "Python 2025 shim also routes MIM data, FOM module data, synchronization point MOM request/report interactions, "
        "and service/exception reporting MOM adjust interactions plus exposed HLAsetSwitches adjust interactions"
        in slices["2025-mom-service-report-serialization"]["supported_scope"]
    )
    assert "declaration-management MOM service actions" in slices["2025-mom-service-report-serialization"]["supported_scope"]
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
    assert payload["verification_matrix"]["high_priority_missing_anchor_count"] == 0
    assert payload["route_parity_matrix"]["by_status"]["missing"] > 0

    markdown = paths["markdown"].read_text(encoding="utf-8")
    assert markdown.startswith("# IEEE 1516-2025 Requirements Finish Line")
    assert "Implemented Evidence Slices" in markdown
    matrix = paths["verification_matrix"].read_text(encoding="utf-8")
    assert "HLA2025-VER-001" in matrix
    assert "2025-verification-anchor-matrix" in matrix
    route_matrix = paths["route_parity_matrix"].read_text(encoding="utf-8")
    assert "object_exchange,java-standard-2025-jpype,missing,gap-record" in route_matrix
    assert "federation_lifecycle,java-standard-2025-jpype,partial,runtime-capability" in route_matrix
    assert "federation_lifecycle,cpp-standard-2025-grpc,partial,lifecycle-trace" in route_matrix
