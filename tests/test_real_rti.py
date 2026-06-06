from pathlib import Path

from hla2010.real_rti import discover_certi_runtime, discover_pitch_runtime


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


def test_discover_certi_runtime_from_env(tmp_path, monkeypatch):
    prefix = tmp_path / "certi-install"
    (prefix / "bin").mkdir(parents=True)
    (prefix / "lib").mkdir()
    (prefix / "bin" / "rtig").write_text("")
    monkeypatch.setenv("HLA2010_CERTI_PREFIX", str(prefix))
    runtime = discover_certi_runtime()
    assert runtime.prefix == prefix
    assert runtime.executable("rtig") == prefix / "bin" / "rtig"
