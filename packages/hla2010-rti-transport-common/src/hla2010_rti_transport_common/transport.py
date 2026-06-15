"""Shared transport primitives for RTI backend adapters."""
from __future__ import annotations

import os
import select
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence
from urllib.parse import quote, unquote

from hla2010_rti_backend_common import BackendUnavailableError


def _encode_field(value: Any) -> str:
    return quote("" if value is None else str(value), safe="")


def _decode_field(value: str) -> str:
    return unquote(value)


class TransportError(RuntimeError):
    """Raised when a transport reports an application-level failure."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class TransportRequest:
    """Typed request envelope for backend transports."""

    command: str
    fields: tuple[Any, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TransportResponse:
    """Typed response envelope returned by backend transports."""

    fields: tuple[Any, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


class RTITransport(ABC):
    """Generic request/response transport used by backend adapters."""

    @abstractmethod
    def start(self) -> RTITransport:
        raise NotImplementedError

    @abstractmethod
    def request(self, request: TransportRequest) -> TransportResponse:
        raise NotImplementedError

    def close(self) -> None:
        return None


@dataclass
class SubprocessLineTransport(RTITransport):
    """Line-oriented request/response transport backed by a subprocess."""

    command: Sequence[str]
    env: Mapping[str, str] | None = None
    cwd: str | os.PathLike[str] | None = None
    text: bool = True
    default_timeout: float | None = None
    process: subprocess.Popen[str] | None = field(default=None, init=False)

    def start(self) -> SubprocessLineTransport:
        if self.process is not None:
            return self
        self.process = subprocess.Popen(
            [str(item) for item in self.command],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=self.text,
            env=dict(self.env) if self.env is not None else None,
            cwd=self.cwd,
            bufsize=1,
        )
        return self

    def request(self, request: TransportRequest) -> TransportResponse:
        process = self.process
        if process is None or process.stdin is None or process.stdout is None:
            raise BackendUnavailableError("Subprocess transport is not running")

        if process.poll() is not None:
            stderr = process.stderr.read() if process.stderr is not None else ""
            raise BackendUnavailableError(
                f"Subprocess transport exited with code {process.returncode}: {stderr.strip()}"
            )

        encoded = "\t".join([request.command, *(_encode_field(field) for field in request.fields)])
        process.stdin.write(encoded + "\n")
        process.stdin.flush()

        timeout = request.metadata.get("timeout") if request.metadata else None
        if timeout is None:
            timeout = self.default_timeout

        noise: list[str] = []
        while True:
            if timeout is not None:
                ready, _, _ = select.select([process.stdout], [], [], float(timeout))
                if not ready:
                    self.close()
                    raise BackendUnavailableError(
                        f"Subprocess transport timed out waiting for response to {request.command}"
                    )
            response = process.stdout.readline()
            if not response:
                stderr = process.stderr.read() if process.stderr is not None else ""
                noisy = " | ".join(line.strip() for line in noise if line.strip())
                raise BackendUnavailableError(
                    f"Subprocess transport produced no response. stdout noise: {noisy}. stderr: {stderr.strip()}"
                )

            parts = response.rstrip("\n").split("\t")
            if not parts:
                continue
            if parts[0] == "OK":
                return TransportResponse(fields=tuple(_decode_field(field) for field in parts[1:]))
            if parts[0] == "ERR":
                code = parts[1] if len(parts) >= 2 else "RTIinternalError"
                message = _decode_field(parts[2]) if len(parts) >= 3 else code
                raise TransportError(code, message)
            noise.append(response)

    def close(self) -> None:
        process = self.process
        if process is None:
            return
        try:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
        finally:
            self.process = None


__all__ = [
    "RTITransport",
    "SubprocessLineTransport",
    "TransportError",
    "TransportRequest",
    "TransportResponse",
]
