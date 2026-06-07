"""Run the backend-neutral target/radar HLA scenario."""
from __future__ import annotations

import json
from pathlib import Path
import sys

# Allow running directly from the source checkout.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hla2010.scenarios import make_target_radar_factory, run_target_radar_scenario


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="python", help="python, java-shim-jpype, java-shim-py4j, jpype, or py4j")
    parser.add_argument("--steps", type=int, default=3)
    parser.add_argument("--dt", type=float, default=1.0)
    args = parser.parse_args()

    result = run_target_radar_scenario(make_target_radar_factory(args.backend), steps=args.steps, dt=args.dt)
    print(json.dumps(result.as_dict(), indent=2))


if __name__ == "__main__":
    main()
