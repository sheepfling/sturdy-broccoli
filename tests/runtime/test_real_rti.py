import os
import subprocess
from pathlib import Path

import hla2010_rti_pitch_common.real_rti_pitch as pitch_runtime_module
import pytest
from hla2010_rti_backend_common import BackendUnavailableError
from hla2010_rti_certi.real_rti_certi import (
    discover_certi_runtime,
    discover_certi_runtime_profile,
)
from hla2010_rti_pitch_common.real_rti_pitch import (
    _parse_pitch_license_list,
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

    monkeypatch.setattr(pitch_runtime_module.subprocess, "Popen", fake_popen)

    runtime = launch_pitch_runtime(
        ui_automation=True,
        _wait_for_process_boot=lambda *args, **kwargs: None,
        _wait_for_tcp_listener=lambda *args, **kwargs: None,
    )
    runtime.terminate()

    assert any(env.get("HLA2010_PITCH_UI_AUTOMATION") == "1" for env in captured["envs"])


def test_launch_pitch_runtime_can_use_docker_crc_mode(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin").mkdir(parents=True)
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin" / "java").write_text("")
    (home / "lib").mkdir()
    (home / "lib" / "prtifull.jar").write_text("")

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
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

    monkeypatch.setattr(pitch_runtime_module.subprocess, "Popen", fake_popen)

    runtime = launch_pitch_runtime(
        crc_mode="docker",
        _wait_for_process_boot=lambda *args, **kwargs: None,
        _wait_for_tcp_listener=lambda *args, **kwargs: None,
    )
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

    monkeypatch.setattr(pitch_runtime_module.subprocess, "Popen", fake_popen)

    runtime = launch_pitch_runtime(
        _wait_for_process_boot=lambda *args, **kwargs: None,
        _wait_for_tcp_listener=lambda *args, **kwargs: None,
    )
    runtime.terminate()

    commands = captured["commands"]
    assert any(command[0].endswith("scripts/run_pitch_docker_crc.sh") for command in commands)
    assert any(env.get("HLA2010_PITCH_CRC_MODE") == "docker" for env in captured["envs"])
    assert runtime.name == "pitch-docker"


def test_launch_pitch_runtime_honors_listener_and_boot_timeout_env(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin").mkdir(parents=True)
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin" / "java").write_text("")
    (home / "lib").mkdir()
    (home / "lib" / "prtifull.jar").write_text("")

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setenv("HLA2010_PITCH_FEDPRO_LISTENER_TIMEOUT_SECONDS", "21.5")
    monkeypatch.setenv("HLA2010_PITCH_CRC_LISTENER_TIMEOUT_SECONDS", "46.5")
    monkeypatch.setenv("HLA2010_PITCH_PROCESS_BOOT_TIMEOUT_SECONDS", "11.5")

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

    boot_calls: list[tuple[object, float]] = []
    listener_calls: list[tuple[str, int, float]] = []

    def fake_popen(command, **kwargs):
        return FakeProcess()

    def fake_wait_for_process_boot(process, *, timeout):
        boot_calls.append((process, timeout))

    def fake_wait_for_tcp_listener(host, port, *, timeout):
        listener_calls.append((host, port, timeout))

    monkeypatch.setattr(pitch_runtime_module.subprocess, "Popen", fake_popen)

    runtime = launch_pitch_runtime(
        _wait_for_process_boot=fake_wait_for_process_boot,
        _wait_for_tcp_listener=fake_wait_for_tcp_listener,
    )
    runtime.terminate()

    assert boot_calls
    assert all(timeout == 11.5 for _, timeout in boot_calls)
    assert len(listener_calls) == 2
    assert listener_calls[0][0] == "127.0.0.1"
    assert listener_calls[1][0] == "127.0.0.1"
    assert listener_calls[0][2] == 21.5
    assert listener_calls[1][2] == 46.5
    assert listener_calls[0][1] != listener_calls[1][1]


def test_launch_pitch_runtime_honors_explicit_custom_ports(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin").mkdir(parents=True)
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin" / "java").write_text("")
    (home / "lib").mkdir()
    (home / "lib" / "prtifull.jar").write_text("")

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setenv("HLA2010_PITCH_CRC_PORT", "18989")
    monkeypatch.setenv("HLA2010_PITCH_FEDPRO_PORT", "25164")

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

    listener_calls: list[tuple[str, int, float]] = []

    def fake_popen(command, **kwargs):
        return FakeProcess()

    def fake_wait_for_process_boot(process, *, timeout):
        return None

    def fake_wait_for_tcp_listener(host, port, *, timeout):
        listener_calls.append((host, port, timeout))

    monkeypatch.setattr(pitch_runtime_module.subprocess, "Popen", fake_popen)

    runtime = launch_pitch_runtime(
        _wait_for_process_boot=fake_wait_for_process_boot,
        _wait_for_tcp_listener=fake_wait_for_tcp_listener,
    )
    runtime.terminate()

    assert ("127.0.0.1", 25164, 20.0) in listener_calls
    assert ("127.0.0.1", 18989, 45.0) in listener_calls
    assert runtime.tcp_port == 25164


def test_launch_pitch_runtime_chooses_fallback_ports_when_defaults_are_busy(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin").mkdir(parents=True)
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin" / "java").write_text("")
    (home / "lib").mkdir()
    (home / "lib" / "prtifull.jar").write_text("")

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.delenv("HLA2010_PITCH_CRC_PORT", raising=False)
    monkeypatch.delenv("HLA2010_PITCH_FEDPRO_PORT", raising=False)

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

    listener_calls: list[tuple[str, int, float]] = []
    fallback_values = iter((28001, 28002))

    def fake_popen(command, **kwargs):
        return FakeProcess()

    def fake_wait_for_process_boot(process, *, timeout):
        return None

    def fake_wait_for_tcp_listener(host, port, *, timeout):
        listener_calls.append((host, port, timeout))

    def fake_port_is_available(host, port):
        return False if port in {8989, 15164} else True

    def fake_reserve_tcp_port(host):
        return next(fallback_values)

    monkeypatch.setattr(pitch_runtime_module.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(pitch_runtime_module, "_port_is_available", fake_port_is_available)
    monkeypatch.setattr(pitch_runtime_module, "reserve_tcp_port", fake_reserve_tcp_port)

    runtime = launch_pitch_runtime(
        _wait_for_process_boot=fake_wait_for_process_boot,
        _wait_for_tcp_listener=fake_wait_for_tcp_listener,
    )
    runtime.terminate()

    assert ("127.0.0.1", 28002, 20.0) in listener_calls
    assert ("127.0.0.1", 28001, 45.0) in listener_calls
    assert runtime.tcp_port == 28002
    assert os.environ["HLA2010_PITCH_CRC_PORT"] == "28001"
    assert os.environ["HLA2010_PITCH_FEDPRO_PORT"] == "28002"


def test_launch_pitch_runtime_retries_with_isolated_user_home_and_cleans_it_up(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    local_state = tmp_path / "local-state"
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin").mkdir(parents=True)
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin" / "java").write_text("")
    (home / "lib").mkdir()
    (home / "lib" / "prtifull.jar").write_text("")
    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setenv("HLA2010_LOCAL_STATE_ROOT", str(local_state))
    monkeypatch.setenv("HLA2010_PITCH_STARTUP_RETRIES", "1")
    monkeypatch.setenv("HLA2010_PITCH_LAUNCHER_FALLBACKS", "raw,install4j")
    launcher = home / "bin" / "pRTI cmdline"
    launcher.parent.mkdir(parents=True, exist_ok=True)
    launcher.write_text("", encoding="utf-8")
    launcher.chmod(0o755)

    popen_calls: list[tuple[list[str], dict[str, str]]] = []

    class FakeProcess:
        def __init__(self, label: str):
            self.label = label
            self.returncode = None

        def poll(self):
            return self.returncode

        def terminate(self):
            self.returncode = 0

        def wait(self, timeout=None):
            self.returncode = 0

        def kill(self):
            self.returncode = -9

        def communicate(self, timeout=None):
            self.returncode = 0
            return (f"{self.label}-stdout\n", f"{self.label}-stderr\n")

    def fake_popen(command, **kwargs):
        popen_calls.append((list(command), dict(kwargs["env"])))
        return FakeProcess(Path(command[0]).name if command else "process")

    listener_attempt = {"count": 0}

    def fake_wait_for_process_boot(process, *, timeout):
        return None

    def fake_wait_for_tcp_listener(host, port, *, timeout):
        if port == 8989:
            listener_attempt["count"] += 1
            if listener_attempt["count"] == 1:
                raise BackendUnavailableError("Timed out waiting for listener on 127.0.0.1:8989")
        return None

    monkeypatch.setattr(pitch_runtime_module.subprocess, "Popen", fake_popen)

    runtime = launch_pitch_runtime(
        _wait_for_process_boot=fake_wait_for_process_boot,
        _wait_for_tcp_listener=fake_wait_for_tcp_listener,
    )

    assert listener_attempt["count"] == 2
    launch_envs = [
        env
        for command, env in popen_calls
        if command
        and (
            command[0].endswith("run_pitch_local.sh")
            or command[-1] == "se.pitch.fedpro.server.hla.FedProServerApp"
        )
    ]
    assert len(launch_envs) == 4
    first_user_home = launch_envs[0]["HLA2010_PITCH_USER_HOME"]
    second_user_home = launch_envs[2]["HLA2010_PITCH_USER_HOME"]
    assert first_user_home != second_user_home
    assert "runtime-homes" in second_user_home
    assert launch_envs[0]["HLA2010_PITCH_LAUNCHER_MODE"] == "raw"
    assert launch_envs[2]["HLA2010_PITCH_LAUNCHER_MODE"] == "install4j"
    cleanup_path = Path(second_user_home)
    assert cleanup_path.exists()
    assert runtime.cleanup_paths == (cleanup_path,)

    runtime.terminate()
    assert not cleanup_path.exists()


def test_launch_pitch_runtime_reports_attempt_diagnostics_on_exhausted_retries(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin").mkdir(parents=True)
    (home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin" / "java").write_text("")
    (home / "lib").mkdir()
    (home / "lib" / "prtifull.jar").write_text("")
    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setenv("HLA2010_PITCH_STARTUP_RETRIES", "0")

    class FakeProcess:
        returncode = None

        def poll(self):
            return self.returncode

        def terminate(self):
            self.returncode = 0

        def wait(self, timeout=None):
            self.returncode = 0

        def kill(self):
            self.returncode = -9

        def communicate(self, timeout=None):
            self.returncode = 0
            return ("crc-stdout\n", "crc-stderr\n")

    def fake_popen(command, **kwargs):
        return FakeProcess()

    def fake_wait_for_process_boot(process, *, timeout):
        return None

    def fake_wait_for_tcp_listener(host, port, *, timeout):
        raise BackendUnavailableError("Timed out waiting for listener on 127.0.0.1:8989")

    monkeypatch.setattr(pitch_runtime_module.subprocess, "Popen", fake_popen)

    with pytest.raises(BackendUnavailableError) as excinfo:
        launch_pitch_runtime(
            _wait_for_process_boot=fake_wait_for_process_boot,
            _wait_for_tcp_listener=fake_wait_for_tcp_listener,
        )

    text = str(excinfo.value)
    assert "Timed out waiting for listener on 127.0.0.1:8989" in text
    assert "pitch crc attempt 1 (raw) diagnostics:" in text
    assert "stdout tail:" in text
    assert "stderr tail:" in text


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

    monkeypatch.setattr(pitch_runtime_module, "list_pitch_licenses", fake_list_pitch_licenses)
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
    monkeypatch.setattr(pitch_runtime_module, "list_pitch_licenses", lambda *_args, **_kwargs: ())

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
    monkeypatch.setattr(pitch_runtime_module, "list_pitch_licenses", lambda *_args, **_kwargs: ())

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
    monkeypatch.setattr(pitch_runtime_module, "list_pitch_licenses", lambda *_args, **_kwargs: ())

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
    monkeypatch.setattr(pitch_runtime_module, "list_pitch_licenses", lambda *_args, **_kwargs: ())

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
    monkeypatch.setattr(pitch_runtime_module, "list_pitch_licenses", lambda *_args, **_kwargs: ())

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


def test_prepare_pitch_user_home_applies_loss_detection_overrides(tmp_path, monkeypatch):
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
        "CRC.heartbeat.enable=false\nCRC.heartbeat.interval=15\nCRC.heartbeat.action=ignore\n",
    )
    (bundled_user_home / "FedProServer.properties").write_text(
        "timeout-heart-seconds = 180\ntimeout-purge-seconds = 600\n",
    )

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setenv("HLA2010_PITCH_CRC_HEARTBEAT_ENABLE", "true")
    monkeypatch.setenv("HLA2010_PITCH_CRC_HEARTBEAT_INTERVAL", "1")
    monkeypatch.setenv("HLA2010_PITCH_CRC_HEARTBEAT_ACTION", "drop")
    monkeypatch.setenv("HLA2010_PITCH_LRC_PEER_HEARTBEAT_INTERVAL_MILLIS", "1000")
    monkeypatch.setenv("HLA2010_PITCH_FEDPRO_TIMEOUT_HEART_SECONDS", "5")
    monkeypatch.setenv("HLA2010_PITCH_FEDPRO_TIMEOUT_PURGE_SECONDS", "15")
    monkeypatch.setattr(pitch_runtime_module, "list_pitch_licenses", lambda *_args, **_kwargs: ())

    runtime = discover_pitch_runtime()
    prepared = prepare_pitch_user_home(runtime, user_home=tmp_path / "pitch-user-home-work")

    crc_settings = (prepared / "prti1516e" / "prti1516eCRC.settings").read_text()
    lrc_settings = (prepared / "prti1516e" / "prti1516eLRC.settings").read_text()
    fedpro_settings = (prepared / "prti1516e" / "FedProServer.properties").read_text()

    assert "CRC.heartbeat.enable=true\n" in crc_settings
    assert "CRC.heartbeat.interval=1\n" in crc_settings
    assert "CRC.heartbeat.action=drop\n" in crc_settings
    assert "se.pitch.prti1516e.peerHeartbeatIntervalMillis=1000\n" in lrc_settings
    assert "timeout-heart-seconds=5\n" in fedpro_settings
    assert "timeout-purge-seconds=15\n" in fedpro_settings


def test_prepare_pitch_user_home_applies_extra_lrc_and_fedpro_settings(tmp_path, monkeypatch):
    home = tmp_path / "pitch-install"
    java_bin = home / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin"
    java_bin.mkdir(parents=True)
    (java_bin / "java").write_text("")
    lib = home / "lib"
    lib.mkdir()
    (lib / "prtifull.jar").write_text("")

    bundled_user_home = home / "user.home" / "prti1516e"
    bundled_user_home.mkdir(parents=True)
    (bundled_user_home / "prti1516eLRC.settings").write_text(
        "existing=value\nse.pitch.prti1516e.peerHeartbeatIntervalMillis=5000\n",
    )
    (bundled_user_home / "FedProServer.properties").write_text(
        "timeout-heart-seconds = 180\nrecover-session=true\n",
    )

    monkeypatch.setenv("HLA2010_PITCH_HOME", str(home))
    monkeypatch.setenv(
        "HLA2010_PITCH_LRC_EXTRA_SETTINGS",
        "se.pitch.prti1516e.peerHeartbeatIntervalMillis=750\nse.pitch.prti1516e.sessionResume=false",
    )
    monkeypatch.setenv(
        "HLA2010_PITCH_FEDPRO_EXTRA_SETTINGS",
        "recover-session=false;peer-drop-policy=abort",
    )
    monkeypatch.setattr(pitch_runtime_module, "list_pitch_licenses", lambda *_args, **_kwargs: ())

    runtime = discover_pitch_runtime()
    prepared = prepare_pitch_user_home(runtime, user_home=tmp_path / "pitch-user-home-work")

    lrc_settings = (prepared / "prti1516e" / "prti1516eLRC.settings").read_text()
    fedpro_settings = (prepared / "prti1516e" / "FedProServer.properties").read_text()

    assert "existing=value\n" in lrc_settings
    assert "se.pitch.prti1516e.peerHeartbeatIntervalMillis=750\n" in lrc_settings
    assert "se.pitch.prti1516e.sessionResume=false\n" in lrc_settings
    assert "timeout-heart-seconds = 180\n" in fedpro_settings
    assert "recover-session=false\n" in fedpro_settings
    assert "peer-drop-policy=abort\n" in fedpro_settings
