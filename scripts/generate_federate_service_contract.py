from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla.verification.repo_internal.verification.federate_service_fastapi import federate_service_contract_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the metadata-derived federate service contract JSON.")
    parser.add_argument(
        "--output",
        type=Path,
        default=SCRIPT_REPO_ROOT / "docs" / "reference" / "federate_service_contract.json",
    )
    args = parser.parse_args(argv)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(federate_service_contract_json(), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
