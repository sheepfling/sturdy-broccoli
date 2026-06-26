from __future__ import annotations

from types import SimpleNamespace

from hla.backends.common import java_invocation_resolver_name
from hla.bridges.java.common.java_binding_profile import load_python_java_binding_profile


class _FakeJavaFactory:
    def __init__(self, name: str) -> None:
        self._name = name

    def getRtiAmbassador(self):
        return object()

    def rtiName(self):  # noqa: N802
        return self._name

    def rtiVersion(self):  # noqa: N802
        return "1.0"

    def getEncoderFactory(self):  # noqa: N802
        return object()


class _FakeJPypeFactoryFactory:
    def getRtiFactory(self, _name=None):  # noqa: N802
        return _FakeJavaFactory("fake-jpype")


class _FakeJPypeBridge:
    def __init__(self, config) -> None:
        self.config = config
        self.python_binding = load_python_java_binding_profile("2010")
        self.api_profile = SimpleNamespace(factory_factory_class="vendor.rti.FactoryFactory")

    def JClass(self, class_name: str):
        if class_name == self.api_profile.factory_factory_class:
            return _FakeJPypeFactoryFactory()
        raise AssertionError(class_name)

    def encoder_factory(self, java_factory):
        return java_factory.getEncoderFactory()

    def close(self) -> None:
        return None


class _FakeGatewayFactoryFactory:
    def getRtiFactory(self, _name=None):  # noqa: N802
        return _FakeJavaFactory("fake-py4j")


class _FakePy4JBridge:
    def __init__(self, config) -> None:
        self.config = config
        self.python_binding = load_python_java_binding_profile("2010")
        self.api_profile = SimpleNamespace(factory_factory_class="vendor.rti.FactoryFactory")
        self.gateway = SimpleNamespace(
            jvm=SimpleNamespace(
                vendor=SimpleNamespace(
                    rti=SimpleNamespace(
                        FactoryFactory=_FakeGatewayFactoryFactory(),
                    )
                )
            )
        )

    def encoder_factory(self, java_factory):
        return java_factory.getEncoderFactory()

    def close(self) -> None:
        return None


def test_jpype_backend_factory_keeps_router_selection_per_backend(monkeypatch) -> None:
    import hla.bridges.java.jpype.factory as factory_module
    from hla.bridges.java.jpype import JPypeConfig

    monkeypatch.setattr(factory_module, "JPypeBridge", _FakeJPypeBridge)

    weighted = factory_module.create_jpype_backend(JPypeConfig(invocation_router="weighted"))
    deterministic = factory_module.create_jpype_backend(JPypeConfig(invocation_router="deterministic"))

    assert java_invocation_resolver_name(weighted.invocation_resolver) == "weighted"
    assert java_invocation_resolver_name(deterministic.invocation_resolver) == "deterministic"
    assert weighted.invocation_resolver is not deterministic.invocation_resolver


def test_py4j_backend_factory_keeps_router_selection_per_backend(monkeypatch) -> None:
    import hla.bridges.java.py4j.factory as factory_module
    from hla.bridges.java.py4j import Py4JConfig

    monkeypatch.setattr(factory_module, "Py4JBridge", _FakePy4JBridge)

    weighted = factory_module.create_py4j_backend(Py4JConfig(invocation_router="weighted"))
    deterministic = factory_module.create_py4j_backend(Py4JConfig(invocation_router="deterministic"))

    assert java_invocation_resolver_name(weighted.invocation_resolver) == "weighted"
    assert java_invocation_resolver_name(deterministic.invocation_resolver) == "deterministic"
    assert weighted.invocation_resolver is not deterministic.invocation_resolver
