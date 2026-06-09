from __future__ import annotations

import inspect

import hla2010
import hla2010.spec as hla_spec
import hla2010.rti as rti_module
from hla2010.backends.base import RecordingBackend, make_rti_ambassador
from hla2010.rti import available_backend_plugins, create_rti_ambassador, discover_rti_backends, iter_rti_backend_plugins
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

    probed = {row.name: row for row in discover_rti_backends(probe=True)}
    assert probed["python"].available is True
    assert probed["python"].info.kind == "python/in-memory"


def test_backend_entry_point_loader_skips_unimportable_optional_plugins(monkeypatch):
    class _BrokenEntryPoint:
        name = "broken"

        def load(self):
            raise ModuleNotFoundError("missing_optional_backend")

    class _EntryPoints:
        def select(self, *, group):
            assert group == "hla2010.rti_backends"
            return (_BrokenEntryPoint(),)

    monkeypatch.setattr(rti_module.metadata, "entry_points", lambda: _EntryPoints())

    assert rti_module._iter_entry_point_backend_plugins() == []


def test_top_level_package_defaults_to_the_clean_spec_layer():
    assert not hasattr(hla2010, "RTIambassador")
    assert not hasattr(hla2010, "FederateAmbassador")
    assert not hasattr(hla2010, "NullFederateAmbassador")
    assert not hasattr(hla2010, "RTIambassadorSpec")
    assert not hasattr(hla2010, "FederateAmbassadorSpec")


def test_standalone_spec_package_is_public():
    assert hla_spec.RTIambassadorSpec is RTIambassadorSpec
    assert hla_spec.FederateAmbassadorSpec is FederateAmbassadorSpec
    assert not hasattr(hla_spec, "RTIAmbassador")
    assert not hasattr(hla_spec, "FederateAmbassador")
    assert not hasattr(hla_spec, "NullFederateAmbassador")
