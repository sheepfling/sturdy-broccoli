from __future__ import annotations

from hla2010.handles import ParameterHandle
from hla2010_verification_harness import decode_handle_value_map, jsonable


class _BrokenAsDict:
    value = 7

    def as_dict(self):
        raise RuntimeError("java proxy method does not exist")


def test_jsonable_falls_back_when_as_dict_is_present_but_not_callable_for_real() -> None:
    assert jsonable(_BrokenAsDict()) == {"type": "_BrokenAsDict", "value": 7}


class _FakeRTI:
    def get_parameter_name(self, interaction, handle):
        assert interaction == "interaction"
        assert handle == ParameterHandle(5)
        return "Message"


def test_decode_handle_value_map_uses_receiver_parameter_names_and_decodes_bytes() -> None:
    payload = {ParameterHandle(5): b"near"}
    assert decode_handle_value_map(_FakeRTI(), "interaction", payload) == {"Message": "near"}
