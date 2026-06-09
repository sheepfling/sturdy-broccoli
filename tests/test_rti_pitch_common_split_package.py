from __future__ import annotations

from hla2010_rti_pitch_common import PitchRuntime, pitch_fedpro_local_settings_designator


def test_split_pitch_common_package_exports_runtime_helpers():
    from hla2010.real_rti_pitch import PitchRuntime as OldPitchRuntime
    from hla2010.real_rti_pitch import pitch_fedpro_local_settings_designator as old_designator

    assert OldPitchRuntime is PitchRuntime
    assert old_designator is pitch_fedpro_local_settings_designator


def test_pitch_plugins_import_common_runtime_helpers():
    from hla2010_rti_pitch_jpype.plugin import plugin as jpype_plugin
    from hla2010_rti_pitch_py4j.plugin import plugin as py4j_plugin

    assert jpype_plugin().name == "pitch-jpype"
    assert py4j_plugin().name == "pitch-py4j"
