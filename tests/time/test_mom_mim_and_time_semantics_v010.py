from __future__ import annotations

import pytest

from hla2010 import mom
from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010_rti_python import InMemoryRTIEngine, rti_ambassador
from hla2010.enums import CallbackModel
from hla2010.enums import ResignAction
from hla2010.exceptions import (
    InTimeAdvancingState,
    LogicalTimeAlreadyPassed,
    InvalidLookahead,
    MessageCanNoLongerBeRetracted,
    TimeConstrainedAlreadyEnabled,
    TimeRegulationAlreadyEnabled,
    TimeRegulationIsNotEnabled,
)
from hla2010.handles import MessageRetractionHandle


def drain(*rtis, rounds: int = 20):
    for _ in range(rounds):
        for rti in rtis:
            rti.evokeMultipleCallbacks(0.0, 0.0)


def joined_pair(name: str):
    engine = InMemoryRTIEngine()
    r1 = rti_ambassador(engine=engine)
    r2 = rti_ambassador(engine=engine)
    f1 = RecordingFederateAmbassador()
    f2 = RecordingFederateAmbassador()
    r1.connect(f1, CallbackModel.HLA_EVOKED)
    r2.connect(f2, CallbackModel.HLA_EVOKED)
    r1.createFederationExecution(name, "TargetRadarFOMmodule.xml")
    r1.joinFederationExecution("Sender", "Producer", name)
    r2.joinFederationExecution("Receiver", "Consumer", name)
    return r1, r2, f1, f2


def setup_target_object(r1, r2):
    target = r1.getObjectClassHandle("HLAobjectRoot.Target")
    position = r1.getAttributeHandle(target, "Position")
    r1.publishObjectClassAttributes(target, {position})
    r2.subscribeObjectClassAttributes(target, {position})
    obj = r1.registerObjectInstance(target, "Target-TSO")
    drain(r1, r2)
    return obj, position


def test_standard_mim_is_loaded_and_exposes_mom_classes_and_interactions():
    r1, _r2, f1, _f2 = joined_pair("mom-loaded-fed")

    federation_class = r1.getObjectClassHandle(mom.MOM_FEDERATION_OBJECT_CLASS)
    federate_class = r1.getObjectClassHandle(mom.MOM_FEDERATE_OBJECT_CLASS)
    fed_name_attr = r1.getAttributeHandle(federation_class, "HLAfederationName")
    federate_name_attr = r1.getAttributeHandle(federate_class, "HLAfederateName")
    request = r1.getInteractionClassHandle(f"{mom.MOM_FEDERATION_INTERACTION_ROOT}.HLArequest.HLArequestFOMmoduleData")
    report = r1.getInteractionClassHandle(f"{mom.MOM_FEDERATION_INTERACTION_ROOT}.HLAreport.HLAreportFOMmoduleData")
    indicator_param = r1.getParameterHandle(request, "HLAFOMmoduleIndicator")
    data_param = r1.getParameterHandle(report, "HLAFOMmoduleData")

    assert fed_name_attr.value > 0
    assert federate_name_attr.value > 0
    assert indicator_param.value > 0
    assert data_param.value > 0
    summary = r1.backend.current_mom_summary()
    assert mom.MOM_FEDERATION_OBJECT_CLASS in summary["mom_object_classes"]
    assert any("HLArequestFOMmoduleData" in name for name in summary["mom_interaction_classes"])


def test_mom_objects_can_be_discovered_and_attribute_values_requested():
    r1, _r2, f1, _f2 = joined_pair("mom-objects-fed")
    federation_class = r1.getObjectClassHandle(mom.MOM_FEDERATION_OBJECT_CLASS)
    federation_name_attr = r1.getAttributeHandle(federation_class, "HLAfederationName")

    r1.subscribeObjectClassAttributes(federation_class, {federation_name_attr})
    drain(r1)
    discoveries = f1.callbacks_named("discoverObjectInstance")
    assert discoveries
    mom_federation_object = discoveries[-1].args[0]

    r1.requestAttributeValueUpdate(mom_federation_object, {federation_name_attr}, b"mom-query")
    drain(r1)
    reflections = f1.callbacks_named("reflectAttributeValues")
    assert reflections
    reflected_object, reflected_attrs = reflections[-1].args[0], reflections[-1].args[1]
    assert reflected_object == mom_federation_object
    assert federation_name_attr in reflected_attrs


def test_mom_request_interaction_produces_report_interaction_for_subscribers():
    r1, _r2, f1, _f2 = joined_pair("mom-report-fed")
    request_name = f"{mom.MOM_FEDERATION_INTERACTION_ROOT}.HLArequest.HLArequestFOMmoduleData"
    report_name = f"{mom.MOM_FEDERATION_INTERACTION_ROOT}.HLAreport.HLAreportFOMmoduleData"
    request = r1.getInteractionClassHandle(request_name)
    report = r1.getInteractionClassHandle(report_name)
    indicator = r1.getParameterHandle(request, "HLAFOMmoduleIndicator")
    data = r1.getParameterHandle(report, "HLAFOMmoduleData")

    r1.subscribeInteractionClass(report)
    r1.sendInteraction(request, {indicator: b"0"}, b"mom-request")
    drain(r1)

    reports = [record for record in f1.callbacks_named("receiveInteraction") if record.args[0] == report]
    assert reports
    assert data in reports[-1].args[1]


def test_timestamp_order_attribute_updates_are_released_in_time_order():
    r1, r2, _f1, f2 = joined_pair("tso-order-fed")
    obj, position = setup_target_object(r1, r2)
    tf = r1.getTimeFactory()

    r1.enableTimeRegulation(tf.make_interval(0.0))
    r2.enableTimeConstrained()
    drain(r1, r2)

    ret10 = r1.updateAttributeValues(obj, {position: b"t10"}, b"late", tf.make_time(10.0))
    ret05 = r1.updateAttributeValues(obj, {position: b"t05"}, b"early", tf.make_time(5.0))
    assert ret10 is not None and isinstance(ret10.handle, MessageRetractionHandle)
    assert ret05 is not None and isinstance(ret05.handle, MessageRetractionHandle)

    # Let the regulating sender's time position stop constraining the receiver.
    r1.timeAdvanceRequestAvailable(tf.make_time(10.0))
    r2.timeAdvanceRequestAvailable(tf.make_time(10.0))
    drain(r1, r2)

    ordered = [record.args[1][position] for record in f2.callbacks_named("reflectAttributeValues") if position in record.args[1]]
    assert ordered[-2:] == [b"t05", b"t10"]
    assert f2.callbacks_named("timeAdvanceGrant")[-1].args[0] == tf.make_time(10.0)


def test_retracted_timestamp_order_message_is_not_delivered():
    r1, r2, _f1, f2 = joined_pair("tso-retract-fed")
    obj, position = setup_target_object(r1, r2)
    tf = r1.getTimeFactory()

    r1.enableTimeRegulation(tf.make_interval(0.0))
    r2.enableTimeConstrained()
    drain(r1, r2)

    ret = r1.updateAttributeValues(obj, {position: b"withdraw"}, b"ret", tf.make_time(5.0))
    assert ret is not None
    r1.retract(ret.handle)
    with pytest.raises(MessageCanNoLongerBeRetracted):
        r1.retract(ret.handle)

    r1.timeAdvanceRequestAvailable(tf.make_time(5.0))
    r2.timeAdvanceRequestAvailable(tf.make_time(5.0))
    drain(r1, r2)

    delivered = [record for record in f2.callbacks_named("reflectAttributeValues") if record.args[2] == b"ret"]
    assert delivered == []


def test_time_state_errors_and_zero_lookahead_are_enforced():
    r1, _r2, _f1, _f2 = joined_pair("time-errors-fed")
    tf = r1.getTimeFactory()

    r1.enableTimeRegulation(tf.make_interval(0.0))
    with pytest.raises(TimeRegulationAlreadyEnabled):
        r1.enableTimeRegulation(tf.make_interval(0.0))
    r1.modifyLookahead(tf.make_interval(0.0))
    r1.timeAdvanceRequest(tf.make_time(4.0))
    drain(r1)
    with pytest.raises(LogicalTimeAlreadyPassed):
        r1.timeAdvanceRequest(tf.make_time(3.0))

    r2 = rti_ambassador(engine=r1.backend.engine)
    f2 = RecordingFederateAmbassador()
    r2.connect(f2, CallbackModel.HLA_EVOKED)
    r2.joinFederationExecution("Constrained", "Consumer", "time-errors-fed")
    r2.enableTimeConstrained()
    with pytest.raises(TimeConstrainedAlreadyEnabled):
        r2.enableTimeConstrained()


def test_query_lookahead_requires_time_regulation_and_modify_lookahead_rejects_pending_advance():
    r1, r2, _f1, _f2 = joined_pair("lookahead-negative-fed")
    tf = r1.getTimeFactory()

    r1.enableTimeRegulation(tf.make_interval(1.0))
    with pytest.raises(TimeRegulationIsNotEnabled):
        r2.queryLookahead()

    r2.enableTimeRegulation(tf.make_interval(1.0))
    r2.enableTimeConstrained()
    drain(r1, r2)

    r1.timeAdvanceRequest(tf.make_time(4.0))
    drain(r1, r2)
    assert r1.backend.state.time_advancing is False

    r2.timeAdvanceRequest(tf.make_time(5.0))
    assert r2.backend.state.time_advancing is True
    with pytest.raises(InTimeAdvancingState):
        r2.modifyLookahead(tf.make_interval(2.0))


def test_negative_lookahead_is_rejected_for_regulation_and_modification():
    r1, r2, _f1, _f2 = joined_pair("negative-lookahead-fed")
    tf = r1.getTimeFactory()

    with pytest.raises(InvalidLookahead):
        r1.enableTimeRegulation(tf.make_interval(-1.0))

    r1.enableTimeRegulation(tf.make_interval(1.0))
    with pytest.raises(InvalidLookahead):
        r1.modifyLookahead(tf.make_interval(-0.5))

    r2.enableTimeRegulation(tf.make_interval(1.0))
    r2.enableTimeConstrained()
    drain(r1, r2)
    r2.timeAdvanceRequest(tf.make_time(5.0))
    with pytest.raises(InTimeAdvancingState):
        r2.modifyLookahead(tf.make_interval(-0.5))


def test_section8_core_time_management_surface_covers_callbacks_states_and_grants():
    r1, r2, f1, f2 = joined_pair("section8-core-fed")
    tf = r1.getTimeFactory()

    assert r1.queryLogicalTime() == tf.make_time(0.0)
    assert r2.queryLogicalTime() == tf.make_time(0.0)

    r1.enableTimeRegulation(tf.make_interval(1.0))
    r2.enableTimeConstrained()
    drain(r1, r2)
    assert f1.last_callback("timeRegulationEnabled").args[0] == tf.make_time(0.0)
    assert f2.last_callback("timeConstrainedEnabled").args[0] == tf.make_time(0.0)
    assert r1.queryLookahead() == tf.make_interval(1.0)

    r1.disableTimeRegulation()
    r2.disableTimeConstrained()
    assert r1.backend.state.time_regulation_enabled is False
    assert r2.backend.state.time_constrained_enabled is False

    r1.enableTimeRegulation(tf.make_interval(1.0))
    r2.enableTimeConstrained()
    drain(r1, r2)

    r1.timeAdvanceRequest(tf.make_time(4.0))
    r2.timeAdvanceRequestAvailable(tf.make_time(4.0))
    drain(r1, r2)
    assert f1.last_callback("timeAdvanceGrant").args[0] == tf.make_time(4.0)
    assert f2.last_callback("timeAdvanceGrant").args[0] == tf.make_time(4.0)
    assert r1.queryLogicalTime() == tf.make_time(4.0)

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("section8-core-fed")


def test_section8_next_message_request_grants_earliest_tso_message():
    r1, r2, f1, f2 = joined_pair("section8-nmr-fed")
    tf = r1.getTimeFactory()

    cls = r1.getObjectClassHandle("HLAobjectRoot.Target")
    attr = r1.getAttributeHandle(cls, "Position")
    r1.publishObjectClassAttributes(cls, {attr})
    r2.subscribeObjectClassAttributes(cls, {attr})
    r1.enableTimeRegulation(tf.make_interval(1.0))
    r2.enableTimeConstrained()
    drain(r1, r2)

    obj = r1.registerObjectInstance(cls, "Section8-NMR")
    drain(r1, r2)
    f2.clear()

    r1.updateAttributeValues(obj, {attr: b"early"}, b"early", tf.make_time(2.0))
    r1.updateAttributeValues(obj, {attr: b"late"}, b"late", tf.make_time(3.0))
    drain(r1, r2)
    assert not f2.callbacks_named("reflectAttributeValues")

    r1.timeAdvanceRequest(tf.make_time(4.0))
    drain(r1, r2)
    assert f1.last_callback("timeAdvanceGrant").args[0] == tf.make_time(4.0)

    r2.nextMessageRequest(tf.make_time(10.0))
    drain(r1, r2)
    first = f2.last_callback("reflectAttributeValues")
    assert first is not None
    assert first.args[1][attr] == b"early"
    assert f2.last_callback("timeAdvanceGrant").args[0] == tf.make_time(2.0)

    r2.nextMessageRequest(tf.make_time(10.0))
    drain(r1, r2)
    second = f2.last_callback("reflectAttributeValues")
    assert second is not None
    assert second.args[1][attr] == b"late"
    assert f2.last_callback("timeAdvanceGrant").args[0] == tf.make_time(3.0)

    r1.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("section8-nmr-fed")
