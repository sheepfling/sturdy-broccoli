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


def test_2025_standard_route_artifact_reports_record_bounded_scenario_parity() -> None:
    java_report = json.loads((ROOT / "docs/evidence/shim_routes/java-standard-2025.json").read_text(encoding="utf-8"))
    cpp_report = json.loads((ROOT / "docs/evidence/shim_routes/cpp-standard-2025.json").read_text(encoding="utf-8"))

    for report in (java_report, cpp_report):
        scenario_evidence = report["scenario_evidence"]
        scenarios = "\n".join(scenario_evidence["scenarios"])
        tests = set(scenario_evidence["tests"])

        assert scenario_evidence["status"] == "scenario-parity-green"
        assert "bounded scenario-parity evidence" in scenario_evidence["scope"]
        assert scenario_evidence["runtime_provider"] == "python1516_2025"
        assert scenario_evidence["implementation_lane"] == "hla-backend-python1516-2025"
        assert scenario_evidence["counts_as_python_2025_rti"] is False
        assert scenario_evidence["wrapper_only"] is False
        assert "object exchange" in scenarios
        assert "logical time" in scenarios
        assert "ownership" in scenarios
        assert "DDM" in scenarios
        assert "support services" in scenarios
        assert "save/restore" in scenarios
        assert "MOM" in scenarios
        assert "runtime capability" in scenarios
        assert "tests/backends/test_standard_shim_artifacts.py::test_standard_2025_routes_pass_object_exchange_when_built" in tests
        assert "tests/backends/test_standard_shim_artifacts.py::test_standard_2025_routes_pass_mom_when_built" in tests
        assert "tests/backends/test_standard_shim_artifacts.py::test_standard_2025_routes_pass_runtime_capability_when_built" in tests

    for route, row in java_report["routes"].items():
        assert route.startswith("java-standard-2025-")
        assert row["runtime_provider"] == "python1516_2025"
        assert row["implementation_lane"] == "hla-backend-python1516-2025"
        assert row["counts_as_python_2025_rti"] is False
        assert row["wrapper_only"] is False

    for route, row in cpp_report["routes"].items():
        assert route.startswith("cpp-standard-2025-")
        assert row["runtime_provider"] == "python1516_2025"
        assert row["implementation_lane"] == "hla-backend-python1516-2025"
        assert row["counts_as_python_2025_rti"] is False
        assert row["wrapper_only"] is False


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
