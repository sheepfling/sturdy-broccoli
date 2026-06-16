#!/usr/bin/env python3
"""Run the backend-neutral Target/Radar HLA scenario.

Default backend is the dependency-free Python in-memory RTI.  Java backends need
a vendor RTI jar/process plus a FOM module that defines the names used by the
scenario.
"""
from __future__ import annotations

import argparse

from hla.foms.target_radar.scenarios import make_target_radar_factory, run_target_radar_scenario


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
        make_target_radar_factory(
            args.backend,
            classpath=args.classpath,
            rti_factory_name=args.rti_factory_name,
            py4j_address=args.py4j_address,
            py4j_port=args.py4j_port,
            py4j_callback_port=args.py4j_callback_port,
        ),
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
