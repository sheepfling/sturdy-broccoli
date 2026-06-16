"""ByteWrapper abstraction modeled after Java encoding/ByteWrapper.java.

This is a protocol/abstract surface; concrete RTIs provide storage and encoding behavior.
"""

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
    def put(self, src: bytes) -> None: ...

    @overload
    def put(self, src: bytes, offset: int, count: int) -> None: ...

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
    def slice(self) -> "ByteWrapper": ...
    @overload
    def slice(self, length: int) -> "ByteWrapper": ...
    @abstractmethod
    def slice(self, length: int | None = None) -> "ByteWrapper": ...

    @abstractmethod
    def toString(self) -> str: ...
