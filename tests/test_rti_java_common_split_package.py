from __future__ import annotations


def test_split_java_common_package_exports_shared_java_support_surface():
    from hla2010.backends.java_common import JavaBridge as OldJavaBridge
    from hla2010.backends.java_common import JavaRTIBackend as OldJavaRTIBackend
    from hla2010.backends.java_common import resolve_java_arguments as old_resolve_java_arguments
    from hla2010_rti_java_common import JavaBridge, JavaRTIBackend, resolve_java_arguments

    assert OldJavaBridge is JavaBridge
    assert OldJavaRTIBackend is JavaRTIBackend
    assert old_resolve_java_arguments is resolve_java_arguments


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
