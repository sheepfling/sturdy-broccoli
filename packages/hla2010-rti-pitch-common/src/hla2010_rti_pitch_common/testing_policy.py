"""Pitch-owned verification profile policy helpers."""
from __future__ import annotations

from .real_rti_pitch import PitchRuntime, launch_pitch_runtime


def launch_pitch_two_federate_profile() -> PitchRuntime:
    """Launch the shared Pitch runtime used by two-federate verification."""
    return launch_pitch_runtime()


__all__ = ["launch_pitch_two_federate_profile"]
