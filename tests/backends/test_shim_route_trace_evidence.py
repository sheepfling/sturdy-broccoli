from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACE_DIR = ROOT / "docs/evidence/shim_routes/route_traces"


def _load(route: str) -> dict[str, object]:
    return json.loads((TRACE_DIR / f"{route}.json").read_text(encoding="utf-8"))


def _assert_route_selected_uses_python2025_main_lane(
    evidence: dict[str, object],
    route: str,
    *,
    standard_backed: bool | None,
    counts_as_python_2025_rti: bool,
    wrapper_only: bool | None,
) -> None:
    route_selected = evidence["trace"][0]  # type: ignore[index]

    assert route_selected["event"] == "routeSelected"
    assert route_selected["backend"] == route
    assert route_selected["spec"] == "rti1516_2025"
    assert route_selected["standardBacked"] is standard_backed
    assert route_selected["runtimeProvider"] == "python1516_2025"
    assert route_selected["implementationLane"] == "hla-backend-python2025"
    assert route_selected["countsAsPython2025Rti"] is counts_as_python_2025_rti
    assert route_selected["wrapperOnly"] is wrapper_only


def test__route_trace_summary_lists_mvp_scope() -> None:
    summary = json.loads((TRACE_DIR / "summary.json").read_text(encoding="utf-8"))

    assert summary["status"] == "trace-green"
    assert summary["scope"] == "MVP route proof, not full HLA conformance"
    assert set(summary["routes"]) == {
        "cpp-standard-2010-pybind",
        "cpp-standard-2010-grpc",
        "java-standard-2025-jpype",
        "java-standard-2025-py4j",
        "cpp-standard-2025-pybind",
        "cpp-standard-2025-grpc",
    }


def test__2010_cpp_traces_cover_exchange_callbacks() -> None:
    for route in ("cpp-standard-2010-pybind", "cpp-standard-2010-grpc"):
        evidence = _load(route)
        events = {event["event"] for event in evidence["trace"]}  # type: ignore[index]

        assert evidence["edition"] == "2010"
        assert evidence["scenario"] == "two-federate-core-exchange"
        assert evidence["status"] == "core-exchange-green"
        assert {"HLA2025-FR-003", "HLA2025-FR-004"} <= set(evidence["requirements_exercised"])
        assert {"discoverObjectInstance", "reflectAttributeValues", "receiveInteraction", "timeAdvanceGrant"} <= events


def test__2025_traces_cover_lifecycle_core() -> None:
    for route in ("java-standard-2025-jpype", "java-standard-2025-py4j", "cpp-standard-2025-pybind", "cpp-standard-2025-grpc"):
        evidence = _load(route)
        events = [event["event"] for event in evidence["trace"]]  # type: ignore[index]

        assert evidence["edition"] == "2025"
        assert evidence["scenario"] == "lifecycle-core"
        assert evidence["status"] == "lifecycle-green"
        assert {"HLA2025-FR-004", "HLA2025-FI-005", "HLA2025-FI-006"} <= set(evidence["requirements_exercised"])
        _assert_route_selected_uses_python2025_main_lane(
            evidence,
            route,
            standard_backed=True,
            counts_as_python_2025_rti=False,
            wrapper_only=False,
        )
        assert events == [
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


def test__2025_time_management_trace_exercises_selected_logical_time_runtime() -> None:
    from hla.verification.shim_route_evidence import run_2025_time_management_trace

    evidence = run_2025_time_management_trace()
    events = [event["event"] for event in evidence["trace"]]

    assert evidence["edition"] == "2025"
    assert evidence["scenario"] == "logical-time-runtime"
    assert evidence["status"] == "trace-green"
    assert {"HLA2025-FR-010", "HLA2025-FI-005", "HLA2025-FI-009", "HLA2025-MOD-006"} <= set(
        evidence["requirements_exercised"]
    )
    _assert_route_selected_uses_python2025_main_lane(
        evidence,
        "python1516_2025",
        standard_backed=None,
        counts_as_python_2025_rti=True,
        wrapper_only=None,
    )
    assert events == [
        "routeSelected",
        "connect",
        "createFederationExecution",
        "joinFederationExecution",
        "getTimeFactory",
        "enableTimeRegulation",
        "enableTimeConstrained",
        "queryLookahead",
        "modifyLookahead",
        "queryLookahead",
        "timeAdvanceRequest",
        "flushQueueRequest",
        "queryLogicalTime",
        "queryGALT",
        "queryLITS",
        "resignFederationExecution",
        "destroyFederationExecution",
        "disconnect",
    ]
