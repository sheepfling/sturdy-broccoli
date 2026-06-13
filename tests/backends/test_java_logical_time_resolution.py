from __future__ import annotations

import math
import pytest

from hla2010.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time
from hla2010_rti_java_common.java_common import (
    convert_python_logical_time_with_factory,
    invoke_java_time_factory,
    python_logical_time_shim_spec,
)


class _FakeTimeFactory:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object | None]] = []

    def makeTime(self, value: object) -> tuple[str, object]:  # noqa: N802
        self.calls.append(("makeTime", value))
        return ("makeTime", value)

    def makeInterval(self, value: object) -> tuple[str, object]:  # noqa: N802
        self.calls.append(("makeInterval", value))
        return ("makeInterval", value)

    def makeZero(self) -> tuple[str, None]:  # noqa: N802
        self.calls.append(("makeZero", None))
        return ("makeZero", None)

    def makeEpsilon(self) -> tuple[str, None]:  # noqa: N802
        self.calls.append(("makeEpsilon", None))
        return ("makeEpsilon", None)


class _FakeAmbassador:
    def __init__(self) -> None:
        self.time_factory = _FakeTimeFactory()

    def getTimeFactory(self) -> _FakeTimeFactory:  # noqa: N802
        return self.time_factory


def test_invoke_java_time_factory_uses_explicit_factory_lookup() -> None:
    ambassador = _FakeAmbassador()
    assert invoke_java_time_factory(ambassador) is ambassador.time_factory


def test_convert_python_logical_time_with_factory_handles_times_and_intervals() -> None:
    factory = _FakeTimeFactory()

    assert convert_python_logical_time_with_factory(factory, HLAinteger64Time(7)) == ("makeTime", 7)
    assert convert_python_logical_time_with_factory(factory, HLAfloat64Time(1.5)) == ("makeTime", 1.5)
    assert convert_python_logical_time_with_factory(factory, HLAinteger64Interval(3)) == ("makeInterval", 3)
    assert convert_python_logical_time_with_factory(factory, HLAfloat64Interval(2.5)) == ("makeInterval", 2.5)


def test_convert_python_logical_time_with_factory_uses_zero_and_epsilon_interval_paths() -> None:
    factory = _FakeTimeFactory()

    assert convert_python_logical_time_with_factory(factory, HLAinteger64Interval(0)) == ("makeZero", None)
    assert convert_python_logical_time_with_factory(factory, HLAinteger64Interval(1)) == ("makeEpsilon", None)
    assert convert_python_logical_time_with_factory(factory, HLAfloat64Interval(0.0)) == ("makeZero", None)
    assert convert_python_logical_time_with_factory(factory, HLAfloat64Interval(math.ulp(1.0))) == ("makeEpsilon", None)


def test_python_logical_time_shim_spec_maps_supported_types() -> None:
    assert python_logical_time_shim_spec(HLAinteger64Time(4)) == ("HLAinteger64Time", 4)
    assert python_logical_time_shim_spec(HLAinteger64Interval(2)) == ("HLAinteger64Interval", 2)
    assert python_logical_time_shim_spec(HLAfloat64Time(1.25)) == ("HLAfloat64Time", 1.25)
    assert python_logical_time_shim_spec(HLAfloat64Interval(0.5)) == ("HLAfloat64Interval", 0.5)


def test_python_logical_time_shim_spec_rejects_unknown_values() -> None:
    with pytest.raises(TypeError, match="str"):
        python_logical_time_shim_spec("not-a-logical-time")
