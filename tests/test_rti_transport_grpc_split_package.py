from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRPC_SRC = ROOT / "packages" / "hla-transport-grpc" / "src"


def test_split_grpc_transport_package_exports_transport_surface():
    assert GRPC_SRC.exists()
    import hla.transports.grpc

    assert hla.transports.grpc.GrpcTransport.__name__ == "GrpcTransport"
    assert hla.transports.grpc.GrpcTransportConfig.__name__ == "GrpcTransportConfig"
    assert hasattr(hla.transports.grpc, "rti_transport_pb2")
    assert hasattr(hla.transports.grpc, "rti_transport_pb2_grpc")


def test_legacy_grpc_transport_modules_are_removed():
    for module_name in (
        "hla.rti1516e.backends.grpc_transport",
        "hla.rti1516e.backends.grpc_transport.client",
        "hla.rti1516e.backends.grpc_transport.python_server",
        "hla.rti1516e.backends.grpc_transport.transport",
    ):
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        raise AssertionError(f"legacy compatibility module still imports: {module_name}")
