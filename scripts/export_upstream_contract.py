#!/usr/bin/env python3
"""Export a local standard-facing contract snapshot.

This script introspects local facade modules only. It never imports upstream_reference.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import sys
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Any

DEFAULT_MODULE_SUFFIXES = (
    "",
    "rti_ambassador",
    "federate_ambassador",
    "enums",
    "exceptions",
    "datatypes",
    "handles",
    "logical_time",
    "time",
    "encoding",
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = (
    "packages/hla-rti1516e/src",
    "packages/hla-rti1516-2025/src",
    "packages/hla-rti-core/src",
)


def _ensure_source_checkout_path() -> None:
    for rel in reversed(SOURCE_ROOTS):
        path = str(REPO_ROOT / rel)
        if path not in sys.path:
            sys.path.insert(0, path)


def _public_names(module: ModuleType) -> list[str]:
    explicit = getattr(module, "__all__", None)
    if explicit is not None:
        return sorted(str(name) for name in explicit)
    return sorted(name for name in vars(module) if not name.startswith("_"))


def _class_contract(cls: type[Any]) -> dict[str, Any]:
    methods = []
    attributes = []
    for name, value in vars(cls).items():
        if name.startswith("_"):
            continue
        if inspect.isfunction(value) or inspect.ismethoddescriptor(value):
            methods.append(name)
        elif isinstance(value, property):
            attributes.append(name)
    return {
        "bases": [base.__name__ for base in cls.__bases__ if base is not object],
        "methods": sorted(methods),
        "attributes": sorted(attributes),
    }


def module_contract(module_name: str) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    classes: dict[str, Any] = {}
    enums: dict[str, list[str]] = {}
    exceptions: list[str] = []
    functions: list[str] = []
    for name in _public_names(module):
        value = getattr(module, name, None)
        if inspect.isclass(value) and getattr(value, "__module__", module_name) == module_name:
            if issubclass(value, Enum):
                enums[name] = [member.name for member in value]
            elif issubclass(value, BaseException):
                exceptions.append(name)
            else:
                classes[name] = _class_contract(value)
        elif inspect.isfunction(value) and getattr(value, "__module__", module_name) == module_name:
            functions.append(name)
    return {
        "public_names": _public_names(module),
        "classes": dict(sorted(classes.items())),
        "functions": sorted(functions),
        "enums": dict(sorted(enums.items())),
        "exceptions": sorted(exceptions),
    }


def _standard_name(package: str) -> str:
    return {"hla.rti1516e": "ieee1516e", "hla.rti1516_2025": "ieee1516_2025"}[package]


def package_contract(package: str, *, source: str | dict[str, Any]) -> dict[str, Any]:
    _ensure_source_checkout_path()
    source_payload = source if isinstance(source, dict) else {"repo": "upstream_reference", "tag": source.removeprefix("upstream_reference "), "commit": None}
    modules: dict[str, Any] = {}
    for suffix in DEFAULT_MODULE_SUFFIXES:
        module_name = package if not suffix else f"{package}.{suffix}"
        try:
            modules[module_name] = module_contract(module_name)
        except ModuleNotFoundError:
            continue
    return {
        "schema_version": 1,
        "standard": _standard_name(package),
        "source": source_payload,
        "package": package,
        "modules": dict(sorted(modules.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", choices=("hla.rti1516e", "hla.rti1516_2025"))
    parser.add_argument("--source", default="upstream_reference v0.1.1")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    _ensure_source_checkout_path()
    payload = package_contract(args.package, source=args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
