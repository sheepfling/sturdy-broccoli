"""gRPC transport package for RTI backend adapters."""
from __future__ import annotations

import importlib
from typing import Any

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

_EXPORT_MODULES = {
    "CERTIRTIGrpcServer": "hla.transports.grpc.python_server",
    "CERTIRTIGrpcServerConfig": "hla.transports.grpc.python_server",
    "PythonRTIGrpcServer": "hla.transports.grpc.python_server",
    "PythonRTIGrpcServerConfig": "hla.transports.grpc.python_server",
    "start_certi_grpc_server": "hla.transports.grpc.python_server",
    "start_python_grpc_server": "hla.transports.grpc.python_server",
    "GrpcTransport": "hla.transports.grpc.transport",
    "GrpcTransportConfig": "hla.transports.grpc.transport",
    "create_grpc_transport": "hla.transports.grpc.transport",
}


def __getattr__(name: str) -> Any:
    if name in {"rti_transport_pb2", "rti_transport_pb2_grpc"}:
        return importlib.import_module(f"hla.transports.grpc.{name}")
    if name == "RTI_TRANSPORT_PROTO_DESCRIPTOR":
        return importlib.import_module("hla.transports.grpc.rti_transport_pb2").DESCRIPTOR
    module_name = _EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError(name)
    return getattr(importlib.import_module(module_name), name)
