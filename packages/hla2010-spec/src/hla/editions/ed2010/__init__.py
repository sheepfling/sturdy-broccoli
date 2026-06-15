"""Neutral edition-qualified facade for the IEEE 1516.1-2010 surface."""
from __future__ import annotations

import importlib
import sys


_ALIASED_SUBMODULES = (
    "ambassadors",
    "api",
    "encoding",
    "enums",
    "exceptions",
    "fom",
    "handles",
    "mom",
    "raw_api",
    "rti",
    "runtime_api",
    "spec",
    "spec_api",
    "spec_inventory",
    "spec_refs",
    "spec_sources",
    "time",
    "types",
)


def _load_alias(name: str):
    module = importlib.import_module(f"hla2010.{name}")
    sys.modules[f"{__name__}.{name}"] = module
    return module


def __getattr__(name: str):
    if name in _ALIASED_SUBMODULES:
        return _load_alias(name)
    raise AttributeError(name)


for _module_name in _ALIASED_SUBMODULES:
    _load_alias(_module_name)


edition_year = 2010
legacy_namespace = "hla2010"

__all__ = [
    "edition_year",
    "legacy_namespace",
    *_ALIASED_SUBMODULES,
]
