"""Standard-backed C++ language-shim route helpers."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from hla.backends.common import BackendInfo, RecordingBackend
from hla.rti.plugin_api import BackendRequest

from .backend import create_cpp_shim_backend

REPORTS = {
    "2010": Path(os.environ.get("ROSETTA_CPP_STANDARD_2010_REPORT", os.environ.get("HLA_X_CPP_STANDARD_2010_REPORT", "docs/evidence/shim_routes/cpp-standard-2010.json"))),
    "2025": Path(os.environ.get("ROSETTA_CPP_STANDARD_2025_REPORT", os.environ.get("HLA_X_CPP_STANDARD_2025_REPORT", "docs/evidence/shim_routes/cpp-standard-2025.json"))),
}
ARTIFACTS = {
    "2010": Path(os.environ.get("ROSETTA_CPP_STANDARD_2010_ARTIFACT", os.environ.get("HLA_X_CPP_STANDARD_2010_ARTIFACT", "build/shim_routes/cpp-standard-2010/librti1516e_standard_cpp_shim.a"))),
    "2025": Path(os.environ.get("ROSETTA_CPP_STANDARD_2025_ARTIFACT", os.environ.get("HLA_X_CPP_STANDARD_2025_ARTIFACT", "build/shim_routes/cpp-standard-2025/librti1516_2025_standard_cpp_shim.a"))),
}


def _edition_for_spec(spec_name: str) -> str:
    if spec_name == "rti1516e":
        return "2010"
    if spec_name == "rti1516_2025":
        return "2025"
    raise ValueError(f"C++ standard route does not support HLA spec {spec_name!r}")


def _load_report(edition: str, report_path: Path) -> dict[str, Any]:
    if not report_path.exists():
        raise RuntimeError(f"C++ {edition} standard shim evidence is missing. Run ./tools/shim-routes build cpp-standard-{edition} first.")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("compile_status") != "passed":
        raise RuntimeError(f"C++ {edition} standard shim has not compiled successfully. Run ./tools/shim-routes build cpp-standard-{edition}.")
    return report


def discover_cpp_standard(route: str, edition: str) -> BackendInfo:
    artifact_path = ARTIFACTS[edition]
    report_path = REPORTS[edition]
    return BackendInfo(
        name=f"cpp-standard-{edition}-{route}",
        kind=f"cpp/{route}/standard-{edition}",
        details={
            "route": route,
            "edition": edition,
            "spec": "rti1516_2025" if edition == "2025" else "rti1516e",
            "runtime_provider": "python1516_2025" if edition == "2025" else "python1516e",
            "implementation_lane": "hla-backend-python1516-2025" if edition == "2025" else "hla-backend-python1516e",
            **({"counts_as_python_2025_rti": False} if edition == "2025" else {}),
            "standard_backed": artifact_path.exists() and report_path.exists(),
            "artifact_path": str(artifact_path),
        },
    )


def create_cpp_standard_backend(route: str, request: BackendRequest) -> Any:
    edition = _edition_for_spec(request.spec.name)
    options = dict(request.options)
    artifact_path = Path(str(options.pop("artifact_path", ARTIFACTS[edition]))).expanduser()
    report_path = Path(str(options.pop("report_path", REPORTS[edition]))).expanduser()
    if not artifact_path.exists():
        raise RuntimeError(f"C++ {edition} standard shim artifact is missing at {artifact_path}. Run ./tools/shim-routes build cpp-standard-{edition} first.")
    report = _load_report(edition, report_path)
    if edition == "2010":
        from hla.backends.python1516e import InMemoryRTIEngine, PythonRTIConfig, create_python_backend

        config = options.pop("config", None)
        engine = options.pop("engine", None) or InMemoryRTIEngine()
        if options:
            config = config or PythonRTIConfig(**options)
        object_class = engine.get_or_create_object_class("HLAobjectRoot.DemoObject")
        engine.get_or_create_attribute(object_class.handle, "Payload")
        interaction_class = engine.get_or_create_interaction_class("HLAinteractionRoot.DemoInteraction")
        engine.get_or_create_parameter(interaction_class.handle, "Message")
        engine.get_or_create_dimension("RoutingSpace")
        backend = create_python_backend(engine=engine, config=config)
    else:
        backend = create_cpp_shim_backend(route, BackendRequest(spec=request.spec, transport=request.transport, options=options))
    info = BackendInfo(
        name=f"cpp-standard-{edition}-{route}",
        kind=f"cpp/{route}/standard-{edition}",
        version=getattr(getattr(backend, "info", None), "version", None),
        details={
            **dict(getattr(getattr(backend, "info", None), "details", {})),
            "route": route,
            "edition": edition,
            "runtime_provider": "python1516_2025" if edition == "2025" else "python1516e",
            "implementation_lane": "hla-backend-python1516-2025" if edition == "2025" else "hla-backend-python1516e",
            **({"counts_as_python_2025_rti": False} if edition == "2025" else {}),
            "wrapper_only": False,
            "standard_backed": True,
            "artifact_path": str(artifact_path),
            "surface": report.get("surface"),
        },
    )
    if isinstance(backend, RecordingBackend) or hasattr(backend, "info"):
        backend.info = info
    return backend


__all__ = ["create_cpp_standard_backend", "discover_cpp_standard"]
