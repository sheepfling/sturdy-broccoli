from __future__ import annotations

import pytest

from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.backends.python_rti import InMemoryRTIEngine, PythonRTIConfig, rti_ambassador
from hla2010.enums import CallbackModel, ResignAction
from hla2010.exceptions import InvalidLogicalTime
from hla2010.types import MessageRetractionReturn


def drain(*rtis, limit: int = 25) -> None:
    for _ in range(limit):
        for rti in rtis:
            rti.evoke_multiple_callbacks(0.0, 0.0)


def build_two_federates(name: str, *, enforce_galt: bool = False):
    engine = InMemoryRTIEngine()
    config = PythonRTIConfig(enforce_galt=enforce_galt)
    a = rti_ambassador(engine=engine, config=config)
    b = rti_ambassador(engine=engine, config=config)
    fa = RecordingFederateAmbassador()
    fb = RecordingFederateAmbassador()
    a.connect(fa, CallbackModel.HLA_EVOKED)
    b.connect(fb, CallbackModel.HLA_EVOKED)
    a.create_federation_execution(name, "TargetRadarFOMmodule.xml")
    a.join_federation_execution("sender", "sender-type", name)
    b.join_federation_execution("receiver", "receiver-type", name)
    drain(a, b)
    return a, b, fa, fb


def cleanup(name: str, *rtis) -> None:
    for rti in rtis:
        try:
            rti.resign_federation_execution(ResignAction.NO_ACTION)
        except Exception:
            pass
    try:
        rtis[0].destroy_federation_execution(name)
    except Exception:
        pass


def test_standard_mim_object_classes_are_loaded_and_mom_attributes_are_reflected():
    name = "mom-object-v010"
    rti, _unused, fed, _ = build_two_federates(name)
    try:
        cls = rti.get_object_class_handle("HLAobjectRoot.HLAmanager.HLAfederate")
        attr = rti.get_attribute_handle(cls, "HLAfederateName")
        rti.subscribe_object_class_attributes(cls, {attr})
        drain(rti)

        discoveries = fed.callbacks_named("discoverObjectInstance")
        assert any("HLAmanager.HLAfederate" in rec.args[2] for rec in discoveries)

        rti.request_attribute_value_update(cls, {attr}, b"mom-snapshot")
        drain(rti)
        reflections = fed.callbacks_named("reflectAttributeValues")
        assert any(attr in rec.args[1] and rec.args[2] == b"mom-snapshot" for rec in reflections)
    finally:
        cleanup(name, rti, _unused)


def test_mim_data_request_reports_bundled_hlastandardmim_payload():
    name = "mim-report-v010"
    rti, _unused, fed, _ = build_two_federates(name)
    try:
        report = rti.get_interaction_class_handle(
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata"
        )
        request = rti.get_interaction_class_handle(
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata"
        )
        data_param = rti.get_parameter_handle(report, "HLAMIMdata")
        rti.subscribe_interaction_class(report)
        rti.send_interaction(request, {}, b"request-mim")
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
    rti, _unused, fed, _ = build_two_federates(name)
    try:
        report = rti.get_interaction_class_handle(
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"
        )
        adjust = rti.get_interaction_class_handle(
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetSwitches"
        )
        service_param = rti.get_parameter_handle(report, "HLAservice")
        rti.subscribe_interaction_class(report)
        rti.send_interaction(adjust, {}, b"switch-on")
        rti.query_logical_time()
        drain(rti)

        received = [rec for rec in fed.callbacks_named("receiveInteraction") if rec.args[0] == report]
        assert received
        assert any(service_param in rec.args[1] for rec in received)
    finally:
        cleanup(name, rti, _unused)


def _publish_subscribe_target(a, b):
    cls = a.get_object_class_handle("HLAobjectRoot.Target")
    pos = a.get_attribute_handle(cls, "Position")
    a.publish_object_class_attributes(cls, {pos})
    b.subscribe_object_class_attributes(cls, {pos})
    obj = a.register_object_instance(cls, "TimedTarget")
    drain(a, b)
    return obj, pos


def test_timestamp_ordered_updates_are_delivered_by_time_advance_order():
    name = "time-order-v010"
    a, b, _fa, fb = build_two_federates(name)
    try:
        tf = a.get_time_factory()
        a.enable_time_regulation(tf.make_interval(1.0))
        b.enable_time_constrained()
        drain(a, b)
        obj, pos = _publish_subscribe_target(a, b)
        fb.clear()

        a.update_attribute_values(obj, {pos: b"five"}, b"t5", tf.make_time(5.0))
        a.update_attribute_values(obj, {pos: b"three"}, b"t3", tf.make_time(3.0))
        drain(a, b)
        assert not fb.callbacks_named("reflectAttributeValues")

        lits = b.query_lits()
        # Per §8.1.5/§8.18, LITS is based on GALT and queued TSO messages;
        # here GALT is 1.0 and the first queued TSO update is at 3.0.
        assert lits.time_is_valid and getattr(lits.time, "value") == 1.0

        # Once the regulating sender advances, the receiver can consume the
        # queued TSO updates via NMR.  NMR grants to the next queued timestamp
        # and preserves timestamp order even though the updates were sent 5, 3.
        a.time_advance_request(tf.make_time(6.0))
        drain(a, b)
        assert getattr(b.query_lits().time, "value") == 3.0

        b.next_message_request(tf.make_time(5.0))
        drain(a, b)
        reflections = fb.callbacks_named("reflectAttributeValues")
        assert [rec.args[1][pos] for rec in reflections] == [b"three"]
        grants = fb.callbacks_named("timeAdvanceGrant")
        assert getattr(grants[-1].args[0], "value") == 3.0

        b.next_message_request(tf.make_time(5.0))
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
        tf = a.get_time_factory()
        obj, pos = _publish_subscribe_target(a, b)
        # Per §8.1.2, a timestamp supplied by a non-time-regulating sender
        # remains receive-order and does not return a retraction handle.
        assert a.update_attribute_values(obj, {pos: b"receive-order"}, b"ro", tf.make_time(2.0)) is None

        a.enable_time_regulation(tf.make_interval(1.0))
        drain(a, b)
        with pytest.raises(InvalidLogicalTime):
            a.update_attribute_values(obj, {pos: b"too-early"}, b"bad", tf.make_time(0.5))
    finally:
        cleanup(name, a, b)


def test_tso_message_retraction_prevents_later_delivery():
    name = "time-retraction-v010"
    a, b, _fa, fb = build_two_federates(name)
    try:
        tf = a.get_time_factory()
        a.enable_time_regulation(tf.make_interval(1.0))
        b.enable_time_constrained()
        drain(a, b)
        obj, pos = _publish_subscribe_target(a, b)
        fb.clear()

        result = a.update_attribute_values(obj, {pos: b"retract-me"}, b"retract", tf.make_time(4.0))
        assert isinstance(result, MessageRetractionReturn)
        a.retract(result.handle)
        a.time_advance_request(tf.make_time(6.0))
        drain(a, b)
        b.time_advance_request_available(tf.make_time(5.0))
        drain(a, b)
        assert not fb.callbacks_named("reflectAttributeValues")
        assert getattr(fb.callbacks_named("timeAdvanceGrant")[-1].args[0], "value") == 5.0
    finally:
        cleanup(name, a, b)
