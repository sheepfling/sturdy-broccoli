"""Transport primitives for RTI backend adapters.

The backend layer in :mod:`hla2010.backends.base` works at the HLA service
level.  This module adds one layer lower: a generic request/response transport
that can be implemented with in-process calls, subprocess pipes, sockets,
gRPC, REST, or any other protocol that can carry a command name plus fields.

The goal is to keep transport concerns out of the service adapter.  Backends can
focus on translating HLA invocations, while a transport implementation handles
how bytes move between processes or machines.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import os
import subprocess
from typing import Any, Mapping, Sequence
from urllib.parse import quote, unquote

from .base import BackendUnavailableError


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


class RTITransport(ABC):
    """Generic request/response transport used by backend adapters."""

    @abstractmethod
    def start(self) -> "RTITransport":
        """Initialize transport resources."""
        raise NotImplementedError

    @abstractmethod
    def request(self, command: str, *fields: Any) -> list[str]:
        """Send one command and return decoded response fields."""
        raise NotImplementedError

    def close(self) -> None:
        """Release transport resources."""
        return None


@dataclass
class SubprocessLineTransport(RTITransport):
    """Line-oriented request/response transport backed by a subprocess.

    The process is expected to speak a simple tab-separated protocol:

    - each request line contains ``COMMAND`` plus encoded fields
    - each response line begins with ``OK`` or ``ERR``
    - ``OK`` responses return decoded fields
    - ``ERR`` responses raise :class:`TransportError`
    """

    command: Sequence[str]
    env: Mapping[str, str] | None = None
    cwd: str | os.PathLike[str] | None = None
    text: bool = True
    process: subprocess.Popen[str] | None = field(default=None, init=False)

    def start(self) -> "SubprocessLineTransport":
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

    def request(self, command: str, *fields: Any) -> list[str]:
        process = self.process
        if process is None or process.stdin is None or process.stdout is None:
            raise BackendUnavailableError("Subprocess transport is not running")

        if process.poll() is not None:
            stderr = process.stderr.read() if process.stderr is not None else ""
            raise BackendUnavailableError(
                f"Subprocess transport exited with code {process.returncode}: {stderr.strip()}"
            )

        encoded = "\t".join([command, *(_encode_field(field) for field in fields)])
        process.stdin.write(encoded + "\n")
        process.stdin.flush()

        noise: list[str] = []
        while True:
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
                return [_decode_field(field) for field in parts[1:]]
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
]
