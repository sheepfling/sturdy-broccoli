"""Minimal HLA encoding elements for early tests and FOM adapters.

This module intentionally implements a small, practical subset first. It uses
big/little-endian names that match the public API names and can be extended to
full encoder-factory coverage.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field


class EncoderException(Exception):
    pass

class DecoderException(Exception):
    pass

class DataElement:
    def encode(self) -> bytes:
        raise NotImplementedError

    def decode(self, data: bytes) -> None:
        raise NotImplementedError

    def encoded_length(self) -> int:
        return len(self.encode())

@dataclass
class _Scalar(DataElement):
    value: object = 0
    _fmt: str = ''

    def encode(self) -> bytes:
        return struct.pack(self._fmt, self.value)

    def decode(self, data: bytes) -> None:
        self.value = struct.unpack(self._fmt, data[:struct.calcsize(self._fmt)])[0]

class HLAboolean(_Scalar):
    def __init__(self, value: bool = False):
        super().__init__(bool(value), '>B')

    def encode(self) -> bytes:
        return struct.pack('>B', 1 if self.value else 0)

    def decode(self, data: bytes) -> None:
        self.value = bool(struct.unpack('>B', data[:1])[0])

class HLAbyte(_Scalar):
    def __init__(self, value: int = 0):
        super().__init__(value, 'b')

class HLAoctet(_Scalar):
    def __init__(self, value: int = 0):
        super().__init__(value, 'B')

class HLAinteger16BE(_Scalar):
    def __init__(self, value: int = 0):
        super().__init__(value, '>h')
class HLAinteger16LE(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, '<h')
class HLAinteger32BE(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, '>i')
class HLAinteger32LE(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, '<i')
class HLAinteger64BE(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, '>q')
class HLAinteger64LE(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, '<q')
class HLAfloat32BE(_Scalar):
    def __init__(self, value: float=0.0): super().__init__(value, '>f')
class HLAfloat32LE(_Scalar):
    def __init__(self, value: float=0.0): super().__init__(value, '<f')
class HLAfloat64BE(_Scalar):
    def __init__(self, value: float=0.0): super().__init__(value, '>d')
class HLAfloat64LE(_Scalar):
    def __init__(self, value: float=0.0): super().__init__(value, '<d')
class HLAoctetPairBE(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, '>H')
class HLAoctetPairLE(_Scalar):
    def __init__(self, value: int=0): super().__init__(value, '<H')

@dataclass
class HLAASCIIchar(DataElement):
    value: str = '\x00'
    def encode(self) -> bytes: return self.value.encode('ascii')[:1]
    def decode(self, data: bytes) -> None: self.value = data[:1].decode('ascii')

@dataclass
class HLAunicodeChar(DataElement):
    value: str = '\x00'
    def encode(self) -> bytes: return self.value.encode('utf-16-be')[:2]
    def decode(self, data: bytes) -> None: self.value = data[:2].decode('utf-16-be')

@dataclass
class HLAASCIIstring(DataElement):
    value: str = ''
    def encode(self) -> bytes:
        payload = self.value.encode('ascii')
        return struct.pack('>I', len(payload)) + payload
    def decode(self, data: bytes) -> None:
        n = struct.unpack('>I', data[:4])[0]
        self.value = data[4:4+n].decode('ascii')

@dataclass
class HLAunicodeString(DataElement):
    value: str = ''
    def encode(self) -> bytes:
        payload = self.value.encode('utf-16-be')
        return struct.pack('>I', len(payload) // 2) + payload
    def decode(self, data: bytes) -> None:
        n = struct.unpack('>I', data[:4])[0]
        self.value = data[4:4+(n * 2)].decode('utf-16-be')

@dataclass
class HLAopaqueData(DataElement):
    value: bytes = b''
    def encode(self) -> bytes: return struct.pack('>I', len(self.value)) + self.value
    def decode(self, data: bytes) -> None:
        n = struct.unpack('>I', data[:4])[0]
        self.value = data[4:4+n]

@dataclass
class HLAfixedRecord(DataElement):
    fields: list[DataElement] = field(default_factory=list)
    def encode(self) -> bytes: return b''.join(f.encode() for f in self.fields)
    def decode(self, data: bytes) -> None:
        offset = 0
        for f in self.fields:
            f.decode(data[offset:])
            offset += f.encoded_length()

@dataclass
class HLAfixedArray(DataElement):
    elements: list[DataElement] = field(default_factory=list)
    def encode(self) -> bytes: return b''.join(e.encode() for e in self.elements)
    def decode(self, data: bytes) -> None:
        offset = 0
        for e in self.elements:
            e.decode(data[offset:])
            offset += e.encoded_length()

@dataclass
class HLAvariableArray(DataElement):
    elements: list[DataElement] = field(default_factory=list)
    def encode(self) -> bytes: return struct.pack('>I', len(self.elements)) + b''.join(e.encode() for e in self.elements)
    def decode(self, data: bytes) -> None:
        # Caller must provide pre-sized element instances; we decode up to that count.
        count = struct.unpack('>I', data[:4])[0]
        if count != len(self.elements):
            raise DecoderException(f'variable array expected {len(self.elements)} elements, encoded {count}')
        offset = 4
        for e in self.elements:
            e.decode(data[offset:])
            offset += e.encoded_length()

__all__ = [
    "DataElement",
    "DecoderException",
    "EncoderException",
    "HLAASCIIchar",
    "HLAASCIIstring",
    "HLAboolean",
    "HLAbyte",
    "HLAfixedArray",
    "HLAfixedRecord",
    "HLAfloat32BE",
    "HLAfloat32LE",
    "HLAfloat64BE",
    "HLAfloat64LE",
    "HLAinteger16BE",
    "HLAinteger16LE",
    "HLAinteger32BE",
    "HLAinteger32LE",
    "HLAinteger64BE",
    "HLAinteger64LE",
    "HLAoctet",
    "HLAoctetPairBE",
    "HLAoctetPairLE",
    "HLAopaqueData",
    "HLAunicodeChar",
    "HLAunicodeString",
    "HLAvariableArray",
]
