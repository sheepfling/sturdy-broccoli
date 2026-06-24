#!/usr/bin/env python3
"""Run the backend-neutral demo federate through a Java bridge profile.

By default this uses the in-process Java-shaped shim, so it works without a real
RTI, JPype, or Py4J.  The important point is that the federate scenario itself
is identical for both bridge profiles and both supported Java HLA editions.

Examples:

    python examples/java_shim_federate.py --edition 2010 --bridge jpype
    python examples/java_shim_federate.py --edition 2010 --bridge py4j
    python examples/java_shim_federate.py --edition 2025 --bridge jpype
    python examples/java_shim_federate.py --edition 2025 --bridge py4j

With optional bridge dependencies installed and a compiled shim jar, the same
scenario can target the real bridge modules:

    python java_shims/hla-rti1516e-shim/tools/build_java_shim.py --output /tmp/hla-shim.jar
    python examples/java_shim_federate.py --edition 2010 --bridge jpype --real-java-shim /tmp/hla-shim.jar
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from hla.backends.common import make_rti_ambassador
from hla.bridges.java.common.java_shim_factory import create_java_shim_backend
from hla.fom.proto2025 import scenario_fom_paths
from hla.runtime.rti1516_2025_factory import create_rti_ambassador as create_2025_rti_ambassador
from hla.rti1516_2025.enums import CallbackModel as CallbackModel2025
from hla.rti1516_2025.enums import ResignAction as ResignAction2025
from hla.rti1516_2025.federate_ambassador import NullFederateAmbassador as NullFederateAmbassador2025
from hla.verification.scenario_basic import run_basic_federate_scenario


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    if isinstance(value, dict):
        return {str(_jsonable(k)): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "name") and hasattr(value, "kind"):
        return {"name": value.name, "kind": value.kind, "version": getattr(value, "version", None)}
    if hasattr(value, "value") and value.__class__.__module__.startswith("hla2010"):
        return {value.__class__.__name__: getattr(value, "value")}
    if hasattr(value, "name") and value.__class__.__module__.startswith("hla2010"):
        return value.name
    return repr(value)


def _rti_factory(edition: str, bridge: str, real_java_shim: Path | None):
    if real_java_shim is None:
        if edition == "2025":
            return lambda: create_2025_rti_ambassador(backend=f"java-shim-{bridge}")
        return lambda: make_rti_ambassador(create_java_shim_backend(bridge))

    if bridge == "jpype":
        from hla.bridges.java.jpype import JPypeConfig, rti_ambassador

        return lambda: rti_ambassador(
            JPypeConfig(
                classpath=[str(real_java_shim)],
                shutdown_jvm_on_close=False,
                java_api_profile=edition,
            )
        )

    from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway, launch_gateway

    from hla.bridges.java.py4j import Py4JConfig, rti_ambassador

    port = launch_gateway(classpath=str(real_java_shim), die_on_exit=True)
    gateway = JavaGateway(
        gateway_parameters=GatewayParameters(port=port, auto_convert=True),
        callback_server_parameters=CallbackServerParameters(port=0),
    )
    gateway.start_callback_server()
    return lambda: rti_ambassador(Py4JConfig(gateway=gateway, java_api_profile=edition))


def _run_2025_java_route_smoke(rti_factory, *, federation_name: str) -> dict[str, Any]:  # noqa: ANN001
    rti = rti_factory()
    callbacks = NullFederateAmbassador2025()
    summary = {"backend": getattr(rti, "backend_info", None)}
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--edition", choices=["2010", "2025"], default="2010")
    parser.add_argument("--bridge", choices=["jpype", "py4j"], default="jpype")
    parser.add_argument(
        "--real-java-shim",
        type=Path,
        default=None,
        help="Optional compiled Java shim jar. Without this, use the in-process shim route.",
    )
    args = parser.parse_args()

    federation_name = f"example-{args.edition}-{args.bridge}"
    factory = _rti_factory(args.edition, args.bridge, args.real_java_shim)
    if args.edition == "2025":
        summary = _run_2025_java_route_smoke(factory, federation_name=federation_name)
    else:
        summary = run_basic_federate_scenario(factory, federation_name=federation_name)
    print(json.dumps(_jsonable({"edition": args.edition, "bridge": args.bridge, **summary}), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
