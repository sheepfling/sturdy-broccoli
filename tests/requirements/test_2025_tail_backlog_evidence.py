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
HARMONIZATION_REVIEW_QUEUE = ROOT / "requirements/2025/harmonization/hla_2025_review_queue.csv"
HARMONIZATION_DISPOSITION_CSV = ROOT / "requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv"
HARMONIZATION_DISPOSITION_JSON = ROOT / "requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.json"
FEDPRO_PROTO_DIR = ROOT / "packages/hla-transport-grpc/proto/rti1516_2025/fedpro"
FEDPRO_2025_TEST = ROOT / "tests/transport/test_grpc_transport_2025.py"
WSDL_2010 = ROOT / "CERTI/xml/ieee1516-2010/1516_1-2010/hla1516e.wsdl"


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(handle)]


def _json_rows(path: Path) -> list[dict[str, object]]:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.requirements("HLA2025-BLG-001",
    "HLA2025-REQ-001",
    "HLA2025-OMT-SU-001",
    "HLA2025-OMT-SU-002",
    "HLA2025-OMT-SU-003",
    "HLA2025-OMT-SU-004",
    "HLA2025-OMT-SU-005",
    "HLA2025-OMT-SU-006",
    "HLA2025-OMT-SU-007",
    "HLA2025-OMT-SU-008",
    "HLA2025-OMT-SU-009",
    "HLA2025-OMT-SU-010",
    "HLA2025-OMT-SU-011",
    "HLA2025-OMT-SU-012",
    "HLA2025-OMT-SU-013",
    "HLA2025-OMT-SU-014",
    "HLA2025-OMT-SU-015",
    "HLA2025-OMT-SU-016",
    "HLA2025-OMT-SU-017",
    "HLA2025-OMT-SU-018",
    "HLA2025-OMT-SU-019",
    "HLA2025-OMT-SU-020",
    "HLA2025-OMT-SU-021",
    "HLA2025-OMT-SU-022",
    "HLA2025-OMT-SU-023",
    "HLA2025-OMT-SU-024",
    "HLA2025-OMT-SU-025",
    "HLA2025-OMT-SU-026",
    "HLA2025-OMT-SU-027",
    "HLA2025-OMT-SU-028",
    "HLA2025-OMT-SU-029",
    "HLA2025-OMT-SU-030",
    "HLA2025-OMT-SU-031",
    "HLA2025-OMT-SU-032",
    "HLA2025-OMT-SU-033",
    "HLA2025-OMT-SU-034",
    "HLA2025-OMT-SU-035",
    "HLA2025-OMT-SU-036",
    "HLA2025-OMT-SU-037",
    "HLA2025-OMT-SU-038",
    "HLA2025-OMT-SU-039",
    "HLA2025-OMT-SU-040",
    "HLA2025-OMT-SU-041",
    "HLA2025-OMT-SU-042",
    "HLA2025-OMT-SU-043",
    "HLA2025-OMT-SU-044",
    "HLA2025-OMT-SU-045",
    "HLA2025-OMT-SU-046",
    "HLA2025-OMT-SU-047",
    "HLA2025-OMT-SU-048",
    "HLA2025-OMT-SU-049",
    "HLA2025-OMT-SU-050",
    "HLA2025-OMT-SU-051",
    "HLA2025-OMT-SU-052",
    "HLA2025-OMT-SU-053",
    "HLA2025-OMT-SU-054",
    "HLA2025-OMT-SU-055",
    "HLA2025-OMT-SU-056",
    "HLA2025-OMT-SU-057",
    "HLA2025-OMT-SU-058",
    "HLA2025-OMT-SU-059",
    "HLA2025-OMT-SU-060",
    "HLA2025-OMT-SU-061",
    "HLA2025-OMT-SU-062",
    "HLA2025-OMT-SU-063",
    "HLA2025-OMT-SU-064",
    "HLA2025-OMT-SU-065",
    "HLA2025-OMT-SU-066",
    "HLA2025-OMT-SU-067",
    "HLA2025-OMT-SU-068",
    "HLA2025-OMT-SU-069",
    "HLA2025-OMT-SU-070",
    "HLA2025-OMT-SU-071",
    "HLA2025-OMT-SU-072",
    "HLA2025-OMT-SU-073",
    "HLA2025-OMT-SU-074",
    "HLA2025-OMT-SU-075",
    "HLA2025-OMT-SU-076",
    "HLA2025-OMT-SU-077",
    "HLA2025-OMT-SU-078",
    "HLA2025-OMT-SU-079",
    "HLA2025-OMT-SU-080",
    "HLA2025-OMT-SU-081",
    "HLA2025-OMT-SU-082",
    "HLA2025-OMT-SU-083",
    "HLA2025-OMT-SU-084",
    "HLA2025-OMT-SU-085",
    "HLA2025-OMT-SU-086",
    "HLA2025-OMT-SU-087",
    "HLA2025-OMT-SU-088",
    "HLA2025-OMT-SU-089",
    "HLA2025-OMT-SU-090",
    "HLA2025-OMT-SU-091",
    "HLA2025-OMT-SU-092",
    "HLA2025-OMT-SU-093",
    "HLA2025-OMT-SU-094",
    "HLA2025-OMT-SU-095",
    "HLA2025-OMT-SU-096",
    "HLA2025-OMT-SU-097",
    "HLA2025-OMT-SU-098",
    "HLA2025-OMT-SU-099",
    "HLA2025-OMT-SU-100",
    "HLA2025-OMT-SU-101",
    "HLA2025-OMT-SU-102",
    "HLA2025-OMT-SU-103",
    "HLA2025-OMT-SU-104",
    "HLA2025-OMT-SU-105",
    "HLA2025-OMT-SU-106",
    "HLA2025-OMT-SU-107",
    "HLA2025-OMT-SU-108",
    "HLA2025-OMT-SU-109",
    "HLA2025-OMT-SU-110",
    "HLA2025-OMT-SU-111",
    "HLA2025-OMT-SU-112",
    "HLA2025-OMT-SU-113",
    "HLA2025-OMT-SU-114",
    "HLA2025-OMT-SU-115",
    "HLA2025-OMT-SU-116",
    "HLA2025-OMT-SU-117",
    "HLA2025-OMT-SU-118",
    "HLA2025-OMT-SU-119",
    "HLA2025-OMT-SU-120",
    "HLA2025-OMT-SU-121",
    "HLA2025-OMT-SU-122",
    "HLA2025-OMT-SU-123",
    "HLA2025-OMT-SU-124",
    "HLA2025-OMT-SU-125",
    "HLA2025-OMT-SU-126",
    "HLA2025-OMT-SU-127",
    "HLA2025-OMT-SU-128",
    "HLA2025-OMT-SU-129",
    "HLA2025-OMT-SU-130",
    "HLA2025-OMT-SU-131",
    "HLA2025-OMT-SU-132",
    "HLA2025-OMT-SU-133",
    "HLA2025-OMT-SU-134",
    "HLA2025-OMT-SU-135",
    "HLA2025-OMT-SU-136",
    "HLA2025-OMT-SU-137",
    "HLA2025-OMT-SU-138",
    "HLA2025-OMT-SU-139",
    "HLA2025-OMT-SU-140",
    "HLA2025-OMT-SU-141",
    "HLA2025-OMT-SU-142",
    "HLA2025-OMT-SU-143",
    "HLA2025-OMT-SU-144",
    "HLA2025-OMT-SU-145",
    "HLA2025-OMT-SU-146",
    "HLA2025-OMT-SU-147",
    "HLA2025-OMT-SU-148",
    "HLA2025-OMT-SU-149",
    "HLA2025-OMT-SU-150",
    "HLA2025-OMT-SU-151",
    "HLA2025-OMT-SU-152",
    "HLA2025-OMT-SU-153",
    "HLA2025-OMT-SU-154",
    "HLA2025-OMT-SU-155",
    "HLA2025-OMT-SU-156",
    "HLA2025-OMT-SU-157",
    "HLA2025-OMT-SU-158",
    "HLA2025-OMT-SU-159",
    "HLA2025-OMT-SU-160",
    "HLA2025-OMT-SU-161",
    "HLA2025-OMT-SU-162",
    "HLA2025-OMT-SU-163",
    "HLA2025-OMT-SU-164",
    "HLA2025-OMT-SU-165",
    "HLA2025-OMT-SU-166",
    "HLA2025-OMT-SU-167",
    "HLA2025-OMT-SU-168",
    "HLA2025-OMT-SU-169",
    "HLA2025-OMT-SU-170",
    "HLA2025-OMT-SU-171",
    "HLA2025-OMT-SU-172",
    "HLA2025-OMT-SU-173",
    "HLA2025-OMT-SU-174",
    "HLA2025-OMT-SU-175",
    "HLA2025-OMT-SU-176",
    "HLA2025-OMT-SU-177",
    "HLA2025-OMT-SU-178",
    "HLA2025-OMT-SU-179",
    "HLA2025-OMT-SU-180",
    "HLA2025-OMT-SU-181",
    "HLA2025-OMT-SU-182",
    "HLA2025-OMT-SU-183",
    "HLA2025-OMT-SU-184",
    "HLA2025-OMT-SU-185",
    "HLA2025-OMT-SU-186",
    "HLA2025-OMT-SU-187",
    "HLA2025-OMT-SU-188",
    "HLA2025-OMT-SU-189",
    "HLA2025-OMT-SU-190",
    "HLA2025-OMT-SU-191",
    "HLA2025-OMT-SU-192",
    "HLA2025-OMT-SU-193",
    "HLA2025-OMT-SU-194",
    "HLA2025-OMT-SU-195",
    "HLA2025-OMT-SU-196"
)
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


def test_2025_standard_route_artifact_reports_record_bounded_scenario_parity() -> None:
    java_report = json.loads((ROOT / "docs/evidence/shim_routes/java-standard-2025.json").read_text(encoding="utf-8"))
    cpp_report = json.loads((ROOT / "docs/evidence/shim_routes/cpp-standard-2025.json").read_text(encoding="utf-8"))

    for report in (java_report, cpp_report):
        scenario_evidence = report["scenario_evidence"]
        scenarios = "\n".join(scenario_evidence["scenarios"])
        tests = set(scenario_evidence["tests"])

        assert scenario_evidence["status"] == "scenario-parity-green"
        assert "bounded scenario-parity evidence" in scenario_evidence["scope"]
        assert scenario_evidence["runtime_provider"] == "python2025"
        assert scenario_evidence["implementation_lane"] == "hla-backend-python2025"
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
        assert row["runtime_provider"] == "python2025"
        assert row["implementation_lane"] == "hla-backend-python2025"
        assert row["counts_as_python_2025_rti"] is False
        assert row["wrapper_only"] is False

    for route, row in cpp_report["routes"].items():
        assert route.startswith("cpp-standard-2025-")
        assert row["runtime_provider"] == "python2025"
        assert row["implementation_lane"] == "hla-backend-python2025"
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


@pytest.mark.requirements("HLA2025-TRACE-001", "HLA2025-TRACE-002", "HLA2025-REQ-001")
def test_2025_harmonization_ledgers_track_refined_finish_line_slice_ids() -> None:
    stale_slice_ids = {
        "2025-logical-time",
        "2025-fedpro-transport-contract",
        "2025-mom-service-report-serialization",
        "2025-object-management-support-callbacks",
        "2025-object-advisory-and-transport-callbacks",
        "2025-ownership-basic-tag-callbacks",
        "2025-federation-lifecycle-services",
        "2025-basic-declaration-services",
        "2025-object-delete-and-update-request-callbacks",
        "2025-object-transport-reporting-callbacks",
        "2025-ownership-divestiture-and-release-flows",
        "2025-ownership-acquisition-and-notification-flows",
        "2025-support-identity-and-catalog-lookups",
        "2025-support-policy-and-dimension-lookups",
        "2025-support-switch-state-inquiries",
        "2025-support-switch-state-control",
        "2025-mom-manager-interaction-routing",
        "2025-switch-inquiry-control",
        "2025-support-handle-normalization-and-switches",
        "2025-support-query-lookups",
        "2025-time-control-and-advances",
    }

    review_rows = _csv_rows(HARMONIZATION_REVIEW_QUEUE)
    disposition_rows = _csv_rows(HARMONIZATION_DISPOSITION_CSV)
    disposition_json_rows = _json_rows(HARMONIZATION_DISPOSITION_JSON)

    for rows in (review_rows, disposition_rows, disposition_json_rows):
        assert stale_slice_ids.isdisjoint({str(row["known_seed_slice"]) for row in rows})

    review_by_id = {row["id"]: row for row in review_rows}
    disposition_by_id = {row["id"]: row for row in disposition_rows}
    disposition_json_by_id = {str(row["id"]): row for row in disposition_json_rows}

    expected_seed_by_id = {
        "HLA2025-FI-SVC-065": "2025-object-delete-remove-flows",
        "HLA2025-FI-SVC-068": "2025-object-scope-advisory-callbacks",
        "HLA2025-FI-SVC-071": "2025-object-attribute-update-request-callbacks",
        "HLA2025-FI-SVC-072": "2025-object-update-rate-advisory-callbacks",
        "HLA2025-FI-SVC-074": "2025-object-attribute-transport-callbacks",
        "HLA2025-FI-SVC-082": "2025-object-interaction-transport-callbacks",
        "HLA2025-FI-SVC-083": "2025-ownership-divestiture-confirmation-flows",
        "HLA2025-FI-SVC-092": "2025-ownership-release-and-if-wanted-flows",
        "HLA2025-FI-SVC-089": "2025-ownership-acquisition-assumption-flows",
        "HLA2025-FI-SVC-090": "2025-ownership-acquisition-availability-cancellation-flows",
        "HLA2025-FI-SVC-098": "2025-ownership-query-and-resign-policies",
        "HLA2025-FI-SVC-035": "2025-declaration-publication-services",
        "HLA2025-FI-SVC-041": "2025-declaration-subscription-services",
        "HLA2025-FI-SVC-047": "2025-declaration-relevance-advisory-callbacks",
        "HLA2025-FI-SVC-001": "2025-connect-and-federation-catalog-services",
        "HLA2025-FI-SVC-010": "2025-federate-membership-and-resign-services",
        "HLA2025-FI-SVC-013": "2025-synchronization-point-services",
        "HLA2025-FI-SVC-138": "2025-support-federate-and-object-identity-lookups",
        "HLA2025-FI-SVC-145": "2025-support-attribute-interaction-catalog-lookups",
        "HLA2025-FI-SVC-162": "2025-support-handle-normalization-and-region-introspection",
        "HLA2025-FI-SVC-170": "2025-support-advisory-and-reporting-state-inquiries",
        "HLA2025-FI-SVC-171": "2025-support-advisory-and-reporting-state-controls",
        "HLA2025-FI-SVC-180": "2025-support-runtime-policy-state-inquiries",
        "HLA2025-FI-SVC-181": "2025-support-runtime-policy-state-controls",
        "HLA2025-FI-SVC-147": "2025-support-policy-update-and-transport-lookups",
        "HLA2025-FI-SVC-163": "2025-support-interaction-dimension-and-range-lookups",
        "HLA2025-FI-SVC-101": "2025-time-mode-enable-disable",
        "HLA2025-FI-SVC-116": "2025-time-query-and-lookahead-control",
        "HLA2025-FI-SVC-123": "2025-time-queries-retraction-and-order",
        "HLA2025-FI-SVC-124": "2025-time-queries-retraction-and-order",
    }

    for requirement_id, expected_seed in expected_seed_by_id.items():
        assert review_by_id[requirement_id]["known_seed_slice"] == expected_seed
        assert expected_seed in review_by_id[requirement_id]["disposition_rationale"]
        assert disposition_by_id[requirement_id]["known_seed_slice"] == expected_seed
        assert expected_seed in disposition_by_id[requirement_id]["disposition_rationale"]
        assert disposition_json_by_id[requirement_id]["known_seed_slice"] == expected_seed
        assert expected_seed in str(disposition_json_by_id[requirement_id]["disposition_rationale"])
