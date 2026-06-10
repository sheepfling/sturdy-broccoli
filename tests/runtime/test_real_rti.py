import os
import subprocess
from pathlib import Path

from hla2010.real_rti import (
    _parse_pitch_license_list,
    discover_certi_runtime,
    discover_certi_runtime_profile,
    discover_pitch_runtime,
    list_pitch_licenses,
    launch_pitch_runtime,
    pitch_connect_local_settings_designator,
    pitch_fedpro_local_settings_designator,
    prepare_pitch_user_home,
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
    local_state_root = Path(
        os.environ.get(
            "HLA2010_LOCAL_STATE_ROOT",
            str(Path(__file__).resolve().parents[2] / ".local"),
        )
    )
    expected_user_home = local_state_root / "pitch" / "user-home"
    assert any(str(expected_user_home) in arg for arg in config.jvm_args)
    assert any("java.library.path=" in arg for arg in config.jvm_args)
    assert config.connect_local_settings_designator == "localhost"


def test_pitch_fedpro_local_settings_designator_defaults_to_localhost(monkeypatch):
    monkeypatch.delenv("HLA2010_PITCH_FEDPRO_LOCAL_SETTINGS_DESIGNATOR", raising=False)
    monkeypatch.delenv("HLA2010_PITCH_FEDPRO_ADDRESS", raising=False)

    assert pitch_fedpro_local_settings_designator() == "localhost"
    assert pitch_connect_local_settings_designator() == "localhost"


def test_pitch_fedpro_local_settings_designator_honors_explicit_designator(monkeypatch):
    monkeypatch.setenv("HLA2010_PITCH_FEDPRO_LOCAL_SETTINGS_DESIGNATOR", "fedpro.example:15164")

    assert pitch_fedpro_local_settings_designator() == "fedpro.example:15164"


def test_pitch_fedpro_local_settings_designator_uses_container_crc_loopback_in_docker_mode(monkeypatch):
    monkeypatch.delenv("HLA2010_PITCH_FEDPRO_LOCAL_SETTINGS_DESIGNATOR", raising=False)
    monkeypatch.setenv("HLA2010_PITCH_CRC_MODE", "docker")
    monkeypatch.setenv("HLA2010_PITCH_CRC_PORT", "18989")

    assert pitch_fedpro_local_settings_designator() == "localhost;;crcAddress=127.0.0.1:18989"


def test_discover_pitch_runtime_from_installed_layout(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    (home / "lib").mkdir(parents=True)
    (home / "lib" / "prtifull.jar").write_text("")
    (home / "lib" / "clang12").mkdir()
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin").mkdir(parents=True)
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin" / "java").write_text("")

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    runtime = discover_pitch_runtime()

    assert runtime.home == home
    assert runtime.java_home == home / ".install4j" / "jre.bundle" / "Contents" / "Home"
    assert runtime.java_library_path[0] == home / "lib"
    assert runtime.java_library_path[1] == home / "lib" / "clang12"


def test_discover_pitch_runtime_honors_external_java_home_override(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    external_java_home = tmp_path / "external-jdk"
    (home / "lib").mkdir(parents=True)
    (home / "lib" / "prtifull.jar").write_text("")
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin").mkdir(parents=True)
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin" / "java").write_text("")
    (external_java_home / "bin").mkdir(parents=True)
    (external_java_home / "bin" / "java").write_text("")

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setenv("HLA2010_PITCH_JAVA_HOME", str(external_java_home))

    runtime = discover_pitch_runtime()

    assert runtime.home == home
    assert runtime.java_home == external_java_home


def test_launch_pitch_runtime_passes_ui_automation_env(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin").mkdir(parents=True)
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin" / "java").write_text("")
    (home / "lib").mkdir()
    (home / "lib" / "prtifull.jar").write_text("")

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setattr("hla2010.real_rti.wait_for_process_boot", lambda *args, **kwargs: None)
    monkeypatch.setattr("hla2010.real_rti.wait_for_tcp_listener", lambda *args, **kwargs: None)

    captured: dict[str, object] = {}

    class FakeProcess:
        returncode = None

        def poll(self):
            return None

        def terminate(self):
            self.returncode = 0

        def wait(self, timeout=None):
            self.returncode = 0

        def kill(self):
            self.returncode = -9

    def fake_popen(command, **kwargs):
        captured.setdefault("commands", []).append(command)
        captured.setdefault("envs", []).append(kwargs["env"])
        return FakeProcess()

    monkeypatch.setattr("hla2010.real_rti.subprocess.Popen", fake_popen)

    runtime = launch_pitch_runtime(ui_automation=True)
    runtime.terminate()

    assert any(env.get("HLA2010_PITCH_UI_AUTOMATION") == "1" for env in captured["envs"])


def test_launch_pitch_runtime_can_use_docker_crc_mode(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin").mkdir(parents=True)
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin" / "java").write_text("")
    (home / "lib").mkdir()
    (home / "lib" / "prtifull.jar").write_text("")

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setattr("hla2010.real_rti.wait_for_process_boot", lambda *args, **kwargs: None)
    monkeypatch.setattr("hla2010.real_rti.wait_for_tcp_listener", lambda *args, **kwargs: None)

    captured: dict[str, object] = {}

    class FakeProcess:
        returncode = None

        def poll(self):
            return None

        def terminate(self):
            self.returncode = 0

        def wait(self, timeout=None):
            self.returncode = 0

        def kill(self):
            self.returncode = -9

    def fake_popen(command, **kwargs):
        captured.setdefault("commands", []).append(command)
        captured.setdefault("envs", []).append(kwargs["env"])
        return FakeProcess()

    monkeypatch.setattr("hla2010.real_rti.subprocess.Popen", fake_popen)

    runtime = launch_pitch_runtime(crc_mode="docker")
    runtime.terminate()

    commands = captured["commands"]
    assert any(command[0].endswith("scripts/run_pitch_docker_crc.sh") for command in commands)
    assert not any(command[-1] == "se.pitch.fedpro.server.hla.FedProServerApp" for command in commands)
    docker_env = captured["envs"][commands.index(next(command for command in commands if command[0].endswith("scripts/run_pitch_docker_crc.sh")))]
    assert docker_env["HOME"] != docker_env["HLA2010_PITCH_USER_HOME"]
    assert runtime.name == "pitch-docker"
    assert runtime.children == ()


def test_launch_pitch_runtime_honors_docker_crc_mode_env(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin").mkdir(parents=True)
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin" / "java").write_text("")
    (home / "lib").mkdir()
    (home / "lib" / "prtifull.jar").write_text("")

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setenv("HLA2010_PITCH_CRC_MODE", "docker")
    monkeypatch.setattr("hla2010.real_rti.wait_for_process_boot", lambda *args, **kwargs: None)
    monkeypatch.setattr("hla2010.real_rti.wait_for_tcp_listener", lambda *args, **kwargs: None)

    captured: dict[str, object] = {}

    class FakeProcess:
        returncode = None

        def poll(self):
            return None

        def terminate(self):
            self.returncode = 0

        def wait(self, timeout=None):
            self.returncode = 0

        def kill(self):
            self.returncode = -9

    def fake_popen(command, **kwargs):
        captured.setdefault("commands", []).append(command)
        captured.setdefault("envs", []).append(kwargs["env"])
        return FakeProcess()

    monkeypatch.setattr("hla2010.real_rti.subprocess.Popen", fake_popen)

    runtime = launch_pitch_runtime()
    runtime.terminate()

    commands = captured["commands"]
    assert any(command[0].endswith("scripts/run_pitch_docker_crc.sh") for command in commands)
    assert any(env.get("HLA2010_PITCH_CRC_MODE") == "docker" for env in captured["envs"])
    assert runtime.name == "pitch-docker"


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


def test_discover_certi_upstream_profile_does_not_use_repo_overlay(tmp_path, monkeypatch):
    prefix = tmp_path / "upstream-certi-install"
    repo_overlay = tmp_path / "repo-certi-build"
    (prefix / "bin").mkdir(parents=True)
    (prefix / "lib").mkdir()
    (prefix / "bin" / "rtig").write_text("")
    (repo_overlay / "libRTI" / "ieee1516-2010").mkdir(parents=True)
    (repo_overlay / "libCERTI").mkdir(parents=True)
    (repo_overlay / "libRTI" / "ieee1516-2010" / "libRTI1516ed.dylib").write_text("")
    (repo_overlay / "libCERTI" / "libCERTId.dylib").write_text("")

    monkeypatch.delenv("HLA2010_CERTI_PREFIX", raising=False)
    monkeypatch.setenv("HLA2010_CERTI_UPSTREAM_PREFIX", str(prefix))
    monkeypatch.setenv("HLA2010_CERTI_BUILD_ROOT", str(repo_overlay))

    profile = discover_certi_runtime_profile("certi-upstream")

    assert profile.name == "certi-upstream"
    assert profile.source == "upstream"
    assert profile.runtime.prefix == prefix
    assert profile.runtime.profile == "certi-upstream"
    assert repo_overlay / "libRTI" / "ieee1516-2010" not in profile.runtime.lib_dirs
    assert profile.runtime.lib_dirs == (prefix / "lib",)


def test_discover_certi_patched_profile_prefers_patched_over_generic_env(tmp_path, monkeypatch):
    generic_prefix = tmp_path / "generic-certi-install"
    patched_prefix = tmp_path / "patched-certi-install"
    patched_build = tmp_path / "patched-certi-build"
    for prefix in (generic_prefix, patched_prefix):
        (prefix / "bin").mkdir(parents=True)
        (prefix / "lib").mkdir()
        (prefix / "bin" / "rtig").write_text("")
    (patched_build / "libRTI" / "ieee1516-2010").mkdir(parents=True)
    (patched_build / "libCERTI").mkdir(parents=True)
    (patched_build / "libRTI" / "ieee1516-2010" / "libRTI1516ed.dylib").write_text("")
    (patched_build / "libCERTI" / "libCERTId.dylib").write_text("")

    monkeypatch.setenv("HLA2010_CERTI_PREFIX", str(generic_prefix))
    monkeypatch.setenv("HLA2010_CERTI_PATCHED_PREFIX", str(patched_prefix))
    monkeypatch.setenv("HLA2010_CERTI_PATCHED_BUILD_ROOT", str(patched_build))

    profile = discover_certi_runtime_profile("certi-patched")

    assert profile.name == "certi-patched"
    assert profile.source == "repo-local patched"
    assert profile.runtime.prefix == patched_prefix
    assert profile.runtime.profile == "certi-patched"
    assert profile.runtime.lib_dirs[0] == patched_build / "libRTI" / "ieee1516-2010"
    assert profile.runtime.lib_dirs[1] == patched_build / "libCERTI"


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


def test_prepare_pitch_user_home_copies_license_state_and_validates(tmp_path, monkeypatch):
    home = tmp_path / "pitch-home"
    java_bin = home / "Contents" / "Home" / "bin"
    java_bin.mkdir(parents=True)
    (java_bin / "java").write_text("")
    lib = home / "lib"
    lib.mkdir()
    (lib / "prtifull.jar").write_text("")

    source_user_home = tmp_path / "pitch-user-home-source"
    source_user_home.mkdir()
    (source_user_home / "license.dat").write_text("licensed")

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setenv("HLA2010_PITCH_USER_HOME", str(source_user_home))

    def fake_list_pitch_licenses(_pitch_home=None, *, user_home=None):
        assert Path(user_home) == tmp_path / "pitch-user-home-work"
        assert (Path(user_home) / "license.dat").read_text() == "licensed"
        return _parse_pitch_license_list(
            " Id  Type     Seats  Hardware id  User\n"
            " 1   primary  2      abcd1234     rick\n"
        )

    monkeypatch.setattr("hla2010.real_rti.list_pitch_licenses", fake_list_pitch_licenses)
    runtime = discover_pitch_runtime()
    prepared = prepare_pitch_user_home(runtime, user_home=tmp_path / "pitch-user-home-work")

    assert prepared == tmp_path / "pitch-user-home-work"
    assert (prepared / "license.dat").read_text() == "licensed"


def test_prepare_pitch_user_home_tolerates_empty_license_list_and_copies_bundled_defaults(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    java_bin = home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin"
    java_bin.mkdir(parents=True)
    (java_bin / "java").write_text("")
    lib = home / "lib"
    lib.mkdir()
    (lib / "prtifull.jar").write_text("")

    bundled_user_home = home / "user.home" / "prti1516e"
    bundled_user_home.mkdir(parents=True)
    (bundled_user_home / "FedProServer.properties").write_text("server-address = all\n")

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setattr("hla2010.real_rti.list_pitch_licenses", lambda *_args, **_kwargs: ())

    runtime = discover_pitch_runtime()
    prepared = prepare_pitch_user_home(runtime, user_home=tmp_path / "pitch-user-home-work")

    assert prepared == tmp_path / "pitch-user-home-work"
    assert (prepared / "prti1516e" / "FedProServer.properties").read_text() == "server-address = all\n"


def test_prepare_pitch_user_home_preserves_existing_runtime_state(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    java_bin = home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin"
    java_bin.mkdir(parents=True)
    (java_bin / "java").write_text("")
    lib = home / "lib"
    lib.mkdir()
    (lib / "prtifull.jar").write_text("")

    bundled_user_home = home / "user.home" / "prti1516e"
    bundled_user_home.mkdir(parents=True)
    (bundled_user_home / "prti_common.settings").write_text("accepted = false\n")

    working_user_home = tmp_path / "pitch-user-home-work" / "prti1516e"
    working_user_home.mkdir(parents=True)
    (working_user_home / "prti_common.settings").write_text("accepted = true\n")

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setattr("hla2010.real_rti.list_pitch_licenses", lambda *_args, **_kwargs: ())

    runtime = discover_pitch_runtime()
    prepared = prepare_pitch_user_home(runtime, user_home=tmp_path / "pitch-user-home-work")

    assert prepared == tmp_path / "pitch-user-home-work"
    assert (prepared / "prti1516e" / "prti_common.settings").read_text() == "accepted = true\n"
    assert (prepared / ".hla2010_pitch_user_home_seeded").exists()


def test_prepare_pitch_user_home_sets_pitch_free_eula_accepted_when_missing(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    java_bin = home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin"
    java_bin.mkdir(parents=True)
    (java_bin / "java").write_text("")
    lib = home / "lib"
    lib.mkdir()
    (lib / "prtifull.jar").write_text("")

    bundled_user_home = home / "user.home" / "prti1516e"
    bundled_user_home.mkdir(parents=True)
    (bundled_user_home / "prti_common.settings").write_text("# Settings that apply to all pRTI applications\n")

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setattr("hla2010.real_rti.list_pitch_licenses", lambda *_args, **_kwargs: ())

    runtime = discover_pitch_runtime()
    prepared = prepare_pitch_user_home(runtime, user_home=tmp_path / "pitch-user-home-work")

    assert prepared == tmp_path / "pitch-user-home-work"
    assert (prepared / "prti1516e" / "prti_common.settings").read_text().endswith("accepted = true\n")


def test_prepare_pitch_user_home_disables_crc_webview_passphrase(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    java_bin = home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin"
    java_bin.mkdir(parents=True)
    (java_bin / "java").write_text("")
    lib = home / "lib"
    lib.mkdir()
    (lib / "prtifull.jar").write_text("")

    bundled_user_home = home / "user.home" / "prti1516e"
    bundled_user_home.mkdir(parents=True)
    (bundled_user_home / "prti1516eCRC.settings").write_text(
        "CRC.requireWebViewPassPhrase=true\nCRC.webViewPassPhrase=secret\n",
    )

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setattr("hla2010.real_rti.list_pitch_licenses", lambda *_args, **_kwargs: ())

    runtime = discover_pitch_runtime()
    prepared = prepare_pitch_user_home(runtime, user_home=tmp_path / "pitch-user-home-work")

    assert prepared == tmp_path / "pitch-user-home-work"
    assert (prepared / "prti1516e" / "prti1516eCRC.settings").read_text() == (
        "CRC.requireWebViewPassPhrase=false\nCRC.webViewPassPhrase=\n"
    )


def test_prepare_pitch_user_home_normalizes_docker_crc_and_lrc_networking(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    java_bin = home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin"
    java_bin.mkdir(parents=True)
    (java_bin / "java").write_text("")
    lib = home / "lib"
    lib.mkdir()
    (lib / "prtifull.jar").write_text("")

    bundled_user_home = home / "user.home" / "prti1516e"
    bundled_user_home.mkdir(parents=True)
    (bundled_user_home / "prti1516eCRC.settings").write_text(
        "CRC.skipConnectivityCheck=false\nCRC.requireWebViewPassPhrase=true\nCRC.webViewPassPhrase=secret\n",
    )
    (bundled_user_home / "prti1516eLRC.settings").write_text(
        "LRC.TCP.advertise.mode=IP\n"
        "LRC.TCP.advertise.address=\n"
        "LRC.TCP.port-range.start=6000\n"
        "LRC.TCP.port-range.end=6999\n"
        "LRC.skipConnectivityCheck=false\n",
    )

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setenv("HLA2010_PITCH_LRC_ADVERTISE_ADDRESS", "host.docker.internal")
    monkeypatch.setattr("hla2010.real_rti.list_pitch_licenses", lambda *_args, **_kwargs: ())

    runtime = discover_pitch_runtime()
    prepared = prepare_pitch_user_home(runtime, user_home=tmp_path / "pitch-user-home-work", crc_mode="docker")

    crc_settings = (prepared / "prti1516e" / "prti1516eCRC.settings").read_text()
    assert "CRC.skipConnectivityCheck=true\n" in crc_settings
    assert "CRC.requireWebViewPassPhrase=false\n" in crc_settings
    assert "CRC.webViewPassPhrase=\n" in crc_settings

    lrc_settings = (prepared / "prti1516e" / "prti1516eLRC.settings").read_text()
    assert "LRC.TCP.advertise.mode=User\n" in lrc_settings
    assert "LRC.TCP.advertise.address=host.docker.internal\n" in lrc_settings
    assert "LRC.TCP.port-range.start=6010\n" in lrc_settings
    assert "LRC.TCP.port-range.end=6099\n" in lrc_settings
    assert "LRC.UDP.port-range.start=5010\n" in lrc_settings
    assert "LRC.UDP.port-range.end=5099\n" in lrc_settings
    assert "LRC.skipConnectivityCheck=true\n" in lrc_settings
