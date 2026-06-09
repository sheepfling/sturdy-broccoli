"""Entry point descriptor for the Pitch JPype RTI backend."""
from __future__ import annotations

from typing import Any

from hla2010.backends.base import BackendInfo, BackendUnavailableError
from hla2010.rti import RTIBackendPlugin

from .factory import create_jpype_backend


def _discover_pitch_runtime() -> BackendInfo | None:
    try:
        from hla2010_rti_pitch_common import discover_pitch_runtime

        runtime = discover_pitch_runtime()
        return BackendInfo(name="Pitch", kind="vendor/pitch", details={"home": str(runtime.home)})
    except BackendUnavailableError:
        return None


def _pitch_jpype_backend_factory(options: dict[str, Any]):
    from hla2010_rti_pitch_common import discover_pitch_runtime, pitch_fedpro_local_settings_designator

    pitch_home = options.pop("pitch_home", None)
    runtime = discover_pitch_runtime(pitch_home)
    options.setdefault("rti_factory_name", "Federate Protocol")
    options.setdefault("connect_local_settings_designator", pitch_fedpro_local_settings_designator())
    config = options.pop("config", None) or runtime.jpype_config(**options)
    return create_jpype_backend(config)


def pitch_jpype_plugin() -> RTIBackendPlugin:
    return RTIBackendPlugin(
        name="pitch-jpype",
        aliases=("java-pitch-jpype",),
        family="pitch/java",
        description="Pitch Federate Protocol adapter through JPype.",
        create_backend=_pitch_jpype_backend_factory,
        discover=_discover_pitch_runtime,
    )


def plugin() -> RTIBackendPlugin:
    return pitch_jpype_plugin()


def backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    return (plugin(),)


__all__ = ["backend_plugins", "pitch_jpype_plugin", "plugin"]
