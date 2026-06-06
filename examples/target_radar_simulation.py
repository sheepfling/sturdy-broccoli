#!/usr/bin/env python3
"""Run the backend-neutral Target/Radar HLA scenario.

Default backend is the dependency-free Python in-memory RTI.  Java backends need
a vendor RTI jar/process plus a FOM module that defines the names used by the
scenario.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hla2010.backends.python_rti import InMemoryRTIEngine
from hla2010.rti import create_rti_ambassador
from hla2010.scenarios.target_radar import run_target_radar_scenario


def build_factory(args):
    if args.backend == "python":
        engine = InMemoryRTIEngine(name="target-radar-engine")
        return lambda role: create_rti_ambassador("python", engine=engine)

    if args.backend == "jpype":
        from hla2010.backends.jpype_backend import JPypeConfig, rti_ambassador

        classpath = [item for item in args.classpath if item]
        return lambda role: rti_ambassador(JPypeConfig(classpath=classpath, rti_factory_name=args.rti_factory_name))

    if args.backend in {"java-shim-jpype", "java-shim-py4j"}:
        from hla2010.testing.java_shim import SharedJavaShimKernel

        kernel = SharedJavaShimKernel()
        return lambda role: create_rti_ambassador(args.backend, kernel=kernel, shared=True)

    if args.backend == "py4j":
        from hla2010.backends.py4j_backend import Py4JConfig, rti_ambassador

        gateway_parameters = {"address": args.py4j_address, "port": args.py4j_port}
        callback_server_parameters = {"port": args.py4j_callback_port}
        return lambda role: rti_ambassador(
            Py4JConfig(
                gateway_parameters=gateway_parameters,
                callback_server_parameters=callback_server_parameters,
                rti_factory_name=args.rti_factory_name,
            )
        )

    raise ValueError(f"unsupported backend {args.backend!r}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=["python", "java-shim-jpype", "java-shim-py4j", "jpype", "py4j"], default="python")
    parser.add_argument("--steps", type=int, default=5)
    parser.add_argument("--dt", type=float, default=1.0)
    parser.add_argument("--federation-name", default="TargetRadarFederation")
    parser.add_argument("--classpath", action="append", default=[], help="JPype Java classpath entry; repeat as needed")
    parser.add_argument("--fom-module", action="append", default=[], help="FOM module reference to pass to createFederationExecution; repeat as needed")
    parser.add_argument("--rti-factory-name", default=None, help="Optional Java RtiFactoryFactory name")
    parser.add_argument("--py4j-address", default="127.0.0.1")
    parser.add_argument("--py4j-port", type=int, default=25333)
    parser.add_argument("--py4j-callback-port", type=int, default=0)
    args = parser.parse_args(argv)

    result = run_target_radar_scenario(
        build_factory(args),
        federation_name=args.federation_name,
        steps=args.steps,
        dt=args.dt,
        fom_modules=args.fom_module,
    )

    print(
        f"backend={','.join(result.backend_kinds)} federation={result.federation_name} "
        f"tracks={len(result.track_reports)}"
    )
    for report in result.track_reports:
        print(
            f"{report.track_id:>8s} target={report.target_name:<10s} "
            f"t={report.time_seconds:5.1f} "
            f"pos=({report.position.x:8.1f},{report.position.y:8.1f},{report.position.z:7.1f}) "
            f"range={report.range_m:9.1f} bearing={report.bearing_rad:7.3f} "
            f"rcs={report.rcs_square_meters:6.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
