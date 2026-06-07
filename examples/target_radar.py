"""Run the backend-neutral target/radar HLA scenario."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

# Allow running directly from the source checkout.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hla2010.backends.python import InMemoryRTIEngine
from hla2010.rti import create_rti_ambassador
from hla2010.scenarios.target_radar import run_target_radar_scenario


def make_factory(kind: str):
    normalized = kind.strip().lower()
    if normalized in {"python", "inmemory", "in-memory"}:
        engine = InMemoryRTIEngine()

        def factory(role: str):
            return create_rti_ambassador("python", engine=engine)

        return factory

    if normalized in {"java-shim-jpype", "java-shim-py4j"}:
        from hla2010.testing.java_shim import SharedJavaShimKernel

        kernel = SharedJavaShimKernel()

        def factory(role: str):
            return create_rti_ambassador(normalized, kernel=kernel, shared=True)

        return factory

    if normalized in {"jpype", "py4j", "java-jpype", "java-py4j"}:
        def factory(role: str):
            return create_rti_ambassador(normalized)

        return factory

    raise ValueError(f"Unsupported backend kind for this example: {kind}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="python", help="python, java-shim-jpype, java-shim-py4j, jpype, or py4j")
    parser.add_argument("--steps", type=int, default=3)
    parser.add_argument("--dt", type=float, default=1.0)
    args = parser.parse_args()

    result = run_target_radar_scenario(make_factory(args.backend), steps=args.steps, dt=args.dt)
    print(json.dumps(result.as_dict(), indent=2))


if __name__ == "__main__":
    main()
