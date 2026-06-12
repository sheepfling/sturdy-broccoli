"""Factory functions for the in-memory Python RTI backend."""
from __future__ import annotations

from hla2010_rti_backend_common import make_rti_ambassador
from .engine import InMemoryRTIEngine
from .state import PythonRTIConfig


def create_python_backend(
    *,
    engine: InMemoryRTIEngine | None = None,
    config: PythonRTIConfig | None = None,
):
    from .backend import PythonRTIBackend

    return PythonRTIBackend(engine=engine, config=config)


def rti_ambassador(
    *,
    engine: InMemoryRTIEngine | None = None,
    config: PythonRTIConfig | None = None,
):
    return make_rti_ambassador(create_python_backend(engine=engine, config=config))


def create_python_ambassador(
    *,
    engine: InMemoryRTIEngine | None = None,
    config: PythonRTIConfig | None = None,
):
    return rti_ambassador(engine=engine, config=config)


def create_python_pair(
    *,
    engine: InMemoryRTIEngine | None = None,
    config: PythonRTIConfig | None = None,
):
    engine = engine or InMemoryRTIEngine()
    return (
        rti_ambassador(engine=engine, config=config),
        rti_ambassador(engine=engine, config=config),
    )


__all__ = ["create_python_ambassador", "create_python_backend", "create_python_pair", "rti_ambassador"]
