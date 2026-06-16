from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REST_SRC = ROOT / "packages" / "hla-transport-rest" / "src"


def test_split_rest_transport_package_exports_transport_surface():
    assert REST_SRC.exists()
    import hla.transports.rest
    from hla.transports.rest import RestTransport
    from hla.transports.rest import RestTransportConfig

    assert hla.transports.rest.RestTransport is RestTransport
    assert hla.transports.rest.RestTransportConfig is RestTransportConfig
    assert hla.transports.rest.PythonRTIRestServer.__module__.startswith(
        "hla.transports.rest"
    )


def test_split_rest_transport_package_exports_host_surface():
    from hla.transports.rest.client import RestTransportClientAdapter
    from hla.transports.rest.rest_transport_host import PythonRTIRestServer
    from hla.transports.rest.rest_transport_host import start_python_rest_server

    assert RestTransportClientAdapter.__module__ == "hla.transports.rest.client"
    assert PythonRTIRestServer.__module__ == "hla.transports.rest.rest_transport_host"
    assert start_python_rest_server.__module__ == "hla.transports.rest.rest_transport_host"
