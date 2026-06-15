from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from hla2010.enums import CallbackModel
from hla2010.spec import FederateAmbassadorSpec
from hla2010_rti_backend_common import BackendInfo, RTIBackend
from hla2010_rti_java import (
    JavaRTIImplementation,
    debug_java_rti_implementation,
    discover_java_rti,
    java_2010_rti_ambassador,
)
import hla2010_rti_java
from hla2010_rti_java.implementation import create_java_2010_backend
from hla2010_rti_java.factory_selection import create_java_backend, create_java_rti_ambassador
from hla2010_rti_java_common.java_shim_kernel import SharedJavaShimKernel
from hla2010_verification_harness import run_basic_federate_scenario


@dataclass
class _FakeBackend(RTIBackend):
    info: BackendInfo

    @property
    def backend_info(self) -> BackendInfo:
        return self.info

    def invoke(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError(method_name)


def test_create_java_backend_forwards_implementation_to_jpype_config(monkeypatch: pytest.MonkeyPatch) -> None:
    import hla2010_rti_java_jpype.factory as jpype_factory

    captured: dict[str, Any] = {}

    def fake_create_backend(config: Any) -> _FakeBackend:
        captured["config"] = config
        return _FakeBackend(BackendInfo(name="fake", kind="java/jpype"))

    monkeypatch.setattr(jpype_factory, "create_jpype_backend", fake_create_backend)

    with pytest.warns(DeprecationWarning, match="Direct Java backend factory helpers are deprecated"):
        backend = create_java_backend(
            bridge="java-jpype",
            implementation="vendor.rti.Factory",
            classpath=("vendor.jar",),
            connect_local_settings_designator="crcHost=localhost",
        )

    assert backend.backend_info.kind == "java/jpype"
    assert captured["config"].rti_factory_name == "vendor.rti.Factory"
    assert tuple(captured["config"].classpath) == ("vendor.jar",)
    assert captured["config"].connect_local_settings_designator == "crcHost=localhost"


def test_create_java_backend_forwards_implementation_to_py4j_config(monkeypatch: pytest.MonkeyPatch) -> None:
    import hla2010_rti_java_py4j.factory as py4j_factory

    captured: dict[str, Any] = {}

    def fake_create_backend(config: Any) -> _FakeBackend:
        captured["config"] = config
        return _FakeBackend(BackendInfo(name="fake", kind="java/py4j"))

    monkeypatch.setattr(py4j_factory, "create_py4j_backend", fake_create_backend)

    with pytest.warns(DeprecationWarning, match="Direct Java backend factory helpers are deprecated"):
        backend = create_java_backend(bridge="py4j", implementation="vendor.rti.Factory")

    assert backend.backend_info.kind == "java/py4j"
    assert captured["config"].rti_factory_name == "vendor.rti.Factory"


def test_create_java_rti_ambassador_wraps_selected_java_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    import hla2010_rti_java_jpype.factory as jpype_factory

    def fake_create_backend(config: Any) -> _FakeBackend:
        return _FakeBackend(BackendInfo(name=config.rti_factory_name, kind="java/jpype"))

    monkeypatch.setattr(jpype_factory, "create_jpype_backend", fake_create_backend)

    with pytest.warns(DeprecationWarning, match="Direct Java backend factory helpers are deprecated"):
        ambassador = create_java_rti_ambassador(bridge="jpype", implementation="vendor.rti.Factory")

    assert ambassador.backend_info.name == "vendor.rti.Factory"
    assert ambassador.backend_info.kind == "java/jpype"


def test_create_java_backend_rejects_conflicting_implementation_names() -> None:
    with pytest.raises(ValueError, match="different Java RTI factories"):
        with pytest.warns(DeprecationWarning, match="Direct Java backend factory helpers are deprecated"):
            create_java_backend(
                bridge="jpype",
                implementation="vendor.a.Factory",
                rti_factory_name="vendor.b.Factory",
            )


def test_create_java_backend_rejects_unknown_bridge() -> None:
    with pytest.raises(ValueError, match="Unknown Java RTI bridge"):
        with pytest.warns(DeprecationWarning, match="Direct Java backend factory helpers are deprecated"):
            create_java_backend(bridge="unknown")


@pytest.mark.parametrize(
    ("bridge", "expected_kind"),
    [
        ("jpype", "java/jpype/shim"),
        ("py4j", "java/py4j/shim"),
        ("java-shim-jpype", "java/jpype/shim"),
        ("java-shim-py4j", "java/py4j/shim"),
    ],
)
def test_create_java_rti_ambassador_routes_reserved_shim_implementation(bridge: str, expected_kind: str) -> None:
    with pytest.warns(DeprecationWarning, match="Direct Java backend factory helpers are deprecated"):
        ambassador = create_java_rti_ambassador(bridge=bridge, implementation="java-shim")
    try:
        assert ambassador.backend_info.kind == expected_kind
        ambassador.connect(FederateAmbassadorSpec(), CallbackModel.HLA_EVOKED)
        ambassador.disconnect()
    finally:
        ambassador.close()


@pytest.mark.parametrize("bridge", ["jpype", "py4j"])
def test_create_java_rti_ambassador_shim_runs_backend_neutral_scenario(bridge: str) -> None:
    summary = run_basic_federate_scenario(
        lambda: JavaRTIImplementation("java-shim", bridge=bridge).create_rti_ambassador(),
        federation_name=f"selector-{bridge}-shim",
    )

    assert summary["backend"].kind == f"java/{bridge}/shim"
    assert summary["event_names"].count("discover") == 1
    assert summary["event_names"].count("reflect") == 1
    assert summary["event_names"].count("interaction") == 1


def test_create_java_backend_shim_supports_shared_kernel_option() -> None:
    with pytest.warns(DeprecationWarning, match="Direct Java backend factory helpers are deprecated"):
        backend = create_java_backend(bridge="java-shim-py4j", shared=True, kernel=SharedJavaShimKernel())

    assert backend.info.kind == "java/py4j/shared-shim"


def test_java_2010_implementation_facade_is_jpype_first(monkeypatch: pytest.MonkeyPatch) -> None:
    import hla2010_rti_java_jpype.factory as jpype_factory

    captured: dict[str, Any] = {}

    def fake_create_backend(config: Any) -> _FakeBackend:
        captured["config"] = config
        return _FakeBackend(BackendInfo(name=config.rti_factory_name, kind="java/jpype"))

    monkeypatch.setattr(jpype_factory, "create_jpype_backend", fake_create_backend)

    ambassador = java_2010_rti_ambassador(
        "vendor.rti.Factory",
        classpath=("vendor.jar",),
        jvm_args=("-Xmx512m",),
        connect_local_settings_designator="crcHost=localhost",
        convert_strings=True,
    )

    assert ambassador.backend_info.name == "vendor.rti.Factory"
    assert ambassador.backend_info.kind == "java/jpype"
    assert captured["config"].rti_factory_name == "vendor.rti.Factory"
    assert tuple(captured["config"].classpath) == ("vendor.jar",)
    assert tuple(captured["config"].jvm_args) == ("-Xmx512m",)
    assert captured["config"].connect_local_settings_designator == "crcHost=localhost"
    assert captured["config"].convert_strings is True


def test_java_2010_implementation_rejects_future_edition_until_split_exists() -> None:
    with pytest.raises(ValueError, match="only supports edition '2010' today"):
        JavaRTIImplementation("vendor.rti.Factory", edition="2025").create_backend()


def test_java_2010_implementation_facade_can_drive_java_shim_test_tool() -> None:
    summary = run_basic_federate_scenario(
        lambda: java_2010_rti_ambassador("java-shim"),
        federation_name="java-2010-implementation-shim",
    )

    assert summary["backend"].kind == "java/jpype/shim"
    assert summary["event_names"].count("discover") == 1
    assert summary["event_names"].count("reflect") == 1
    assert summary["event_names"].count("interaction") == 1


def test_java_implementation_facade_has_py4j_slot(monkeypatch: pytest.MonkeyPatch) -> None:
    import hla2010_rti_java_py4j.factory as py4j_factory

    captured: dict[str, Any] = {}

    def fake_create_backend(config: Any) -> _FakeBackend:
        captured["config"] = config
        return _FakeBackend(BackendInfo(name=config.rti_factory_name, kind="java/py4j"))

    monkeypatch.setattr(py4j_factory, "create_py4j_backend", fake_create_backend)

    ambassador = JavaRTIImplementation(
        "vendor.rti.Factory",
        bridge="py4j",
        gateway_parameters={"address": "127.0.0.1", "port": 25333},
        callback_server_parameters={"port": 0},
        connect_local_settings_designator="crcHost=localhost",
    ).create_rti_ambassador()

    assert ambassador.backend_info.kind == "java/py4j"
    assert captured["config"].rti_factory_name == "vendor.rti.Factory"
    assert captured["config"].gateway_parameters == {"address": "127.0.0.1", "port": 25333}
    assert captured["config"].callback_server_parameters == {"port": 0}
    assert captured["config"].connect_local_settings_designator == "crcHost=localhost"


def test_discover_java_rti_reports_shim_debug_metadata() -> None:
    report = discover_java_rti(bridge="jpype", implementation="java-shim")

    assert report.available is True
    assert report.requested_edition == "2010"
    assert report.factory_name == "inprocess-jpype-java-shim"
    assert report.hla_version == "HLA 1516-2010"
    assert "hla.rti1516e.RTIambassador" in report.interface_names
    assert report.warnings == ()


def test_debug_discovery_keeps_future_edition_visible_without_constructing_backend() -> None:
    report = debug_java_rti_implementation("java-shim", edition="2025")

    assert report.available is True
    assert report.requested_edition == "2025"
    assert report.warnings
    assert "2025" in report.warnings[0]


def test_package_root_exports_only_application_facing_java_rti_api() -> None:
    assert sorted(hla2010_rti_java.__all__) == [
        "JavaRTIDiscoveryReport",
        "JavaRTIImplementation",
        "debug_java_rti_implementation",
        "discover_java_rti",
        "java_2010_rti_ambassador",
        "java_rti_ambassador_for_edition",
    ]
    assert not hasattr(hla2010_rti_java, "create_java_backend")
    assert not hasattr(hla2010_rti_java, "create_java_2010_backend")


def test_direct_backend_helper_is_deprecated(monkeypatch: pytest.MonkeyPatch) -> None:
    import hla2010_rti_java_jpype.factory as jpype_factory

    def fake_create_backend(config: Any) -> _FakeBackend:
        return _FakeBackend(BackendInfo(name=config.rti_factory_name, kind="java/jpype"))

    monkeypatch.setattr(jpype_factory, "create_jpype_backend", fake_create_backend)

    with pytest.warns(DeprecationWarning, match="Direct Java backend helper functions are deprecated"):
        backend = create_java_2010_backend("vendor.rti.Factory")

    assert backend.backend_info.kind == "java/jpype"
