from __future__ import annotations

import pytest

from hla_x.runtime import HlaRuntimeFactory


REQUIRED_CODECS: tuple[str, ...] = (
    'HLAASCIIchar',
    'HLAASCIIstring',
    'HLAboolean',
    'HLAbyte',
    'HLAfloat32BE',
    'HLAfloat32LE',
    'HLAfloat64BE',
    'HLAfloat64LE',
    'HLAinteger16BE',
    'HLAinteger16LE',
    'HLAinteger32BE',
    'HLAinteger32LE',
    'HLAinteger64BE',
    'HLAinteger64LE',
    'HLAunsignedInteger16BE',
    'HLAunsignedInteger16LE',
    'HLAunsignedInteger32BE',
    'HLAunsignedInteger32LE',
    'HLAunsignedInteger64BE',
    'HLAunsignedInteger64LE',
    'HLAoctet',
    'HLAoctetPairBE',
    'HLAoctetPairLE',
    'HLAopaqueData',
    'HLAunicodeChar',
    'HLAunicodeString',
    'HLAfixedArray',
    'HLAvariableArray',
    'HLAfixedRecord',
    'HLAvariantRecord',
)


def test_factory_returns_matching_encoding_context(fake_runtime_config: dict[str, object]) -> None:
    factory = HlaRuntimeFactory.select(**fake_runtime_config)
    encoding = factory.create_encoding_context()

    assert encoding.edition == fake_runtime_config['edition']
    assert encoding.provider == fake_runtime_config['provider']
    assert encoding.registry is not None
####


def test_registry_resolves_required_builtins(fake_runtime_config: dict[str, object]) -> None:
    factory = HlaRuntimeFactory.select(**fake_runtime_config)
    registry = factory.create_encoding_context().registry

    missing = [name for name in REQUIRED_CODECS if not registry.has(name)]

    assert missing == []
####


def test_registry_rejects_unknown_encoding_name(fake_runtime_config: dict[str, object]) -> None:
    factory = HlaRuntimeFactory.select(**fake_runtime_config)
    registry = factory.create_encoding_context().registry

    with pytest.raises(Exception, match='Unknown|unsupported|not registered'):
        registry.get('HLAxDefinitelyNotAStandardCodec')
    ####
####
