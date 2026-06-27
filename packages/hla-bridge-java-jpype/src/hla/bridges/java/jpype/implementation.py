"""Easy standard Java RTI implementation facade."""
# pyright: reportMissingImports=false
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from hla.backends.common import DelegatingRTIAmbassador
from hla.bridges.java.common import JavaRTIDiscoveryReport, create_java_backend, create_java_rti_ambassador, discover_java_rti
from hla.bridges.java.common.java_common import JavaRTIBackend
from hla.bridges.java.common.java_intake import java_api_profile


def _normalize_bridge(bridge: str) -> str:
    return bridge.strip().lower().replace("_", "-")


@dataclass(frozen=True)
class JavaRTIImplementation:
    """Concrete selector for one standard Java RTI implementation.

    ``implementation`` is forwarded to
    ``hla.rti1516e.RtiFactoryFactory.getRtiFactory(String)``. JPype is the
    default bridge, while ``bridge`` and ``edition`` keep the Python API open
    for Py4J and future HLA editions.
    """

    implementation: str
    bridge: str = "jpype"
    edition: str = "2010"
    classpath: Sequence[str] = field(default_factory=tuple)
    jvm_args: Sequence[str] = field(default_factory=tuple)
    connect_local_settings_designator: str | None = None
    start_jvm: bool = True
    shutdown_jvm_on_close: bool = False
    convert_strings: bool = False
    gateway: Any | None = None
    gateway_parameters: dict[str, Any] = field(default_factory=dict)
    callback_server_parameters: dict[str, Any] = field(default_factory=dict)
    shutdown_gateway_on_close: bool = False

    def _require_supported_edition(self) -> None:
        java_api_profile(self.edition)

    def _explicit_bridge_options(self) -> dict[str, Any]:
        bridge = _normalize_bridge(self.bridge)
        options: dict[str, Any] = {}
        if bridge in {"jpype", "java-jpype"}:
            if self.classpath:
                options["classpath"] = tuple(self.classpath)
            if self.jvm_args:
                options["jvm_args"] = tuple(self.jvm_args)
            if not self.start_jvm:
                options["start_jvm"] = self.start_jvm
            if self.shutdown_jvm_on_close:
                options["shutdown_jvm_on_close"] = self.shutdown_jvm_on_close
            if self.convert_strings:
                options["convert_strings"] = self.convert_strings
        elif bridge in {"py4j", "java-py4j"}:
            if self.gateway is not None:
                options["gateway"] = self.gateway
            if self.gateway_parameters:
                options["gateway_parameters"] = dict(self.gateway_parameters)
            if self.callback_server_parameters:
                options["callback_server_parameters"] = dict(self.callback_server_parameters)
            if self.shutdown_gateway_on_close:
                options["shutdown_gateway_on_close"] = self.shutdown_gateway_on_close
        if self.connect_local_settings_designator is not None:
            options["connect_local_settings_designator"] = self.connect_local_settings_designator
        return options

    def create_backend(self) -> JavaRTIBackend:
        """Create the wrapped Java RTI backend."""

        self._require_supported_edition()
        return create_java_backend(
            bridge=self.bridge,
            implementation=self.implementation,
            edition=self.edition,
            **self._explicit_bridge_options(),
        )

    def create_rti_ambassador(self) -> DelegatingRTIAmbassador:
        """Create a backend-neutral RTI ambassador for the selected Java RTI."""

        self._require_supported_edition()
        return create_java_rti_ambassador(
            bridge=self.bridge,
            implementation=self.implementation,
            edition=self.edition,
            **self._explicit_bridge_options(),
        )

    def discover(self) -> JavaRTIDiscoveryReport:
        """Probe the selected factory and return debug metadata."""

        return discover_java_rti(
            bridge=self.bridge,
            implementation=self.implementation,
            edition=self.edition,
            **self._explicit_bridge_options(),
        )


@dataclass(frozen=True)
class JavaRTI2010Implementation(JavaRTIImplementation):
    """Compatibility alias for the 2010 Java implementation selector."""

    edition: str = "2010"

    def _require_supported_edition(self) -> None:
        normalized = self.edition.strip().lower().removeprefix("ed")
        if normalized != "2010":
            raise ValueError(f"JavaRTI2010Implementation only supports edition '2010'; got {self.edition!r}")


def _implementation(
    implementation: str,
    *,
    bridge: str = "jpype",
    edition: str = "2010",
    classpath: Sequence[str] = (),
    jvm_args: Sequence[str] = (),
    connect_local_settings_designator: str | None = None,
    start_jvm: bool = True,
    shutdown_jvm_on_close: bool = False,
    convert_strings: bool = False,
    gateway: Any | None = None,
    gateway_parameters: dict[str, Any] | None = None,
    callback_server_parameters: dict[str, Any] | None = None,
    shutdown_gateway_on_close: bool = False,
) -> JavaRTIImplementation:
    return JavaRTIImplementation(
        implementation=implementation,
        bridge=bridge,
        edition=edition,
        classpath=tuple(classpath),
        jvm_args=tuple(jvm_args),
        connect_local_settings_designator=connect_local_settings_designator,
        start_jvm=start_jvm,
        shutdown_jvm_on_close=shutdown_jvm_on_close,
        convert_strings=convert_strings,
        gateway=gateway,
        gateway_parameters=dict(gateway_parameters or {}),
        callback_server_parameters=dict(callback_server_parameters or {}),
        shutdown_gateway_on_close=shutdown_gateway_on_close,
    )


def debug_java_rti_implementation(
    implementation: str,
    *,
    bridge: str = "jpype",
    edition: str = "2010",
    classpath: Sequence[str] = (),
    jvm_args: Sequence[str] = (),
    connect_local_settings_designator: str | None = None,
    start_jvm: bool = True,
    shutdown_jvm_on_close: bool = False,
    convert_strings: bool = False,
    gateway: Any | None = None,
    gateway_parameters: dict[str, Any] | None = None,
    callback_server_parameters: dict[str, Any] | None = None,
    shutdown_gateway_on_close: bool = False,
) -> JavaRTIDiscoveryReport:
    """Return debug/discovery metadata for a standard Java RTI selection."""

    return _implementation(
        implementation,
        bridge=bridge,
        edition=edition,
        classpath=classpath,
        jvm_args=jvm_args,
        connect_local_settings_designator=connect_local_settings_designator,
        start_jvm=start_jvm,
        shutdown_jvm_on_close=shutdown_jvm_on_close,
        convert_strings=convert_strings,
        gateway=gateway,
        gateway_parameters=gateway_parameters,
        callback_server_parameters=callback_server_parameters,
        shutdown_gateway_on_close=shutdown_gateway_on_close,
    ).discover()


def create_java_backend_for_edition(
    implementation: str,
    *,
    bridge: str = "jpype",
    edition: str = "2010",
    classpath: Sequence[str] = (),
    jvm_args: Sequence[str] = (),
    connect_local_settings_designator: str | None = None,
    start_jvm: bool = True,
    shutdown_jvm_on_close: bool = False,
    convert_strings: bool = False,
    gateway: Any | None = None,
    gateway_parameters: dict[str, Any] | None = None,
    callback_server_parameters: dict[str, Any] | None = None,
    shutdown_gateway_on_close: bool = False,
) -> JavaRTIBackend:
    """Create a standard Java RTI backend for a supported HLA edition."""

    return _implementation(
        implementation,
        bridge=bridge,
        edition=edition,
        classpath=classpath,
        jvm_args=jvm_args,
        connect_local_settings_designator=connect_local_settings_designator,
        start_jvm=start_jvm,
        shutdown_jvm_on_close=shutdown_jvm_on_close,
        convert_strings=convert_strings,
        gateway=gateway,
        gateway_parameters=gateway_parameters,
        callback_server_parameters=callback_server_parameters,
        shutdown_gateway_on_close=shutdown_gateway_on_close,
    ).create_backend()


def java_rti_ambassador_for_edition(
    implementation: str,
    *,
    bridge: str = "jpype",
    edition: str = "2010",
    classpath: Sequence[str] = (),
    jvm_args: Sequence[str] = (),
    connect_local_settings_designator: str | None = None,
    start_jvm: bool = True,
    shutdown_jvm_on_close: bool = False,
    convert_strings: bool = False,
    gateway: Any | None = None,
    gateway_parameters: dict[str, Any] | None = None,
    callback_server_parameters: dict[str, Any] | None = None,
    shutdown_gateway_on_close: bool = False,
) -> DelegatingRTIAmbassador:
    """Create a wrapped RTI ambassador for a supported standard Java edition."""

    return _implementation(
        implementation,
        bridge=bridge,
        edition=edition,
        classpath=classpath,
        jvm_args=jvm_args,
        connect_local_settings_designator=connect_local_settings_designator,
        start_jvm=start_jvm,
        shutdown_jvm_on_close=shutdown_jvm_on_close,
        convert_strings=convert_strings,
        gateway=gateway,
        gateway_parameters=gateway_parameters,
        callback_server_parameters=callback_server_parameters,
        shutdown_gateway_on_close=shutdown_gateway_on_close,
    ).create_rti_ambassador()


def create_java_2010_backend(
    implementation: str,
    *,
    classpath: Sequence[str] = (),
    jvm_args: Sequence[str] = (),
    connect_local_settings_designator: str | None = None,
    start_jvm: bool = True,
    shutdown_jvm_on_close: bool = False,
    convert_strings: bool = False,
) -> JavaRTIBackend:
    """Create a JPype-backed standard Java HLA 1516-2010 RTI backend."""

    return create_java_backend_for_edition(
        implementation,
        bridge="jpype",
        edition="2010",
        classpath=classpath,
        jvm_args=jvm_args,
        connect_local_settings_designator=connect_local_settings_designator,
        start_jvm=start_jvm,
        shutdown_jvm_on_close=shutdown_jvm_on_close,
        convert_strings=convert_strings,
    )


def java_2010_rti_ambassador(
    implementation: str,
    *,
    classpath: Sequence[str] = (),
    jvm_args: Sequence[str] = (),
    connect_local_settings_designator: str | None = None,
    start_jvm: bool = True,
    shutdown_jvm_on_close: bool = False,
    convert_strings: bool = False,
) -> DelegatingRTIAmbassador:
    """Create a wrapped RTI ambassador for a standard Java HLA 1516-2010 RTI."""

    return java_rti_ambassador_for_edition(
        implementation,
        bridge="jpype",
        edition="2010",
        classpath=classpath,
        jvm_args=jvm_args,
        connect_local_settings_designator=connect_local_settings_designator,
        start_jvm=start_jvm,
        shutdown_jvm_on_close=shutdown_jvm_on_close,
        convert_strings=convert_strings,
    )


__all__ = [
    "JavaRTI2010Implementation",
    "JavaRTIImplementation",
    "create_java_2010_backend",
    "create_java_backend_for_edition",
    "debug_java_rti_implementation",
    "java_2010_rti_ambassador",
    "java_rti_ambassador_for_edition",
]
