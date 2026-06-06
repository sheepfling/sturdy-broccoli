"""Backend adapters for the HLA 1516.1-2010 Python API scaffold.

The base adapter has no optional dependencies. JPype and Py4J adapters are
imported explicitly from their modules so importing ``hla2010.backends`` does not
require a Java bridge package.
"""
from .base import (
    BackendConversionError,
    BackendInfo,
    BackendUnavailableError,
    CALLBACK_METHOD_NAMES,
    DelegatingRTIAmbassador,
    Invocation,
    RTIBackend,
    RTI_METHOD_NAMES,
    RecordingBackend,
    UnsupportedBackendService,
    lower_camel_to_snake,
    make_rti_ambassador,
    snake_to_lower_camel,
)
from .conversion import NativeHandleRegistry, NativeObjectRef, ValueConverter
from .certi import (
    CERTIBackend,
    CERTIConfig,
    CERTITransport,
    CERTITransportError,
    CERTITransportProtocol,
    build_certi_smoke_helper,
    create_certi_backend,
    create_certi_transport,
    TransportRequest as CERTITransportRequest,
    TransportResponse as CERTITransportResponse,
)
from .java_common import JavaBridge, JavaRTIBackend, JavaValueConverter, PythonFederateAmbassadorDispatcher
from .transport import RTITransport, SubprocessLineTransport, TransportError, TransportRequest, TransportResponse
from ..real_rti import (
    CERTIRuntime,
    PitchRuntime,
    RuntimeProcess,
    discover_certi_smoke_fom,
    discover_certi_runtime,
    discover_pitch_runtime,
    launch_certi_rtig,
    launch_pitch_py4j_gateway,
    launch_pitch_runtime,
)
from .python_rti import (
    InMemoryRTIEngine,
    PythonRTIBackend,
    PythonRTIConfig,
    SupplementalReflectInfo,
    SupplementalReceiveInfo,
    SupplementalRemoveInfo,
    create_python_backend,
    rti_ambassador as python_rti_ambassador,
)
from .rest_transport import RestTransport, RestTransportConfig, create_rest_transport

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
    "CERTIRuntime",
    "NativeHandleRegistry",
    "NativeObjectRef",
    "PitchRuntime",
    "PythonFederateAmbassadorDispatcher",
    "PythonRTIBackend",
    "PythonRTIConfig",
    "RTIBackend",
    "RTI_METHOD_NAMES",
    "RuntimeProcess",
    "RecordingBackend",
    "RTITransport",
    "GrpcTransport",
    "GrpcTransportConfig",
    "RestTransport",
    "RestTransportConfig",
    "TransportRequest",
    "TransportResponse",
    "build_certi_smoke_helper",
    "create_certi_backend",
    "create_certi_transport",
    "discover_certi_smoke_fom",
    "discover_certi_runtime",
    "discover_pitch_runtime",
    "launch_certi_rtig",
    "launch_pitch_py4j_gateway",
    "launch_pitch_runtime",
    "SupplementalReflectInfo",
    "SupplementalReceiveInfo",
    "SupplementalRemoveInfo",
    "UnsupportedBackendService",
    "ValueConverter",
    "create_python_backend",
    "create_grpc_transport",
    "create_rest_transport",
    "lower_camel_to_snake",
    "make_rti_ambassador",
    "python_rti_ambassador",
    "SubprocessLineTransport",
    "snake_to_lower_camel",
    "TransportError",
]


def __getattr__(name: str):
    if name in {"GrpcTransport", "GrpcTransportConfig", "create_grpc_transport"}:
        from .grpc_transport import GrpcTransport, GrpcTransportConfig, create_grpc_transport

        return {
            "GrpcTransport": GrpcTransport,
            "GrpcTransportConfig": GrpcTransportConfig,
            "create_grpc_transport": create_grpc_transport,
        }[name]
    raise AttributeError(name)
