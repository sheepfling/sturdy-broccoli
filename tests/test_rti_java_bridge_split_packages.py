from __future__ import annotations


def test_split_java_jpype_package_exports_generic_bridge_surface():
    from hla2010_rti_java_jpype import JPypeConfig
    from hla2010_rti_java_jpype.factory import create_jpype_backend
    from hla2010_rti_pitch_jpype import JPypeConfig as OldPitchConfig
    from hla2010_rti_pitch_jpype.factory import create_jpype_backend as old_pitch_create_backend

    assert OldPitchConfig is JPypeConfig
    assert old_pitch_create_backend is create_jpype_backend


def test_split_java_py4j_package_exports_generic_bridge_surface():
    from hla2010_rti_java_py4j import Py4JConfig
    from hla2010_rti_java_py4j.factory import create_py4j_backend
    from hla2010_rti_pitch_py4j import Py4JConfig as OldPitchConfig
    from hla2010_rti_pitch_py4j.factory import create_py4j_backend as old_pitch_create_backend

    assert OldPitchConfig is Py4JConfig
    assert old_pitch_create_backend is create_py4j_backend
