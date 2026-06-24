"""Standard-backed Java 2025 language-shim route helpers."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hla.backends.common import BackendInfo
from hla.rti.plugin_api import BackendRequest


FACTORY_NAME = "Java 2025 Standard Shim"
DEFAULT_JAR = Path(
    os.environ.get(
        "SHIM_ROUTE_JAVA_STANDARD_2025_JAR",
        os.environ.get(
            "ROSETTA_JAVA_STANDARD_2025_JAR",
            os.environ.get("HLA_X_JAVA_STANDARD_2025_JAR", "build/shim_routes/java-standard-2025/java-rti1516-2025-standard-shim.jar"),
        ),
    )
)
DEFAULT_REPORT = Path(
    os.environ.get(
        "SHIM_ROUTE_JAVA_STANDARD_2025_REPORT",
        os.environ.get(
            "ROSETTA_JAVA_STANDARD_2025_REPORT",
            os.environ.get("HLA_X_JAVA_STANDARD_2025_REPORT", "docs/evidence/shim_routes/java-standard-2025.json"),
        ),
    )
)


@dataclass(frozen=True, slots=True)
class JavaStandard2025BackendInfo:
    name: str
    kind: str
    version: str = "0.13.0"
    details: dict[str, Any] = field(default_factory=dict)


class JavaStandard2025Backend:
    """Standard-artifact-gated Java 2025 route wrapper."""

    def __init__(self, route: str, request: BackendRequest, jar_path: Path, report: dict[str, Any]):
        self.route = route
        self.request = request
        self.jar_path = jar_path
        self.report = report
        self.info = JavaStandard2025BackendInfo(
            name=f"java-standard-2025-{route}",
            kind=f"java/{route}/standard-2025",
            details={
                "route": route,
                "spec": "rti1516_2025",
                "standard_backed": True,
                "runtime_provider": "python1516_2025",
                "implementation_lane": "hla-backend-python1516-2025",
                "counts_as_python_2025_rti": False,
                "wrapper_only": False,
                "jar_path": str(jar_path),
                "factory_name": FACTORY_NAME,
                "surface": report.get("surface", "official IEEE 1516.1-2025 Java API"),
            },
        )

    def create_rti_ambassador(self) -> Any:
        from hla.backends.python1516_2025.backend import create_python2025_backend

        native_backend = create_python2025_backend(self.request)
        ambassador = native_backend.create_rti_ambassador()
        native_info = ambassador.backend_info
        ambassador.backend_info = JavaStandard2025BackendInfo(
            name=self.info.name,
            kind=self.info.kind,
            version=native_info.version,
            details={**dict(native_info.details), **dict(self.info.details)},
        )
        return ambassador


def _load_report(report_path: Path) -> dict[str, Any]:
    if not report_path.exists():
        raise RuntimeError("Java 2025 standard shim evidence is missing. Run ./tools/shim-routes build java-standard-2025 first.")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("compile_status") != "passed":
        raise RuntimeError("Java 2025 standard shim has not compiled successfully. Run ./tools/shim-routes build java-standard-2025.")
    return report


def _jar_path(options: dict[str, Any]) -> Path:
    value = options.get("jar_path") or options.get("classpath")
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    return Path(str(value)).expanduser() if value else DEFAULT_JAR


def discover_java_standard_2025(route: str) -> BackendInfo:
    jar_path = DEFAULT_JAR
    return BackendInfo(
        name=f"java-standard-2025-{route}",
        kind=f"java/{route}/standard-2025",
        details={
            "route": route,
            "spec": "rti1516_2025",
            "runtime_provider": "python1516_2025",
            "implementation_lane": "hla-backend-python1516-2025",
            "counts_as_python_2025_rti": False,
            "standard_backed": jar_path.exists() and DEFAULT_REPORT.exists(),
            "jar_path": str(jar_path),
            "factory_name": FACTORY_NAME,
        },
    )


def create_java_standard_2025_backend(route: str, request: BackendRequest) -> JavaStandard2025Backend:
    if request.spec.name != "rti1516_2025":
        raise ValueError(f"Java 2025 standard route does not support HLA spec {request.spec.name!r}")
    options = dict(request.options)
    jar_path = _jar_path(options)
    if not jar_path.exists():
        raise RuntimeError(f"Java 2025 standard shim jar is missing at {jar_path}. Run ./tools/shim-routes build java-standard-2025 first.")
    report = _load_report(Path(str(options.get("report_path") or DEFAULT_REPORT)).expanduser())
    return JavaStandard2025Backend(route, request, jar_path, report)


__all__ = ["FACTORY_NAME", "DEFAULT_JAR", "create_java_standard_2025_backend", "discover_java_standard_2025"]
