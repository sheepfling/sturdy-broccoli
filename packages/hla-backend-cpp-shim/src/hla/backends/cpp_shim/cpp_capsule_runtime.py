"""Runtime loader and smoke harness for generated C++ capsules."""
from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from hla.rti.real_rti_process import reserve_tcp_port, wait_for_tcp_listener

from .cpp_capsule_contract import CAPSULE_C_ABI_FUNCTIONS, SMOKE_TRACE_EVENTS, UNSUPPORTED_SERVICE_LEDGER


@dataclass(frozen=True, slots=True)
class CapsuleRuntimeResult:
    transport: str
    status: str
    library_path: str
    process_pid: int | None
    invocation_count: int
    callback_count: int
    trace: tuple[dict[str, Any], ...]
    checks: dict[str, str]
    unsupported_services: tuple[str, ...]
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


def find_capsule_library(capsule_dir: str | Path) -> Path:
    root = Path(capsule_dir)
    candidates = [
        *root.glob("build/lib/lib_*_capsule.*"),
        *root.glob("build/**/*.dylib"),
        *root.glob("build/**/*.so"),
        *root.glob("build/**/*.dll"),
    ]
    candidates = [candidate for candidate in candidates if candidate.is_file()]
    if not candidates:
        raise FileNotFoundError(f"No built C++ capsule shared library found under {root}")
    return sorted(candidates)[0]


class CAbiCapsuleClient:
    def __init__(self, library_path: str | Path):
        self.library_path = Path(library_path)
        self._lib = ctypes.CDLL(str(self.library_path))
        self._configure()

    def _configure(self) -> None:
        for name in CAPSULE_C_ABI_FUNCTIONS:
            if not hasattr(self._lib, name):
                raise RuntimeError(f"C++ capsule is missing C ABI function {name}")
        for name in (
            "shim_capsule_discover_json",
            "shim_capsule_create_json",
            "shim_capsule_invoke_json",
            "shim_capsule_evoke_callbacks_json",
        ):
            func = getattr(self._lib, name)
            func.argtypes = [ctypes.c_char_p]
            func.restype = ctypes.c_void_p
        self._lib.shim_capsule_free_string.argtypes = [ctypes.c_void_p]
        self._lib.shim_capsule_free_string.restype = None
        self._lib.shim_capsule_close.argtypes = []
        self._lib.shim_capsule_close.restype = None

    def _call(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        raw_request = json.dumps(payload, sort_keys=True).encode("utf-8")
        pointer = getattr(self._lib, name)(raw_request)
        if not pointer:
            raise RuntimeError(f"C++ capsule function {name} returned null")
        try:
            text = ctypes.string_at(pointer).decode("utf-8")
        finally:
            self._lib.shim_capsule_free_string(pointer)
        result = json.loads(text)
        if not isinstance(result, dict):
            raise RuntimeError(f"C++ capsule function {name} returned non-object JSON")
        return result

    def discover(self) -> dict[str, Any]:
        return self._call("shim_capsule_discover_json", {"contract": "shim_capsule_v1"})

    def create(self) -> dict[str, Any]:
        return self._call("shim_capsule_create_json", {"contract": "shim_capsule_v1"})

    def invoke(self, method: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._call("shim_capsule_invoke_json", {"method": method, "args": args or {}})

    def evoke_callbacks(self, min_seconds: float = 0.0, max_seconds: float = 0.0) -> dict[str, Any]:
        return self._call("shim_capsule_evoke_callbacks_json", {"min_seconds": min_seconds, "max_seconds": max_seconds})

    def close(self) -> None:
        self._lib.shim_capsule_close()


class GrpcCapsuleClient:
    def __init__(self, library_path: str | Path, timeout_seconds: float = 30.0):
        import grpc

        self.library_path = Path(library_path)
        self.port = reserve_tcp_port()
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(path for path in sys.path if path)
        self.process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "hla.backends.cpp_shim.cpp_capsule_sidecar",
                "--library",
                str(self.library_path),
                "--port",
                str(self.port),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        try:
            wait_for_tcp_listener("127.0.0.1", self.port, timeout=timeout_seconds)
        except Exception:
            self.close()
            raise
        self.channel = grpc.insecure_channel(f"127.0.0.1:{self.port}")

    @property
    def process_pid(self) -> int:
        return int(self.process.pid)

    def _call(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        request = json.dumps(payload, sort_keys=True).encode("utf-8")
        rpc = self.channel.unary_unary(
            f"/shim_routes.cpp_capsule.Capsule/{method}",
            request_serializer=lambda value: value,
            response_deserializer=lambda value: value,
        )
        response = rpc(request, timeout=10.0)
        result = json.loads(response.decode("utf-8"))
        if not isinstance(result, dict):
            raise RuntimeError(f"C++ capsule gRPC method {method} returned non-object JSON")
        return result

    def discover(self) -> dict[str, Any]:
        return self._call("Discover", {"contract": "shim_capsule_v1"})

    def create(self) -> dict[str, Any]:
        return self._call("CreateRtiAmbassador", {"contract": "shim_capsule_v1"})

    def invoke(self, method: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._call("Invoke", {"method": method, "args": args or {}})

    def evoke_callbacks(self, min_seconds: float = 0.0, max_seconds: float = 0.0) -> dict[str, Any]:
        return self._call("EvokeCallbacks", {"min_seconds": min_seconds, "max_seconds": max_seconds})

    def close(self) -> None:
        try:
            if hasattr(self, "channel"):
                self._call("Close", {})
                self.channel.close()
        except Exception:
            pass
        if hasattr(self, "process") and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)


def _client_for_transport(transport: str, library_path: Path, timeout_seconds: float):
    if transport == "pybind":
        return CAbiCapsuleClient(library_path), None
    if transport == "grpc":
        client = GrpcCapsuleClient(library_path, timeout_seconds=timeout_seconds)
        return client, client.process_pid
    raise ValueError("C++ capsule transport must be one of: pybind, grpc")


def smoke_capsule(capsule_dir: str | Path, transport: str, *, timeout_seconds: float = 30.0) -> CapsuleRuntimeResult:
    library_path = find_capsule_library(capsule_dir)
    trace: list[dict[str, Any]] = []
    invocation_count = 0
    callback_count = 0
    process_pid = None
    checks = {
        "capsule_launch": "not-run",
        "discover": "not-run",
        "create_ambassador": "not-run",
        "connect_disconnect": "not-run",
        "unsupported_service": "not-run",
        "callback_poll": "not-run",
    }
    try:
        client, process_pid = _client_for_transport(transport, library_path, timeout_seconds)
        checks["capsule_launch"] = "pass"
        try:
            discovered = client.discover()
            checks["discover"] = "pass" if discovered.get("ok") else "fail"
            trace.append({"event": "capsuleDiscover", "transport": transport, "metadata": discovered})
            created = client.create()
            checks["create_ambassador"] = "pass" if created.get("ok") else "fail"
            trace.append({"event": "createRtiAmbassador", "result": created})
            connected = client.invoke("connect")
            invocation_count += 1
            trace.append({"event": "connect", "result": connected})
            disconnected = client.invoke("disconnect")
            invocation_count += 1
            trace.append({"event": "disconnect", "result": disconnected})
            checks["connect_disconnect"] = "pass" if connected.get("ok") and disconnected.get("ok") else "fail"
            unsupported = client.invoke("requestFederationSave")
            invocation_count += 1
            checks["unsupported_service"] = "pass" if unsupported.get("error_type") == "UnsupportedService" else "fail"
            trace.append({"event": "unsupportedService", "result": unsupported})
            callbacks = client.evoke_callbacks(0.0, 0.0)
            events = callbacks.get("events", [])
            callback_count = len(events) if isinstance(events, list) else 0
            checks["callback_poll"] = "pass" if callback_count >= 1 else "fail"
            trace.append({"event": "callbackPoll", "result": callbacks})
            client.close()
            trace.append({"event": "close"})
        finally:
            close = getattr(client, "close", None)
            if callable(close):
                close()
        failed = [name for name, status in checks.items() if status != "pass"]
        missing = [event for event in SMOKE_TRACE_EVENTS if event not in {item.get("event") for item in trace}]
        status = "adapter-smoke-green" if not failed and not missing else "failed"
        return CapsuleRuntimeResult(
            transport=transport,
            status=status,
            library_path=str(library_path),
            process_pid=process_pid,
            invocation_count=invocation_count,
            callback_count=callback_count,
            trace=tuple(trace),
            checks=checks,
            unsupported_services=UNSUPPORTED_SERVICE_LEDGER,
            errors=tuple(f"Smoke check failed: {name}" for name in failed) + tuple(f"Missing trace event: {event}" for event in missing),
        )
    except Exception as exc:
        return CapsuleRuntimeResult(
            transport=transport,
            status="failed",
            library_path=str(library_path),
            process_pid=process_pid,
            invocation_count=invocation_count,
            callback_count=callback_count,
            trace=tuple(trace),
            checks=checks,
            unsupported_services=UNSUPPORTED_SERVICE_LEDGER,
            errors=(f"C++ capsule smoke failed: {exc}",),
        )


__all__ = [
    "CAbiCapsuleClient",
    "CapsuleRuntimeResult",
    "GrpcCapsuleClient",
    "find_capsule_library",
    "smoke_capsule",
]
