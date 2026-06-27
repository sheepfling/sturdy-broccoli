from __future__ import annotations


def test_split_java_common_package_exports_shared_java_support_surface():
    from hla.bridges.java.common import JavaBridge, JavaRTIBackend, resolve_java_arguments

    assert JavaBridge.__module__.startswith("hla.bridges.java.common")
    assert JavaRTIBackend.__module__.startswith("hla.bridges.java.common")
    assert resolve_java_arguments.__module__ in {
        "hla.bridges.java.common.java_common",
        "hla.backends.common.invocation",
        "hla.backends.common.java_invocation_policy",
    }


def test_split_java_bridge_packages_import_shared_java_support_from_new_package():
    from hla.bridges.java.common import JavaBridge, JavaRTIBackend
    from hla.bridges.java.jpype.adapter import JPypeRTIBackend
    from hla.bridges.java.jpype.runtime import JPypeBridge
    from hla.bridges.java.py4j.adapter import Py4JRTIBackend
    from hla.bridges.java.py4j.runtime import Py4JBridge

    assert issubclass(JPypeBridge, JavaBridge)
    assert issubclass(Py4JBridge, JavaBridge)
    assert issubclass(JPypeRTIBackend, JavaRTIBackend)
    assert issubclass(Py4JRTIBackend, JavaRTIBackend)
