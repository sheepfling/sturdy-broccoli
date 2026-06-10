from __future__ import annotations

from hla2010.rti import RTIBackendPlugin


def test_split_pitch_jpype_package_exports_adapter_surface():
    from hla2010_rti_pitch_jpype import JPypeConfig
    from hla2010_rti_pitch_jpype.factory import create_jpype_backend

    assert JPypeConfig.__module__.startswith("hla2010_rti_java_jpype")
    assert create_jpype_backend.__module__.startswith("hla2010_rti_java_jpype")


def test_split_pitch_py4j_package_exports_adapter_surface():
    from hla2010_rti_pitch_py4j import Py4JConfig
    from hla2010_rti_pitch_py4j.factory import create_py4j_backend

    assert Py4JConfig.__module__.startswith("hla2010_rti_java_py4j")
    assert create_py4j_backend.__module__.startswith("hla2010_rti_java_py4j")


def test_split_pitch_plugin_descriptors_are_registered():
    from hla2010_rti_pitch_jpype.plugin import plugin as jpype_plugin
    from hla2010_rti_pitch_py4j.plugin import plugin as py4j_plugin

    jpype_descriptor = jpype_plugin()
    py4j_descriptor = py4j_plugin()

    assert isinstance(jpype_descriptor, RTIBackendPlugin)
    assert isinstance(py4j_descriptor, RTIBackendPlugin)
    assert jpype_descriptor.name == "pitch-jpype"
    assert py4j_descriptor.name == "pitch-py4j"
    assert jpype_descriptor.family == "pitch/java"
    assert py4j_descriptor.family == "pitch/java"
