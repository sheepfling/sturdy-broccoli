from __future__ import annotations

from pathlib import Path

from hla.vendors.pitch import (
    PitchRuntime,
    pitch_hla4_direct_classpath,
    pitch_hla4_fedpro_classpath,
    launch_pitch_two_federate_profile,
    pitch_fedpro_local_settings_designator,
)


def test_split_pitch_common_package_exports_runtime_helpers():
    from hla.vendors.pitch.real_rti_pitch import (
        PitchRuntime as RuntimeFromModule,
    )
    from hla.vendors.pitch.real_rti_pitch import (
        pitch_fedpro_local_settings_designator as designator_from_module,
    )
    from hla.vendors.pitch.testing_policy import (
        launch_pitch_two_federate_profile as launch_profile_from_module,
    )

    assert RuntimeFromModule is PitchRuntime
    assert launch_profile_from_module is launch_pitch_two_federate_profile
    assert designator_from_module is pitch_fedpro_local_settings_designator


def test_pitch_plugins_import_common_runtime_helpers():
    from hla.vendors.pitch.jpype.plugin import pitch_native_202x_plugin as jpype_native_202x_plugin
    from hla.vendors.pitch.jpype.plugin import pitch_202x_plugin as jpype_202x_plugin
    from hla.vendors.pitch.jpype.plugin import plugin as jpype_plugin
    from hla.vendors.pitch.py4j.plugin import pitch_native_202x_plugin as py4j_native_202x_plugin
    from hla.vendors.pitch.py4j.plugin import pitch_202x_plugin as py4j_202x_plugin
    from hla.vendors.pitch.py4j.plugin import plugin as py4j_plugin

    assert jpype_plugin().name == "pitch-jpype"
    assert py4j_plugin().name == "pitch-py4j"
    assert jpype_202x_plugin().name == "pitch-202x-jpype"
    assert py4j_202x_plugin().name == "pitch-202x-py4j"
    assert jpype_native_202x_plugin().name == "pitch-native-202x-jpype"
    assert py4j_native_202x_plugin().name == "pitch-native-202x-py4j"


def test_pitch_hla4_classpath_helpers_split_direct_and_fedpro_surfaces(tmp_path: Path):
    runtime = PitchRuntime(
        home=tmp_path / "pitch",
        java_home=tmp_path / "java-home",
        classpath=(tmp_path / "lib" / "pitch.jar",),
        java_library_path=(tmp_path / "lib",),
    )
    lib_dir = runtime.home / "lib"
    lib_dir.mkdir(parents=True)
    (lib_dir / "prti1516_202X.jar").write_text("", encoding="utf-8")
    for name in (
        "fedpro-client-hla4.jar",
        "fedpro-session.jar",
        "protobuf-java-3.21.7.jar",
        "protobuf.jar",
        "slf4j-api-2.0.5.jar",
        "slf4j-nop-2.0.5.jar",
    ):
        (lib_dir / name).write_text("", encoding="utf-8")

    direct = pitch_hla4_direct_classpath(runtime)
    fedpro = pitch_hla4_fedpro_classpath(runtime)

    assert [path.name for path in direct] == ["prti1516_202X.jar"]
    assert [path.name for path in fedpro] == [
        "fedpro-client-hla4.jar",
        "fedpro-session.jar",
        "protobuf-java-3.21.7.jar",
        "protobuf.jar",
        "slf4j-api-2.0.5.jar",
        "slf4j-nop-2.0.5.jar",
    ]


def test_launch_pitch_py4j_gateway_can_return_process_handle(monkeypatch, tmp_path: Path):
    from hla.vendors.pitch import real_rti_pitch

    runtime = PitchRuntime(
        home=tmp_path / "pitch",
        java_home=tmp_path / "java-home",
        classpath=(tmp_path / "lib" / "pitch.jar",),
        java_library_path=(tmp_path / "lib",),
    )
    (tmp_path / "lib").mkdir(parents=True)
    runtime.home.mkdir(parents=True)
    (tmp_path / "user-home").mkdir(parents=True)

    recorded: dict[str, object] = {}

    def fake_launch_gateway(**kwargs):
        recorded.update(kwargs)
        return (4242, object())

    monkeypatch.setattr(real_rti_pitch, "discover_pitch_runtime", lambda pitch_home=None: runtime)
    monkeypatch.setattr(real_rti_pitch, "ensure_java_home", lambda: None)
    monkeypatch.setattr(real_rti_pitch, "discover_java_tool", lambda name: "/fake/java")
    monkeypatch.setattr(real_rti_pitch, "prepare_pitch_user_home", lambda runtime: tmp_path / "user-home")
    monkeypatch.setattr("py4j.java_gateway.launch_gateway", fake_launch_gateway)

    port, proc = real_rti_pitch.launch_pitch_py4j_gateway(return_proc=True)

    assert port == 4242
    assert proc is not None
    assert recorded["return_proc"] is True
    assert recorded["java_path"] == "/fake/java"
