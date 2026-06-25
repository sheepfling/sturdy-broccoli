"""gRPC transport package for RTI backend adapters."""
from __future__ import annotations

import importlib
from typing import Any

__all__ = [
    "CERTIRTIGrpcServer",
    "CERTIRTIGrpcServerConfig",
    "FEDPRO2010_PROTO_DESCRIPTOR",
    "FEDPRO2025_PROTO_DESCRIPTOR",
    "GrpcTransport",
    "GrpcTransportConfig",
    "RTI2025GrpcServer",
    "RTI2025GrpcServerConfig",
    "PythonRTIGrpcServer",
    "PythonRTIGrpcServerConfig",
    "QuirkyVendorGrpcWireAdapter",
    "VendorGrpcTransport",
    "VendorGrpcTransportConfig",
    "VendorGrpcWireAdapter",
    "create_grpc_transport",
    "create_quirky_vendor_grpc_transport",
    "create_vendor_grpc_transport",
    "fedpro2010",
    "fedpro2025",
    "start_2025_grpc_server",
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
    "RTI2025GrpcServer": "hla.transports.grpc.python_server_2025",
    "RTI2025GrpcServerConfig": "hla.transports.grpc.python_server_2025",
    "start_2025_grpc_server": "hla.transports.grpc.python_server_2025",
    "GrpcTransport": "hla.transports.grpc.transport",
    "GrpcTransportConfig": "hla.transports.grpc.transport",
    "create_grpc_transport": "hla.transports.grpc.transport",
    "QuirkyVendorGrpcWireAdapter": "hla.transports.grpc.vendor_variant",
    "VendorGrpcTransport": "hla.transports.grpc.vendor_variant",
    "VendorGrpcTransportConfig": "hla.transports.grpc.vendor_variant",
    "VendorGrpcWireAdapter": "hla.transports.grpc.vendor_variant",
    "create_quirky_vendor_grpc_transport": "hla.transports.grpc.vendor_variant",
    "create_vendor_grpc_transport": "hla.transports.grpc.vendor_variant",
}


def __getattr__(name: str) -> Any:
    if name == "fedpro2010":
        return importlib.import_module("hla.transports.grpc.fedpro2010")
    if name == "fedpro2025":
        return importlib.import_module("hla.transports.grpc.fedpro2025")
    if name == "FEDPRO2010_PROTO_DESCRIPTOR":
        return importlib.import_module("hla.transports.grpc.fedpro2010.RTIambassador_pb2").DESCRIPTOR
    if name == "FEDPRO2025_PROTO_DESCRIPTOR":
        return importlib.import_module("hla.transports.grpc.fedpro2025.RTIambassador_2025_pb2").DESCRIPTOR
    module_name = _EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError(name)
    return getattr(importlib.import_module(module_name), name)
