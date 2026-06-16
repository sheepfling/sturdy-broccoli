"""Spec plugin descriptor for IEEE 1516.1-2025."""
from __future__ import annotations

from hla.rti.plugin_api import HLASpec, SpecPlugin


def plugin() -> SpecPlugin:
    return SpecPlugin(
        spec=HLASpec(
            name="rti1516_2025",
            year=2025,
            standard="IEEE 1516.1",
            python_package="hla.rti1516_2025",
            java_package="hla.rti1516_2025",
            cpp_namespace="rti1516_2025",
            aliases=("1516.1-2025", "1516-2025", "1516_2025", "2025", "hla4", "hla2025"),
            capabilities=frozenset({"fdd", "mim", "encoding", "time", "auth", "fedpro"}),
        ),
        description="IEEE 1516.1-2025 HLA API",
    )


__all__ = ["plugin"]
