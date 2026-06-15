import pytest

from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010_rti_backend_common import make_rti_ambassador
from hla2010.exceptions import FederationExecutionDoesNotExist
from hla2010.handles import AttributeHandle, DimensionHandle, InteractionClassHandle, ObjectClassHandle, ObjectInstanceHandle, ParameterHandle, RegionHandle
from hla2010.enums import CallbackModel, OrderType, ResignAction
from hla2010.time import HLAfloat64Interval, HLAfloat64Time
from hla2010_rti_java_common.java_shim_factory import create_java_shim_backend, create_shared_java_shim_backend
from hla2010_rti_java_common.java_shim_kernel import SharedJavaShimKernel
from hla2010_verification_harness import run_basic_federate_scenario
from hla2010_verification_harness.scenario_support import drain_callbacks_pair


@pytest.mark.parametrize("profile", ["jpype", "py4j"])
def test_java_bridge_profile_runs_backend_neutral_federate_scenario(profile):
    summary = run_basic_federate_scenario(
        lambda: make_rti_ambassador(create_java_shim_backend(profile)),
        federation_name=f"{profile}-scenario",
    )
    assert summary["backend"].kind == f"java/{profile}/shim"
    assert summary["event_names"].count("discover") == 1
    assert summary["event_names"].count("reflect") == 1
    assert summary["event_names"].count("interaction") == 1


def test_same_federate_scenario_does_not_branch_on_java_bridge_profile():
    jpype_summary = run_basic_federate_scenario(
        lambda: make_rti_ambassador(create_java_shim_backend("jpype")),
        federation_name="same-code-jpype",
    )
    py4j_summary = run_basic_federate_scenario(
        lambda: make_rti_ambassador(create_java_shim_backend("py4j")),
        federation_name="same-code-py4j",
    )
    assert jpype_summary["event_names"] == py4j_summary["event_names"]


def test_java_like_exceptions_translate_to_python_rti_exceptions():
    rti = make_rti_ambassador(create_java_shim_backend("jpype"))
    # Destroying a federation before connect should first show NotConnected.  We
    # then connect and ask for a missing federation to prove Java simple class
    # names map into the Python exception hierarchy.
    from hla2010.spec import FederateAmbassadorSpec
    from hla2010.enums import CallbackModel

    rti.connect(FederateAmbassadorSpec(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederationExecutionDoesNotExist):
        rti.destroyFederationExecution("missing")
    rti.disconnect()
    rti.close()


@pytest.mark.parametrize("profile", ["jpype", "py4j"])
def test_shared_java_bridge_profile_round_trips_basic_objects_and_callbacks(profile: str) -> None:
    kernel = SharedJavaShimKernel()
    publisher = make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))
    subscriber = make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))
    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    federation_name = f"java-roundtrip-{profile}"
    try:
        publisher.connect(publisher_fed, CallbackModel.HLA_EVOKED)
        subscriber.connect(subscriber_fed, CallbackModel.HLA_EVOKED)
        publisher.createFederationExecution(federation_name, "DemoFOMmodule.xml", "HLAfloat64Time")
        publisher_handle = publisher.joinFederationExecution("publisher", "demo", federation_name)
        subscriber_handle = subscriber.joinFederationExecution("subscriber", "demo", federation_name)

        assert publisher.backend_info.kind == f"java/{profile}/shared-shim"
        assert subscriber.backend_info.kind == f"java/{profile}/shared-shim"
        assert publisher.getFederateName(publisher_handle) == "publisher"
        assert subscriber.getFederateName(subscriber_handle) == "subscriber"

        publisher_object_class = publisher.getObjectClassHandle("HLAobjectRoot.DemoObject")
        publisher_attribute = publisher.getAttributeHandle(publisher_object_class, "Payload")
        publisher_interaction = publisher.getInteractionClassHandle("HLAinteractionRoot.DemoInteraction")
        publisher_parameter = publisher.getParameterHandle(publisher_interaction, "Message")
        publisher_dimension = publisher.getDimensionHandle("RoutingSpace")
        region = publisher.createRegion({publisher_dimension})

        subscriber_object_class = subscriber.getObjectClassHandle("HLAobjectRoot.DemoObject")
        subscriber_attribute = subscriber.getAttributeHandle(subscriber_object_class, "Payload")
        subscriber_interaction = subscriber.getInteractionClassHandle("HLAinteractionRoot.DemoInteraction")
        subscriber_parameter = subscriber.getParameterHandle(subscriber_interaction, "Message")

        assert isinstance(publisher_object_class, ObjectClassHandle)
        assert isinstance(publisher_attribute, AttributeHandle)
        assert isinstance(publisher_interaction, InteractionClassHandle)
        assert isinstance(publisher_parameter, ParameterHandle)
        assert isinstance(publisher_dimension, DimensionHandle)
        assert isinstance(region, RegionHandle)
        assert subscriber_object_class == publisher_object_class
        assert subscriber_attribute == publisher_attribute
        assert subscriber_interaction == publisher_interaction
        assert subscriber_parameter == publisher_parameter

        publisher.publishObjectClassAttributes(publisher_object_class, {publisher_attribute})
        subscriber.subscribeObjectClassAttributes(subscriber_object_class, {subscriber_attribute})
        publisher.publishInteractionClass(publisher_interaction)
        subscriber.subscribeInteractionClass(subscriber_interaction)

        obj = publisher.registerObjectInstance(publisher_object_class, f"{profile}-Object-1")
        assert isinstance(obj, ObjectInstanceHandle)
        drain_callbacks_pair(publisher, subscriber)

        discover = subscriber_fed.last_callback("discoverObjectInstance")
        subscriber_obj = subscriber.getObjectInstanceHandle(f"{profile}-Object-1")
        assert discover is not None
        assert discover.args == (subscriber_obj, subscriber_object_class, f"{profile}-Object-1")

        publisher.enableTimeRegulation(HLAfloat64Interval(1.0))
        subscriber.enableTimeRegulation(HLAfloat64Interval(1.0))
        publisher.enableTimeConstrained()
        subscriber.enableTimeConstrained()
        drain_callbacks_pair(publisher, subscriber)

        publisher.timeAdvanceRequest(HLAfloat64Time(2.0))
        subscriber.timeAdvanceRequest(HLAfloat64Time(2.0))
        drain_callbacks_pair(publisher, subscriber)
        assert publisher_fed.last_callback("timeRegulationEnabled").args == (HLAfloat64Time(0.0),)
        assert subscriber_fed.last_callback("timeRegulationEnabled").args == (HLAfloat64Time(0.0),)
        assert publisher_fed.last_callback("timeConstrainedEnabled").args == (HLAfloat64Time(0.0),)
        assert subscriber_fed.last_callback("timeConstrainedEnabled").args == (HLAfloat64Time(0.0),)
        assert publisher_fed.last_callback("timeAdvanceGrant").args == (HLAfloat64Time(2.0),)
        assert subscriber_fed.last_callback("timeAdvanceGrant").args == (HLAfloat64Time(2.0),)

        publisher.updateAttributeValues(obj, {publisher_attribute: b"route-bytes"}, b"route-tag")
        publisher.sendInteraction(publisher_interaction, {publisher_parameter: b"route-hello"}, b"interaction-tag")
        drain_callbacks_pair(publisher, subscriber)

        reflect = subscriber_fed.last_callback("reflectAttributeValues")
        receive = subscriber_fed.last_callback("receiveInteraction")
        assert reflect is not None
        assert receive is not None
        assert reflect.args[0] == subscriber_obj
        assert reflect.args[1] == {subscriber_attribute: b"route-bytes"}
        assert reflect.args[2] == b"route-tag"
        assert reflect.args[3] is OrderType.RECEIVE
        assert receive.args[0] == subscriber_interaction
        assert receive.args[1] == {subscriber_parameter: b"route-hello"}
        assert receive.args[2] == b"interaction-tag"
        assert receive.args[3] is OrderType.RECEIVE

        publisher.deleteRegion(region)
        publisher.resignFederationExecution(ResignAction.DELETE_OBJECTS)
        subscriber.resignFederationExecution(ResignAction.NO_ACTION)
        publisher.destroyFederationExecution(federation_name)
        subscriber.disconnect()
        publisher.disconnect()
    finally:
        subscriber.close()
        publisher.close()
