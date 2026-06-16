"""gRPC transport package for RTI backend adapters."""
from __future__ import annotations

import importlib
from typing import Any

__all__ = [
    "CERTIRTIGrpcServer",
    "CERTIRTIGrpcServerConfig",
    "FEDPRO2010_PROTO_DESCRIPTOR",
    "GrpcTransport",
    "GrpcTransportConfig",
    "PythonRTIGrpcServer",
    "PythonRTIGrpcServerConfig",
    "create_grpc_transport",
    "fedpro2010",
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
    if name == "fedpro2010":
        return importlib.import_module("hla.transports.grpc.fedpro2010")
    if name == "FEDPRO2010_PROTO_DESCRIPTOR":
        return importlib.import_module("hla.transports.grpc.fedpro2010.RTIambassador_pb2").DESCRIPTOR
    module_name = _EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError(name)
    return getattr(importlib.import_module(module_name), name)
