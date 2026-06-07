#!/usr/bin/env python3
"""Run the backend-neutral demo federate through a Java bridge profile.

By default this uses the in-process Java-shaped shim, so it works without a real
RTI, JPype, or Py4J.  The important point is that the federate scenario itself
is identical for both bridge profiles.

Examples:

    python examples/java_shim_federate.py --bridge jpype
    python examples/java_shim_federate.py --bridge py4j

With optional bridge dependencies installed and a compiled shim jar, the same
scenario can target the real bridge modules:

    python java_shims/hla-rti1516e-shim/tools/build_java_shim.py --output /tmp/hla-shim.jar
    python examples/java_shim_federate.py --bridge jpype --real-java-shim /tmp/hla-shim.jar
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hla2010.backends.base import make_rti_ambassador
from hla2010.testing.java_shim import create_java_shim_backend
from hla2010.testing.scenarios import run_basic_federate_scenario


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


def _rti_factory(bridge: str, real_java_shim: Path | None):
    if real_java_shim is None:
        return lambda: make_rti_ambassador(create_java_shim_backend(bridge))

    if bridge == "jpype":
        from hla2010.backends.jpype import JPypeConfig, rti_ambassador

        return lambda: rti_ambassador(JPypeConfig(classpath=[str(real_java_shim)], shutdown_jvm_on_close=False))

    from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway, launch_gateway
    from hla2010.backends.py4j import Py4JConfig, rti_ambassador

    port = launch_gateway(classpath=str(real_java_shim), die_on_exit=True)
    gateway = JavaGateway(
        gateway_parameters=GatewayParameters(port=port, auto_convert=True),
        callback_server_parameters=CallbackServerParameters(port=0),
    )
    gateway.start_callback_server()
    return lambda: rti_ambassador(Py4JConfig(gateway=gateway))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bridge", choices=["jpype", "py4j"], default="jpype")
    parser.add_argument(
        "--real-java-shim",
        type=Path,
        default=None,
        help="Optional compiled hla-rti1516e-shim.jar. Without this, use the in-process shim.",
    )
    args = parser.parse_args()

    summary = run_basic_federate_scenario(
        _rti_factory(args.bridge, args.real_java_shim),
        federation_name=f"example-{args.bridge}",
    )
    print(json.dumps(_jsonable({"bridge": args.bridge, **summary}), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
