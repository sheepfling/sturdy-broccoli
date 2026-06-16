"""IEEE 1516.1-2025 HLA API namespace."""
from __future__ import annotations

from ._generated import FederateAmbassador, NullFederateAmbassador, RTIambassador

__version__ = "0.13.0"


def __getattr__(name: str):
    if name in {"RtiFactory", "create_rti_ambassador"}:
        from .factory import RtiFactory, create_rti_ambassador

        return {"RtiFactory": RtiFactory, "create_rti_ambassador": create_rti_ambassador}[name]
    raise AttributeError(name)


__all__ = [
    "FederateAmbassador",
    "NullFederateAmbassador",
    "RTIambassador",
    "RtiFactory",
    "__version__",
    "create_rti_ambassador",
]
