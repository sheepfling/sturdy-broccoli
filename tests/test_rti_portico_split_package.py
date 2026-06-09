from __future__ import annotations

from hla2010.rti import RTIBackendPlugin


def test_split_portico_package_exports_runtime_helpers():
    from hla2010.real_rti_portico import PorticoRuntime as OldRuntime
    from hla2010.real_rti_portico import discover_portico_runtime as old_discover
    from hla2010_rti_portico import PorticoRuntime, discover_portico_runtime

    assert OldRuntime is PorticoRuntime
    assert old_discover is discover_portico_runtime


def test_split_portico_plugin_descriptors_are_registered():
    from hla2010.backends.java_plugins import portico_jpype_plugin as old_jpype_plugin
    from hla2010.backends.java_plugins import portico_py4j_plugin as old_py4j_plugin
    from hla2010_rti_portico.plugin import portico_jpype_plugin, portico_py4j_plugin

    jpype_descriptor = portico_jpype_plugin()
    py4j_descriptor = portico_py4j_plugin()

    assert isinstance(jpype_descriptor, RTIBackendPlugin)
    assert isinstance(py4j_descriptor, RTIBackendPlugin)
    assert jpype_descriptor.name == "portico-jpype"
    assert py4j_descriptor.name == "portico-py4j"
    assert jpype_descriptor.family == "portico/java"
    assert py4j_descriptor.family == "portico/java"
    assert old_jpype_plugin().name == jpype_descriptor.name
    assert old_py4j_plugin().name == py4j_descriptor.name
