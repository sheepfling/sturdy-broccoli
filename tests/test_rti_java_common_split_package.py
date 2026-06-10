from __future__ import annotations


def test_split_java_common_package_exports_shared_java_support_surface():
    from hla2010_rti_java_common import JavaBridge, JavaRTIBackend, resolve_java_arguments

    assert JavaBridge.__module__.startswith("hla2010_rti_java_common")
    assert JavaRTIBackend.__module__.startswith("hla2010_rti_java_common")
    assert resolve_java_arguments.__module__ in {
        "hla2010_rti_java_common.java_common",
        "hla2010_rti_backend_common.invocation",
    }


def test_split_java_bridge_packages_import_shared_java_support_from_new_package():
    from hla2010_rti_java_common import JavaBridge, JavaRTIBackend
    from hla2010_rti_java_jpype.adapter import JPypeRTIBackend
    from hla2010_rti_java_jpype.runtime import JPypeBridge
    from hla2010_rti_java_py4j.adapter import Py4JRTIBackend
    from hla2010_rti_java_py4j.runtime import Py4JBridge

    assert issubclass(JPypeBridge, JavaBridge)
    assert issubclass(Py4JBridge, JavaBridge)
    assert issubclass(JPypeRTIBackend, JavaRTIBackend)
    assert issubclass(Py4JRTIBackend, JavaRTIBackend)
