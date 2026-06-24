#!/usr/bin/env python3
"""Run the backend-neutral Target/Radar HLA scenario.

Default backend is the direct Python 1516e RTI.

For IEEE 1516.1-2025, treat ``python1516_2025`` as the main full Python RTI
implementation lane. Legacy ``hla.backends.shim`` imports remain
compatibility-wrapper code around that same runtime and do not define a
separate RTI family or public backend-selection lane.

Java backends need a vendor RTI jar/process plus a FOM module that defines the
names used by the scenario.
"""
from __future__ import annotations

import argparse

from hla.foms.target_radar._internal import (
    make_target_radar_factory,
    run_target_radar_scenario,
    target_radar_fom_path,
)

_BACKEND_CHOICES = [
    "python1516e",
    "python-1516e",
    "python1516_2025",
    "python-1516-2025",
    "java-shim-jpype",
    "java-shim-py4j",
    "jpype",
    "py4j",
]
_BACKEND_HELP = (
    "Backend/provider name. Use 'python1516_2025' for the primary IEEE 1516.1-2025 Python RTI."
)
_PACKAGED_FOM_BACKENDS = {
    "python1516_2025",
    "python-1516-2025",
    "python-1516-2025",
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=_BACKEND_CHOICES, default="python1516e", help=_BACKEND_HELP)
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
    fom_modules = list(args.fom_module)
    if not fom_modules and args.backend.strip().lower() in _PACKAGED_FOM_BACKENDS:
        fom_modules = [target_radar_fom_path()]

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
        fom_modules=fom_modules,
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
