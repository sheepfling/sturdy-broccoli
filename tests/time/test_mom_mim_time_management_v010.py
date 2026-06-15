from __future__ import annotations

import pytest

from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010 import mom as hla_mom
from hla2010_rti_python import InMemoryRTIEngine, PythonRTIConfig, rti_ambassador
from hla2010.enums import CallbackModel, ResignAction
from hla2010.exceptions import InvalidLogicalTime
from hla2010.types import MessageRetractionReturn


def drain(*rtis, limit: int = 25) -> None:
    for _ in range(limit):
        for rti in rtis:
            rti.evokeMultipleCallbacks(0.0, 0.0)


def build_two_federates(name: str, *, enforce_galt: bool = False):
    engine = InMemoryRTIEngine()
    config = PythonRTIConfig(enforce_galt=enforce_galt)
    a = rti_ambassador(engine=engine, config=config)
    b = rti_ambassador(engine=engine, config=config)
    fa = RecordingFederateAmbassador()
    fb = RecordingFederateAmbassador()
    a.connect(fa, CallbackModel.HLA_EVOKED)
    b.connect(fb, CallbackModel.HLA_EVOKED)
    a.createFederationExecution(name, "TargetRadarFOMmodule.xml")
    a.joinFederationExecution("sender", "sender-type", name)
    b.joinFederationExecution("receiver", "receiver-type", name)
    drain(a, b)
    return a, b, fa, fb


def cleanup(name: str, *rtis) -> None:
    for rti in rtis:
        try:
            rti.resignFederationExecution(ResignAction.NO_ACTION)
        except Exception:
            pass
    try:
        rtis[0].destroyFederationExecution(name)
    except Exception:
        pass


def test_standard_mim_object_classes_are_loaded_and_mom_attributes_are_reflected():
    name = "mom-object-v010"
    rti, _unused, fed, _ = build_two_federates(name)
    try:
        cls = rti.getObjectClassHandle("HLAobjectRoot.HLAmanager.HLAfederate")
        attr = rti.getAttributeHandle(cls, "HLAfederateName")
        rti.subscribeObjectClassAttributes(cls, {attr})
        drain(rti)

        discoveries = fed.callbacks_named("discoverObjectInstance")
        assert any("HLAmanager.HLAfederate" in rec.args[2] for rec in discoveries)

        rti.requestAttributeValueUpdate(cls, {attr}, b"mom-snapshot")
        drain(rti)
        reflections = fed.callbacks_named("reflectAttributeValues")
        assert any(attr in rec.args[1] and rec.args[2] == b"mom-snapshot" for rec in reflections)
    finally:
        cleanup(name, rti, _unused)


def test_mim_data_request_reports_bundled_hlastandardmim_payload():
    name = "mim-report-v010"
    rti, _unused, fed, _ = build_two_federates(name)
    try:
        report = rti.getInteractionClassHandle(
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata"
        )
        request = rti.getInteractionClassHandle(
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata"
        )
        data_param = rti.getParameterHandle(report, "HLAMIMdata")
        rti.subscribeInteractionClass(report)
        rti.sendInteraction(request, {}, b"request-mim")
        drain(rti)

        received = [rec for rec in fed.callbacks_named("receiveInteraction") if rec.args[0] == report]
        assert received, "MOM request should result in a MOM report interaction"
        params = received[-1].args[1]
        assert data_param in params
        assert b"HLAstandardMIM" in params[data_param] or b"HLAmanager" in params[data_param]
    finally:
        cleanup(name, rti, _unused)


def test_service_reporting_switch_exposes_service_invocation_reports():
    name = "mom-service-report-v010"
    reporter, observer, _reporter_fed, observer_fed = build_two_federates(name)
    try:
        report = reporter.getInteractionClassHandle(
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"
        )
        adjust = reporter.getInteractionClassHandle(
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
        )
        federate_param = reporter.getParameterHandle(adjust, "HLAfederate")
        state_param = reporter.getParameterHandle(adjust, "HLAreportingState")
        service_param = reporter.getParameterHandle(report, "HLAservice")
        observer.subscribeInteractionClass(report)
        reporter.sendInteraction(
            adjust,
            {
                federate_param: reporter.backend.state.handle.encode(),
                state_param: hla_mom.encode_bool(True),
            },
            b"switch-on",
        )
        drain(reporter, observer)
        reporter.queryLogicalTime()
        drain(reporter, observer)

        received = [rec for rec in observer_fed.callbacks_named("receiveInteraction") if rec.args[0] == report]
        assert received
        assert any(service_param in rec.args[1] for rec in received)
    finally:
        cleanup(name, reporter, observer)


def _publish_subscribe_target(a, b):
    cls = a.getObjectClassHandle("HLAobjectRoot.Target")
    pos = a.getAttributeHandle(cls, "Position")
    a.publishObjectClassAttributes(cls, {pos})
    b.subscribeObjectClassAttributes(cls, {pos})
    obj = a.registerObjectInstance(cls, "TimedTarget")
    drain(a, b)
    return obj, pos


def test_timestamp_ordered_updates_are_delivered_by_time_advance_order():
    name = "time-order-v010"
    a, b, _fa, fb = build_two_federates(name)
    try:
        tf = a.getTimeFactory()
        a.enableTimeRegulation(tf.make_interval(1.0))
        b.enableTimeConstrained()
        drain(a, b)
        obj, pos = _publish_subscribe_target(a, b)
        fb.clear()

        a.updateAttributeValues(obj, {pos: b"five"}, b"t5", tf.make_time(5.0))
        a.updateAttributeValues(obj, {pos: b"three"}, b"t3", tf.make_time(3.0))
        drain(a, b)
        assert not fb.callbacks_named("reflectAttributeValues")

        lits = b.queryLITS()
        # Per §8.1.5/§8.18, LITS is based on GALT and queued TSO messages;
        # here GALT is 1.0 and the first queued TSO update is at 3.0.
        assert lits.time_is_valid and getattr(lits.time, "value") == 1.0

        # Once the regulating sender advances, the receiver can consume the
        # queued TSO updates via NMR.  NMR grants to the next queued timestamp
        # and preserves timestamp order even though the updates were sent 5, 3.
        a.timeAdvanceRequest(tf.make_time(6.0))
        drain(a, b)
        assert getattr(b.queryLITS().time, "value") == 3.0

        b.nextMessageRequest(tf.make_time(5.0))
        drain(a, b)
        reflections = fb.callbacks_named("reflectAttributeValues")
        assert [rec.args[1][pos] for rec in reflections] == [b"three"]
        grants = fb.callbacks_named("timeAdvanceGrant")
        assert getattr(grants[-1].args[0], "value") == 3.0

        b.nextMessageRequest(tf.make_time(5.0))
        drain(a, b)
        reflections = fb.callbacks_named("reflectAttributeValues")
        assert [rec.args[1][pos] for rec in reflections] == [b"three", b"five"]
        assert getattr(fb.callbacks_named("timeAdvanceGrant")[-1].args[0], "value") == 5.0
    finally:
        cleanup(name, a, b)


def test_timestamped_send_requires_time_regulation_and_lookahead_bound():
    name = "time-validation-v010"
    a, b, _fa, _fb = build_two_federates(name)
    try:
        tf = a.getTimeFactory()
        obj, pos = _publish_subscribe_target(a, b)
        # Per §8.1.2, a timestamp supplied by a non-time-regulating sender
        # remains receive-order and does not return a retraction handle.
        assert a.updateAttributeValues(obj, {pos: b"receive-order"}, b"ro", tf.make_time(2.0)) is None

        a.enableTimeRegulation(tf.make_interval(1.0))
        drain(a, b)
        with pytest.raises(InvalidLogicalTime):
            a.updateAttributeValues(obj, {pos: b"too-early"}, b"bad", tf.make_time(0.5))
    finally:
        cleanup(name, a, b)


def test_tso_message_retraction_prevents_later_delivery():
    name = "time-retraction-v010"
    a, b, _fa, fb = build_two_federates(name)
    try:
        tf = a.getTimeFactory()
        a.enableTimeRegulation(tf.make_interval(1.0))
        b.enableTimeConstrained()
        drain(a, b)
        obj, pos = _publish_subscribe_target(a, b)
        fb.clear()

        result = a.updateAttributeValues(obj, {pos: b"retract-me"}, b"retract", tf.make_time(4.0))
        assert isinstance(result, MessageRetractionReturn)
        a.retract(result.handle)
        a.timeAdvanceRequest(tf.make_time(6.0))
        drain(a, b)
        b.timeAdvanceRequestAvailable(tf.make_time(5.0))
        drain(a, b)
        assert not fb.callbacks_named("reflectAttributeValues")
        assert getattr(fb.callbacks_named("timeAdvanceGrant")[-1].args[0], "value") == 5.0
    finally:
        cleanup(name, a, b)
