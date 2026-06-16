from __future__ import annotations

from pathlib import Path
import ast
import types

from hla.backends.common import RTIBackendPlugin


def test_split_pitch_jpype_package_exports_adapter_surface():
    from hla.vendors.pitch.jpype import JPypeConfig
    from hla.vendors.pitch.jpype.factory import create_jpype_backend

    assert JPypeConfig.__module__.startswith("hla.bridges.java.jpype")
    assert create_jpype_backend.__module__.startswith("hla.bridges.java.jpype")


def test_split_pitch_py4j_package_exports_adapter_surface():
    from hla.vendors.pitch.py4j import Py4JConfig
    from hla.vendors.pitch.py4j.factory import create_py4j_backend

    assert Py4JConfig.__module__.startswith("hla.bridges.java.py4j")
    assert create_py4j_backend.__module__.startswith("hla.bridges.java.py4j")


def _assert_thin_facade_module(path: Path) -> None:
    module = ast.parse(path.read_text(encoding="utf-8"))
    allowed_import_roots = {
        "hla.bridges.java.jpype",
        "hla.bridges.java.py4j",
    }
    for node in module.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        if isinstance(node, ast.ImportFrom):
            assert node.level == 0
            assert node.module is not None
            if node.module == "__future__":
                assert [alias.name for alias in node.names] == ["annotations"], (path, node.module)
                continue
            assert any(node.module == root or node.module.startswith(f"{root}.") for root in allowed_import_roots), (
                path,
                node.module,
            )
            continue
        if isinstance(node, ast.Assign):
            assert all(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets), path
            continue
        raise AssertionError(f"{path} contains non-facade statement: {ast.dump(node, include_attributes=False)}")


def test_pitch_shim_packages_keep_only_expected_module_set() -> None:
    project_root = Path(__file__).resolve().parents[1]
    expected = {"__init__.py", "adapter.py", "factory.py", "plugin.py", "runtime.py"}
    for package_rel in (
        "packages/hla-vendor-pitch-jpype/src/hla/vendors/pitch/jpype",
        "packages/hla-vendor-pitch-py4j/src/hla/vendors/pitch/py4j",
    ):
        package_root = project_root / package_rel
        files = {path.name for path in package_root.glob("*.py")}
        assert files == expected, (package_rel, files)


def test_pitch_retained_facade_source_files_stay_thin_reexport_modules() -> None:
    project_root = Path(__file__).resolve().parents[1]
    for rel in (
        "packages/hla-vendor-pitch-jpype/src/hla/vendors/pitch/jpype/adapter.py",
        "packages/hla-vendor-pitch-jpype/src/hla/vendors/pitch/jpype/factory.py",
        "packages/hla-vendor-pitch-jpype/src/hla/vendors/pitch/jpype/runtime.py",
        "packages/hla-vendor-pitch-py4j/src/hla/vendors/pitch/py4j/adapter.py",
        "packages/hla-vendor-pitch-py4j/src/hla/vendors/pitch/py4j/factory.py",
        "packages/hla-vendor-pitch-py4j/src/hla/vendors/pitch/py4j/runtime.py",
    ):
        _assert_thin_facade_module(project_root / rel)


def test_pitch_jpype_retained_facade_modules_are_thin_reexports():
    from hla.bridges.java.jpype.adapter import JPypeRTIBackend as GenericJPypeRTIBackend
    from hla.bridges.java.jpype.factory import (
        create_jpype_backend as generic_create_jpype_backend,
        rti_ambassador as generic_rti_ambassador,
    )
    from hla.bridges.java.jpype.runtime import (
        JPypeBridge as GenericJPypeBridge,
        JPypeConfig as GenericJPypeConfig,
    )
    from hla.vendors.pitch.jpype.adapter import JPypeRTIBackend
    from hla.vendors.pitch.jpype.factory import create_jpype_backend, rti_ambassador
    from hla.vendors.pitch.jpype.runtime import JPypeBridge, JPypeConfig

    assert JPypeRTIBackend is GenericJPypeRTIBackend
    assert create_jpype_backend is generic_create_jpype_backend
    assert rti_ambassador is generic_rti_ambassador
    assert JPypeBridge is GenericJPypeBridge
    assert JPypeConfig is GenericJPypeConfig


def test_pitch_py4j_retained_facade_modules_are_thin_reexports():
    from hla.bridges.java.py4j.adapter import (
        Py4JFederateAmbassadorProxy as GenericPy4JFederateAmbassadorProxy,
        Py4JRTIBackend as GenericPy4JRTIBackend,
    )
    from hla.bridges.java.py4j.factory import (
        create_py4j_backend as generic_create_py4j_backend,
        rti_ambassador as generic_rti_ambassador,
    )
    from hla.bridges.java.py4j.runtime import (
        Py4JBridge as GenericPy4JBridge,
        Py4JConfig as GenericPy4JConfig,
        Py4JFederateAmbassadorProxy as GenericRuntimePy4JFederateAmbassadorProxy,
    )
    from hla.vendors.pitch.py4j.adapter import Py4JFederateAmbassadorProxy, Py4JRTIBackend
    from hla.vendors.pitch.py4j.factory import create_py4j_backend, rti_ambassador
    from hla.vendors.pitch.py4j.runtime import Py4JBridge, Py4JConfig, Py4JFederateAmbassadorProxy as RuntimeProxy

    assert Py4JFederateAmbassadorProxy is GenericPy4JFederateAmbassadorProxy
    assert Py4JRTIBackend is GenericPy4JRTIBackend
    assert create_py4j_backend is generic_create_py4j_backend
    assert rti_ambassador is generic_rti_ambassador
    assert Py4JBridge is GenericPy4JBridge
    assert Py4JConfig is GenericPy4JConfig
    assert RuntimeProxy is GenericRuntimePy4JFederateAmbassadorProxy


def test_split_pitch_plugin_descriptors_are_registered():
    from hla.vendors.pitch.jpype.plugin import plugin as jpype_plugin
    from hla.vendors.pitch.py4j.plugin import plugin as py4j_plugin

    jpype_descriptor = jpype_plugin()
    py4j_descriptor = py4j_plugin()

    assert isinstance(jpype_descriptor, RTIBackendPlugin)
    assert isinstance(py4j_descriptor, RTIBackendPlugin)
    assert jpype_descriptor.name == "pitch-jpype"
    assert py4j_descriptor.name == "pitch-py4j"
    assert jpype_descriptor.family == "pitch/java"
    assert py4j_descriptor.family == "pitch/java"


def test_pitch_py4j_factory_attaches_gateway_process(monkeypatch):
    import sys

    from hla.vendors.pitch.py4j import plugin as pitch_py4j_plugin

    gateway_process = object()
    captured: dict[str, object] = {}

    class FakeGateway:
        def __init__(self, *, gateway_parameters, callback_server_parameters):
            self.gateway_parameters = gateway_parameters
            self.callback_server_parameters = callback_server_parameters
            self.started = False

        def start_callback_server(self):
            self.started = True

    fake_py4j = types.ModuleType("py4j.java_gateway")
    fake_py4j.CallbackServerParameters = lambda **kwargs: ("callback", kwargs)
    fake_py4j.GatewayParameters = lambda **kwargs: ("gateway", kwargs)
    fake_py4j.JavaGateway = FakeGateway
    monkeypatch.setitem(sys.modules, "py4j.java_gateway", fake_py4j)

    monkeypatch.setattr(
        pitch_py4j_plugin,
        "reset_py4j_callback_client",
        lambda gateway: captured.setdefault("reset_gateway", gateway),
    )

    import hla.vendors.pitch as pitch_common

    monkeypatch.setattr(
        pitch_common,
        "launch_pitch_py4j_gateway",
        lambda **kwargs: (31337, gateway_process),
    )
    monkeypatch.setattr(
        pitch_common,
        "pitch_fedpro_local_settings_designator",
        lambda: "crcHost=127.0.0.1\ncrcPort=8989",
    )
    monkeypatch.setattr(
        pitch_py4j_plugin,
        "create_py4j_backend",
        lambda config: captured.setdefault("config", config),
    )

    config = pitch_py4j_plugin._pitch_py4j_backend_factory({})

    gateway = config.gateway
    assert isinstance(gateway, FakeGateway)
    assert gateway.started is True
    assert getattr(gateway, "_hla2010_gateway_process") is gateway_process
    assert config.shutdown_gateway_on_close is True
    assert config.connect_local_settings_designator == "crcHost=127.0.0.1\ncrcPort=8989"


def test_pitch_jpype_factory_uses_inprocess_runtime_without_gateway_process(monkeypatch):
    from hla.vendors.pitch.jpype import plugin as pitch_jpype_plugin

    captured: dict[str, object] = {}

    class FakeRuntime:
        def jpype_config(self, **kwargs):
            captured["jpype_config_kwargs"] = kwargs
            return {"config": kwargs}

    monkeypatch.setattr(
        pitch_jpype_plugin,
        "create_jpype_backend",
        lambda config: captured.setdefault("config", config),
    )

    import hla.vendors.pitch as pitch_common

    monkeypatch.setattr(pitch_common, "discover_pitch_runtime", lambda pitch_home=None: FakeRuntime())
    monkeypatch.setattr(
        pitch_common,
        "pitch_fedpro_local_settings_designator",
        lambda: "crcHost=127.0.0.1\ncrcPort=8989",
    )

    config = pitch_jpype_plugin._pitch_jpype_backend_factory({})

    assert config == {"config": {"rti_factory_name": "Federate Protocol", "connect_local_settings_designator": "crcHost=127.0.0.1\ncrcPort=8989"}}
    assert captured["config"] == config
    assert captured["jpype_config_kwargs"] == {
        "rti_factory_name": "Federate Protocol",
        "connect_local_settings_designator": "crcHost=127.0.0.1\ncrcPort=8989",
    }


def test_pitch_vendor_matrix_runtime_bootstrap_is_centralized():
    project_root = Path(__file__).resolve().parents[1]
    source = (project_root / "tests" / "vendors" / "test_pitch_real_backend_matrix.py").read_text(encoding="utf-8")

    assert source.count("launch_pitch_runtime(") == 1
    assert source.count("runtime_resources=(runtime,)") == 1
    assert "def _pitch_runtime_case(kind: str, ambassador_count: int):" in source
