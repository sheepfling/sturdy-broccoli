from __future__ import annotations


def test_split_backend_common_package_root_re_exports_conversion_surface():
    from hla2010_rti_backend_common import NativeHandleRegistry, ValueConverter, clean_java_type_name
    from hla2010_rti_backend_common.conversion import (
        NativeHandleRegistry as NativeHandleRegistryFromModule,
    )
    from hla2010_rti_backend_common.conversion import ValueConverter as ValueConverterFromModule
    from hla2010_rti_backend_common.conversion import clean_java_type_name as clean_java_type_name_from_module

    assert NativeHandleRegistryFromModule is NativeHandleRegistry
    assert ValueConverterFromModule is ValueConverter
    assert clean_java_type_name_from_module is clean_java_type_name


def test_split_java_common_package_imports_backend_common_from_new_package():
    from hla2010_rti_backend_common import NativeHandleRegistry, ValueConverter
    from hla2010_rti_java_common import JavaValueConverter

    assert issubclass(JavaValueConverter, ValueConverter)
    converter = JavaValueConverter.__mro__[1]
    assert converter is ValueConverter
    assert NativeHandleRegistry.__name__ == "NativeHandleRegistry"
