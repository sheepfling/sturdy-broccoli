"""Spec plugin descriptor for IEEE 1516.1-2010."""
from __future__ import annotations

from hla.rti.plugin_api import HLASpec, SpecPlugin


def plugin() -> SpecPlugin:
    return SpecPlugin(
        spec=HLASpec(
            name="rti1516e",
            year=2010,
            standard="IEEE 1516.1",
            python_package="hla.rti1516e",
            java_package="hla.rti1516e",
            cpp_namespace="rti1516e",
            aliases=("1516e", "1516.1-2010", "2010", "hla2010"),
            capabilities=frozenset({"fdd", "mim", "encoding", "time"}),
        ),
        description="IEEE 1516.1-2010 HLA API",
    )


__all__ = ["plugin"]
