"""gRPC transport package for RTI backend adapters."""
from __future__ import annotations

from .python_server import (
    CERTIRTIGrpcServer,
    CERTIRTIGrpcServerConfig,
    PythonRTIGrpcServer,
    PythonRTIGrpcServerConfig,
    start_certi_grpc_server,
    start_python_grpc_server,
)
from .rti_transport_pb2 import DESCRIPTOR as RTI_TRANSPORT_PROTO_DESCRIPTOR
from .transport import GrpcTransport, GrpcTransportConfig, create_grpc_transport
import hla2010_rti_transport_grpc.rti_transport_pb2 as rti_transport_pb2

try:  # pragma: no cover - optional dependency guard
    import hla2010_rti_transport_grpc.rti_transport_pb2_grpc as rti_transport_pb2_grpc
except Exception:  # pragma: no cover - optional dependency guard
    rti_transport_pb2_grpc = None

__all__ = [
    "CERTIRTIGrpcServer",
    "CERTIRTIGrpcServerConfig",
    "GrpcTransport",
    "GrpcTransportConfig",
    "PythonRTIGrpcServer",
    "PythonRTIGrpcServerConfig",
    "RTI_TRANSPORT_PROTO_DESCRIPTOR",
    "create_grpc_transport",
    "rti_transport_pb2",
    "rti_transport_pb2_grpc",
    "start_certi_grpc_server",
    "start_python_grpc_server",
]
