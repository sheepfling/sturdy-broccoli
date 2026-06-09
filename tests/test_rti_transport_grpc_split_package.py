from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRPC_SRC = ROOT / "packages" / "hla2010-rti-transport-grpc" / "src"


def test_split_grpc_transport_package_exports_transport_surface():
    sys.path.insert(0, str(GRPC_SRC))
    try:
        import hla2010_rti_transport_grpc
        from hla2010.backends.grpc_transport import GrpcTransport as OldTransport
        from hla2010.backends.grpc_transport import GrpcTransportConfig as OldConfig

        assert hla2010_rti_transport_grpc.GrpcTransport is OldTransport
        assert hla2010_rti_transport_grpc.GrpcTransportConfig is OldConfig
        assert hasattr(hla2010_rti_transport_grpc, "rti_transport_pb2")
        assert hasattr(hla2010_rti_transport_grpc, "rti_transport_pb2_grpc")
    finally:
        sys.path.remove(str(GRPC_SRC))


def test_legacy_grpc_transport_modules_are_compatibility_facades():
    sys.path.insert(0, str(GRPC_SRC))
    try:
        from hla2010.backends.grpc_transport.client import GrpcTransportClientAdapter as OldClientAdapter
        from hla2010.backends.grpc_transport.python_server import PythonRTIGrpcServer as OldServer
        from hla2010.backends.grpc_transport.transport import GrpcTransport as OldTransport
        from hla2010_rti_transport_grpc.client import GrpcTransportClientAdapter
        from hla2010_rti_transport_grpc.python_server import PythonRTIGrpcServer
        from hla2010_rti_transport_grpc.transport import GrpcTransport

        assert OldClientAdapter is GrpcTransportClientAdapter
        assert OldServer is PythonRTIGrpcServer
        assert OldTransport is GrpcTransport
    finally:
        sys.path.remove(str(GRPC_SRC))
