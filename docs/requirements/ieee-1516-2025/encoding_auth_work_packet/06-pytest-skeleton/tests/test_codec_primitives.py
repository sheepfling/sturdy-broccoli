from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from hla_x.runtime import HlaRuntimeFactory


@pytest.mark.parametrize(
    ('codec_name', 'value', 'expected_hex'),
    [
        ('HLAinteger16BE', 1, '0001'),
        ('HLAinteger16LE', 1, '0100'),
        ('HLAinteger32BE', 1, '00000001'),
        ('HLAinteger32LE', 1, '01000000'),
        ('HLAinteger64BE', 1, '0000000000000001'),
        ('HLAinteger64LE', 1, '0100000000000000'),
        ('HLAfloat32BE', 1.0, '3f800000'),
        ('HLAfloat64BE', 1.0, '3ff0000000000000'),
    ],
)
def test_primitive_known_bytes(
    fake_runtime_config: dict[str, object],
    codec_name: str,
    value: int | float,
    expected_hex: str,
) -> None:
    factory = HlaRuntimeFactory.select(**fake_runtime_config)
    codec = factory.create_encoding_context().registry.get(codec_name)

    encoded = codec.encode(value)

    assert encoded.hex() == expected_hex
####


def test_primitive_vectors_round_trip(
    fake_runtime_config: dict[str, object],
    primitive_vectors_path: Path,
) -> None:
    factory = HlaRuntimeFactory.select(**fake_runtime_config)
    registry = factory.create_encoding_context().registry
    vectors: dict[str, list[dict[str, Any]]] = yaml.safe_load(primitive_vectors_path.read_text())

    for codec_name, cases in vectors.items():
        codec = registry.get(codec_name)
        for case in cases:
            value = case.get('value')
            if value is None and 'value_hex' in case:
                value = bytes.fromhex(case['value_hex'])
            ####
            result = codec.decode(codec.encode(value), strict=True)
            assert result.value == value
        ####
    ####
####


def test_decode_rejects_truncated_bytes(fake_runtime_config: dict[str, object]) -> None:
    factory = HlaRuntimeFactory.select(**fake_runtime_config)
    codec = factory.create_encoding_context().registry.get('HLAinteger32BE')

    with pytest.raises(Exception, match='truncated|malformed|length'):
        codec.decode(bytes.fromhex('000001'), strict=True)
    ####
####
