from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from typing import Any

from hla2010_rti_runtime_common import (
    debug_rti_backend_registry,
    get_rti_factory,
    iter_rti_factories,
)


def _serialize_probe_info(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if is_dataclass(value):
        return {
            key: _serialize_probe_info(item)
            for key, item in asdict(value).items()
        }
    if isinstance(value, dict):
        return {
            str(key): _serialize_probe_info(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_serialize_probe_info(item) for item in value]
    if hasattr(value, "__dict__"):
        return {
            key: _serialize_probe_info(item)
            for key, item in vars(value).items()
            if not key.startswith("_")
        }
    return str(value)


def cmd_list(_: argparse.Namespace) -> int:
    resolved_edition = debug_rti_backend_registry(edition=_.edition).selected_backend_edition
    print("Installed RTI factories")
    print(f"selected_backend_edition: {resolved_edition}")
    for factory in iter_rti_factories(edition=_.edition):
        aliases = ", ".join(factory.aliases) if factory.aliases else "-"
        selectable = ", ".join(factory.selectable_names)
        editions = ", ".join(factory.supported_editions)
        print(f"- {factory.name} [{factory.family}]")
        print(f"  supported_editions: {editions}")
        print(f"  selectable_names: {selectable}")
        print(f"  aliases: {aliases}")
        print(f"  source_kind: {factory.source_kind}")
        print(f"  probe_supported: {'yes' if factory.probe_supported else 'no'}")
        if factory.description:
            print(f"  description: {factory.description}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    resolved_edition = debug_rti_backend_registry(edition=args.edition).selected_backend_edition
    factory = get_rti_factory(args.name, edition=args.edition)
    probe = factory.discover() if args.probe else None
    payload = {
        "name": factory.name,
        "family": factory.family,
        "aliases": list(factory.aliases),
        "supported_editions": list(factory.supported_editions),
        "selectable_names": list(factory.selectable_names),
        "selected_backend_edition": resolved_edition,
        "probe_supported": factory.probe_supported,
        "description": factory.description,
        "source_kind": factory.source_kind,
        "source_module": factory.source_module,
        "entry_point_group": factory.entry_point_group,
        "entry_point_name": factory.entry_point_name,
        "entry_point_value": factory.entry_point_value,
    }
    if probe is not None:
        payload["probe"] = {
            key: _serialize_probe_info(value)
            for key, value in asdict(probe).items()
        }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_instantiate(args: argparse.Namespace) -> int:
    resolved_edition = debug_rti_backend_registry(edition=args.edition).selected_backend_edition
    factory = get_rti_factory(args.name, edition=args.edition)
    ambassador = factory.create_rti_ambassador(edition=args.edition)
    payload = {
        "name": factory.name,
        "aliases": list(factory.aliases),
        "supported_editions": list(factory.supported_editions),
        "selectable_names": list(factory.selectable_names),
        "family": factory.family,
        "selected_backend_edition": resolved_edition,
        "source_kind": factory.source_kind,
        "source_module": factory.source_module,
        "entry_point_group": factory.entry_point_group,
        "entry_point_name": factory.entry_point_name,
        "entry_point_value": factory.entry_point_value,
        "backend_info": {
            "name": ambassador.backend_info.name,
            "kind": ambassador.backend_info.kind,
            "version": ambassador.backend_info.version,
            "details": ambassador.backend_info.details,
        },
    }
    if args.probe:
        probe = factory.discover()
        payload["probe"] = {
            key: _serialize_probe_info(value)
            for key, value in asdict(probe).items()
        }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_debug(args: argparse.Namespace) -> int:
    payload = {
        key: _serialize_probe_info(value)
        for key, value in asdict(debug_rti_backend_registry(edition=args.edition)).items()
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="./tools/rti-factories",
        description="List installed RTI ambassador factories and inspect one by name or alias.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List installed RTI factories.")
    list_parser.add_argument(
        "--edition",
        help="Filter factories to one edition key such as 2010.",
    )
    list_parser.set_defaults(func=cmd_list)

    show_parser = subparsers.add_parser("show", help="Describe one RTI factory by canonical name or alias.")
    show_parser.add_argument("name", help="Canonical factory name or alias such as python, in-memory, or certi.")
    show_parser.add_argument(
        "--edition",
        help="Resolve the factory against one edition key such as 2010.",
    )
    show_parser.add_argument("--probe", action="store_true", help="Run backend discovery/probe for the selected factory.")
    show_parser.set_defaults(func=cmd_show)

    instantiate_parser = subparsers.add_parser(
        "instantiate",
        help="Instantiate one RTI factory by canonical name or alias and print the selected backend info.",
    )
    instantiate_parser.add_argument(
        "name",
        help="Canonical factory name or alias such as python, in-memory, or certi.",
    )
    instantiate_parser.add_argument(
        "--edition",
        help="Resolve and instantiate the factory against one edition key such as 2010.",
    )
    instantiate_parser.add_argument(
        "--probe",
        action="store_true",
        help="Include backend discovery/probe information for the selected factory.",
    )
    instantiate_parser.set_defaults(func=cmd_instantiate)

    debug_parser = subparsers.add_parser(
        "debug",
        help="Print backend-plugin registry provenance and skipped-load diagnostics.",
    )
    debug_parser.add_argument(
        "--edition",
        help="Annotate the registry against one edition key such as 2010.",
    )
    debug_parser.set_defaults(func=cmd_debug)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
