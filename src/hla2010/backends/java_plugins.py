"""Compatibility exports for split Java RTI plugin descriptors."""
from __future__ import annotations

from ..rti import RTIBackendPlugin


def jpype_plugin() -> RTIBackendPlugin:
    from hla2010_rti_java_jpype.plugin import jpype_plugin as plugin

    return plugin()


def py4j_plugin() -> RTIBackendPlugin:
    from hla2010_rti_java_py4j.plugin import py4j_plugin as plugin

    return plugin()


def pitch_jpype_plugin() -> RTIBackendPlugin:
    from hla2010_rti_pitch_jpype.plugin import pitch_jpype_plugin as plugin

    return plugin()


def pitch_py4j_plugin() -> RTIBackendPlugin:
    from hla2010_rti_pitch_py4j.plugin import pitch_py4j_plugin as plugin

    return plugin()


def portico_jpype_plugin() -> RTIBackendPlugin:
    from hla2010_rti_portico.plugin import portico_jpype_plugin as plugin

    return plugin()


def portico_py4j_plugin() -> RTIBackendPlugin:
    from hla2010_rti_portico.plugin import portico_py4j_plugin as plugin

    return plugin()


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return ()


__all__ = [
    "backend_plugins",
    "jpype_plugin",
    "pitch_jpype_plugin",
    "pitch_py4j_plugin",
    "portico_jpype_plugin",
    "portico_py4j_plugin",
    "py4j_plugin",
]
