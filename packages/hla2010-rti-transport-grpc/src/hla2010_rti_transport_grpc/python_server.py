"""Transport-hosted Python RTI server for proving the gRPC wire path."""
from __future__ import annotations

from concurrent import futures
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping

from hla2010_rti_transport_common.hosted_server import HostedRTICommandProcessor

from hla2010.exceptions import RTIexception
from hla2010_rti_backend_common import BackendUnavailableError
from hla2010_rti_runtime_common import create_rti_ambassador
from hla2010_rti_runtime_common.real_rti_process import reserve_tcp_port

from .client import GrpcTransportClientAdapter
from .wire_adapter import TransportWireAdapter

grpc: Any | None
pb2_grpc: Any | None

try:  # pragma: no cover - import guarded for optional dependency
    import grpc as _grpc
except Exception as exc:  # pragma: no cover - optional dependency
    grpc = None
    _GRPC_IMPORT_ERROR = exc
    pb2_grpc = None
else:
    grpc = _grpc
    _GRPC_IMPORT_ERROR = None
    import hla2010_rti_transport_grpc.rti_transport_pb2_grpc as pb2_grpc


@dataclass(frozen=True)
class PythonRTIGrpcServerConfig:
    host: str = "127.0.0.1"
    port: int = 0
    max_workers: int = 4
    engine: Any | None = None
    python_config: Any | None = None
    wire_adapter: TransportWireAdapter | None = None


@dataclass(frozen=True)
class CERTIRTIGrpcServerConfig:
    host: str = "127.0.0.1"
    port: int = 0
    max_workers: int = 4
    backend_options: Mapping[str, Any] = field(default_factory=dict)
    wire_adapter: TransportWireAdapter | None = None


if TYPE_CHECKING:
    class _RTI_TRANSPORT_SERVICER_BASE:
        pass
elif pb2_grpc is not None:
    _RTI_TRANSPORT_SERVICER_BASE = pb2_grpc.RTITransportServiceServicer
else:
    class _RTI_TRANSPORT_SERVICER_BASE:
        pass


class _RTITransportServicer(_RTI_TRANSPORT_SERVICER_BASE):
    def __init__(self, rti: Any, *, wire_adapter: TransportWireAdapter | None = None) -> None:
        self.adapter = wire_adapter or GrpcTransportClientAdapter()
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
        self.servicer = _RTITransportServicer(
            create_rti_ambassador("python", engine=config.engine, config=config.python_config),
            wire_adapter=config.wire_adapter,
        )
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=config.max_workers))
        assert pb2_grpc is not None
        pb2_grpc.add_RTITransportServiceServicer_to_server(self.servicer, self.server)
        requested_port = int(config.port) if int(config.port) != 0 else reserve_tcp_port(config.host)
        try:
            self.port = self.server.add_insecure_port(f"{config.host}:{requested_port}")
        except Exception as exc:
            raise BackendUnavailableError(
                f"Python gRPC host could not bind loopback listener on {config.host}:{requested_port}: {exc}"
            ) from exc
        self.target = f"{config.host}:{self.port}"
        self._started = False

    def start(self) -> PythonRTIGrpcServer:
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
        self.servicer = _RTITransportServicer(
            create_rti_ambassador("certi", **dict(config.backend_options)),
            wire_adapter=config.wire_adapter,
        )
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=config.max_workers))
        assert pb2_grpc is not None
        pb2_grpc.add_RTITransportServiceServicer_to_server(self.servicer, self.server)
        requested_port = int(config.port) if int(config.port) != 0 else reserve_tcp_port(config.host)
        try:
            self.port = self.server.add_insecure_port(f"{config.host}:{requested_port}")
        except Exception as exc:
            raise BackendUnavailableError(
                f"CERTI gRPC host could not bind loopback listener on {config.host}:{requested_port}: {exc}"
            ) from exc
        self.target = f"{config.host}:{self.port}"
        self._started = False

    def start(self) -> CERTIRTIGrpcServer:
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
    engine: Any | None = None,
    python_config: Any | None = None,
    host: str = "127.0.0.1",
    port: int = 0,
    wire_adapter: TransportWireAdapter | None = None,
) -> PythonRTIGrpcServer:
    return PythonRTIGrpcServer(
        PythonRTIGrpcServerConfig(
            host=host,
            port=port,
            engine=engine,
            python_config=python_config,
            wire_adapter=wire_adapter,
        )
    ).start()


def start_certi_grpc_server(
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    wire_adapter: TransportWireAdapter | None = None,
    **backend_options: Any,
) -> CERTIRTIGrpcServer:
    return CERTIRTIGrpcServer(
        CERTIRTIGrpcServerConfig(
            host=host,
            port=port,
            backend_options=dict(backend_options),
            wire_adapter=wire_adapter,
        )
    ).start()


__all__ = [
    "CERTIRTIGrpcServer",
    "CERTIRTIGrpcServerConfig",
    "PythonRTIGrpcServer",
    "PythonRTIGrpcServerConfig",
    "start_certi_grpc_server",
    "start_python_grpc_server",
]
