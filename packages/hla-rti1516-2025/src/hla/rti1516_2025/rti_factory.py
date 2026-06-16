"""RTI factory discovery and factory protocol for IEEE 1516.1-2025.

Sources: Java RtiFactory.java/RtiFactoryFactory.java and C++ RTIambassadorFactory.h.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from os import getenv
from typing import Iterable
from importlib.metadata import entry_points

from .encoding import EncoderFactory
from .rti_ambassador import RTIambassador

ENTRY_POINT_GROUPS: tuple[str, ...] = ("hla.ieee1516_2025", "hla.implementation")


class RtiFactory(ABC):
    @abstractmethod
    def getRtiAmbassador(self) -> RTIambassador: ...

    @abstractmethod
    def getEncoderFactory(self) -> EncoderFactory: ...

    @property
    @abstractmethod
    def rtiName(self) -> str: ...

    @property
    @abstractmethod
    def rtiVersion(self) -> str: ...

    @classmethod
    @abstractmethod
    def create(cls, settings: str | None = None) -> "RtiFactory": ...


class RtiFactoryFactory:
    @staticmethod
    def _load_factories(settings: str | None = None) -> Iterable[RtiFactory]:
        for group in ENTRY_POINT_GROUPS:
            for ep in entry_points(group=group):
                try:
                    factory_type = ep.load()
                    factory = factory_type.create(settings)
                except TypeError:
                    try:
                        factory = ep.load()()
                    except Exception:
                        continue
                except Exception:
                    continue
                if isinstance(factory, RtiFactory):
                    yield factory

    @staticmethod
    def getRtiFactory(name: str | None = None) -> RtiFactory:
        if name is None:
            name = getenv("HLA_RTI_FACTORY_NAME")

        settings = None
        if name is not None and ":" in name:
            name, settings = name.split(":", 1)

        for factory in RtiFactoryFactory._load_factories(settings):
            if not name or factory.rtiName == name:
                return factory

        raise ValueError(f"No RtiFactory registered or could not find RTI name {name}")

    @staticmethod
    def getAvailableRtiFactories() -> set[RtiFactory]:
        return set(RtiFactoryFactory._load_factories())
