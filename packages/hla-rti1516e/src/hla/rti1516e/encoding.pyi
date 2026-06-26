from __future__ import annotations

from typing import Generic, TypeVar

TScalar = TypeVar("TScalar")

class EncoderException(Exception): ...
class DecoderException(Exception): ...

class DataElement:
    def encode(self) -> bytes: ...
    def decode(self, data: bytes) -> None: ...
    def encoded_length(self) -> int: ...

class _Scalar(DataElement, Generic[TScalar]):
    value: TScalar
    _fmt: str
    def __init__(self, value: TScalar, _fmt: str = "") -> None: ...

class HLAboolean(_Scalar[bool]):
    value: bool
    def __init__(self, value: bool = False) -> None: ...

class HLAbyte(_Scalar[int]):
    value: int
    def __init__(self, value: int = 0) -> None: ...

class HLAoctet(_Scalar[int]):
    value: int
    def __init__(self, value: int = 0) -> None: ...

class HLAinteger16BE(_Scalar[int]):
    value: int
    def __init__(self, value: int = 0) -> None: ...

class HLAinteger16LE(_Scalar[int]):
    value: int
    def __init__(self, value: int = 0) -> None: ...

class HLAinteger32BE(_Scalar[int]):
    value: int
    def __init__(self, value: int = 0) -> None: ...

class HLAinteger32LE(_Scalar[int]):
    value: int
    def __init__(self, value: int = 0) -> None: ...

class HLAinteger64BE(_Scalar[int]):
    value: int
    def __init__(self, value: int = 0) -> None: ...

class HLAinteger64LE(_Scalar[int]):
    value: int
    def __init__(self, value: int = 0) -> None: ...

class HLAfloat32BE(_Scalar[float]):
    value: float
    def __init__(self, value: float = 0.0) -> None: ...

class HLAfloat32LE(_Scalar[float]):
    value: float
    def __init__(self, value: float = 0.0) -> None: ...

class HLAfloat64BE(_Scalar[float]):
    value: float
    def __init__(self, value: float = 0.0) -> None: ...

class HLAfloat64LE(_Scalar[float]):
    value: float
    def __init__(self, value: float = 0.0) -> None: ...

class HLAoctetPairBE(_Scalar[int]):
    value: int
    def __init__(self, value: int = 0) -> None: ...

class HLAoctetPairLE(_Scalar[int]):
    value: int
    def __init__(self, value: int = 0) -> None: ...

class HLAASCIIchar(DataElement):
    value: str
    def __init__(self, value: str = "\x00") -> None: ...

class HLAunicodeChar(DataElement):
    value: str
    def __init__(self, value: str = "\x00") -> None: ...

class HLAASCIIstring(DataElement):
    value: str
    def __init__(self, value: str = "") -> None: ...

class HLAunicodeString(DataElement):
    value: str
    def __init__(self, value: str = "") -> None: ...

class HLAopaqueData(DataElement):
    value: bytes
    def __init__(self, value: bytes = b"") -> None: ...

class HLAfixedRecord(DataElement):
    fields: list[DataElement]
    def __init__(self, fields: list[DataElement] = ...) -> None: ...

class HLAfixedArray(DataElement):
    elements: list[DataElement]
    def __init__(self, elements: list[DataElement] = ...) -> None: ...

class HLAvariableArray(DataElement):
    elements: list[DataElement]
    def __init__(self, elements: list[DataElement] = ...) -> None: ...

__all__: list[str]
