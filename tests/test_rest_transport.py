from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from hla2010.api import FederateAmbassador
from hla2010.backends import make_rti_ambassador
from hla2010.backends.transport import TransportRequest, TransportResponse
from hla2010.backends.rest_transport import RestTransport, RestTransportConfig
from hla2010.enums import CallbackModel
from hla2010.rti import create_backend


class _RestHandler(BaseHTTPRequestHandler):
    requests: list[dict[str, object]] = []

    def do_POST(self):  # noqa: N802 - HTTP handler naming
        content_length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(content_length).decode("utf-8")
        data = json.loads(payload)
        self.requests.append(data)

        command = data.get("command")
        if command == "GET_HLA_VERSION":
            response = {"fields": ["HLA 1516.1-2010"], "metadata": {"fields": {"kind": "rest"}}}
        elif command == "CONNECT":
            response = {"fields": []}
        else:
            response = {"error": {"code": "RTIinternalError", "message": f"Unknown command: {command}"}}

        body = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args, **_kwargs):  # pragma: no cover - keep test output quiet
        return None


def _start_server() -> tuple[ThreadingHTTPServer, str]:
    _RestHandler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), _RestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_port}"


def test_rest_transport_round_trips_typed_envelopes():
    server, base_url = _start_server()
    try:
        transport = RestTransport(RestTransportConfig(base_url=base_url)).start()
        response = transport.request(TransportRequest(command="GET_HLA_VERSION", fields=("ignored",)))

        assert response.fields == ("HLA 1516.1-2010",)
        assert response.metadata == {"kind": "rest"}
        assert _RestHandler.requests[0]["command"] == "GET_HLA_VERSION"
        assert _RestHandler.requests[0]["metadata"] == {"fields": {}}

        direct = transport.request(TransportRequest(command="CONNECT", fields=(CallbackModel.HLA_EVOKED.name, "")))
        assert direct.fields == ()
    finally:
        server.shutdown()
        server.server_close()


def test_rest_transport_registers_with_backend_factory():
    server, base_url = _start_server()
    try:
        backend = create_backend("certi", transport={"kind": "rest", "base_url": base_url})
        rti = make_rti_ambassador(backend)

        assert rti.getHLAversion() == "HLA 1516.1-2010"
        rti.connect(FederateAmbassador(), CallbackModel.HLA_EVOKED)
        assert _RestHandler.requests[0]["command"] == "GET_HLA_VERSION"
        assert _RestHandler.requests[1]["command"] == "CONNECT"
        assert _RestHandler.requests[1]["metadata"] == {"fields": {}}
    finally:
        server.shutdown()
        server.server_close()
