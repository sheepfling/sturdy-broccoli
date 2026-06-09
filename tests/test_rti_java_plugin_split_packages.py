from __future__ import annotations

from hla2010.rti import RTIBackendPlugin


def test_split_java_plugin_packages_export_generic_plugin_descriptors():
    from hla2010_rti_java_jpype.plugin import plugin as jpype_plugin
    from hla2010_rti_java_py4j.plugin import plugin as py4j_plugin

    jpype_descriptor = jpype_plugin()
    py4j_descriptor = py4j_plugin()

    assert isinstance(jpype_descriptor, RTIBackendPlugin)
    assert isinstance(py4j_descriptor, RTIBackendPlugin)
    assert jpype_descriptor.name == "jpype"
    assert py4j_descriptor.name == "py4j"
    assert jpype_descriptor.family == "java"
    assert py4j_descriptor.family == "java"


def test_legacy_java_plugins_module_delegates_to_split_generic_plugins():
    from hla2010.backends.java_plugins import jpype_plugin as old_jpype_plugin
    from hla2010.backends.java_plugins import py4j_plugin as old_py4j_plugin
    from hla2010_rti_java_jpype.plugin import jpype_plugin
    from hla2010_rti_java_py4j.plugin import py4j_plugin

    assert old_jpype_plugin().name == jpype_plugin().name
    assert old_py4j_plugin().name == py4j_plugin().name
