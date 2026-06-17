from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACE_DIR = ROOT / "docs/evidence/rosetta/route_traces"


def _load(route: str) -> dict[str, object]:
    return json.loads((TRACE_DIR / f"{route}.json").read_text(encoding="utf-8"))


def test_rosetta_route_trace_summary_lists_mvp_scope() -> None:
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


def test_rosetta_2010_cpp_traces_cover_exchange_callbacks() -> None:
    for route in ("cpp-standard-2010-pybind", "cpp-standard-2010-grpc"):
        evidence = _load(route)
        events = {event["event"] for event in evidence["trace"]}  # type: ignore[index]

        assert evidence["edition"] == "2010"
        assert evidence["scenario"] == "two-federate-core-exchange"
        assert evidence["status"] == "core-exchange-green"
        assert {"HLA-X-2025-FR-003", "HLA-X-2025-FR-004"} <= set(evidence["requirements_exercised"])
        assert {"discoverObjectInstance", "reflectAttributeValues", "receiveInteraction", "timeAdvanceGrant"} <= events


def test_rosetta_2025_traces_cover_lifecycle_core() -> None:
    for route in ("java-standard-2025-jpype", "java-standard-2025-py4j", "cpp-standard-2025-pybind", "cpp-standard-2025-grpc"):
        evidence = _load(route)
        events = [event["event"] for event in evidence["trace"]]  # type: ignore[index]

        assert evidence["edition"] == "2025"
        assert evidence["scenario"] == "lifecycle-core"
        assert evidence["status"] == "lifecycle-green"
        assert {"HLA-X-2025-FR-004", "HLA-X-2025-FI-005", "HLA-X-2025-FI-006"} <= set(evidence["requirements_exercised"])
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
