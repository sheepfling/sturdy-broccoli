from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REST_SRC = ROOT / "packages" / "hla2010-rti-transport-rest" / "src"


def test_split_rest_transport_package_exports_transport_surface():
    sys.path.insert(0, str(REST_SRC))
    try:
        import hla2010_rti_transport_rest
        from hla2010.backends.rest_transport import RestTransport as OldTransport
        from hla2010.backends.rest_transport import RestTransportConfig as OldConfig
        from hla2010.backends.rest_transport_host import PythonRTIRestServer as OldServer

        assert hla2010_rti_transport_rest.RestTransport is OldTransport
        assert hla2010_rti_transport_rest.RestTransportConfig is OldConfig
        assert hla2010_rti_transport_rest.PythonRTIRestServer is OldServer
    finally:
        sys.path.remove(str(REST_SRC))


def test_legacy_rest_transport_modules_are_compatibility_facades():
    sys.path.insert(0, str(REST_SRC))
    try:
        from hla2010.backends.rest_transport.client import RestTransportClientAdapter as OldClientAdapter
        from hla2010.backends.rest_transport_host import start_python_rest_server as old_start_python_rest_server
        from hla2010_rti_transport_rest.client import RestTransportClientAdapter
        from hla2010_rti_transport_rest.rest_transport_host import start_python_rest_server

        assert OldClientAdapter is RestTransportClientAdapter
        assert old_start_python_rest_server is start_python_rest_server
    finally:
        sys.path.remove(str(REST_SRC))
