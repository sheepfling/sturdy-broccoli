"""Neutral umbrella namespace for editioned HLA Python surfaces."""
from __future__ import annotations

import importlib
import sys
from types import ModuleType


__version__ = "0.13.0"

DEFAULT_EDITION = "2010"
_EDITION_MODULES = {
    "2010": "hla.editions.ed2010",
}
_EDITION_ALIASES = {
    "2010": "2010",
    "ed2010": "2010",
    "1516.1-2010": "2010",
    "ieee-1516.1-2010": "2010",
}
_FORWARDED_SUBMODULES = (
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
_SELECTED_EDITION = DEFAULT_EDITION


def _normalize_edition_name(name: str) -> str:
    normalized = name.strip().lower()
    try:
        return _EDITION_ALIASES[normalized]
    except KeyError as exc:
        raise ValueError(f"Unsupported HLA edition selection: {name!r}") from exc


def available_editions() -> tuple[str, ...]:
    """Return the supported edition keys for the neutral namespace."""

    return tuple(sorted(_EDITION_MODULES))


def get_edition(name: str = DEFAULT_EDITION) -> ModuleType:
    """Return one explicit edition module without mutating the active selection."""

    edition_key = _normalize_edition_name(name)
    return importlib.import_module(_EDITION_MODULES[edition_key])


def selected_edition() -> str:
    """Return the active neutral edition key."""

    return _SELECTED_EDITION


def select_edition(name: str = DEFAULT_EDITION) -> ModuleType:
    """Activate one supported edition for the neutral `hla.*` import surface."""

    global _SELECTED_EDITION
    edition_key = _normalize_edition_name(name)
    edition_module = importlib.import_module(_EDITION_MODULES[edition_key])
    for submodule_name in _FORWARDED_SUBMODULES:
        module = importlib.import_module(f"{edition_module.__name__}.{submodule_name}")
        sys.modules[f"{__name__}.{submodule_name}"] = module
        globals()[submodule_name] = module
    try:
        importlib.import_module("hla2010_rti_runtime_common").set_selected_backend_edition(edition_key)
    except ModuleNotFoundError:
        pass
    _SELECTED_EDITION = edition_key
    return edition_module


current = select_edition(DEFAULT_EDITION)

__all__ = [
    "__version__",
    "DEFAULT_EDITION",
    "available_editions",
    "current",
    "get_edition",
    "select_edition",
    "selected_edition",
    *_FORWARDED_SUBMODULES,
]
