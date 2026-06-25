"""REST transport package for RTI backend adapters."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from hla.backends.common import BackendUnavailableError
from hla.transports.common import RTITransport, TransportRequest, TransportResponse, register_transport_factory
from .client import RestTransportClientAdapter
from .rest_transport_host import (
    CERTIRestServer,
    CERTIRestServerConfig,
    Python2025RestServer,
    Python2025RestServerConfig,
    PythonRTIRestServer,
    PythonRTIRestServerConfig,
    RTI2025RestServer,
    RTI2025RestServerConfig,
    start_2025_rest_server,
    start_certi_rest_server,
    start_python_rest_server,
)


@dataclass(frozen=True)
class RestTransportConfig:
    """Configuration for :class:`RestTransport`."""

    base_url: str
    request_path: str = "/rti/request"
    timeout: float = 30.0
    headers: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        if not self.base_url:
            raise ValueError("base_url must be provided")
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must use http:// or https://")


class RestTransport(RTITransport):
    """Typed JSON-over-HTTP transport for HLA backend adapters."""

    def __init__(self, config: RestTransportConfig):
        self.config = config
        self._started = False
        self.client_adapter = RestTransportClientAdapter()

    def start(self) -> "RestTransport":
        self._started = True
        return self

    def request(self, request: TransportRequest) -> TransportResponse:
        if not self._started:
            self.start()

        url = urljoin(self.config.base_url.rstrip("/") + "/", self.config.request_path.lstrip("/"))
        payload = self.client_adapter.encode_request(request)
        headers = {"Content-Type": "application/json", **dict(self.config.headers or {})}
        http_request = Request(url, data=payload, headers=headers, method="POST")

        try:
            with urlopen(http_request, timeout=self.config.timeout) as response:
                body = response.read().decode("utf-8")
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            self.client_adapter.raise_for_error_body(body, default_code=f"HTTP{exc.code}")
        except URLError as exc:
            raise BackendUnavailableError(f"REST transport could not reach {url}: {exc.reason}") from exc

        return self.client_adapter.decode_response(body)


def create_rest_transport(config: RestTransportConfig) -> RestTransport:
    return RestTransport(config)


def _rest_transport_config_from_spec(spec) -> RestTransportConfig:  # noqa: ANN001 - transport registry protocol
    options = dict(spec.options)
    options.pop("schema", None)
    return RestTransportConfig(**options)


register_transport_factory("rest", lambda spec: create_rest_transport(_rest_transport_config_from_spec(spec)))
register_transport_factory("http-json", lambda spec: create_rest_transport(_rest_transport_config_from_spec(spec)))


__all__ = [
    "CERTIRestServer",
    "CERTIRestServerConfig",
    "Python2025RestServer",
    "Python2025RestServerConfig",
    "PythonRTIRestServer",
    "RTI2025RestServer",
    "RTI2025RestServerConfig",
    "PythonRTIRestServerConfig",
    "RestTransport",
    "RestTransportClientAdapter",
    "RestTransportConfig",
    "create_rest_transport",
    "start_2025_rest_server",
    "start_certi_rest_server",
    "start_python_rest_server",
]
