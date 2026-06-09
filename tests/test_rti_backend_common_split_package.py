from __future__ import annotations


def test_split_backend_common_package_exports_conversion_surface():
    from hla2010.backends.conversion import NativeHandleRegistry as OldNativeHandleRegistry
    from hla2010.backends.conversion import ValueConverter as OldValueConverter
    from hla2010.backends.conversion import clean_java_type_name as old_clean_java_type_name
    from hla2010_rti_backend_common import NativeHandleRegistry, ValueConverter, clean_java_type_name

    assert OldNativeHandleRegistry is NativeHandleRegistry
    assert OldValueConverter is ValueConverter
    assert old_clean_java_type_name is clean_java_type_name


def test_split_java_common_package_imports_backend_common_from_new_package():
    from hla2010_rti_backend_common import NativeHandleRegistry, ValueConverter
    from hla2010_rti_java_common import JavaValueConverter

    assert issubclass(JavaValueConverter, ValueConverter)
    converter = JavaValueConverter.__mro__[1]
    assert converter is ValueConverter
    assert NativeHandleRegistry.__name__ == "NativeHandleRegistry"
