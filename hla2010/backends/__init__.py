"""Backend abstractions and a minimal canonical import surface.

Import backend-family specifics from their package modules:

- ``hla2010.backends.python``
- ``hla2010.backends.certi``
- ``hla2010.backends.grpc_transport``
- ``hla2010.backends.jpype``
- ``hla2010.backends.py4j``
- ``hla2010.backends.certi_java``
"""
from __future__ import annotations

from .base import (
    CALLBACK_METHOD_NAMES,
    RTI_METHOD_NAMES,
    BackendConversionError,
    BackendInfo,
    BackendUnavailableError,
    DelegatingRTIAmbassador,
    Invocation,
    RecordingBackend,
    RTIBackend,
    UnsupportedBackendService,
    lower_camel_to_snake,
    make_rti_ambassador,
    snake_to_lower_camel,
)
from .certi import (
    CERTIBackend,
    CERTIConfig,
    CERTITransport,
    CERTITransportError,
    CERTITransportProtocol,
    TransportRequest as CERTITransportRequest,
    TransportResponse as CERTITransportResponse,
    build_certi_smoke_helper,
    create_certi_backend,
    create_certi_transport,
)
from .conversion import NativeHandleRegistry, NativeObjectRef, ValueConverter
from .java_common import JavaBridge, JavaRTIBackend, JavaValueConverter, PythonFederateAmbassadorDispatcher
from .python import (
    InMemoryRTIEngine,
    PythonRTIBackend,
    PythonRTIConfig,
    SupplementalReceiveInfo,
    SupplementalReflectInfo,
    SupplementalRemoveInfo,
    create_python_ambassador,
    create_python_backend,
    rti_ambassador as python_ambassador,
)
from .rest_transport import RestTransport, RestTransportConfig, create_rest_transport
from .transport import RTITransport, SubprocessLineTransport, TransportError, TransportRequest, TransportResponse

__all__ = [
    "BackendConversionError",
    "BackendInfo",
    "BackendUnavailableError",
    "CALLBACK_METHOD_NAMES",
    "CERTIBackend",
    "CERTIConfig",
    "CERTITransport",
    "CERTITransportError",
    "CERTITransportProtocol",
    "CERTITransportRequest",
    "CERTITransportResponse",
    "DelegatingRTIAmbassador",
    "InMemoryRTIEngine",
    "Invocation",
    "JavaBridge",
    "JavaRTIBackend",
    "JavaValueConverter",
    "NativeHandleRegistry",
    "NativeObjectRef",
    "PythonFederateAmbassadorDispatcher",
    "PythonRTIBackend",
    "PythonRTIConfig",
    "RTIBackend",
    "RTITransport",
    "RTI_METHOD_NAMES",
    "RecordingBackend",
    "RestTransport",
    "RestTransportConfig",
    "SubprocessLineTransport",
    "SupplementalReceiveInfo",
    "SupplementalReflectInfo",
    "SupplementalRemoveInfo",
    "TransportError",
    "TransportRequest",
    "TransportResponse",
    "UnsupportedBackendService",
    "ValueConverter",
    "build_certi_smoke_helper",
    "create_certi_backend",
    "create_certi_transport",
    "create_python_ambassador",
    "create_python_backend",
    "create_rest_transport",
    "lower_camel_to_snake",
    "make_rti_ambassador",
    "python_ambassador",
    "snake_to_lower_camel",
]
