"""Packaged IEEE 1516-2025-style HLA-X prototype FOM resources."""
from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Final

FOM_RESOURCE_PACKAGE: Final = "hla.rti1516_2025.resources.foms"

HLAX_BASE: Final = "HLAx_Base.xml"
HLAX_MESSAGE_TEST: Final = "HLAx_MessageTest.xml"
HLAX_SPACE_LITE: Final = "HLAx_SpaceLite.xml"
HLAX_TIME_MGMT_TEST: Final = "HLAx_TimeMgmtTest.xml"

HLAX_V0_1_MODULES: Final = (
    HLAX_BASE,
    HLAX_MESSAGE_TEST,
    HLAX_SPACE_LITE,
    HLAX_TIME_MGMT_TEST,
)

HLAX_V0_1_SCENARIO_MODULES: Final = {
    "message-test": (HLAX_BASE, HLAX_MESSAGE_TEST),
    "space-lite": (HLAX_BASE, HLAX_SPACE_LITE),
    "time-mgmt-test": (HLAX_BASE, HLAX_TIME_MGMT_TEST),
    "full": HLAX_V0_1_MODULES,
}


def fom_path(name: str) -> Path:
    """Return a filesystem path for one packaged HLA-X v0.1 FOM XML module."""

    if name not in HLAX_V0_1_MODULES:
        valid = ", ".join(HLAX_V0_1_MODULES)
        raise KeyError(f"Unknown HLA-X v0.1 FOM module {name!r}; expected one of: {valid}")
    return Path(str(resources.files(FOM_RESOURCE_PACKAGE).joinpath(name)))


def fom_paths(*names: str) -> tuple[Path, ...]:
    """Return packaged FOM paths in caller-provided order."""

    selected = names or HLAX_V0_1_MODULES
    return tuple(fom_path(name) for name in selected)


def scenario_fom_paths(scenario: str) -> tuple[Path, ...]:
    """Return the base-plus-extension FOM set for a named prototype scenario."""

    try:
        module_names = HLAX_V0_1_SCENARIO_MODULES[scenario]
    except KeyError as exc:
        valid = ", ".join(sorted(HLAX_V0_1_SCENARIO_MODULES))
        raise KeyError(f"Unknown HLA-X v0.1 scenario {scenario!r}; expected one of: {valid}") from exc
    return fom_paths(*module_names)
