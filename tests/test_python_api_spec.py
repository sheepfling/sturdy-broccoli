from __future__ import annotations

import inspect

import pytest

import hla.rti1516e
import hla.rti1516e.rti as rti_module
from hla.backends.common import RecordingBackend, make_rti_ambassador
import hla.rti.factory as runtime_factory
from hla.rti1516e.rti import available_backend_plugins, create_rti_ambassador, discover_rti_backends, iter_rti_backend_plugins
from hla.rti1516e import FederateAmbassador, NullFederateAmbassador, RTIambassador, lower_camel_to_snake
from hla.rti1516e.federate_ambassador import UnimplementedFederateAmbassador
from hla.rti1516e.rti_ambassador import UnimplementedRTIambassador

_PYTHON2025_PROVIDER_ALIASES = ("python2025", "python-2025", "python-2025-backend")


def _public_callables(cls: type) -> dict[str, object]:
    return {
        name: value
        for name, value in inspect.getmembers(cls, inspect.isfunction)
        if not name.startswith("_")
    }


def _assert_no_generic_signature(cls: type) -> None:
    for method_name, method in _public_callables(cls).items():
        parameters = inspect.signature(method).parameters
        assert "args" not in parameters, f"{cls.__name__}.{method_name} still accepts *args"
        assert "kwargs" not in parameters, f"{cls.__name__}.{method_name} still accepts **kwargs"


def test_spec_rti_is_abstract_and_pythonic():
    assert getattr(RTIambassador, "_is_protocol", False)
    assert not hasattr(RTIambassador, "get_hla_version")
    assert hasattr(RTIambassador, "getHLAversion")
    assert lower_camel_to_snake("getHLAversion") == "get_hla_version"
    assert "Strict overloads live in the .pyi stub" in RTIambassador.__doc__


def test_runtime_rti_signatures_are_not_generic():
    _assert_no_generic_signature(RTIambassador)
    _assert_no_generic_signature(UnimplementedRTIambassador)


def test_runtime_federate_signatures_are_not_generic():
    _assert_no_generic_signature(FederateAmbassador)
    _assert_no_generic_signature(UnimplementedFederateAmbassador)


def test_spec_federate_is_a_noop_prototype():
    fed = NullFederateAmbassador()
    assert fed.announce_synchronization_point("label") is None
    assert fed.announceSynchronizationPoint("label") is None
    assert NullFederateAmbassador.__name__ == "NullFederateAmbassador"


def test_runtime_rti_alias_routes_through_pythonic_method():
    rti = make_rti_ambassador(RecordingBackend(results={"getHLAversion": "HLA 1516.1-2010"}))
    assert rti.get_hla_version() == "HLA 1516.1-2010"


def test_runtime_backends_are_discovered_as_plugins():
    plugins = available_backend_plugins()
    assert plugins["python"].name == "inmemory"
    assert plugins["in-memory"].name == "inmemory"
    assert plugins["pitch-jpype"].family == "pitch/java"
    assert plugins["portico-jpype"].family == "portico/java"
    assert plugins["portico"].name == "portico-jpype"

    rti = create_rti_ambassador("in-memory")
    assert rti.backend_info.name == "python-inmemory-rti"


def test_runtime_backend_listing_is_deduplicated_and_probeable():
    plugins = iter_rti_backend_plugins()
    names = {plugin.name for plugin in plugins}
    assert "inmemory" in names
    assert "certi" in names
    assert "pitch-jpype" in names
    assert "portico-jpype" in names
    assert len(plugins) == len(names)

    registered = {row.name: row for row in discover_rti_backends()}
    assert registered["inmemory"].available is None
    assert registered["inmemory"].family == "inmemory"

    probed = {row.name: row for row in discover_rti_backends(probe=True)}
    assert probed["inmemory"].available is True
    assert probed["inmemory"].info.kind == "python/in-memory"


def test_runtime_backend_listing_exposes_python2025_as_primary_2025_lane() -> None:
    from hla.rti import discover_rti_backends as discover_runtime_backends

    registered = {row.name: row for row in discover_runtime_backends(spec="2025")}
    probed = {row.name: row for row in discover_runtime_backends(spec="2025", probe=True)}

    assert registered["python2025"].family == "inmemory-2025"
    assert registered["python2025"].aliases == _PYTHON2025_PROVIDER_ALIASES[1:]
    assert registered["python2025"].supports == ("rti1516_2025",)
    assert registered["python2025"].description == "Primary Python 2025 RTI implementation package."
    assert registered["python2025"].available is None
    assert registered["python2025"].info is None
    assert probed["python2025"].available is True
    assert probed["python2025"].aliases == _PYTHON2025_PROVIDER_ALIASES[1:]
    assert probed["python2025"].info.kind == "python/2025"
    assert probed["python2025"].info.details["implementation_lane"] == "hla-backend-python2025"
    assert probed["python2025"].info.details["counts_as_python_2025_rti"] is True
    assert "wrapper_only" not in probed["python2025"].info.details


@pytest.mark.parametrize("backend_name", _PYTHON2025_PROVIDER_ALIASES)
def test_generic_runtime_creation_for_2025_accepts_python2025_aliases_and_keeps_primary_identity(
    backend_name: str,
) -> None:
    from hla.rti import create_rti_ambassador as create_runtime_rti_ambassador

    runtime_rti = create_runtime_rti_ambassador(spec="2025", backend=backend_name)

    assert runtime_rti.backend_info.details["provider"] == "python2025"
    assert runtime_rti.backend_info.details["implementation_lane"] == "hla-backend-python2025"
    assert runtime_rti.backend_info.details["counts_as_python_2025_rti"] is True
    assert runtime_rti.backend_info.kind == "python/2025"
    assert "wrapper_only" not in runtime_rti.backend_info.details


def test_generic_runtime_creation_for_2025_rejects_legacy_shim_provider_name() -> None:
    from hla.rti import create_rti_ambassador as create_runtime_rti_ambassador

    with pytest.raises(ValueError, match="Unknown RTI backend 'shim'"):
        create_runtime_rti_ambassador(spec="2025", backend="shim")


@pytest.mark.parametrize("backend_name", _PYTHON2025_PROVIDER_ALIASES)
def test_generic_runtime_creation_for_2025_accepts_hosted_transport_on_python2025_aliases(backend_name: str) -> None:
    from hla.backends.python2025.hosted_fedpro import FedPro2025RTIAmbassador
    from hla.rti import create_rti_ambassador as create_runtime_rti_ambassador

    rti = create_runtime_rti_ambassador(
        spec="2025",
        backend=backend_name,
        transport={"kind": "grpc", "target": "127.0.0.1:15164"},
    )

    assert isinstance(rti, FedPro2025RTIAmbassador)
    assert rti.backend_info.details["provider"] == "python2025"
    assert rti.backend_info.details["implementation_lane"] == "hla-backend-python2025"
    assert rti.backend_info.details["counts_as_python_2025_rti"] is True
    assert rti.backend_info.details["wrapper_only"] is False
    rti.close()


def test_generic_runtime_creation_for_2025_rejects_hosted_transport_on_legacy_shim_provider() -> None:
    from hla.rti import create_rti_ambassador as create_runtime_rti_ambassador

    with pytest.raises(ValueError, match="Unknown RTI backend 'shim'"):
        create_runtime_rti_ambassador(
            spec="2025",
            backend="shim",
            transport={"kind": "grpc", "target": "127.0.0.1:15164"},
        )


def test_root_rti_facade_stays_narrow():
    assert sorted(rti_module.__all__) == [
        "available_backend_plugins",
        "create_backend",
        "create_rti_ambassador",
        "discover_rti_backends",
        "iter_rti_backend_plugins",
        "register_backend_plugin",
    ]
    assert not hasattr(rti_module, "RTIBackendPlugin")
    assert not hasattr(rti_module, "RTIBackendSpec")
    assert not hasattr(rti_module, "RTITransportSpec")
    assert not hasattr(rti_module, "RTIBackendDiscovery")
    assert not hasattr(rti_module, "BACKEND_ENTRY_POINT_GROUP")
    assert not hasattr(rti_module, "register_backend_factory")
    assert not hasattr(rti_module, "register_transport_factory")


def test_backend_entry_point_loader_skips_unimportable_optional_plugins(monkeypatch):
    class _BrokenEntryPoint:
        name = "broken"

        def load(self):
            raise ModuleNotFoundError("missing_optional_backend")

    class _EntryPoints:
        def select(self, *, group):
            assert group == "hla.rti_backends"
            return (_BrokenEntryPoint(),)

    monkeypatch.setattr(runtime_factory.metadata, "entry_points", lambda: _EntryPoints())
    monkeypatch.setattr(runtime_factory, "_SOURCE_CHECKOUT_PLUGIN_MODULES", ())

    assert runtime_factory._iter_entry_point_backend_plugins() == []


def test_runtime_factory_falls_back_to_source_checkout_plugins(monkeypatch):
    class _EntryPoints:
        def select(self, *, group):
            assert group == "hla.rti_backends"
            return ()

    monkeypatch.setattr(runtime_factory.metadata, "entry_points", lambda: _EntryPoints())

    plugins = runtime_factory._iter_source_checkout_backend_plugins()
    names = {plugin.name for plugin in plugins}
    assert "inmemory" in names


def test_top_level_package_defaults_to_the_clean_spec_layer():
    assert hasattr(hla.rti1516e, "RTIambassador")
    assert hasattr(hla.rti1516e, "FederateAmbassador")
    assert hasattr(hla.rti1516e, "NullFederateAmbassador")


def test_standalone_spec_package_is_removed():
    assert hla.rti1516e.RTIambassador is RTIambassador
    assert hla.rti1516e.FederateAmbassador is FederateAmbassador
    assert hla.rti1516e.NullFederateAmbassador is NullFederateAmbassador
