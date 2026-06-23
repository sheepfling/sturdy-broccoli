"""ByteWrapper abstraction modeled after Java hla/rti1516e/encoding/ByteWrapper.java.

This is a protocol/abstract surface; concrete RTIs provide storage and encoding behavior.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import overload

BytesLike = bytes | bytearray | memoryview


class ByteWrapper(ABC):
    @abstractmethod
    def reassign(self, buffer: bytearray, offset: int, length: int) -> None: ...

    @abstractmethod
    def reset(self) -> None: ...

    @abstractmethod
    def verify(self, length: int) -> None: ...

    @abstractmethod
    def getInt(self) -> int: ...

    @overload
    def get(self) -> int: ...
    @overload
    def get(self, dest: bytearray) -> None: ...  # dubious
    @abstractmethod
    def get(self, dest: bytearray | None = None) -> int | None: ...

    @abstractmethod
    def putInt(self, value: int) -> None: ...

    @overload
    def put(self, b: int) -> None: ...

    @overload
    def put(self, src: BytesLike) -> None: ...

    @overload
    def put(self, src: BytesLike, offset: int, count: int) -> None: ...

    # Match the 2025 protocol exactly; implementation is intentionally free to
    # accept an optional offset and count on top-level writes.
    @abstractmethod
    def put(
        self,
        value: int | BytesLike,
        offset: int | None = None,
        count: int | None = None,
    ) -> None: ...

    @abstractmethod
    def array(self) -> bytearray: ...

    @abstractmethod
    def getPos(self) -> int: ...

    @abstractmethod
    def remaining(self) -> int: ...

    @abstractmethod
    def advance(self, n: int) -> None: ...

    @abstractmethod
    def align(self, n: int) -> None: ...

    @overload
    def slice(self) -> ByteWrapper: ...
    @overload
    def slice(self, length: int) -> ByteWrapper: ...
    @abstractmethod
    def slice(self, length: int | None = None) -> ByteWrapper: ...

    @abstractmethod
    def toString(self) -> str: ...
