from __future__ import annotations

import json
from pathlib import Path

import pytest

from hla2010 import mom as hla_mom
from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.backends.python import InMemoryRTIEngine, PythonRTIConfig
from hla2010.backends.python.state import CallbackEvent
from hla2010.enums import CallbackModel, OrderType, ResignAction
from hla2010.exceptions import FederateServiceInvocationsAreBeingReportedViaMOM
from hla2010.rti import create_rti_ambassador
from hla2010.types import RangeBounds
from hla2010_verification_harness import (
    NegotiatedOwnershipScenarioConfig,
    ReleaseRequestOwnershipScenarioConfig,
    run_negotiated_attribute_ownership_scenario,
    run_release_request_ownership_scenario,
)


def _rti(engine: InMemoryRTIEngine, *, config: PythonRTIConfig | None = None):
    return create_rti_ambassador("python", engine=engine, config=config)


def _drain(*rtis) -> None:
    for _ in range(30):
        for rti in rtis:
            rti.evoke_multiple_callbacks(0.0, 0.0)


def _joined(name: str, *, n: int = 1, config: PythonRTIConfig | None = None):
    engine = InMemoryRTIEngine()
    rtis = [_rti(engine, config=config if i == 0 else None) for i in range(n)]
    feds = [RecordingFederateAmbassador() for _ in range(n)]
    for rti, fed in zip(rtis, feds):
        rti.connect(fed, CallbackModel.HLA_EVOKED)
    rtis[0].create_federation_execution(name, "TargetRadarFOMmodule.xml")
    for i, rti in enumerate(rtis):
        rti.join_federation_execution(f"fed-{i}", f"type-{i}", name)
    return engine, rtis, feds


def test_mom_service_reports_to_file_and_global_report_file(tmp_path: Path):
    global_file = tmp_path / "all-services.jsonl"
    config = PythonRTIConfig(
        service_report_file=str(global_file),
        service_report_file_truncate=True,
        service_report_directory=str(tmp_path),
    )
    _engine, (rti,), (fed,) = _joined("service-report-file-v011", config=config)

    adjust = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetSwitches"
    )
    rti.send_interaction(adjust, {}, b"enable-reports")
    rti.query_logical_time()
    _drain(rti)

    assert global_file.exists()
    global_records = [json.loads(line) for line in global_file.read_text().splitlines() if line.strip()]
    assert any(record["service_name"] == "queryLogicalTime" for record in global_records)

    report_file_value = rti.backend.state.service_report_file
    if report_file_value is not None:
        report_file = Path(report_file_value)
        assert report_file.exists()
        records = [json.loads(line) for line in report_file.read_text().splitlines() if line.strip()]
        assert records[0]["recordType"] == "ServiceReportInitialRecord"
        logical_time_records = [record for record in records if record.get("service") == "queryLogicalTime"]
        assert logical_time_records
        assert logical_time_records[-1]["success"] is True
        assert logical_time_records[-1]["specSection"].endswith("§8.17")
        assert "returned" in logical_time_records[-1]


def test_mom_set_switches_service_reporting_conflict_is_reported():
    _engine, (rti,), (fed,) = _joined("mom-switch-conflict-v011")
    report = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"
    )
    exception_report = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportMOMexception"
    )
    adjust = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
    )
    federate_param = rti.get_parameter_handle(adjust, "HLAfederate")
    service_reporting_param = rti.get_parameter_handle(adjust, "HLAreportingState")

    rti.subscribe_interaction_class(report)
    rti.send_interaction(
        adjust,
        {
            federate_param: rti.backend.state.handle.encode(),
            service_reporting_param: hla_mom.encode_bool(True),
        },
        b"bad-switch",
    )
    _drain(rti)

    assert rti.backend.state.service_reporting is False
    exceptions = [rec for rec in fed.callbacks_named("receiveInteraction") if rec.args[0] == exception_report]
    assert exceptions
    decoded_values = []
    for value in exceptions[-1].args[1].values():
        try:
            decoded_values.append(hla_mom.decode_text(value))
        except Exception:
            decoded_values.append("")
    assert "FederateServiceInvocationsAreBeingReportedViaMOM" in decoded_values

    # The reverse conflict is raised on a normal RTI service call when service
    # reporting is already enabled and the federate attempts to subscribe to the
    # service-invocation report stream.
    rti2 = _rti(InMemoryRTIEngine())
    fed2 = RecordingFederateAmbassador()
    rti2.connect(fed2, CallbackModel.HLA_EVOKED)
    rti2.create_federation_execution("mom-switch-conflict-v011b", "TargetRadarFOMmodule.xml")
    rti2.join_federation_execution("fed", "type", "mom-switch-conflict-v011b")
    rti2.backend.state.service_reporting = True
    report2 = rti2.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"
    )
    with pytest.raises(FederateServiceInvocationsAreBeingReportedViaMOM):
        rti2.subscribe_interaction_class(report2)


def test_mom_service_action_can_drive_time_management_service():
    _engine, (rti,), (fed,) = _joined("mom-service-action-v011")
    service = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAenableTimeConstrained"
    )
    rti.send_interaction(service, {}, b"enable-tc")
    _drain(rti)

    assert fed.last_callback("timeConstrainedEnabled") is not None
    assert rti.backend.state.time_constrained_enabled is True


def test_scheduled_save_waits_for_time_and_restore_reinstates_time_state():
    _engine, (r1, r2), (f1, f2) = _joined("scheduled-save-restore-v011", n=2)
    factory = r1.get_time_factory()
    r1.enable_time_constrained()
    r2.enable_time_constrained()
    _drain(r1, r2)

    r1.request_federation_save("SAVE-AT-5", factory.make_time(5.0))
    _drain(r1, r2)
    assert f1.last_callback("initiateFederateSave") is None
    assert f2.last_callback("initiateFederateSave") is None

    r1.time_advance_request_available(factory.make_time(5.0))
    r2.time_advance_request_available(factory.make_time(5.0))
    _drain(r1, r2)
    assert f1.last_callback("initiateFederateSave").args[0] == "SAVE-AT-5"
    assert f2.last_callback("initiateFederateSave").args[0] == "SAVE-AT-5"

    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_complete()
    _drain(r1, r2)
    assert f1.last_callback("federationSaved") is not None

    r1.time_advance_request_available(factory.make_time(8.0))
    r2.time_advance_request_available(factory.make_time(8.0))
    _drain(r1, r2)
    assert r1.query_logical_time() == factory.make_time(8.0)
    assert r2.query_logical_time() == factory.make_time(8.0)

    r1.request_federation_restore("SAVE-AT-5")
    _drain(r1, r2)
    r1.federate_restore_complete()
    r2.federate_restore_complete()
    _drain(r1, r2)
    assert r1.query_logical_time() == factory.make_time(5.0)
    assert r2.query_logical_time() == factory.make_time(5.0)


def test_restore_reinstates_saved_object_values_names_and_ownership_state():
    _engine, (owner, acquirer), (_owner_fed, _acquirer_fed) = _joined("restore-object-state-v011", n=2)
    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")

    owner.publish_object_class_attributes(cls, {attr})
    acquirer.publish_object_class_attributes(cls, {attr})
    obj = owner.register_object_instance(cls, "Restore-State-Object")
    owner.update_attribute_values(obj, {attr: b"saved-value"}, b"saved")
    _drain(owner, acquirer)

    owner.unconditional_attribute_ownership_divestiture(obj, {attr})
    acquirer.attribute_ownership_acquisition_if_available(obj, {attr})
    _drain(owner, acquirer)
    assert acquirer.is_attribute_owned_by_federate(obj, attr) is True

    owner.request_federation_save("SAVE-OBJECT-STATE")
    _drain(owner, acquirer)
    owner.federate_save_begun()
    acquirer.federate_save_begun()
    owner.federate_save_complete()
    acquirer.federate_save_complete()
    _drain(owner, acquirer)

    acquirer.unconditional_attribute_ownership_divestiture(obj, {attr})
    owner.attribute_ownership_acquisition_if_available(obj, {attr})
    _drain(owner, acquirer)
    assert owner.is_attribute_owned_by_federate(obj, attr) is True
    owner.update_attribute_values(obj, {attr: b"mutated-value"}, b"mutated")
    _drain(owner, acquirer)

    owner.request_federation_restore("SAVE-OBJECT-STATE")
    _drain(owner, acquirer)
    owner.federate_restore_complete()
    acquirer.federate_restore_complete()
    _drain(owner, acquirer)

    restored = owner.backend.state.federation.objects[obj]
    assert restored.name == "Restore-State-Object"
    assert owner.backend.state.federation.object_names["Restore-State-Object"] == obj
    assert restored.attributes[attr] == b"saved-value"
    assert restored.attribute_owners[attr] == acquirer.backend.state.handle
    assert acquirer.is_attribute_owned_by_federate(obj, attr) is True


def test_restore_reinstates_saved_federate_runtime_flags_and_lookahead_state():
    _engine, (r1, r2), (_f1, _f2) = _joined("restore-runtime-flags-v011", n=2)
    factory = r1.get_time_factory()

    r1.enable_time_regulation(factory.make_interval(2.0))
    r1.enable_asynchronous_delivery()
    r2.enable_time_constrained()
    _drain(r1, r2)

    r1.request_federation_save("SAVE-RUNTIME-FLAGS")
    _drain(r1, r2)
    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_complete()
    _drain(r1, r2)

    r1.modify_lookahead(factory.make_interval(5.0))
    r1.disable_asynchronous_delivery()
    r1.disable_time_regulation()
    r2.disable_time_constrained()
    assert r1.backend.state.lookahead == factory.make_interval(5.0)
    assert r1.backend.state.asynchronous_delivery_enabled is False
    assert r1.backend.state.time_regulation_enabled is False
    assert r2.backend.state.time_constrained_enabled is False

    r1.request_federation_restore("SAVE-RUNTIME-FLAGS")
    _drain(r1, r2)
    r1.federate_restore_complete()
    r2.federate_restore_complete()
    _drain(r1, r2)

    assert r1.backend.state.lookahead == factory.make_interval(2.0)
    assert r1.backend.state.asynchronous_delivery_enabled is True
    assert r1.backend.state.time_regulation_enabled is True
    assert r2.backend.state.time_constrained_enabled is True


def test_restore_reinstates_saved_federate_policy_reporting_and_conveyance_switches():
    _engine, (r1, r2), (_f1, _f2) = _joined("restore-switch-state-v011", n=2)

    r1.set_automatic_resign_directive(ResignAction.DELETE_OBJECTS)
    r1.enable_object_class_relevance_advisory_switch()
    r1.enable_attribute_relevance_advisory_switch()
    r1.enable_attribute_scope_advisory_switch()
    r1.enable_interaction_relevance_advisory_switch()

    adjust = r1.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetSwitches"
    )
    set_service_reporting = r1.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
    )
    set_exception_reporting = r1.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetExceptionReporting"
    )
    federate_param = r1.get_parameter_handle(adjust, "HLAfederate")
    convey_pf_param = r1.get_parameter_handle(adjust, "HLAconveyProducingFederate")
    convey_regions_param = r1.get_parameter_handle(adjust, "HLAconveyRegionDesignatorSets")
    service_reporting_fed = r1.get_parameter_handle(set_service_reporting, "HLAfederate")
    service_reporting_param = r1.get_parameter_handle(set_service_reporting, "HLAreportingState")
    exception_reporting_fed = r1.get_parameter_handle(set_exception_reporting, "HLAfederate")
    exception_reporting_param = r1.get_parameter_handle(set_exception_reporting, "HLAreportingState")
    r1.send_interaction(
        adjust,
        {
            federate_param: r1.backend.state.handle.encode(),
            convey_pf_param: hla_mom.encode_bool(False),
            convey_regions_param: hla_mom.encode_bool(True),
        },
        b"save-switches",
    )
    r1.send_interaction(
        set_service_reporting,
        {
            service_reporting_fed: r1.backend.state.handle.encode(),
            service_reporting_param: hla_mom.encode_bool(True),
        },
        b"save-service-reporting",
    )
    r1.send_interaction(
        set_exception_reporting,
        {
            exception_reporting_fed: r1.backend.state.handle.encode(),
            exception_reporting_param: hla_mom.encode_bool(False),
        },
        b"save-exception-reporting",
    )
    _drain(r1, r2)

    r1.request_federation_save("SAVE-SWITCH-STATE")
    _drain(r1, r2)
    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_complete()
    _drain(r1, r2)

    r1.set_automatic_resign_directive(ResignAction.NO_ACTION)
    r1.disable_object_class_relevance_advisory_switch()
    r1.disable_attribute_relevance_advisory_switch()
    r1.disable_attribute_scope_advisory_switch()
    r1.disable_interaction_relevance_advisory_switch()
    r1.send_interaction(
        adjust,
        {
            federate_param: r1.backend.state.handle.encode(),
            convey_pf_param: hla_mom.encode_bool(True),
            convey_regions_param: hla_mom.encode_bool(False),
        },
        b"mutate-switches",
    )
    r1.send_interaction(
        set_service_reporting,
        {
            service_reporting_fed: r1.backend.state.handle.encode(),
            service_reporting_param: hla_mom.encode_bool(False),
        },
        b"mutate-service-reporting",
    )
    r1.send_interaction(
        set_exception_reporting,
        {
            exception_reporting_fed: r1.backend.state.handle.encode(),
            exception_reporting_param: hla_mom.encode_bool(True),
        },
        b"mutate-exception-reporting",
    )
    _drain(r1, r2)

    r1.request_federation_restore("SAVE-SWITCH-STATE")
    _drain(r1, r2)
    r1.federate_restore_complete()
    r2.federate_restore_complete()
    _drain(r1, r2)

    assert r1.get_automatic_resign_directive() is ResignAction.DELETE_OBJECTS
    assert r1.backend.state.object_class_relevance_advisory is True
    assert r1.backend.state.attribute_relevance_advisory is True
    assert r1.backend.state.attribute_scope_advisory is True
    assert r1.backend.state.interaction_relevance_advisory is True
    assert r1.backend.state.convey_producing_federate is False
    assert r1.backend.state.convey_region_designator_sets is True
    assert r1.backend.state.service_reporting is True
    assert r1.backend.state.exception_reporting is False


def test_restore_reinstates_saved_attribute_and_interaction_order_overrides():
    _engine, (r1, r2), (_f1, _f2) = _joined("restore-order-overrides-v011", n=2)
    cls = r1.get_object_class_handle("HLAobjectRoot.Target")
    attr = r1.get_attribute_handle(cls, "Position")
    interaction = r1.get_interaction_class_handle("HLAinteractionRoot.TrackReport")

    r1.publish_object_class_attributes(cls, {attr})
    obj = r1.register_object_instance(cls, "Restore-Order-Overrides")
    _drain(r1, r2)

    r1.change_attribute_order_type(obj, {attr}, OrderType.TIMESTAMP)
    r1.change_interaction_order_type(interaction, OrderType.TIMESTAMP)
    assert r1.backend.state.attribute_order_overrides[(obj, attr)] is OrderType.TIMESTAMP
    assert r1.backend.state.interaction_order_overrides[interaction] is OrderType.TIMESTAMP

    r1.request_federation_save("SAVE-ORDER-OVERRIDES")
    _drain(r1, r2)
    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_complete()
    _drain(r1, r2)

    r1.change_attribute_order_type(obj, {attr}, OrderType.RECEIVE)
    r1.change_interaction_order_type(interaction, OrderType.RECEIVE)
    assert r1.backend.state.attribute_order_overrides[(obj, attr)] is OrderType.RECEIVE
    assert r1.backend.state.interaction_order_overrides[interaction] is OrderType.RECEIVE

    r1.request_federation_restore("SAVE-ORDER-OVERRIDES")
    _drain(r1, r2)
    r1.federate_restore_complete()
    r2.federate_restore_complete()
    _drain(r1, r2)

    assert r1.backend.state.attribute_order_overrides[(obj, attr)] is OrderType.TIMESTAMP
    assert r1.backend.state.interaction_order_overrides[interaction] is OrderType.TIMESTAMP


def test_restore_reinstates_saved_attribute_and_interaction_transportation_overrides():
    _engine, (r1, r2), (_f1, _f2) = _joined("restore-transport-overrides-v011", n=2)
    cls = r1.get_object_class_handle("HLAobjectRoot.Target")
    attr = r1.get_attribute_handle(cls, "Position")
    interaction = r1.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    best_effort = r1.backend.engine.transportation_best_effort

    r1.publish_object_class_attributes(cls, {attr})
    r1.publish_interaction_class(interaction)
    obj = r1.register_object_instance(cls, "Restore-Transport-Overrides")
    _drain(r1, r2)

    r1.request_attribute_transportation_type_change(obj, {attr}, best_effort)
    r1.request_interaction_transportation_type_change(interaction, best_effort)
    _drain(r1, r2)
    assert r1.backend.state.attribute_transportation_overrides[(obj, attr)] == best_effort
    assert r1.backend.state.interaction_transportation_overrides[interaction] == best_effort

    r1.request_federation_save("SAVE-TRANSPORT-OVERRIDES")
    _drain(r1, r2)
    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_complete()
    _drain(r1, r2)

    r1.backend.state.attribute_transportation_overrides.clear()
    r1.backend.state.interaction_transportation_overrides.clear()
    assert not r1.backend.state.attribute_transportation_overrides
    assert not r1.backend.state.interaction_transportation_overrides

    r1.request_federation_restore("SAVE-TRANSPORT-OVERRIDES")
    _drain(r1, r2)
    r1.federate_restore_complete()
    r2.federate_restore_complete()
    _drain(r1, r2)

    assert r1.backend.state.attribute_transportation_overrides[(obj, attr)] == best_effort
    assert r1.backend.state.interaction_transportation_overrides[interaction] == best_effort


def test_restore_treats_callback_enablement_as_runtime_policy_not_saved_state():
    _engine, (r1, r2), (_f1, _f2) = _joined("restore-callback-policy-v011", n=2)

    r1.disable_callbacks()
    assert r1.backend.state.callbacks_enabled is False

    r1.request_federation_save("SAVE-CALLBACK-POLICY")
    _drain(r1, r2)
    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_complete()
    _drain(r1, r2)

    r1.enable_callbacks()
    assert r1.backend.state.callbacks_enabled is True

    r1.request_federation_restore("SAVE-CALLBACK-POLICY")
    _drain(r1, r2)
    r1.federate_restore_complete()
    r2.federate_restore_complete()
    _drain(r1, r2)

    assert r1.backend.state.callbacks_enabled is True


def test_restore_discards_pre_restore_callback_queue_and_retraction_bookkeeping():
    _engine, (sender, receiver), (_sender_fed, _receiver_fed) = _joined("restore-transient-state-v011", n=2)
    factory = sender.get_time_factory()
    interaction = sender.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    track_id = sender.get_parameter_handle(interaction, "TrackId")

    receiver.disable_callbacks()
    receiver.backend.state.queue.append(CallbackEvent("sentinelCallback", (b"stale",)))
    sender.enable_time_regulation(factory.make_interval(1.0))
    receiver.enable_time_constrained()
    sender.publish_interaction_class(interaction)
    receiver.subscribe_interaction_class(interaction)
    _drain(sender, receiver)

    retraction = sender.send_interaction(interaction, {track_id: b"queued"}, b"queued", factory.make_time(5.0))
    assert retraction is not None
    assert receiver.backend.state.retraction_messages
    assert sender.backend.state.retractable_messages.get(retraction.handle) is True

    sender.request_federation_save("SAVE-TRANSIENT-STATE")
    _drain(sender, receiver)
    sender.federate_save_begun()
    receiver.federate_save_begun()
    sender.federate_save_complete()
    receiver.federate_save_complete()
    _drain(sender, receiver)

    sender.request_federation_restore("SAVE-TRANSIENT-STATE")
    _drain(sender, receiver)
    sender.federate_restore_complete()
    receiver.federate_restore_complete()
    _drain(sender, receiver)

    assert all(event.method_name != "sentinelCallback" for event in receiver.backend.state.queue)
    assert not receiver.backend.state.retraction_messages
    assert not receiver.backend.state.delivered_retraction_messages
    assert not sender.backend.state.retractable_messages


def test_ddm_region_filtering_applies_before_timestamp_order_delivery():
    _engine, (sender, receiver), (_sender_fed, receiver_fed) = _joined("ddm-tso-v011", n=2)
    factory = sender.get_time_factory()
    sender.enable_time_regulation(factory.make_interval(1.0))
    receiver.enable_time_constrained()
    _drain(sender, receiver)

    dim = sender.get_dimension_handle("HLAdefaultRoutingSpace")
    source_near = sender.create_region({dim})
    source_far = sender.create_region({dim})
    target_region = receiver.create_region({dim})
    sender.set_range_bounds(source_near, dim, RangeBounds(0, 10))
    sender.set_range_bounds(source_far, dim, RangeBounds(90, 100))
    receiver.set_range_bounds(target_region, dim, RangeBounds(5, 15))
    sender.commit_region_modifications({source_near, source_far})
    receiver.commit_region_modifications({target_region})

    interaction = sender.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    track_id = sender.get_parameter_handle(interaction, "TrackId")
    sender.publish_interaction_class(interaction)
    receiver.subscribe_interaction_class_with_regions(interaction, {target_region})

    sender.send_interaction_with_regions(interaction, {track_id: b"far"}, {source_far}, b"far", factory.make_time(2.0))
    sender.send_interaction_with_regions(interaction, {track_id: b"near"}, {source_near}, b"near", factory.make_time(3.0))
    _drain(sender, receiver)
    assert not receiver_fed.callbacks_named("receiveInteraction")

    sender.time_advance_request(factory.make_time(5.0))
    _drain(sender, receiver)
    receiver.next_message_request_available(factory.make_time(6.0))
    _drain(sender, receiver)

    received = receiver_fed.callbacks_named("receiveInteraction")
    assert len(received) == 1
    record = received[0]
    assert record.args[2] == b"near"
    assert record.args[5] == factory.make_time(3.0)
    assert source_near in record.args[-1].sent_regions


def test_galt_uses_pending_regulator_lbts_not_only_current_time():
    _engine, (a, b, c), (_afed, _bfed, _cfed) = _joined("distributed-galt-v011", n=3)
    factory = a.get_time_factory()

    a.enable_time_regulation(factory.make_interval(1.0))
    b.enable_time_regulation(factory.make_interval(5.0))
    a.enable_time_constrained()
    c.enable_time_constrained()
    _drain(a, b, c)

    assert c.query_galt().time == factory.make_time(1.0)
    a.time_advance_request(factory.make_time(10.0))
    _drain(a, b, c)

    assert a.backend.state.time_advancing is True
    assert c.query_galt().time == factory.make_time(5.0)


def test_core_time_and_sync_compliance_smoke_covers_late_join_sync_and_time_controls():
    engine = InMemoryRTIEngine()
    leader = _rti(engine)
    follower = _rti(engine)
    late = _rti(engine)
    leader_fed = RecordingFederateAmbassador()
    follower_fed = RecordingFederateAmbassador()
    late_fed = RecordingFederateAmbassador()

    leader.connect(leader_fed, CallbackModel.HLA_EVOKED)
    follower.connect(follower_fed, CallbackModel.HLA_EVOKED)
    late.connect(late_fed, CallbackModel.HLA_EVOKED)
    leader.create_federation_execution("core-time-sync-v011", "TargetRadarFOMmodule.xml")
    leader.join_federation_execution("leader", "leader-type", "core-time-sync-v011")
    follower.join_federation_execution("follower", "follower-type", "core-time-sync-v011")

    leader.register_federation_synchronization_point("ReadyToRun", b"startup")
    _drain(leader, follower)
    assert leader_fed.callbacks_named("announceSynchronizationPoint")
    assert follower_fed.callbacks_named("announceSynchronizationPoint")

    late.join_federation_execution("late", "late-type", "core-time-sync-v011")
    _drain(leader, follower, late)
    assert late_fed.callbacks_named("announceSynchronizationPoint")

    leader.synchronization_point_achieved("ReadyToRun")
    follower.synchronization_point_achieved("ReadyToRun")
    _drain(leader, follower, late)
    assert not leader_fed.callbacks_named("federationSynchronized")

    late.synchronization_point_achieved("ReadyToRun")
    _drain(leader, follower, late)
    assert leader_fed.callbacks_named("federationSynchronized")
    assert follower_fed.callbacks_named("federationSynchronized")
    assert late_fed.callbacks_named("federationSynchronized")

    factory = leader.get_time_factory()
    leader.enable_time_regulation(factory.make_interval(1.0))
    follower.enable_time_constrained()
    late.enable_time_constrained()
    _drain(leader, follower, late)
    assert leader.query_logical_time() == factory.make_time(0.0)
    assert leader.query_lookahead() == factory.make_interval(1.0)

    leader.modify_lookahead(factory.make_interval(2.0))
    assert leader.query_lookahead() == factory.make_interval(2.0)

    leader.time_advance_request(factory.make_time(4.0))
    follower.time_advance_request_available(factory.make_time(4.0))
    late.time_advance_request_available(factory.make_time(4.0))
    _drain(leader, follower, late)
    assert leader.query_logical_time() == factory.make_time(4.0)
    assert follower.query_logical_time() == factory.make_time(4.0)
    assert late.query_logical_time() == factory.make_time(4.0)

    leader.disable_time_regulation()
    follower.disable_time_constrained()
    late.disable_time_constrained()
    leader.enable_asynchronous_delivery()
    leader.disable_asynchronous_delivery()
    assert leader.backend.state.time_regulation_enabled is False
    assert follower.backend.state.time_constrained_enabled is False
    assert late.backend.state.time_constrained_enabled is False
    assert leader.backend.state.asynchronous_delivery_enabled is False

    late.resign_federation_execution(ResignAction.NO_ACTION)
    follower.resign_federation_execution(ResignAction.NO_ACTION)
    leader.resign_federation_execution(ResignAction.NO_ACTION)
    leader.destroy_federation_execution("core-time-sync-v011")


def test_core_negotiated_ownership_compliance_smoke_covers_offer_confirm_and_release_branches():
    engine = InMemoryRTIEngine()
    owner = _rti(engine)
    acquirer = _rti(engine)
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    negotiated_config = NegotiatedOwnershipScenarioConfig(
        federation_name="core-negotiated-ownership-v011",
        fom_modules=("TargetRadarFOMmodule.xml",),
        logical_time_implementation_name="HLAfloat64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="Participant",
        object_class_name="HLAobjectRoot.Target",
        attribute_name="Position",
        object_instance_name="Negotiated-1",
        assumption_tag=b"assume-offer",
        request_tag=b"acquire-request",
        cancel_tag=b"reacquire-request",
    )

    negotiated_summary = run_negotiated_attribute_ownership_scenario(
        owner,
        acquirer,
        config=negotiated_config,
        owner_federate=owner_fed,
        acquirer_federate=acquirer_fed,
    )
    assert negotiated_summary["assumption"].args[2] == b"assume-offer"
    assert negotiated_summary["release"].args[2] == b"reacquire-request"
    assert negotiated_summary["cancellation"].args[0] == negotiated_summary["release_acquirer_object_instance"]
    assert negotiated_summary["informed"].args[1] == negotiated_summary["owner_attribute"]

    owner2 = _rti(InMemoryRTIEngine())
    acquirer2 = _rti(owner2.backend.engine)
    owner2_fed = RecordingFederateAmbassador()
    acquirer2_fed = RecordingFederateAmbassador()
    release_config = ReleaseRequestOwnershipScenarioConfig(
        federation_name="core-release-request-v011",
        fom_modules=("TargetRadarFOMmodule.xml",),
        logical_time_implementation_name="HLAfloat64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="Participant",
        object_class_name="HLAobjectRoot.Target",
        attribute_name="Position",
        object_instance_name="Release-1",
        request_tag=b"acquire-request",
        confirm_tag=b"confirm-tag",
        owner_action="ifwanted",
    )

    release_summary = run_release_request_ownership_scenario(
        owner2,
        acquirer2,
        config=release_config,
        owner_federate=owner2_fed,
        acquirer_federate=acquirer2_fed,
    )
    assert release_summary["owner_action"] == "ifwanted"
    assert release_summary["divested"] == {release_summary["owner_attribute"]}
    assert release_summary["acquired"].args[2] == b""

    owner2.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer2.resign_federation_execution(ResignAction.NO_ACTION)
    owner2.destroy_federation_execution("core-release-request-v011")

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    acquirer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("core-negotiated-ownership-v011")
