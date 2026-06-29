from __future__ import annotations

import struct

from hla.transports.common.hosted_server import _decode_logical_time, _logical_scalar


class _CustomTime:
    def __init__(self, value: int) -> None:
        self.value = value

    def encode(self) -> bytes:
        return struct.pack(">q", self.value)


class _CustomFactory:
    def decodeTime(self, data: bytes, offset: int = 0) -> _CustomTime:  # noqa: N802
        return _CustomTime(struct.unpack(">q", data[offset : offset + 8])[0])


def test_custom_logical_time_uses_encoded_wire_value() -> None:
    wire_value = _logical_scalar(_CustomTime(123))

    decoded = _decode_logical_time("CustomTime", wire_value, factory=_CustomFactory())

    assert wire_value == f"encoded:{struct.pack('>q', 123).hex()}"
    assert isinstance(decoded, _CustomTime)
    assert decoded.value == 123
