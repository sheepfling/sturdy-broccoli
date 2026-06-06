"""CERTI backend layers.

This package makes the CERTI split explicit:

- :mod:`hla2010.backends.certi.transport` handles transport/IO concerns.
- :mod:`hla2010.backends.certi.service_adapter` maps HLA invocations to that
  transport.

The flat ``hla2010.backends.certi_backend`` module remains as a compatibility
wrapper for existing imports.
"""
from .service_adapter import CERTIBackend, CERTIConfig, build_certi_smoke_helper, create_certi_backend
from .transport import CERTITransport, CERTITransportError, CERTITransportProtocol, create_certi_transport

__all__ = [
    "CERTIBackend",
    "CERTIConfig",
    "CERTITransport",
    "CERTITransportError",
    "CERTITransportProtocol",
    "build_certi_smoke_helper",
    "create_certi_backend",
    "create_certi_transport",
]
