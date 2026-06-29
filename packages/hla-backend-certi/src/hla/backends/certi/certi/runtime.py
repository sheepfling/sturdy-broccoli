"""Runtime and helper plumbing for the CERTI backend adapter."""
from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from hla.backends.certi.real_rti_certi import CERTIRuntime
from hla.backends.certi.real_rti_certi import _project_root as project_root
from hla.backends.common import BackendUnavailableError, UnsupportedBackendService
from hla.fom import normalize_module_uri
from hla.rti1516e.exceptions import RTIinternalError
from hla.rti1516e.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time
from hla.transports.common import RTITransport

HELPER_SOURCE = project_root() / "tools" / "certi_smoke_helper.cpp"
HELPER_OUTPUT = project_root() / "build" / "certi" / "certi_smoke_helper"


def resolve_certi_module_paths(modules: Any) -> list[str]:
    if isinstance(modules, (str, os.PathLike)):
        values: Sequence[Any] = [modules]
    else:
        values = tuple(modules)

    resolved: list[str] = []
    for value in values:
        _uri, path = normalize_module_uri(value)
        if path is None:
            raise UnsupportedBackendService(f"CERTI backend requires local FOM paths; got {value!r}")
        resolved.append(str(path))
    return resolved


def logical_time_name(value: Any) -> str:
    if isinstance(value, HLAinteger64Time):
        return "HLAinteger64Time"
    if isinstance(value, HLAfloat64Time):
        return "HLAfloat64Time"
    return type(value).__name__


def logical_interval_name(value: Any) -> str:
    if isinstance(value, HLAinteger64Interval):
        return "HLAinteger64Interval"
    if isinstance(value, HLAfloat64Interval):
        return "HLAfloat64Interval"
    return type(value).__name__


def coerce_time_scalar(value: Any) -> int | float:
    raw = getattr(value, "value", value)
    if isinstance(value, (HLAinteger64Time, HLAinteger64Interval)):
        return int(raw)
    if isinstance(value, (HLAfloat64Time, HLAfloat64Interval)):
        return float(raw)
    raise RTIinternalError(f"CERTI backend only supports HLAinteger64Time and HLAfloat64Time logical time values; got {type(value).__name__}")


def decode_logical_time(type_name: str, raw: Any) -> Any:
    if type_name == "HLAinteger64Time":
        if str(raw).lower() in {"inf", "+inf", "-inf"}:
            return HLAfloat64Time(float(raw))
        return HLAinteger64Time(int(float(raw)))
    if type_name == "HLAfloat64Time":
        return HLAfloat64Time(float(raw))
    raise RTIinternalError(f"Unsupported logical time type from transport: {type_name}")


def decode_logical_interval(type_name: str, raw: Any) -> Any:
    if type_name == "HLAinteger64Interval":
        return HLAinteger64Interval(int(raw))
    if type_name == "HLAfloat64Interval":
        return HLAfloat64Interval(float(raw))
    raise RTIinternalError(f"Unsupported logical interval type from transport: {type_name}")


def get_keyword(kwargs: Mapping[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in kwargs:
            return kwargs[name]
    return default


@dataclass(frozen=True)
class CERTIConfig:
    certi_prefix: str | os.PathLike[str] | None = None
    certi_build_root: str | os.PathLike[str] | None = None
    allow_repo_build_overlay: bool = True
    launch_rtig: bool = True
    host: str = "127.0.0.1"
    tcp_port: int | None = None
    udp_port: int | None = None
    rtig_verbose: int = 0
    helper_path: str | os.PathLike[str] | None = None
    helper_request_timeout: float | None = None
    transport: RTITransport | None = None


def build_certi_smoke_helper(runtime: CERTIRuntime, *, output_path: str | os.PathLike[str] | None = None) -> Path:
    compiler = os.environ.get("CXX") or shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        raise BackendUnavailableError("No C++ compiler found for CERTI smoke helper build")

    output = Path(output_path).expanduser().resolve() if output_path is not None else HELPER_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.stat().st_mtime >= HELPER_SOURCE.stat().st_mtime:
        return output

    include_dirs: list[Path] = []
    for lib_dir in runtime.extra_lib_dirs:
        if lib_dir.name == "ieee1516-2010" and lib_dir.parent.name == "libRTI":
            build_root = lib_dir.parent.parent
            include_dirs.append(build_root / "include" / "ieee1516-2010")
            include_dirs.append(build_root / "include" / "libhla")
    include_dirs.extend(
        [
            runtime.prefix / "include" / "ieee1516-2010",
            runtime.prefix / "include" / "libhla",
        ]
    )
    lib_dirs = runtime.lib_dirs

    command = [
        compiler,
        "-std=c++11",
        "-O2",
        "-Wall",
        "-Wextra",
        "-Wno-deprecated-declarations",
        str(HELPER_SOURCE),
    ]
    seen_include_dirs: set[Path] = set()
    include_args: list[str] = []
    for include_dir in include_dirs:
        if include_dir.exists() and include_dir not in seen_include_dirs:
            include_args.append(f"-I{include_dir}")
            seen_include_dirs.add(include_dir)
    command[6:6] = include_args
    for lib_dir in lib_dirs:
        command.extend((f"-L{lib_dir}", f"-Wl,-rpath,{lib_dir}"))
    command.extend(
        [
            "-lRTI1516ed",
            "-lCERTId",
            "-lFedTime1516ed",
            "-o",
            str(output),
        ]
    )
    subprocess.run(command, check=True, capture_output=True, text=True)
    return output
