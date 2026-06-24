"""Edition-aware Python/Java binding profile helpers."""
from __future__ import annotations

import importlib
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Any

from .java_intake import JavaApiProfile, java_api_profile


@dataclass(frozen=True, slots=True)
class PythonJavaBindingProfile:
    """Resolved edition binding used by the Java bridge adapters."""

    api_profile: JavaApiProfile
    root_module: Any
    enums_module: Any
    exceptions_module: Any
    handles_module: Any
    datatypes_module: Any
    time_module: Any
    fom_module: Any
    null_federate_ambassador_type: type[Any]
    raw_api_metadata: dict[str, Any] | None = None

    @property
    def edition(self) -> str:
        return self.api_profile.edition

    @property
    def java_package(self) -> str:
        return self.api_profile.java_package

    def python_type(self, name: str) -> Any:
        for module in (
            self.root_module,
            self.handles_module,
            self.datatypes_module,
            self.time_module,
            self.enums_module,
            self.exceptions_module,
        ):
            value = getattr(module, name, None)
            if value is not None:
                return value
        raise AttributeError(f"Python binding {self.api_profile.python_package!r} does not export {name!r}")

    def python_type_or_none(self, name: str) -> Any | None:
        try:
            return self.python_type(name)
        except AttributeError:
            return None

    def enum_types_by_name(self) -> dict[str, type[Enum]]:
        return {
            name: value
            for name, value in vars(self.enums_module).items()
            if isinstance(value, type) and issubclass(value, Enum)
        }

    def callback_parameter_types(self, method_name: str, arg_count: int | None = None) -> tuple[str | None, ...]:
        metadata = self.raw_api_metadata or {}
        overloads = [
            overload
            for overload in metadata.get("FederateAmbassador", {}).get(method_name, ())
            if overload.get("language") == "java"
        ]
        if arg_count is not None:
            overloads = [overload for overload in overloads if len(overload.get("parameters", ())) == arg_count]
        if not overloads:
            return ()
        return tuple(
            str(parameter.get("java_type") or parameter.get("type") or "").strip() or None
            for parameter in overloads[0].get("parameters", ())
        )


@lru_cache(maxsize=None)
def load_python_java_binding_profile(profile: str | JavaApiProfile) -> PythonJavaBindingProfile:
    api_profile = java_api_profile(profile) if isinstance(profile, str) else profile
    root_module = importlib.import_module(api_profile.python_package)
    federate_module = importlib.import_module(f"{api_profile.python_package}.federate_ambassador")
    raw_api_metadata = None
    try:
        raw_api_metadata = importlib.import_module(f"{api_profile.python_package}.raw_api").API_METADATA
    except Exception:
        raw_api_metadata = None
    return PythonJavaBindingProfile(
        api_profile=api_profile,
        root_module=root_module,
        enums_module=importlib.import_module(f"{api_profile.python_package}.enums"),
        exceptions_module=importlib.import_module(f"{api_profile.python_package}.exceptions"),
        handles_module=importlib.import_module(f"{api_profile.python_package}.handles"),
        datatypes_module=importlib.import_module(f"{api_profile.python_package}.datatypes"),
        time_module=importlib.import_module(f"{api_profile.python_package}.time"),
        fom_module=importlib.import_module("hla.fom"),
        null_federate_ambassador_type=getattr(federate_module, "NullFederateAmbassador"),
        raw_api_metadata=raw_api_metadata,
    )


__all__ = ["PythonJavaBindingProfile", "load_python_java_binding_profile"]
