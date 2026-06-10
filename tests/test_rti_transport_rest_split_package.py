from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REST_SRC = ROOT / "packages" / "hla2010-rti-transport-rest" / "src"


def test_split_rest_transport_package_exports_transport_surface():
    assert REST_SRC.exists()
    import hla2010_rti_transport_rest
    from hla2010_rti_transport_rest import RestTransport
    from hla2010_rti_transport_rest import RestTransportConfig

    assert hla2010_rti_transport_rest.RestTransport is RestTransport
    assert hla2010_rti_transport_rest.RestTransportConfig is RestTransportConfig
    assert hla2010_rti_transport_rest.PythonRTIRestServer.__module__.startswith(
        "hla2010_rti_transport_rest"
    )


def test_split_rest_transport_package_exports_host_surface():
    from hla2010_rti_transport_rest.client import RestTransportClientAdapter
    from hla2010_rti_transport_rest.rest_transport_host import PythonRTIRestServer
    from hla2010_rti_transport_rest.rest_transport_host import start_python_rest_server

    assert RestTransportClientAdapter.__module__ == "hla2010_rti_transport_rest.client"
    assert PythonRTIRestServer.__module__ == "hla2010_rti_transport_rest.rest_transport_host"
    assert start_python_rest_server.__module__ == "hla2010_rti_transport_rest.rest_transport_host"
