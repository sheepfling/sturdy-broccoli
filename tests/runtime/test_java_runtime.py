from pathlib import Path

import pytest

from hla2010_rti_java_common.java_runtime import (
    discover_java_home as package_discover_java_home,
    discover_java_tool as package_discover_java_tool,
    ensure_java_home as package_ensure_java_home,
)
from hla2010_rti_java_common import discover_java_home, discover_java_tool, ensure_java_home


def test_java_home_can_be_discovered():
    home = discover_java_home()
    if home is None:
        pytest.skip("JAVA_HOME is not configured in this environment")
    assert home is not None
    assert (home / "bin" / "java").exists()


def test_java_tools_can_be_discovered():
    if discover_java_home() is None:
        pytest.skip("JAVA_HOME is not configured in this environment")
    assert discover_java_tool("java") is not None
    assert discover_java_tool("javac") is not None
    assert discover_java_tool("jar") is not None


def test_ensure_java_home_sets_environment(monkeypatch):
    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.delenv("JDK_HOME", raising=False)
    home = ensure_java_home()
    if home is None:
        pytest.skip("JAVA_HOME is not configured in this environment")
    assert home is not None
    assert Path(home) == Path(home)


def test_java_common_package_root_re_exports_runtime_helpers():
    assert discover_java_home is package_discover_java_home
    assert discover_java_tool is package_discover_java_tool
    assert ensure_java_home is package_ensure_java_home
