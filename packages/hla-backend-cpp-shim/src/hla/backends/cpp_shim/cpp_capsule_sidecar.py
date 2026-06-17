"""gRPC sidecar for generated C++ capsule C ABI libraries."""
from __future__ import annotations

import argparse
import json
from concurrent import futures
from pathlib import Path

import grpc

from .cpp_capsule_runtime import CAbiCapsuleClient


class _CapsuleGrpcServicer:
    def __init__(self, library_path: str | Path):
        self.client = CAbiCapsuleClient(library_path)

    @staticmethod
    def _decode(request: bytes) -> dict:
        if not request:
            return {}
        payload = json.loads(request.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("request must be a JSON object")
        return payload

    @staticmethod
    def _encode(response: dict) -> bytes:
        return json.dumps(response, sort_keys=True).encode("utf-8")

    def discover(self, request: bytes, _context) -> bytes:
        return self._encode(self.client.discover())

    def create(self, request: bytes, _context) -> bytes:
        return self._encode(self.client.create())

    def invoke(self, request: bytes, _context) -> bytes:
        payload = self._decode(request)
        return self._encode(self.client.invoke(str(payload.get("method", "")), payload.get("args") or {}))

    def evoke_callbacks(self, request: bytes, _context) -> bytes:
        payload = self._decode(request)
        return self._encode(
            self.client.evoke_callbacks(
                float(payload.get("min_seconds", 0.0) or 0.0),
                float(payload.get("max_seconds", 0.0) or 0.0),
            )
        )

    def close(self, _request: bytes, _context) -> bytes:
        self.client.close()
        return self._encode({"ok": True})


def serve(library_path: str | Path, port: int) -> grpc.Server:
    servicer = _CapsuleGrpcServicer(library_path)
    handlers = {
        "Discover": grpc.unary_unary_rpc_method_handler(servicer.discover, request_deserializer=lambda value: value, response_serializer=lambda value: value),
        "CreateRtiAmbassador": grpc.unary_unary_rpc_method_handler(servicer.create, request_deserializer=lambda value: value, response_serializer=lambda value: value),
        "Invoke": grpc.unary_unary_rpc_method_handler(servicer.invoke, request_deserializer=lambda value: value, response_serializer=lambda value: value),
        "EvokeCallbacks": grpc.unary_unary_rpc_method_handler(servicer.evoke_callbacks, request_deserializer=lambda value: value, response_serializer=lambda value: value),
        "Close": grpc.unary_unary_rpc_method_handler(servicer.close, request_deserializer=lambda value: value, response_serializer=lambda value: value),
    }
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    server.add_generic_rpc_handlers((grpc.method_handlers_generic_handler("hla_x.cpp_capsule.Capsule", handlers),))
    server.add_insecure_port(f"127.0.0.1:{port}")
    server.start()
    return server


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    server = serve(args.library, args.port)
    try:
        server.wait_for_termination()
    finally:
        server.stop(0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
