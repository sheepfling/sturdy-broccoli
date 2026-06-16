from __future__ import annotations

from hla.backends.common import RTIBackendPlugin


def test_split_java_plugin_packages_export_generic_plugin_descriptors():
    import hla.bridges.java.jpype
    import hla.bridges.java.py4j
    from hla.bridges.java.jpype import JPypeBridge, JPypeConfig, JPypeRTIBackend, create_jpype_backend
    from hla.bridges.java.jpype.plugin import plugin as jpype_plugin
    from hla.bridges.java.jpype.runtime import JPypeBridge as JPypeBridgeFromModule
    from hla.bridges.java.jpype.runtime import JPypeConfig as JPypeConfigFromModule
    from hla.bridges.java.jpype.adapter import JPypeRTIBackend as JPypeRTIBackendFromModule
    from hla.bridges.java.jpype.factory import create_jpype_backend as create_jpype_backend_from_module
    from hla.bridges.java.py4j import Py4JBridge, Py4JConfig, Py4JFederateAmbassadorProxy, Py4JRTIBackend, create_py4j_backend
    from hla.bridges.java.py4j.plugin import plugin as py4j_plugin
    from hla.bridges.java.py4j.runtime import Py4JBridge as Py4JBridgeFromModule
    from hla.bridges.java.py4j.runtime import Py4JConfig as Py4JConfigFromModule
    from hla.bridges.java.py4j.adapter import (
        Py4JFederateAmbassadorProxy as Py4JFederateAmbassadorProxyFromModule,
    )
    from hla.bridges.java.py4j.adapter import Py4JRTIBackend as Py4JRTIBackendFromModule
    from hla.bridges.java.py4j.factory import create_py4j_backend as create_py4j_backend_from_module

    jpype_descriptor = jpype_plugin()
    py4j_descriptor = py4j_plugin()

    assert hla.bridges.java.jpype.JPypeBridge is JPypeBridge is JPypeBridgeFromModule
    assert hla.bridges.java.jpype.JPypeConfig is JPypeConfig is JPypeConfigFromModule
    assert hla.bridges.java.jpype.JPypeRTIBackend is JPypeRTIBackend is JPypeRTIBackendFromModule
    assert hla.bridges.java.jpype.create_jpype_backend is create_jpype_backend is create_jpype_backend_from_module
    assert hla.bridges.java.py4j.Py4JBridge is Py4JBridge is Py4JBridgeFromModule
    assert hla.bridges.java.py4j.Py4JConfig is Py4JConfig is Py4JConfigFromModule
    assert (
        hla.bridges.java.py4j.Py4JFederateAmbassadorProxy
        is Py4JFederateAmbassadorProxy
        is Py4JFederateAmbassadorProxyFromModule
    )
    assert hla.bridges.java.py4j.Py4JRTIBackend is Py4JRTIBackend is Py4JRTIBackendFromModule
    assert hla.bridges.java.py4j.create_py4j_backend is create_py4j_backend is create_py4j_backend_from_module
    assert isinstance(jpype_descriptor, RTIBackendPlugin)
    assert isinstance(py4j_descriptor, RTIBackendPlugin)
    assert jpype_descriptor.name == "jpype"
    assert py4j_descriptor.name == "py4j"
    assert jpype_descriptor.family == "java"
    assert py4j_descriptor.family == "java"
