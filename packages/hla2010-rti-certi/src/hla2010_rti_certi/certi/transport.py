"""CERTI transport package.

This module isolates CERTI transport concerns from the HLA service adapter. In
the current workspace the concrete transport is still the line-oriented
subprocess protocol used by the CERTI smoke helper, but this package is the
explicit seam for future socket, gRPC, or REST transports.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from hla2010_rti_transport_common import RTITransport as CERTITransportProtocol
from hla2010_rti_transport_common import SubprocessLineTransport, TransportRequest, TransportResponse
from hla2010_rti_transport_common import TransportError as CERTITransportError


@dataclass
class CERTITransportConfig:
    """Configuration for the current CERTI subprocess transport."""

    command: list[str]
    env: dict[str, str] | None = None
    cwd: str | os.PathLike[str] | None = None


CERTITransport = SubprocessLineTransport


def create_certi_transport(config: CERTITransportConfig) -> CERTITransportProtocol:
    return CERTITransport(command=config.command, env=config.env, cwd=config.cwd)


__all__ = [
    "CERTITransport",
    "CERTITransportConfig",
    "CERTITransportError",
    "CERTITransportProtocol",
    "TransportRequest",
    "TransportResponse",
    "create_certi_transport",
]
