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
    assert hla.transports.grpc.QuirkyVendorGrpcWireAdapter.__name__ == "QuirkyVendorGrpcWireAdapter"
    assert hla.transports.grpc.VendorGrpcTransport.__name__ == "VendorGrpcTransport"
    assert hla.transports.grpc.VendorGrpcTransportConfig.__name__ == "VendorGrpcTransportConfig"
    assert hla.transports.grpc.VendorGrpcWireAdapter.__name__ == "VendorGrpcWireAdapter"
    assert hla.transports.grpc.create_quirky_vendor_grpc_transport.__name__ == "create_quirky_vendor_grpc_transport"
    assert hla.transports.grpc.create_vendor_grpc_transport.__name__ == "create_vendor_grpc_transport"
    assert hasattr(hla.transports.grpc, "fedpro2010")
    assert hasattr(hla.transports.grpc, "fedpro2025")
    assert hasattr(hla.transports.grpc, "FEDPRO2010_PROTO_DESCRIPTOR")
    assert hasattr(hla.transports.grpc, "FEDPRO2025_PROTO_DESCRIPTOR")


def test_split_grpc_transport_package_exports_vendor_variant_as_transport_seam():
    import hla.transports.grpc

    assert hla.transports.grpc.QuirkyVendorGrpcWireAdapter.__module__ == "hla.transports.grpc.vendor_variant"
    assert hla.transports.grpc.VendorGrpcTransport.__module__ == "hla.transports.grpc.vendor_variant"
    assert hla.transports.grpc.VendorGrpcTransportConfig.__module__ == "hla.transports.grpc.vendor_variant"
    assert hla.transports.grpc.VendorGrpcWireAdapter.__module__ == "hla.transports.grpc.vendor_variant"
    assert hla.transports.grpc.create_quirky_vendor_grpc_transport.__module__ == "hla.transports.grpc.vendor_variant"
    assert hla.transports.grpc.create_vendor_grpc_transport.__module__ == "hla.transports.grpc.vendor_variant"
    assert "QuirkyVendorGrpcWireAdapter" in hla.transports.grpc.__all__
    assert "VendorGrpcTransport" in hla.transports.grpc.__all__
    assert "VendorGrpcTransportConfig" in hla.transports.grpc.__all__
    assert "VendorGrpcWireAdapter" in hla.transports.grpc.__all__
    assert "create_quirky_vendor_grpc_transport" in hla.transports.grpc.__all__
    assert "create_vendor_grpc_transport" in hla.transports.grpc.__all__


def test_split_grpc_transport_package_exposes_2025_server_as_hosted_route_surface():
    import hla.transports.grpc

    assert hla.transports.grpc.RTI2025GrpcServer.__module__ == "hla.transports.grpc.python_server_2025"
    assert hla.transports.grpc.RTI2025GrpcServerConfig.__module__ == "hla.transports.grpc.python_server_2025"
    assert hla.transports.grpc.start_2025_grpc_server.__module__ == "hla.transports.grpc.python_server_2025"
    assert "start_2025_grpc_server" in hla.transports.grpc.__all__
    assert "RTI2025GrpcServer" in hla.transports.grpc.__all__
    assert "RTI2025GrpcServerConfig" in hla.transports.grpc.__all__
    assert "create_rti_ambassador" not in hla.transports.grpc.__all__
    assert "create_python2025_backend" not in hla.transports.grpc.__all__
    assert "python1516_2025" not in hla.transports.grpc.__all__
    assert "shim" not in hla.transports.grpc.__all__


def test_split_grpc_transport_package_keeps_2025_hosted_server_backend_independent():
    pyproject_text = (ROOT / "packages" / "hla-transport-grpc" / "pyproject.toml").read_text(encoding="utf-8")
    server_2025_text = (
        ROOT / "packages" / "hla-transport-grpc" / "src" / "hla" / "transports" / "grpc" / "python_server_2025.py"
    ).read_text(encoding="utf-8")

    assert "hla-backend-python1516-2025" not in pyproject_text
    assert "hla-backend-shim" not in pyproject_text
    assert "hla.backends.python1516_2025" not in server_2025_text
    assert "hla.backends.shim" not in server_2025_text


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
