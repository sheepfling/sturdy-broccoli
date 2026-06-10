"""Transport-hosted Python RTI server for proving the gRPC wire path."""
from __future__ import annotations

from concurrent import futures
from dataclasses import dataclass, field
from typing import Any, Mapping

from hla2010_rti_python.engine import InMemoryRTIEngine
from hla2010_rti_python.factory import rti_ambassador
from hla2010_rti_python.state import PythonRTIConfig
from hla2010_rti_transport_common.hosted_server import HostedRTICommandProcessor

from hla2010.exceptions import RTIexception
from hla2010.rti import create_rti_ambassador

from . import rti_transport_pb2_grpc as pb2_grpc
from .client import GrpcTransportClientAdapter

try:  # pragma: no cover - import guarded for optional dependency
    import grpc
except Exception as exc:  # pragma: no cover - optional dependency
    grpc = None  # type: ignore[assignment]
    _GRPC_IMPORT_ERROR = exc
else:
    _GRPC_IMPORT_ERROR = None


@dataclass(frozen=True)
class PythonRTIGrpcServerConfig:
    host: str = "127.0.0.1"
    port: int = 0
    max_workers: int = 4
    engine: InMemoryRTIEngine | None = None
    python_config: PythonRTIConfig | None = None


@dataclass(frozen=True)
class CERTIRTIGrpcServerConfig:
    host: str = "127.0.0.1"
    port: int = 0
    max_workers: int = 4
    backend_options: Mapping[str, Any] = field(default_factory=dict)


class _RTITransportServicer(pb2_grpc.RTITransportServiceServicer):
    def __init__(self, rti: Any) -> None:
        self.adapter = GrpcTransportClientAdapter()
        self.processor = HostedRTICommandProcessor(rti)

    def Request(self, request, context):  # noqa: N802 - grpc generated naming
        try:
            transport_request = self.adapter.decode_request(request)
            transport_response = self.processor.handle_request(transport_request)
            return self.adapter.encode_response(transport_response)
        except RTIexception as exc:
            return self.adapter.encode_error(exc.__class__.__name__, str(exc))
        except Exception as exc:  # pragma: no cover - defensive server guard
            return self.adapter.encode_error("RTIinternalError", str(exc))

    def close(self) -> None:
        self.processor.close()


class PythonRTIGrpcServer:
    def __init__(self, config: PythonRTIGrpcServerConfig = PythonRTIGrpcServerConfig()) -> None:
        if grpc is None:  # pragma: no cover - optional dependency guard
            raise RuntimeError("gRPC server requested, but grpcio is not installed") from _GRPC_IMPORT_ERROR
        self.config = config
        self.servicer = _RTITransportServicer(rti_ambassador(engine=config.engine, config=config.python_config))
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=config.max_workers))
        pb2_grpc.add_RTITransportServiceServicer_to_server(self.servicer, self.server)
        self.port = self.server.add_insecure_port(f"{config.host}:{config.port}")
        self.target = f"{config.host}:{self.port}"
        self._started = False

    def start(self) -> "PythonRTIGrpcServer":
        if not self._started:
            self.server.start()
            self._started = True
        return self

    def close(self) -> None:
        self.servicer.close()
        if self._started:
            self.server.stop(0).wait()
            self._started = False


class CERTIRTIGrpcServer:
    def __init__(self, config: CERTIRTIGrpcServerConfig = CERTIRTIGrpcServerConfig()) -> None:
        if grpc is None:  # pragma: no cover - optional dependency guard
            raise RuntimeError("gRPC server requested, but grpcio is not installed") from _GRPC_IMPORT_ERROR
        self.config = config
        self.servicer = _RTITransportServicer(create_rti_ambassador("certi", **dict(config.backend_options)))
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=config.max_workers))
        pb2_grpc.add_RTITransportServiceServicer_to_server(self.servicer, self.server)
        self.port = self.server.add_insecure_port(f"{config.host}:{config.port}")
        self.target = f"{config.host}:{self.port}"
        self._started = False

    def start(self) -> "CERTIRTIGrpcServer":
        if not self._started:
            self.server.start()
            self._started = True
        return self

    def close(self) -> None:
        self.servicer.close()
        if self._started:
            self.server.stop(0).wait()
            self._started = False


def start_python_grpc_server(
    *,
    engine: InMemoryRTIEngine | None = None,
    python_config: PythonRTIConfig | None = None,
    host: str = "127.0.0.1",
    port: int = 0,
) -> PythonRTIGrpcServer:
    return PythonRTIGrpcServer(
        PythonRTIGrpcServerConfig(host=host, port=port, engine=engine, python_config=python_config)
    ).start()


def start_certi_grpc_server(
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    **backend_options: Any,
) -> CERTIRTIGrpcServer:
    return CERTIRTIGrpcServer(
        CERTIRTIGrpcServerConfig(host=host, port=port, backend_options=dict(backend_options))
    ).start()


__all__ = [
    "CERTIRTIGrpcServer",
    "CERTIRTIGrpcServerConfig",
    "PythonRTIGrpcServer",
    "PythonRTIGrpcServerConfig",
    "start_certi_grpc_server",
    "start_python_grpc_server",
]
