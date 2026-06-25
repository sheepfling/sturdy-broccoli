"""Strict real-Pitch 2010 micro lane for SISO showcase rows."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .siso_pitch_micro_parity import SisoPitchMicroParityPaths, write_siso_pitch_micro_parity_artifacts


REAL_PITCH_2010_BACKENDS = ("pitch-jpype", "pitch-py4j")


def write_siso_pitch_2010_micro_strict_artifacts(
    output_dir: str | Path,
    *,
    backends: Sequence[str] | None = None,
) -> SisoPitchMicroParityPaths:
    selected_backends = tuple(backends or REAL_PITCH_2010_BACKENDS)
    return write_siso_pitch_micro_parity_artifacts(
        output_dir,
        backends=selected_backends,
        require_real_vendor_preflight=True,
        real_vendor_only=True,
    )


__all__ = ["REAL_PITCH_2010_BACKENDS", "write_siso_pitch_2010_micro_strict_artifacts"]
