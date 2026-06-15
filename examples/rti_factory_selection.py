from __future__ import annotations

import argparse
import json
from typing import Any

from hla2010_rti_runtime_common import get_rti_factory, iter_rti_factories


def _factory_payload(factory_name: str, *, include_probe: bool) -> dict[str, Any]:
    factory = get_rti_factory(factory_name)
    ambassador = factory.create_rti_ambassador()
    payload: dict[str, Any] = {
        "selected_name": factory.name,
        "selected_aliases": list(factory.aliases),
        "selectable_names": list(factory.selectable_names),
        "family": factory.family,
        "backend_info": {
            "name": ambassador.backend_info.name,
            "kind": ambassador.backend_info.kind,
            "version": ambassador.backend_info.version,
            "details": ambassador.backend_info.details,
        },
        "installed_factories": [
            {
                "name": candidate.name,
                "family": candidate.family,
                "selectable_names": list(candidate.selectable_names),
                "probe_supported": candidate.probe_supported,
            }
            for candidate in iter_rti_factories()
        ],
    }
    if include_probe:
        probe = factory.discover()
        payload["probe"] = {
            "available": probe.available,
            "error": probe.error,
        }
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="List installed RTI factories, choose one by name or alias, and instantiate it.",
    )
    parser.add_argument(
        "--name",
        default="in-memory",
        help="Factory name or alias to instantiate, such as in-memory, python, certi, or portico.",
    )
    parser.add_argument(
        "--probe",
        action="store_true",
        help="Include discovery/probe status for the selected factory.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON instead of the short human-readable summary.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = _factory_payload(args.name, include_probe=args.probe)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print("installed factories:")
    for item in payload["installed_factories"]:
        print(
            f"- {item['name']} [{item['family']}] selectable_names="
            f"{','.join(item['selectable_names'])}"
        )
    backend = payload["backend_info"]
    print("")
    print(
        "selected factory:"
        f" {payload['selected_name']} -> backend={backend['kind']} name={backend['name']}"
    )
    if args.probe:
        probe = payload.get("probe", {})
        print(f"probe: available={probe.get('available')} error={probe.get('error')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
