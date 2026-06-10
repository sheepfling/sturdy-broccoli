"""Repo-level runtime launcher helpers for the two-federate suite."""

from __future__ import annotations

from importlib import import_module
from typing import Any, Callable

RuntimeProfileLauncher = Callable[[], Any]


def _load_launcher(module_name: str, attribute_name: str) -> RuntimeProfileLauncher | None:
    try:
        module = import_module(module_name)
    except ModuleNotFoundError:
        return None
    launcher = getattr(module, attribute_name, None)
    if launcher is None:
        return None
    if not callable(launcher):
        raise TypeError(f"{module_name}.{attribute_name} is not callable")
    return launcher


def build_two_federate_runtime_launchers() -> dict[str, RuntimeProfileLauncher]:
    """Return the vendor-aware launcher registry used by repo-level suites."""
    launchers: dict[str, RuntimeProfileLauncher] = {}

    certi_launcher = _load_launcher(
        "hla2010_rti_certi.testing_policy",
        "prepare_certi_two_federate_profile",
    )
    if certi_launcher is not None:
        launchers["certi"] = certi_launcher

    pitch_launcher = _load_launcher(
        "hla2010_rti_pitch_common.testing_policy",
        "launch_pitch_two_federate_profile",
    )
    if pitch_launcher is not None:
        launchers["pitch-jpype"] = pitch_launcher
        launchers["pitch-py4j"] = pitch_launcher

    return launchers


__all__ = ["build_two_federate_runtime_launchers"]
