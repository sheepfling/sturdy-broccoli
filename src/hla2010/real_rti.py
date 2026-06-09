"""Facade for real RTI runtime discovery and launch helpers."""
from __future__ import annotations

import subprocess  # noqa: F401
from pathlib import Path

from . import real_rti_pitch as _pitch
from .real_rti_certi import (
    CERTIRuntime,
    CERTIRuntimeProfile,
    discover_certi_runtime,
    discover_certi_runtime_profile,
    discover_certi_smoke_fom,
    launch_certi_rtig,
)
from .real_rti_pitch import (
    PitchLicenseRecord,
    PitchRuntime,
    discover_pitch_runtime,
    list_pitch_licenses,
    launch_pitch_py4j_gateway,
    pitch_connect_local_settings_designator,
    pitch_fedpro_local_settings_designator,
    prepare_pitch_user_home,
    _parse_pitch_license_list,
)
from .real_rti_portico import PorticoRuntime, discover_portico_runtime, launch_portico_py4j_gateway
from hla2010_rti_runtime_common import RuntimeProcess, reserve_tcp_port, wait_for_process_boot, wait_for_tcp_listener


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def launch_pitch_runtime(*args, **kwargs):
    return _pitch.launch_pitch_runtime(
        *args,
        _subprocess=subprocess,
        _wait_for_process_boot=wait_for_process_boot,
        _wait_for_tcp_listener=wait_for_tcp_listener,
        **kwargs,
    )


__all__ = [
    "CERTIRuntime",
    "CERTIRuntimeProfile",
    "PitchRuntime",
    "PitchLicenseRecord",
    "PorticoRuntime",
    "RuntimeProcess",
    "discover_certi_runtime",
    "discover_certi_runtime_profile",
    "discover_certi_smoke_fom",
    "discover_pitch_runtime",
    "discover_portico_runtime",
    "launch_certi_rtig",
    "launch_pitch_py4j_gateway",
    "launch_pitch_runtime",
    "launch_portico_py4j_gateway",
    "list_pitch_licenses",
    "pitch_connect_local_settings_designator",
    "pitch_fedpro_local_settings_designator",
    "prepare_pitch_user_home",
    "project_root",
    "reserve_tcp_port",
    "wait_for_process_boot",
    "wait_for_tcp_listener",
    "_parse_pitch_license_list",
]
