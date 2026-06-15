from __future__ import annotations

import inspect
import json
import subprocess

import hla
import hla.editions.ed2010 as hla_ed2010
import hla2010
import hla2010.spec as hla_spec
import hla2010.rti as rti_module
from hla2010_rti_backend_common import RecordingBackend, make_rti_ambassador
import hla2010_rti_runtime_common.factory as runtime_factory
from hla2010.rti import (
    available_backend_plugins,
    create_rti_ambassador,
    discover_rti_backends,
    get_rti_factory,
    iter_rti_backend_plugins,
    iter_rti_factories,
)
from hla2010.spec import FederateAmbassadorSpec, RTIambassadorSpec, lower_camel_to_snake


def test_spec_rti_is_abstract_and_pythonic():
    assert inspect.isabstract(RTIambassadorSpec)
    assert hasattr(RTIambassadorSpec, "get_hla_version")
    assert hasattr(RTIambassadorSpec, "getHLAversion")
    assert lower_camel_to_snake("getHLAversion") == "get_hla_version"
    assert "Java:" in RTIambassadorSpec.connect.__doc__
    assert "C++:" in RTIambassadorSpec.connect.__doc__


def test_spec_federate_is_a_noop_prototype():
    fed = FederateAmbassadorSpec()
    assert fed.announce_synchronization_point("label") is None
    assert fed.announceSynchronizationPoint("label") is None
    assert "Java:" in FederateAmbassadorSpec.connection_lost.__doc__
    assert "C++:" in FederateAmbassadorSpec.connection_lost.__doc__


def test_runtime_rti_alias_routes_through_pythonic_method():
    rti = make_rti_ambassador(RecordingBackend(results={"getHLAversion": "HLA 1516.1-2010"}))
    assert rti.get_hla_version() == "HLA 1516.1-2010"


def test_runtime_backends_are_discovered_as_plugins():
    plugins = available_backend_plugins()
    assert plugins["python"].name == "python"
    assert plugins["in-memory"].name == "python"
    assert plugins["pitch-jpype"].family == "pitch/java"
    assert plugins["portico-jpype"].family == "portico/java"
    assert plugins["portico"].name == "portico-jpype"

    rti = create_rti_ambassador("in-memory")
    assert rti.backend_info.name == "python-inmemory-rti"


def test_runtime_backend_listing_is_deduplicated_and_probeable():
    plugins = iter_rti_backend_plugins()
    names = {plugin.name for plugin in plugins}
    assert "python" in names
    assert "certi" in names
    assert "pitch-jpype" in names
    assert "portico-jpype" in names
    assert len(plugins) == len(names)

    registered = {row.name: row for row in discover_rti_backends()}
    assert registered["python"].available is None
    assert registered["python"].family == "python-reference"
    assert "in-memory" in registered["python"].selectable_names
    assert registered["python"].probe_supported is True

    probed = {row.name: row for row in discover_rti_backends(probe=True)}
    assert probed["python"].available is True
    assert probed["python"].info.kind == "python/in-memory"


def test_runtime_factories_are_listable_selectable_and_instantiable():
    factories = iter_rti_factories()
    names = {factory.name for factory in factories}
    assert "python" in names
    assert "certi" in names
    assert "pitch-jpype" in names
    assert len(factories) == len(names)

    python_factory = get_rti_factory("in-memory")
    assert python_factory.name == "python"
    assert "python" in python_factory.selectable_names
    assert "in-memory" in python_factory.selectable_names
    assert python_factory.probe_supported is True

    rti = python_factory.create_rti_ambassador()
    assert rti.backend_info.kind == "python/in-memory"

    probe = python_factory.discover()
    assert probe.name == "python"
    assert probe.available is True
    assert probe.info.kind == "python/in-memory"


def test_rti_factory_tool_lists_and_shows_installed_factories():
    listed = subprocess.run(
        ["bash", "./tools/rti-factories", "list"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Installed RTI factories" in listed.stdout
    assert "- python [python-reference]" in listed.stdout
    assert "selectable_names:" in listed.stdout
    assert "in-memory" in listed.stdout

    shown = subprocess.run(
        ["bash", "./tools/rti-factories", "show", "in-memory", "--probe"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(shown.stdout)
    assert payload["name"] == "python"
    assert "in-memory" in payload["selectable_names"]
    assert payload["probe"]["available"] is True

    instantiated = subprocess.run(
        ["bash", "./tools/rti-factories", "instantiate", "in-memory", "--probe"],
        check=True,
        capture_output=True,
        text=True,
    )
    instantiated_payload = json.loads(instantiated.stdout)
    assert instantiated_payload["name"] == "python"
    assert instantiated_payload["backend_info"]["kind"] == "python/in-memory"
    assert instantiated_payload["probe"]["available"] is True


def test_root_rti_facade_stays_narrow():
    assert sorted(rti_module.__all__) == [
        "available_backend_plugins",
        "create_backend",
        "create_rti_ambassador",
        "discover_rti_backends",
        "get_rti_factory",
        "iter_rti_backend_plugins",
        "iter_rti_factories",
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
        value = "missing_optional_backend:plugin"

        def load(self):
            raise ModuleNotFoundError("missing_optional_backend")

    class _EntryPoints:
        def select(self, *, group):
            assert group in {"hla.rti_backends", "hla2010.rti_backends"}
            return (_BrokenEntryPoint(),)

    monkeypatch.setattr(runtime_factory.metadata, "entry_points", lambda: _EntryPoints())
    monkeypatch.setattr(runtime_factory, "_SOURCE_CHECKOUT_PLUGIN_MODULES", ())

    assert runtime_factory._iter_entry_point_backend_plugins() == []


def test_runtime_factory_falls_back_to_source_checkout_plugins(monkeypatch):
    class _EntryPoints:
        def select(self, *, group):
            assert group in {"hla.rti_backends", "hla2010.rti_backends"}
            return ()

    monkeypatch.setattr(runtime_factory.metadata, "entry_points", lambda: _EntryPoints())

    plugins = runtime_factory._iter_source_checkout_backend_plugins()
    names = {plugin.name for plugin in plugins}
    assert "python" in names


def test_top_level_package_defaults_to_the_clean_spec_layer():
    assert not hasattr(hla2010, "RTIambassador")
    assert not hasattr(hla2010, "FederateAmbassador")
    assert not hasattr(hla2010, "NullFederateAmbassador")
    assert not hasattr(hla2010, "RTIambassadorSpec")
    assert not hasattr(hla2010, "FederateAmbassadorSpec")


def test_neutral_namespace_routes_to_explicit_2010_surface() -> None:
    assert hla.__version__ == hla2010.__version__
    assert hla_ed2010.edition_year == 2010
    assert hla_ed2010.legacy_namespace == "hla2010"
    assert hla_ed2010.spec.RTIambassadorSpec is RTIambassadorSpec
    assert hla_ed2010.rti.create_rti_ambassador is create_rti_ambassador


def test_standalone_spec_package_is_public():
    assert hla_spec.RTIambassadorSpec is RTIambassadorSpec
    assert hla_spec.FederateAmbassadorSpec is FederateAmbassadorSpec
    assert not hasattr(hla_spec, "RTIAmbassador")
    assert not hasattr(hla_spec, "FederateAmbassador")
    assert not hasattr(hla_spec, "NullFederateAmbassador")
