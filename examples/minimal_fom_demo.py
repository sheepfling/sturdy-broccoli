#!/usr/bin/env python3
"""Run the package-backed minimal FOM publisher/subscriber example."""
from __future__ import annotations

import argparse

from hla2010_fom_minimal_demo.scenarios import (
    make_minimal_demo_factory,
    minimal_demo_fom_path,
    run_minimal_demo_scenario,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=["python", "java-shim-jpype", "java-shim-py4j", "jpype", "py4j"], default="python")
    parser.add_argument("--federation-name", default="MinimalDemoFederation")
    parser.add_argument("--object-message", default="hello-object")
    parser.add_argument("--interaction-message", default="hello-interaction")
    args = parser.parse_args(argv)

    result = run_minimal_demo_scenario(
        make_minimal_demo_factory(args.backend),
        federation_name=args.federation_name,
        object_message=args.object_message,
        interaction_message=args.interaction_message,
        fom_modules=[minimal_demo_fom_path()],
    )

    print(
        f"backend={','.join(result.backend_kinds)} federation={result.federation_name} "
        f"object_updates={len(result.object_updates)} interactions={len(result.interactions)}"
    )
    for item in result.object_updates:
        print(f"object name={item.object_name} message={item.message}")
    for item in result.interactions:
        print(f"interaction sender={item.sender} message={item.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
