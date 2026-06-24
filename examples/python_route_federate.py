#!/usr/bin/env python3
"""Run one simple Python RTI demo for either supported HLA edition.

Examples:

    python examples/python_route_federate.py --edition 2010
    python examples/python_route_federate.py --edition 2025
"""
from __future__ import annotations

import argparse
import json
from typing import Any

from hla.backends.python1516e import InMemoryRTIEngine
from hla.fom.proto2025 import scenario_fom_paths
from hla.runtime.factory import create_rti_ambassador as create_2010_rti_ambassador
from hla.runtime.rti1516_2025_factory import create_rti_ambassador as create_2025_rti_ambassador
from hla.rti1516e import NullFederateAmbassador as NullFederateAmbassador2010
from hla.rti1516e.enums import CallbackModel as CallbackModel2010
from hla.rti1516e.enums import ResignAction as ResignAction2010
from hla.rti1516_2025.enums import CallbackModel as CallbackModel2025
from hla.rti1516_2025.enums import ResignAction as ResignAction2025
from hla.rti1516_2025.federate_ambassador import NullFederateAmbassador as NullFederateAmbassador2025


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    if isinstance(value, dict):
        return {str(_jsonable(key)): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "name") and hasattr(value, "kind"):
        return {"name": value.name, "kind": value.kind, "version": getattr(value, "version", None)}
    if hasattr(value, "value"):
        return {"type": value.__class__.__name__, "value": value.value}
    if hasattr(value, "name"):
        return value.name
    return repr(value)


def _run_2025_python_route_smoke(*, federation_name: str, backend: str) -> dict[str, Any]:
    rti = create_2025_rti_ambassador(backend=backend)
    callbacks = NullFederateAmbassador2025()
    summary: dict[str, Any] = {"backend": getattr(rti, "backend_info", None)}
    fom_modules = tuple(str(path) for path in scenario_fom_paths("message-test"))
    try:
        rti.connect(callbacks, CallbackModel2025.HLA_EVOKED)
        rti.create_federation_execution(
            federation_name,
            fom_modules,
            logical_time_implementation_name="HLAinteger64Time",
        )
        federate_handle = rti.join_federation_execution(
            "python-federate",
            "demo",
            federation_name,
        )
        summary.update(
            {
                "federate_handle": federate_handle,
                "fom_modules": fom_modules,
                "event_names": ["connect", "create_federation_execution", "join_federation_execution"],
            }
        )
        rti.resign_federation_execution(ResignAction2025.NO_ACTION)
        rti.destroy_federation_execution(federation_name)
        rti.disconnect()
        return summary
    finally:
        rti.close()


def _run_2010_python_route_smoke(*, federation_name: str, backend: str) -> dict[str, Any]:
    engine = InMemoryRTIEngine()
    rti = create_2010_rti_ambassador(backend=backend, engine=engine)
    callbacks = NullFederateAmbassador2010()
    summary: dict[str, Any] = {"backend": getattr(rti, "backend_info", None)}
    try:
        rti.connect(callbacks, CallbackModel2010.HLA_EVOKED)
        rti.create_federation_execution(federation_name, "DemoFOMmodule.xml")
        federate_handle = rti.join_federation_execution(
            "python-federate",
            "demo",
            federation_name,
        )
        summary.update(
            {
                "federate_handle": federate_handle,
                "fom_modules": ["DemoFOMmodule.xml"],
                "event_names": ["connect", "create_federation_execution", "join_federation_execution"],
            }
        )
        rti.resign_federation_execution(ResignAction2010.NO_ACTION)
        rti.destroy_federation_execution(federation_name)
        rti.disconnect()
        return summary
    finally:
        rti.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--edition", choices=["2010", "2025"], default="2010")
    parser.add_argument(
        "--backend",
        default=None,
        help="Optional override. Defaults to python1516e for 2010 and python1516_2025 for 2025.",
    )
    args = parser.parse_args()

    if args.edition == "2025":
        backend = args.backend or "python1516_2025"
        summary = _run_2025_python_route_smoke(
            federation_name=f"example-python-{args.edition}",
            backend=backend,
        )
    else:
        backend = args.backend or "python1516e"
        summary = _run_2010_python_route_smoke(
            federation_name=f"example-python-{args.edition}",
            backend=backend,
        )

    runtime_backend = summary.pop("backend", None)
    print(
        json.dumps(
            _jsonable(
                {
                    "edition": args.edition,
                    "backend": backend,
                    "runtime_backend": runtime_backend,
                    **summary,
                }
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
