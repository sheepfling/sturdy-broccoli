from __future__ import annotations

import pytest

from hla2010_rti_java_common.java_common import invoke_java_enum_constant, java_hla_enum_simple_name


class _RecordingJavaEnum:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def valueOf(self, member_name: str) -> str:  # noqa: N802
        self.calls.append(member_name)
        return f"enum:{member_name}"


def test_java_hla_enum_simple_name_maps_supported_hla_enums() -> None:
    assert java_hla_enum_simple_name("hla.rti1516e.CallbackModel") == "CallbackModel"
    assert java_hla_enum_simple_name("hla.rti1516e.ServiceGroup") == "ServiceGroup"


def test_java_hla_enum_simple_name_rejects_unknown_enum_class() -> None:
    with pytest.raises(AttributeError, match="hla.rti1516e.UnknownEnum"):
        java_hla_enum_simple_name("hla.rti1516e.UnknownEnum")


def test_invoke_java_enum_constant_uses_value_of_api() -> None:
    enum_class = _RecordingJavaEnum()

    assert invoke_java_enum_constant(enum_class, "HLA_EVOKED") == "enum:HLA_EVOKED"
    assert enum_class.calls == ["HLA_EVOKED"]
