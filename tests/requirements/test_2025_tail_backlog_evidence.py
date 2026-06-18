from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DIFFERENTIAL_SET = ROOT / "requirements/2025/differentials/HLA_1516_2025_vs_2010_Differential_Set.csv"
REUSE_DISPOSITION = ROOT / "requirements/2025/differentials/HLA_1516_2025_vs_2010_Code_Reuse_Disposition.csv"
STRICT_DOC_INVENTORY = ROOT / "requirements/2025/STRICT_DOC_INVENTORY.json"
SOURCE_TRACE = ROOT / "requirements/2025/SOURCE_TRACE.md"
FEDPRO_PROTO_DIR = ROOT / "packages/hla-transport-grpc/proto/rti1516_2025/fedpro"
FEDPRO_2025_TEST = ROOT / "tests/transport/test_grpc_transport_2025.py"
WSDL_2010 = ROOT / "CERTI/xml/ieee1516-2010/1516_1-2010/hla1516e.wsdl"


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(handle)]


@pytest.mark.requirements("HLA2025-BLG-001", "HLA2025-REQ-001")
def test_2025_renumbered_service_utilization_rows_preserve_behavior_and_update_references() -> None:
    rows = _csv_rows(DIFFERENTIAL_SET)
    renumbered = [
        row
        for row in rows
        if row["reuse_action"] == "Carry forward with reference update"
        and row["surface_type"] == "OMT serviceUtilization"
    ]

    assert len(renumbered) >= 90
    assert all(row["2010_section_or_location"] for row in renumbered)
    assert all(row["2025_section_or_location"] for row in renumbered)
    assert all(row["2010_section_or_location"] != row["2025_section_or_location"] for row in renumbered)
    assert all(row["2010_detail"] == row["2025_detail"] for row in renumbered)
    assert all("update clause number" in row["requirement_action"] for row in renumbered)

    sample = {row["item"]: row for row in renumbered}
    assert sample["announceSynchronizationPoint"]["2010_detail"] == "isCallback=true"
    assert sample["announceSynchronizationPoint"]["2025_detail"] == "isCallback=true"
    assert sample["abortFederationRestore"]["2010_detail"] == "isCallback=false"
    assert sample["abortFederationRestore"]["2025_detail"] == "isCallback=false"


@pytest.mark.requirements("HLA2025-BLG-002", "HLA2025-NEW-006", "HLA2025-REQ-001")
def test_2025_common_object_model_reuse_keeps_shared_model_and_adds_nullable_2025_metadata() -> None:
    rows = _csv_rows(REUSE_DISPOSITION)
    by_area = {row["Code area"]: row for row in rows}
    common_model = by_area["Common FOM/SOM object-model representation"]

    assert common_model["Disposition"] == "Reuse directly in common core"
    assert "Object class" in common_model["2010 code candidate"]
    assert "valueRequired" in common_model["2025 impact"]
    assert "nullable/optional fields" in common_model["Implementation recommendation"]
    assert "2025-only metadata" in common_model["Requirement/test action"]


@pytest.mark.requirements("HLA2025-MOD-009", "HLA2025-MOD-001", "HLA2025-MOD-002")
def test_2025_exception_delta_inventory_names_native_2025_exceptions_without_legacy_fdd_terms() -> None:
    inventory = json.loads(STRICT_DOC_INVENTORY.read_text(encoding="utf-8"))
    rti_groups = inventory["rti_overload_groups"]

    connect = " ".join(rti_groups["connect"])
    create = " ".join(rti_groups["createFederationExecution"])
    create_with_mim = " ".join(rti_groups["createFederationExecutionWithMIM"])
    joined = " ".join(rti_groups["joinFederationExecution"])
    native_surface = "\n".join(connect for overloads in rti_groups.values() for connect in overloads)

    assert "Unauthorized" in connect
    assert "InvalidCredentials" in connect
    assert "RtiConfiguration" in connect
    assert "Credentials" in connect
    assert "InvalidLocalSettingsDesignator" not in connect

    assert {"InvalidFOM", "InconsistentFOM", "ErrorReadingFOM", "CouldNotOpenFOM"} <= set(create.replace(",", " ").split())
    assert {"InvalidMIM", "ErrorReadingMIM", "CouldNotOpenMIM", "DesignatorIsHLAstandardMIM"} <= set(
        create_with_mim.replace(",", " ").split()
    )
    assert "CouldNotCreateLogicalTimeFactory" in joined
    assert "InconsistentFDD" not in native_surface
    assert "ErrorReadingFDD" not in native_surface
    assert "CouldNotOpenFDD" not in native_surface


@pytest.mark.requirements("HLA2025-BND-001", "HLA2025-FI-003", "HLA2025-FI-004")
def test_2025_java_binding_source_trace_is_separate_from_common_behavior_rows() -> None:
    inventory = json.loads(STRICT_DOC_INVENTORY.read_text(encoding="utf-8"))
    source_trace = SOURCE_TRACE.read_text(encoding="utf-8")
    rows = _csv_rows(DIFFERENTIAL_SET)
    java_rows = [row for row in rows if row["surface_type"].startswith("Java ")]

    assert inventory["package"] == "hla1516_2025"
    assert inventory["counts"]["java_rti_declarations"] >= 200
    assert inventory["counts"]["java_fed_declarations"] >= 60
    assert inventory["counts"]["java_encoder_declarations"] >= 80
    assert "- Java root: `java/hla/rti1516_2025`" in source_trace
    assert "`RTIambassador.java`" in source_trace
    assert "`FederateAmbassador.java`" in source_trace
    assert any(row["item"] == "connect" and "InvalidCredentials" in row["2025_detail"] for row in java_rows)
    assert any(
        row["item"] == "changeDefaultAttributeTransportationType"
        and row["requirement_action"] == "Add 2025 API/binding requirement"
        for row in java_rows
    )
    assert any(
        row["item"] == "attributeOwnershipAcquisitionIfAvailable"
        and "user-supplied tag byte[] added" in row["notes"]
        for row in java_rows
    )


@pytest.mark.requirements("HLA2025-BND-002", "HLA2025-FI-003", "HLA2025-FI-004")
def test_2025_cpp_binding_source_trace_is_separate_from_common_behavior_rows() -> None:
    source_trace = SOURCE_TRACE.read_text(encoding="utf-8")
    cpp_evidence = [
        ROOT / "docs/evidence/cpp-intake/cpp-standard-2025-2025-pybind.json",
        ROOT / "docs/evidence/cpp-intake/cpp-standard-2025-2025-grpc.json",
        ROOT / "docs/evidence/shim_routes/cpp-standard-2025.json",
    ]

    assert "- C++ root: `cpp/RTI`" in source_trace
    assert "`RTIambassador.h`" in source_trace
    assert "`FederateAmbassador.h`" in source_trace
    assert "| `connect` | §4.2 | 4 | 4 | `RTIambassador.java`, `RTIambassador.h` |" in source_trace
    assert (
        "| `changeDefaultAttributeTransportationType` | §6.27 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` |"
        in source_trace
    )
    assert (
        "| `getAvailableDimensionsForObjectClass` | §10.21 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` |"
        in source_trace
    )
    assert all(path.exists() for path in cpp_evidence)


@pytest.mark.requirements("HLA2025-BND-003", "HLA2025-RET-003", "HLA2025-FI-004")
def test_2025_fedpro_transport_replaces_wsdl_without_cross_wiring_legacy_binding() -> None:
    disposition_rows = _csv_rows(REUSE_DISPOSITION)
    by_area = {row["Code area"]: row for row in disposition_rows}
    fedpro = by_area["FedPro/protobuf binding"]
    wsdl = by_area["2010 WSDL/web-services binding"]
    transport_proto = (FEDPRO_PROTO_DIR / "HLA2025RTITransport.proto").read_text(encoding="utf-8")
    rti_proto = (FEDPRO_PROTO_DIR / "RTIambassador_2025.proto").read_text(encoding="utf-8")
    callback_proto = (FEDPRO_PROTO_DIR / "FederateAmbassador_2025.proto").read_text(encoding="utf-8")
    fedpro_test = FEDPRO_2025_TEST.read_text(encoding="utf-8")

    assert fedpro["Disposition"] == "Keep separate 2025 module"
    assert "protobuf/FedPro" in fedpro["2025 impact"]
    assert "Do not mix generated protobuf code with 2010 WSDL stubs" in fedpro["Implementation recommendation"]
    assert wsdl["Disposition"] == "Retire or legacy-only"
    assert "No WSDL binding in the uploaded 2025 package" in wsdl["2025 impact"]
    assert WSDL_2010.exists()

    assert 'package rti1516_2025.fedpro;' in transport_proto
    assert "service HLA2025FedProGateway" in transport_proto
    assert "rpc Call(CallRequest) returns (CallResponse);" in transport_proto
    assert "rpc EvokeCallback(CallbackResponse) returns (CallbackRequest);" in transport_proto
    assert "ConnectWithConfigurationAndCredentialsRequest" in rti_proto
    assert "SetServiceReportingSwitchRequest" in rti_proto
    assert "ReceiveDirectedInteraction" in callback_proto
    assert "ReportFederationExecutionMembers" in callback_proto
    assert "rti1516_2025.fedpro.CallRequest" in fedpro_test
    assert "test_2025_grpc_transport_round_trips_typed_call_oneofs" in fedpro_test


@pytest.mark.requirements("HLA2025-MOD-007", "HLA2025-NEW-004", "HLA2025-NEW-007")
def test_2025_differentials_capture_replacement_policy_and_mom_switch_surface() -> None:
    rows = _csv_rows(DIFFERENTIAL_SET)
    by_surface_item = {(row["surface_type"], row["item"]): row for row in rows}

    retired_ddm = by_surface_item[("OMT serviceUtilization", "getAvailableDimensionsForClassAttribute")]
    replacement_ddm = by_surface_item[("OMT serviceUtilization", "getAvailableDimensionsForObjectClass")]
    assert retired_ddm["reuse_action"] == "Retire or map"
    assert "Replace with getAvailableDimensionsForObjectClass" in retired_ddm["notes"]
    assert replacement_ddm["reuse_action"] == "Map existing requirement"
    assert replacement_ddm["2025_section_or_location"] == "10.21"

    default_transport = by_surface_item[("OMT serviceUtilization", "changeDefaultAttributeTransportationType")]
    default_order = by_surface_item[("OMT serviceUtilization", "changeDefaultAttributeOrderType")]
    assert default_transport["requirement_action"] == "Add 2025 requirement"
    assert default_transport["2025_section_or_location"] == "6.27"
    assert default_order["requirement_action"] == "Add 2025 requirement"
    assert default_order["2025_section_or_location"] == "8.25"

    service_reporting = by_surface_item[("MIM object attribute", "HLAobjectRoot.HLAmanager.HLAfederate.HLAserviceReporting")]
    report_file = by_surface_item[("MIM object attribute", "HLAobjectRoot.HLAmanager.HLAfederate.HLAreportServiceFile")]
    set_switches_parameter = by_surface_item[
        ("MIM interaction parameter", "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetSwitches.HLAserviceReporting")
    ]
    assert service_reporting["reuse_action"] == "Add"
    assert "valueRequired" in service_reporting["2025_detail"]
    assert report_file["reuse_action"] == "Add"
    assert set_switches_parameter["reuse_action"] == "Add"
