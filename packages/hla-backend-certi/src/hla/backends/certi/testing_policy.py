"""CERTI-owned verification profile policy helpers."""
from __future__ import annotations

from pathlib import Path

from .real_rti_certi import discover_certi_smoke_fom


def prepare_certi_two_federate_profile() -> Path:
    """Validate the local CERTI runtime and return the smoke FOM path."""
    return discover_certi_smoke_fom()


__all__ = ["prepare_certi_two_federate_profile"]
