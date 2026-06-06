from pathlib import Path

from hla2010.java_runtime import discover_java_home, discover_java_tool, ensure_java_home


def test_java_home_can_be_discovered():
    home = discover_java_home()
    assert home is not None
    assert (home / "bin" / "java").exists()


def test_java_tools_can_be_discovered():
    assert discover_java_tool("java") is not None
    assert discover_java_tool("javac") is not None
    assert discover_java_tool("jar") is not None


def test_ensure_java_home_sets_environment(monkeypatch):
    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.delenv("JDK_HOME", raising=False)
    home = ensure_java_home()
    assert home is not None
    assert Path(home) == Path(home)
