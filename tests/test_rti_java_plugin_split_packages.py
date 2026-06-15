from __future__ import annotations

import sys
import types

from hla2010_rti_backend_common import RTIBackendPlugin


def test_split_java_plugin_packages_export_generic_plugin_descriptors():
    import hla2010_rti_java_jpype
    import hla2010_rti_java_py4j
    from hla2010_rti_java_jpype import JPypeBridge, JPypeConfig, JPypeRTIBackend, create_jpype_backend
    from hla2010_rti_java_jpype.plugin import plugin as jpype_plugin
    from hla2010_rti_java_jpype.runtime import JPypeBridge as JPypeBridgeFromModule
    from hla2010_rti_java_jpype.runtime import JPypeConfig as JPypeConfigFromModule
    from hla2010_rti_java_jpype.adapter import JPypeRTIBackend as JPypeRTIBackendFromModule
    from hla2010_rti_java_jpype.factory import create_jpype_backend as create_jpype_backend_from_module
    from hla2010_rti_java_py4j import Py4JBridge, Py4JConfig, Py4JFederateAmbassadorProxy, Py4JRTIBackend, create_py4j_backend
    from hla2010_rti_java_py4j.plugin import plugin as py4j_plugin
    from hla2010_rti_java_py4j.runtime import Py4JBridge as Py4JBridgeFromModule
    from hla2010_rti_java_py4j.runtime import Py4JConfig as Py4JConfigFromModule
    from hla2010_rti_java_py4j.adapter import (
        Py4JFederateAmbassadorProxy as Py4JFederateAmbassadorProxyFromModule,
    )
    from hla2010_rti_java_py4j.adapter import Py4JRTIBackend as Py4JRTIBackendFromModule
    from hla2010_rti_java_py4j.factory import create_py4j_backend as create_py4j_backend_from_module

    jpype_descriptor = jpype_plugin()
    py4j_descriptor = py4j_plugin()

    assert hla2010_rti_java_jpype.JPypeBridge is JPypeBridge is JPypeBridgeFromModule
    assert hla2010_rti_java_jpype.JPypeConfig is JPypeConfig is JPypeConfigFromModule
    assert hla2010_rti_java_jpype.JPypeRTIBackend is JPypeRTIBackend is JPypeRTIBackendFromModule
    assert hla2010_rti_java_jpype.create_jpype_backend is create_jpype_backend is create_jpype_backend_from_module
    assert hla2010_rti_java_py4j.Py4JBridge is Py4JBridge is Py4JBridgeFromModule
    assert hla2010_rti_java_py4j.Py4JConfig is Py4JConfig is Py4JConfigFromModule
    assert (
        hla2010_rti_java_py4j.Py4JFederateAmbassadorProxy
        is Py4JFederateAmbassadorProxy
        is Py4JFederateAmbassadorProxyFromModule
    )
    assert hla2010_rti_java_py4j.Py4JRTIBackend is Py4JRTIBackend is Py4JRTIBackendFromModule
    assert hla2010_rti_java_py4j.create_py4j_backend is create_py4j_backend is create_py4j_backend_from_module
    assert isinstance(jpype_descriptor, RTIBackendPlugin)
    assert isinstance(py4j_descriptor, RTIBackendPlugin)
    assert jpype_descriptor.name == "jpype"
    assert py4j_descriptor.name == "py4j"
    assert jpype_descriptor.family == "java"
    assert py4j_descriptor.family == "java"


def test_generic_py4j_bridge_resets_callback_client_for_provided_gateway(monkeypatch):
    from hla2010_rti_java_py4j.runtime import Py4JBridge, Py4JConfig

    gateway = object()
    captured: list[object] = []
    monkeypatch.setattr(
        "hla2010_rti_java_py4j.runtime.reset_py4j_callback_client",
        lambda actual_gateway: captured.append(actual_gateway),
    )

    bridge = Py4JBridge(Py4JConfig(gateway=gateway))

    assert bridge.gateway is gateway
    assert captured == [gateway]


def test_generic_py4j_bridge_starts_and_resets_owned_gateway(monkeypatch):
    from hla2010_rti_java_py4j.runtime import Py4JBridge, Py4JConfig

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
        "hla2010_rti_java_py4j.runtime.reset_py4j_callback_client",
        lambda gateway: captured.setdefault("gateway", gateway),
    )

    bridge = Py4JBridge(Py4JConfig())

    assert isinstance(bridge.gateway, FakeGateway)
    assert bridge.owns_gateway is True
    assert bridge.gateway.started is True
    assert captured["gateway"] is bridge.gateway
