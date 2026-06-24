"""Packaged IEEE 1516-2025-style Proto2025 prototype FOM resources."""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module, resources
from pathlib import Path
from typing import Any, Final, Iterable

FOM_RESOURCE_PACKAGE: Final = "hla.fom.resources.proto2025.foms"
ENCODING_AUTH_RESOURCE_PACKAGE: Final = "hla.fom.resources.proto2025.encoding_auth"

PROTO2025_BASE: Final = "Proto2025_Base.xml"
PROTO2025_MESSAGE_TEST: Final = "Proto2025_MessageTest.xml"
PROTO2025_SPACE_LITE: Final = "Proto2025_SpaceLite.xml"
PROTO2025_TIME_MGMT_TEST: Final = "Proto2025_TimeMgmtTest.xml"
ENCODING_SMOKE_TEST_2025: Final = "EncodingSmokeTest-2025.xml"

PROTO2025_V0_1_MODULES: Final = (
    PROTO2025_BASE,
    PROTO2025_MESSAGE_TEST,
    PROTO2025_SPACE_LITE,
    PROTO2025_TIME_MGMT_TEST,
)

PROTO2025_V0_1_SCENARIO_MODULES: Final = {
    "message-test": (PROTO2025_BASE, PROTO2025_MESSAGE_TEST),
    "space-lite": (PROTO2025_BASE, PROTO2025_SPACE_LITE),
    "time-mgmt-test": (PROTO2025_BASE, PROTO2025_TIME_MGMT_TEST),
    "full": PROTO2025_V0_1_MODULES,
}


def fom_path(name: str) -> Path:
    """Return a filesystem path for one packaged Proto2025 v0.1 FOM XML module."""

    if name not in PROTO2025_V0_1_MODULES:
        valid = ", ".join(PROTO2025_V0_1_MODULES)
        raise KeyError(f"Unknown Proto2025 v0.1 FOM module {name!r}; expected one of: {valid}")
    return Path(str(resources.files(FOM_RESOURCE_PACKAGE).joinpath(name)))


def fom_paths(*names: str) -> tuple[Path, ...]:
    """Return packaged FOM paths in caller-provided order."""

    selected = names or PROTO2025_V0_1_MODULES
    return tuple(fom_path(name) for name in selected)


def scenario_fom_paths(scenario: str) -> tuple[Path, ...]:
    """Return the base-plus-extension FOM set for a named prototype scenario."""

    try:
        module_names = PROTO2025_V0_1_SCENARIO_MODULES[scenario]
    except KeyError as exc:
        valid = ", ".join(sorted(PROTO2025_V0_1_SCENARIO_MODULES))
        raise KeyError(f"Unknown Proto2025 v0.1 scenario {scenario!r}; expected one of: {valid}") from exc
    return fom_paths(*module_names)


def encoding_smoke_fom_path() -> Path:
    """Return the packaged 2025 encoding/auth smoke-test FOM XML module."""

    return Path(str(resources.files(ENCODING_AUTH_RESOURCE_PACKAGE).joinpath(ENCODING_SMOKE_TEST_2025)))


@dataclass(frozen=True, slots=True)
class FomTypeRepository:
    """2025-facing datatype lookup facade over parsed OMT/DIF FOM modules."""

    catalog: Any | None = None
    modules: tuple[Any, ...] = ()

    @classmethod
    def empty(cls) -> "FomTypeRepository":
        return cls()

    @classmethod
    def from_modules(cls, modules: Iterable[Any]) -> "FomTypeRepository":
        fom = import_module("hla.fom")
        resolved = fom.FOMResolver().resolve_many(tuple(modules))
        return cls(catalog=fom.merge_fom_modules(resolved), modules=resolved)

    def has(self, datatype_name: str) -> bool:
        return self.resolve(datatype_name) is not None

    def resolve(self, datatype_name: str) -> Any | None:
        if self.catalog is None:
            return None
        for collection in (
            self.catalog.basic_datatypes,
            self.catalog.simple_datatypes,
            self.catalog.reference_datatypes,
            self.catalog.enumerated_datatypes,
            self.catalog.array_datatypes,
            self.catalog.fixed_record_datatypes,
            self.catalog.variant_record_datatypes,
        ):
            found = collection.get(datatype_name)
            if found is not None:
                return found
        return None

    def attribute_type(self, object_class: str, attribute: str) -> str | None:
        if self.catalog is None:
            return None
        spec = self.catalog.object_classes.get(object_class)
        if spec is None:
            return None
        return spec.attribute_datatypes.get(attribute)

    def parameter_type(self, interaction_class: str, parameter: str) -> str | None:
        if self.catalog is None:
            return None
        spec = self.catalog.interaction_classes.get(interaction_class)
        if spec is None:
            return None
        return spec.parameter_datatypes.get(parameter)

    def capability_report(self) -> dict[str, object]:
        if self.catalog is None:
            return {
                "status": "empty",
                "modules": [],
                "datatype_count": 0,
                "object_class_count": 0,
                "interaction_class_count": 0,
            }
        return {
            "status": "loaded",
            "modules": [module.name or str(module.source) for module in self.modules],
            "datatype_count": len(self.catalog.datatype_names),
            "object_class_count": len(self.catalog.object_classes),
            "interaction_class_count": len(self.catalog.interaction_classes),
            "datatypes": sorted(self.catalog.datatype_names),
        }
