from __future__ import annotations

import shutil
import struct
import subprocess
from pathlib import Path
from typing import Any

import pytest
from hla.bridges.java.common.java_binding_profile import load_python_java_binding_profile
from hla.bridges.java.common.java_logical_time import (
    JavaLogicalTimeAdapter,
    wrap_java_logical_time_factory,
)

JAVA_SOURCE = """
package testlogicaltime;

public final class QuirkLogicalTimeFactory {
    public String getName() {
        return "Quirk128Time";
    }

    public QuirkLogicalTime decodeTime(byte[] buffer, int offset) {
        return new QuirkLogicalTime(readLong(buffer, offset));
    }

    public QuirkLogicalInterval decodeInterval(byte[] buffer, int offset) {
        return new QuirkLogicalInterval(readLong(buffer, offset));
    }

    public QuirkLogicalTime makeInitial() {
        return new QuirkLogicalTime(0L);
    }

    public QuirkLogicalTime makeFinal() {
        return new QuirkLogicalTime(Long.MAX_VALUE);
    }

    public QuirkLogicalInterval makeZero() {
        return new QuirkLogicalInterval(0L);
    }

    public QuirkLogicalInterval makeEpsilon() {
        return new QuirkLogicalInterval(1L);
    }

    public QuirkLogicalTime makeTime(long value) {
        return new QuirkLogicalTime(value);
    }

    public QuirkLogicalInterval makeInterval(long value) {
        return new QuirkLogicalInterval(value);
    }

    private static long readLong(byte[] buffer, int offset) {
        long value = 0L;
        for (int idx = 0; idx < 8; idx++) {
            value = (value << 8) | (buffer[offset + idx] & 0xffL);
        }
        return value;
    }
}

final class QuirkLogicalTime implements Comparable<QuirkLogicalTime> {
    private final long value;

    QuirkLogicalTime(long value) {
        this.value = value;
    }

    public int encodedLength() {
        return 8;
    }

    public void encode(byte[] buffer, int offset) {
        writeLong(value, buffer, offset);
    }

    public boolean isInitial() {
        return value == 0L;
    }

    public boolean isFinal() {
        return value == Long.MAX_VALUE;
    }

    public QuirkLogicalTime add(QuirkLogicalInterval interval) {
        return new QuirkLogicalTime(value + interval.getValue());
    }

    public QuirkLogicalTime subtract(QuirkLogicalInterval interval) {
        return new QuirkLogicalTime(value - interval.getValue());
    }

    public QuirkLogicalInterval distance(QuirkLogicalTime other) {
        return new QuirkLogicalInterval(value - other.value);
    }

    public long getValue() {
        return value;
    }

    @Override
    public int compareTo(QuirkLogicalTime other) {
        return Long.compare(value, other.value);
    }

    @Override
    public String toString() {
        return "QuirkLogicalTime(" + value + ")";
    }

    static void writeLong(long value, byte[] buffer, int offset) {
        for (int idx = 7; idx >= 0; idx--) {
            buffer[offset + idx] = (byte)(value & 0xffL);
            value >>= 8;
        }
    }
}

final class QuirkLogicalInterval implements Comparable<QuirkLogicalInterval> {
    private final long value;

    QuirkLogicalInterval(long value) {
        this.value = value;
    }

    public int encodedLength() {
        return 8;
    }

    public void encode(byte[] buffer, int offset) {
        QuirkLogicalTime.writeLong(value, buffer, offset);
    }

    public boolean isZero() {
        return value == 0L;
    }

    public boolean isEpsilon() {
        return value == 1L;
    }

    public QuirkLogicalInterval add(QuirkLogicalInterval addend) {
        return new QuirkLogicalInterval(value + addend.value);
    }

    public QuirkLogicalInterval subtract(QuirkLogicalInterval subtrahend) {
        return new QuirkLogicalInterval(value - subtrahend.value);
    }

    public long getValue() {
        return value;
    }

    @Override
    public int compareTo(QuirkLogicalInterval other) {
        return Long.compare(value, other.value);
    }

    @Override
    public String toString() {
        return "QuirkLogicalInterval(" + value + ")";
    }
}
"""


def _compile_quirk_factory(tmp_path: Path) -> Path:
    javac = shutil.which("javac")
    if javac is None:
        pytest.skip("javac is required for live Java logical-time bridge tests")

    source_dir = tmp_path / "src" / "testlogicaltime"
    classes_dir = tmp_path / "classes"
    source_dir.mkdir(parents=True)
    classes_dir.mkdir()
    source_file = source_dir / "QuirkLogicalTimeFactory.java"
    source_file.write_text(JAVA_SOURCE, encoding="utf-8")

    result = subprocess.run(
        [javac, "-d", str(classes_dir), str(source_file)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if "Unable to locate a Java Runtime" in result.stderr:
            pytest.skip("a working Java runtime is required for live Java logical-time bridge tests")
        pytest.fail(f"javac failed:\n{result.stderr}")
    return classes_dir


def _assert_quirk_factory_bridge(bridge: Any, java_factory: Any) -> None:
    factory = wrap_java_logical_time_factory(bridge, java_factory, load_python_java_binding_profile("2010"))
    value = factory.decodeTime(struct.pack(">q", 42))
    interval = factory.decodeInterval(struct.pack(">q", 3))

    assert factory.getName() == "Quirk128Time"
    assert isinstance(value, JavaLogicalTimeAdapter)
    assert value.factory_name == "Quirk128Time"
    assert bytes(value.encode()) == struct.pack(">q", 42)
    assert bytes(value.add(interval).encode()) == struct.pack(">q", 45)
    assert bytes(value.distance(factory.decodeTime(struct.pack(">q", 40))).encode()) == struct.pack(">q", 2)


def test_live_jpype_custom_logical_time_factory_uses_opaque_wrapper(tmp_path: Path) -> None:
    jpype = pytest.importorskip("jpype")
    runtime = pytest.importorskip("hla.bridges.java.jpype.runtime")
    classes_dir = _compile_quirk_factory(tmp_path)

    if jpype.isJVMStarted():
        jpype.addClassPath(str(classes_dir))
        bridge = runtime.JPypeBridge(runtime.JPypeConfig(start_jvm=False))
    else:
        bridge = runtime.JPypeBridge(runtime.JPypeConfig(classpath=(str(classes_dir),), convert_strings=True))

    java_factory = bridge.JClass("testlogicaltime.QuirkLogicalTimeFactory")()

    _assert_quirk_factory_bridge(bridge, java_factory)


def test_live_py4j_custom_logical_time_factory_uses_opaque_wrapper(tmp_path: Path) -> None:
    py4j_gateway = pytest.importorskip("py4j.java_gateway")
    runtime = pytest.importorskip("hla.bridges.java.py4j.runtime")
    classes_dir = _compile_quirk_factory(tmp_path)

    port = py4j_gateway.launch_gateway(classpath=str(classes_dir), die_on_exit=True)
    gateway = py4j_gateway.JavaGateway(gateway_parameters=py4j_gateway.GatewayParameters(port=port, auto_convert=True))
    bridge = runtime.Py4JBridge(runtime.Py4JConfig(gateway=gateway))
    try:
        java_factory = gateway.jvm.testlogicaltime.QuirkLogicalTimeFactory()
        _assert_quirk_factory_bridge(bridge, java_factory)
    finally:
        gateway.shutdown()
