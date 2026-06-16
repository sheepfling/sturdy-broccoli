from __future__ import annotations

import json
from pathlib import Path

import pytest

from hla.rti1516e import mom as hla_mom
from hla.rti1516e.ambassadors import RecordingFederateAmbassador
from hla.rti1516e.backends.python_rti import InMemoryRTIEngine, PythonRTIConfig
from hla.rti1516e.enums import CallbackModel, OrderType
from hla.rti1516e.exceptions import FederateServiceInvocationsAreBeingReportedViaMOM
from hla.rti1516e.rti import create_rti_ambassador
from hla.rti1516e.types import RangeBounds


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

    report_file = Path(rti.backend.state.service_report_file)
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
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetSwitches"
    )
    service_reporting_param = rti.get_parameter_handle(adjust, "HLAserviceReporting")

    rti.subscribe_interaction_class(report)
    rti.send_interaction(adjust, {service_reporting_param: hla_mom.encode_bool(True)}, b"bad-switch")
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

    r1.federate_save_begun(); r2.federate_save_begun()
    r1.federate_save_complete(); r2.federate_save_complete()
    _drain(r1, r2)
    assert f1.last_callback("federationSaved") is not None

    r1.time_advance_request_available(factory.make_time(8.0))
    r2.time_advance_request_available(factory.make_time(8.0))
    _drain(r1, r2)
    assert r1.query_logical_time() == factory.make_time(8.0)
    assert r2.query_logical_time() == factory.make_time(8.0)

    r1.request_federation_restore("SAVE-AT-5")
    _drain(r1, r2)
    r1.federate_restore_complete(); r2.federate_restore_complete()
    _drain(r1, r2)
    assert r1.query_logical_time() == factory.make_time(5.0)
    assert r2.query_logical_time() == factory.make_time(5.0)


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
