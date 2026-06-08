from __future__ import annotations

import inspect

import hla2010
from hla2010.backends.base import RecordingBackend, make_rti_ambassador
from hla2010.spec_api import FederateAmbassadorSpec, RTIambassadorSpec, lower_camel_to_snake


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


def test_top_level_package_defaults_to_the_clean_spec_layer():
    assert hla2010.RTIambassador is RTIambassadorSpec
    assert hla2010.FederateAmbassador is FederateAmbassadorSpec
    assert hla2010.NullFederateAmbassador is FederateAmbassadorSpec
    assert hla2010.RuntimeRTIambassador is not RTIambassadorSpec
