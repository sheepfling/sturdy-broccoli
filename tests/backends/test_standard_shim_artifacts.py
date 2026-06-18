from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
JAVA_2025_BUILD = ROOT / "java_shims/hla-rti1516-2025-standard-shim/tools/build_standard_shim.py"
CPP_BUILD = ROOT / "cpp_shims/build_standard_shim.py"
JAVA_2025_JAR = ROOT / "build/shim_routes/java-standard-2025/java-rti1516-2025-standard-shim.jar"
CPP_2010_LIB = ROOT / "build/shim_routes/cpp-standard-2010/librti1516e_standard_cpp_shim.a"
CPP_2025_LIB = ROOT / "build/shim_routes/cpp-standard-2025/librti1516_2025_standard_cpp_shim.a"


def _load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _usable_java_2025_builder() -> bool:
    module = _load_module(JAVA_2025_BUILD, "shim_routes_build_java_2025_standard_shim")
    try:
        module._java_tool("javac")
        module._java_tool("jar")
    except SystemExit:
        return False
    return True


def _usable_cpp_builder() -> bool:
    try:
        subprocess.run(["c++", "--version"], capture_output=True, check=False, text=True)
        subprocess.run(["ar", "--version"], capture_output=True, check=False, text=True)
    except OSError:
        return False
    return True


def test_java_standard_2025_build_tool_reads_official_api_surface() -> None:
    module = _load_module(JAVA_2025_BUILD, "shim_routes_build_java_2025_standard_shim_read")
    with module.zipfile.ZipFile(module.API_ZIP) as outer:
        nested = outer.read(module.NESTED_API_ZIP)
    with module.zipfile.ZipFile(module.io.BytesIO(nested)) as inner:
        text = inner.read(f"{module.API_PREFIX}/java/hla/rti1516_2025/RTIambassador.java").decode("utf-8")
    methods = module._parse_methods(text)
    names = {method.name for method in methods}

    assert len(methods) > 100
    assert {"connect", "joinFederationExecution", "timeAdvanceRequest", "getHLAversion"} <= names
    assert "saveFederation" not in module.IMPLEMENTED


@pytest.mark.skipif(not _usable_java_2025_builder(), reason="Java 2025 standard shim build requires a usable JDK javac and jar")
def test_java_standard_2025_shim_jar_builds_against_official_api() -> None:
    subprocess.run([sys.executable, str(JAVA_2025_BUILD)], cwd=ROOT, check=True)
    assert JAVA_2025_JAR.exists()


@pytest.mark.skipif(not _usable_cpp_builder(), reason="C++ standard shim build requires usable c++ and ar tools")
@pytest.mark.parametrize("edition, artifact", [("2010", CPP_2010_LIB), ("2025", CPP_2025_LIB)])
def test_cpp_standard_shim_builds_against_official_headers(edition: str, artifact: Path) -> None:
    subprocess.run([sys.executable, str(CPP_BUILD), edition], cwd=ROOT, check=True)
    assert artifact.exists()


@pytest.mark.parametrize(
    "backend_name, spec_name",
    [
        ("java-standard-2025-jpype", "2025"),
        ("java-standard-2025-py4j", "2025"),
        ("cpp-standard-2010-pybind", "rti1516e"),
        ("cpp-standard-2010-grpc", "rti1516e"),
        ("cpp-standard-2025-pybind", "2025"),
        ("cpp-standard-2025-grpc", "2025"),
    ],
)
def test_standard_routes_are_artifact_gated_and_create_ambassadors_when_built(backend_name: str, spec_name: str) -> None:
    from hla.rti import create_rti_ambassador

    if "java-standard-2025" in backend_name and not JAVA_2025_JAR.exists():
        pytest.skip("Java 2025 standard shim jar has not been built")
    if "cpp-standard-2010" in backend_name and not CPP_2010_LIB.exists():
        pytest.skip("C++ 2010 standard shim artifact has not been built")
    if "cpp-standard-2025" in backend_name and not CPP_2025_LIB.exists():
        pytest.skip("C++ 2025 standard shim artifact has not been built")

    rti = create_rti_ambassador(spec=spec_name, backend=backend_name)
    assert rti.backend_info.details["standard_backed"] is True
    assert "standard" in rti.backend_info.kind


@pytest.mark.parametrize("backend_name", ["cpp-standard-2010-pybind", "cpp-standard-2010-grpc"])
def test_cpp_standard_2010_routes_pass_core_exchange_when_built(backend_name: str) -> None:
    if not CPP_2010_LIB.exists():
        pytest.skip("C++ 2010 standard shim artifact has not been built")

    from hla.verification.shim_route_evidence import run_standard_2010_exchange_trace

    evidence = run_standard_2010_exchange_trace(backend_name)
    event_names = {event["event"] for event in evidence["trace"]}
    assert evidence["status"] == "core-exchange-green"
    assert "HLA2025-FR-003" in evidence["requirements_exercised"]
    assert {"discoverObjectInstance", "reflectAttributeValues", "receiveInteraction", "timeAdvanceGrant"} <= event_names


@pytest.mark.parametrize(
    "backend_name",
    [
        "java-standard-2025-jpype",
        "java-standard-2025-py4j",
        "cpp-standard-2025-pybind",
        "cpp-standard-2025-grpc",
    ],
)
def test_standard_2025_routes_pass_lifecycle_core_when_built(backend_name: str) -> None:
    if "java-standard-2025" in backend_name and not JAVA_2025_JAR.exists():
        pytest.skip("Java 2025 standard shim jar has not been built")
    if "cpp-standard-2025" in backend_name and not CPP_2025_LIB.exists():
        pytest.skip("C++ 2025 standard shim artifact has not been built")

    from hla.verification.shim_route_evidence import run_standard_2025_lifecycle_trace

    evidence = run_standard_2025_lifecycle_trace(backend_name)
    event_names = [event["event"] for event in evidence["trace"]]
    assert evidence["status"] == "lifecycle-green"
    assert "HLA2025-FI-005" in evidence["requirements_exercised"]
    assert event_names == [
        "routeSelected",
        "getHLAversion",
        "connect",
        "createFederationExecution",
        "joinFederationExecution",
        "evokeCallback",
        "evokeMultipleCallbacks",
        "resignFederationExecution",
        "destroyFederationExecution",
        "disconnect",
    ]


@pytest.mark.parametrize(
    "backend_name",
    [
        "java-standard-2025-jpype",
        "java-standard-2025-py4j",
        "cpp-standard-2025-pybind",
        "cpp-standard-2025-grpc",
    ],
)
def test_standard_2025_routes_pass_object_exchange_when_built(backend_name: str) -> None:
    if "java-standard-2025" in backend_name and not JAVA_2025_JAR.exists():
        pytest.skip("Java 2025 standard shim jar has not been built")
    if "cpp-standard-2025" in backend_name and not CPP_2025_LIB.exists():
        pytest.skip("C++ 2025 standard shim artifact has not been built")

    from hla.verification.shim_route_evidence import run_standard_2025_object_exchange_trace

    evidence = run_standard_2025_object_exchange_trace(backend_name)
    event_names = {event["event"] for event in evidence["trace"]}
    unsubscribe = next(event for event in evidence["trace"] if event["event"] == "unsubscribeSuppression")

    assert evidence["status"] == "core-exchange-green"
    assert evidence["scenario"] == "object-exchange"
    assert "HLA2025-FR-003" in evidence["requirements_exercised"]
    assert {
        "routeSelected",
        "connect",
        "createFederationExecution",
        "joinFederationExecution",
        "resolveExchangeHandles",
        "subscribe",
        "registerObjectInstance",
        "discoverObjectInstance",
        "updateAttributeValues",
        "reflectAttributeValues",
        "sendInteraction",
        "receiveInteraction",
        "unsubscribeSuppression",
        "disconnect",
    } <= event_names
    assert unsubscribe["reflectedAfterUnsubscribe"] is False
    assert unsubscribe["interactionAfterUnsubscribe"] is False


@pytest.mark.parametrize(
    "backend_name",
    [
        "java-standard-2025-jpype",
        "java-standard-2025-py4j",
        "cpp-standard-2025-pybind",
        "cpp-standard-2025-grpc",
    ],
)
def test_standard_2025_routes_pass_time_management_when_built(backend_name: str) -> None:
    if "java-standard-2025" in backend_name and not JAVA_2025_JAR.exists():
        pytest.skip("Java 2025 standard shim jar has not been built")
    if "cpp-standard-2025" in backend_name and not CPP_2025_LIB.exists():
        pytest.skip("C++ 2025 standard shim artifact has not been built")

    from hla.verification.shim_route_evidence import run_2025_time_management_trace

    evidence = run_2025_time_management_trace(backend_name)
    event_names = {event["event"] for event in evidence["trace"]}

    assert evidence["status"] == "trace-green"
    assert evidence["scenario"] == "logical-time-runtime"
    assert "HLA2025-FI-009" in evidence["requirements_exercised"]
    assert {
        "routeSelected",
        "connect",
        "createFederationExecution",
        "joinFederationExecution",
        "getTimeFactory",
        "enableTimeRegulation",
        "enableTimeConstrained",
        "queryLookahead",
        "modifyLookahead",
        "timeAdvanceRequest",
        "flushQueueRequest",
        "queryLogicalTime",
        "queryGALT",
        "queryLITS",
        "disconnect",
    } <= event_names
    assert any(event["event"] == "queryLogicalTime" and event["value"] == "HLAfloat64Time(value=20.0)" for event in evidence["trace"])


@pytest.mark.parametrize(
    "backend_name",
    [
        "java-standard-2025-jpype",
        "java-standard-2025-py4j",
        "cpp-standard-2025-pybind",
        "cpp-standard-2025-grpc",
    ],
)
def test_standard_2025_routes_pass_ownership_when_built(backend_name: str) -> None:
    if "java-standard-2025" in backend_name and not JAVA_2025_JAR.exists():
        pytest.skip("Java 2025 standard shim jar has not been built")
    if "cpp-standard-2025" in backend_name and not CPP_2025_LIB.exists():
        pytest.skip("C++ 2025 standard shim artifact has not been built")

    from hla.verification.shim_route_evidence import run_standard_2025_ownership_trace

    evidence = run_standard_2025_ownership_trace(backend_name)
    event_names = {event["event"] for event in evidence["trace"]}

    assert evidence["status"] == "trace-green"
    assert evidence["scenario"] == "ownership-runtime"
    assert "HLA2025-FR-005" in evidence["requirements_exercised"]
    assert {
        "routeSelected",
        "connect",
        "createFederationExecution",
        "joinFederationExecution",
        "registerObjectInstance",
        "attributeOwnershipAcquisitionIfAvailable",
        "attributeOwnershipUnavailable",
        "unconditionalAttributeOwnershipDivestiture",
        "queryAttributeOwnership",
        "attributeIsNotOwned",
        "attributeOwnershipAcquisitionNotification",
        "informAttributeOwnership",
        "disconnect",
    } <= event_names
    assert any(event["event"] == "registerObjectInstance" and event["ownerInitiallyOwns"] is True for event in evidence["trace"])
    assert any(event["event"] == "unconditionalAttributeOwnershipDivestiture" and event["ownerStillOwns"] is False for event in evidence["trace"])
    assert any(event["event"] == "attributeOwnershipAcquisitionIfAvailable" and event.get("acquirerOwns") is True for event in evidence["trace"])


@pytest.mark.parametrize(
    "backend_name",
    [
        "java-standard-2025-jpype",
        "java-standard-2025-py4j",
        "cpp-standard-2025-pybind",
        "cpp-standard-2025-grpc",
    ],
)
def test_standard_2025_routes_pass_ddm_when_built(backend_name: str) -> None:
    if "java-standard-2025" in backend_name and not JAVA_2025_JAR.exists():
        pytest.skip("Java 2025 standard shim jar has not been built")
    if "cpp-standard-2025" in backend_name and not CPP_2025_LIB.exists():
        pytest.skip("C++ 2025 standard shim artifact has not been built")

    from hla.verification.shim_route_evidence import run_standard_2025_ddm_trace

    evidence = run_standard_2025_ddm_trace(backend_name)
    event_names = {event["event"] for event in evidence["trace"]}
    outside_subscription = next(event for event in evidence["trace"] if event["event"] == "subscribeObjectClassAttributesWithRegions")
    outside_update = next(event for event in evidence["trace"] if event["event"] == "outsideRegionUpdateSuppressed")
    overlapping_region = next(event for event in evidence["trace"] if event["event"] == "commitOverlappingRegion")
    reflection = next(event for event in evidence["trace"] if event["event"] == "reflectAttributeValues")

    assert evidence["status"] == "trace-green"
    assert evidence["scenario"] == "ddm-region-runtime"
    assert "HLA2025-MOD-007" in evidence["requirements_exercised"]
    assert {
        "routeSelected",
        "connect",
        "createFederationExecution",
        "joinFederationExecution",
        "publishObjectClassAttributes",
        "createAndCommitRegions",
        "subscribeObjectClassAttributesWithRegions",
        "outsideRegionUpdateSuppressed",
        "commitOverlappingRegion",
        "discoverObjectInstance",
        "insideRegionUpdate",
        "reflectAttributeValues",
        "disconnect",
    } <= event_names
    assert outside_subscription["discovered"] is False
    assert outside_update["reflected"] is False
    assert overlapping_region["discovered"] is True
    assert reflection["tag"] == "inside-region"
    assert reflection["sentRegions"]


@pytest.mark.parametrize(
    "backend_name",
    [
        "java-standard-2025-jpype",
        "java-standard-2025-py4j",
        "cpp-standard-2025-pybind",
        "cpp-standard-2025-grpc",
    ],
)
def test_standard_2025_routes_pass_support_services_when_built(backend_name: str) -> None:
    if "java-standard-2025" in backend_name and not JAVA_2025_JAR.exists():
        pytest.skip("Java 2025 standard shim jar has not been built")
    if "cpp-standard-2025" in backend_name and not CPP_2025_LIB.exists():
        pytest.skip("C++ 2025 standard shim artifact has not been built")

    from hla.verification.shim_route_evidence import run_standard_2025_support_services_trace

    evidence = run_standard_2025_support_services_trace(backend_name)
    event_names = {event["event"] for event in evidence["trace"]}
    lookups = next(event for event in evidence["trace"] if event["event"] == "supportLookupRoundTrip")
    switches = next(event for event in evidence["trace"] if event["event"] == "supportSwitchRoundTrip")

    assert evidence["status"] == "trace-green"
    assert evidence["scenario"] == "support-services-runtime"
    assert "HLA2025-FI-001" in evidence["requirements_exercised"]
    assert {
        "routeSelected",
        "connect",
        "createFederationExecution",
        "joinFederationExecution",
        "supportLookupRoundTrip",
        "supportSwitchRoundTrip",
        "disconnect",
    } <= event_names
    assert lookups["federateName"] == "route-support"
    assert lookups["objectClassName"] == "HLAobjectRoot.RouteTarget"
    assert lookups["attributeName"] == "Position"
    assert lookups["objectInstanceName"].startswith("RouteSupportTarget-")
    assert lookups["dimensionName"] == "RoutingSpace"
    assert lookups["dimensionUpperBound"] == 1024
    assert lookups["transportationName"] == "HLAreliable"
    assert lookups["orderName"] == "HLAreceive"
    assert lookups["timeFactoryName"] == "HLAinteger64Time"
    assert switches == {
        "event": "supportSwitchRoundTrip",
        "serviceReporting": True,
        "exceptionReporting": False,
        "conveyRegionDesignatorSets": False,
    }


@pytest.mark.parametrize(
    "backend_name",
    [
        "java-standard-2025-jpype",
        "java-standard-2025-py4j",
        "cpp-standard-2025-pybind",
        "cpp-standard-2025-grpc",
    ],
)
def test_standard_2025_routes_pass_save_restore_when_built(backend_name: str) -> None:
    if "java-standard-2025" in backend_name and not JAVA_2025_JAR.exists():
        pytest.skip("Java 2025 standard shim jar has not been built")
    if "cpp-standard-2025" in backend_name and not CPP_2025_LIB.exists():
        pytest.skip("C++ 2025 standard shim artifact has not been built")

    from hla.verification.shim_route_evidence import run_standard_2025_save_restore_trace

    evidence = run_standard_2025_save_restore_trace(backend_name)
    event_names = {event["event"] for event in evidence["trace"]}
    save = next(event for event in evidence["trace"] if event["event"] == "requestFederationSave")
    saved = next(event for event in evidence["trace"] if event["event"] == "federationSaved")
    restore_failed = next(event for event in evidence["trace"] if event["event"] == "requestFederationRestoreFailed")
    restore = next(event for event in evidence["trace"] if event["event"] == "requestFederationRestore")
    restored = next(event for event in evidence["trace"] if event["event"] == "federationRestored")
    restored_update = next(event for event in evidence["trace"] if event["event"] == "restoredObjectProvidesUpdate")

    assert evidence["status"] == "trace-green"
    assert evidence["scenario"] == "save-restore-runtime"
    assert "HLA2025-FI-005" in evidence["requirements_exercised"]
    assert {
        "routeSelected",
        "connect",
        "createFederationExecution",
        "joinFederationExecution",
        "preparedState",
        "requestFederationSave",
        "queryFederationSaveStatus",
        "federationSaved",
        "mutatedAfterSave",
        "requestFederationRestoreFailed",
        "requestFederationRestore",
        "queryFederationRestoreStatus",
        "federationRestored",
        "restoredObjectProvidesUpdate",
        "disconnect",
    } <= event_names
    assert save["leaderInitiated"] is True
    assert save["wingInitiated"] is True
    assert saved["leaderSaved"] is True
    assert saved["wingSaved"] is True
    assert restore_failed["label"] == "MISSING-SAVE"
    assert restore["leaderSucceeded"] is True
    assert restore["leaderBegun"] is True
    assert restore["wingInitiated"] is True
    assert restored["leaderRestored"] is True
    assert restored["wingRestored"] is True
    assert restored["restoredLogicalTime"]["value"] == 5
    assert restored["restoredObjectName"].startswith("RouteSavedTarget-")
    assert restored_update["callback"][0] == "provideAttributeValueUpdate"


@pytest.mark.parametrize(
    "backend_name",
    [
        "java-standard-2025-jpype",
        "java-standard-2025-py4j",
        "cpp-standard-2025-pybind",
        "cpp-standard-2025-grpc",
    ],
)
def test_standard_2025_routes_pass_runtime_capability_when_built(backend_name: str) -> None:
    if "java-standard-2025" in backend_name and not JAVA_2025_JAR.exists():
        pytest.skip("Java 2025 standard shim jar has not been built")
    if "cpp-standard-2025" in backend_name and not CPP_2025_LIB.exists():
        pytest.skip("C++ 2025 standard shim artifact has not been built")

    from hla.verification.shim_route_evidence import run_standard_2025_runtime_capability_trace

    evidence = run_standard_2025_runtime_capability_trace(backend_name)
    event_names = {event["event"] for event in evidence["trace"]}

    assert evidence["status"] == "trace-green"
    assert evidence["scenario"] == "runtime-capability"
    if "java-standard-2025" in backend_name:
        assert "HLA2025-BND-001" in evidence["requirements_exercised"]
    if "cpp-standard-2025" in backend_name:
        assert "HLA2025-BND-002" in evidence["requirements_exercised"]
    assert {
        "resolveFomHandles",
        "changeDefaultAttributeTransportationType",
        "changeDefaultAttributeOrderType",
        "registerObjectInstance",
        "unconditionalAttributeOwnershipDivestiture",
        "attributeOwnershipAcquisitionIfAvailable",
        "attributeIsNotOwned",
        "attributeOwnershipAcquisitionNotification",
        "getTimeFactory",
        "timeAdvanceRequest",
        "timeAdvanceGrant",
        "serializeMOMServiceReport",
        "disconnect",
    } <= event_names
