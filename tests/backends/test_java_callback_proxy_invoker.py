from __future__ import annotations

from hla2010_rti_java_common.java_common import invoke_java_federate_proxy_callback


class _RecordingJavaProxy:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    def _record(self, name: str, *args: object) -> None:
        self.calls.append((name, args))

    def discoverObjectInstance(self, *args: object) -> None:  # noqa: N802
        self._record("discoverObjectInstance", *args)

    def timeAdvanceGrant(self, *args: object) -> None:  # noqa: N802
        self._record("timeAdvanceGrant", *args)


def test_invoke_java_federate_proxy_callback_routes_to_explicit_method() -> None:
    proxy = _RecordingJavaProxy()

    invoke_java_federate_proxy_callback(proxy, "discoverObjectInstance", 7, 3, "DemoObject")
    invoke_java_federate_proxy_callback(proxy, "timeAdvanceGrant", 9)

    assert proxy.calls == [
        ("discoverObjectInstance", (7, 3, "DemoObject")),
        ("timeAdvanceGrant", (9,)),
    ]
