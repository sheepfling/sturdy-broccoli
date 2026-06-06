from pathlib import Path
import subprocess

from hla2010.real_rti import (
    _parse_pitch_license_list,
    discover_certi_runtime,
    discover_pitch_runtime,
    list_pitch_licenses,
)


def test_discover_pitch_runtime_from_env(tmp_path, monkeypatch):
    home = tmp_path / "pitch-home"
    (home / "Contents" / "Home" / "bin").mkdir(parents=True)
    (home / "Contents" / "Home" / "bin" / "java").write_text("")
    (home / "lib").mkdir()
    (home / "lib" / "prtifull.jar").write_text("")
    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    runtime = discover_pitch_runtime()
    assert runtime.home == home
    assert any(path.name == "prtifull.jar" for path in runtime.classpath)
    config = runtime.jpype_config()
    assert any(str(home / "user.home") in arg for arg in config.jvm_args)
    assert any("java.library.path=" in arg for arg in config.jvm_args)


def test_discover_certi_runtime_from_env(tmp_path, monkeypatch):
    prefix = tmp_path / "certi-install"
    (prefix / "bin").mkdir(parents=True)
    (prefix / "lib").mkdir()
    (prefix / "bin" / "rtig").write_text("")
    monkeypatch.setenv("HLA2010_CERTI_PREFIX", str(prefix))
    runtime = discover_certi_runtime()
    assert runtime.prefix == prefix
    assert runtime.executable("rtig") == prefix / "bin" / "rtig"
    env = runtime.runtime_env()
    assert env["CERTI_HOME"] == str(prefix)
    assert env["CERTI_FOM_PATH"] == str(prefix / "share" / "federations")


def test_discover_certi_runtime_prefers_build_tree_libraries(tmp_path, monkeypatch):
    prefix = tmp_path / "certi-install"
    build_root = tmp_path / "certi-build"
    (prefix / "bin").mkdir(parents=True)
    (prefix / "lib").mkdir()
    (prefix / "bin" / "rtig").write_text("")
    (build_root / "libRTI" / "ieee1516-2010").mkdir(parents=True)
    (build_root / "libCERTI").mkdir(parents=True)
    (build_root / "libRTI" / "ieee1516-2010" / "libRTI1516ed.dylib").write_text("")
    (build_root / "libCERTI" / "libCERTId.dylib").write_text("")

    monkeypatch.setenv("HLA2010_CERTI_PREFIX", str(prefix))
    monkeypatch.setenv("HLA2010_CERTI_BUILD_ROOT", str(build_root))
    runtime = discover_certi_runtime()

    assert runtime.prefix == prefix
    assert runtime.lib_dirs[0] == build_root / "libRTI" / "ieee1516-2010"
    assert runtime.lib_dirs[1] == build_root / "libCERTI"
    assert runtime.lib_dirs[-1] == prefix / "lib"
    env = runtime.runtime_env()
    assert env["DYLD_LIBRARY_PATH"].startswith(
        f"{build_root / 'libRTI' / 'ieee1516-2010'}:{build_root / 'libCERTI'}:{prefix / 'lib'}"
    )


def test_parse_pitch_license_list():
    records = _parse_pitch_license_list(
        " Id  Type     Seats  Hardware id  User\n"
        " 1   primary  2      abcd1234     rick\n"
    )
    assert len(records) == 1
    assert records[0].license_type == "primary"
    assert records[0].seats == "2"
    assert records[0].hardware_id == "abcd1234"


def test_list_pitch_licenses_invokes_license_activator(tmp_path, monkeypatch):
    home = tmp_path / "pitch-home"
    java_bin = home / "Contents" / "Home" / "bin"
    java_bin.mkdir(parents=True)
    (java_bin / "java").write_text("")
    lib = home / "lib"
    lib.mkdir()
    (lib / "prtifull.jar").write_text("")
    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))

    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=" Id  Type     Seats  Hardware id  User\n 1   primary  2      abcd1234     rick\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    licenses = list_pitch_licenses(user_home=tmp_path / "pitch-user-home")
    assert licenses[0].license_id == "1"
    assert licenses[0].user == "rick"
    assert captured["command"][-2:] == ["se.pitch.prti1516e.LicenseActivator", "list"]
