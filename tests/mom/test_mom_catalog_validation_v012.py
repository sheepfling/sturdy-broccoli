from __future__ import annotations

import pytest

import hla.fom.mom as hla_mom
from hla.backends.common import RecordingFederateAmbassador
from hla.backends.inmemory import InMemoryRTIEngine, PythonRTIConfig
from hla.backends.inmemory.state import MOM_FEDERATE_CLASS, MOM_FEDERATION_CLASS, RTI_FEDERATE_HANDLE
from hla.rti1516e.enums import CallbackModel, OrderType
from hla.rti1516e.exceptions import InteractionClassNotPublished, InteractionParameterNotDefined, InvalidRegionContext
from hla.runtime.factory import create_rti_ambassador


def _joined(name: str, *, config: PythonRTIConfig | None = None):
    engine = InMemoryRTIEngine()
    rti = create_rti_ambassador("python", engine=engine, config=config)
    fed = RecordingFederateAmbassador()
    rti.connect(fed, CallbackModel.HLA_EVOKED)
    rti.create_federation_execution(name, "TargetRadarFOMmodule.xml")
    rti.join_federation_execution("fed", "type", name)
    return engine, rti, fed


def _drain(rti) -> None:
    for _ in range(20):
        rti.evoke_multiple_callbacks(0.0, 0.0)


def _decoded_exception_values(fed: RecordingFederateAmbassador):
    values: list[str] = []
    for rec in fed.callbacks_named("receiveInteraction"):
        for payload in rec.args[1].values():
            try:
                values.append(hla_mom.decode_text(payload))
            except Exception:
                pass
    return values


def test_mom_catalog_is_derived_from_standard_mim_and_exposes_validation_matrix():
    _engine, rti, _fed = _joined("mom-catalog-v012")
    federation = rti.backend.state.federation
    model = rti.backend._mom_exposure_model(federation)

    service_reporting = "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
    set_switches = "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetSwitches"
    mim_request = "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata"

    assert service_reporting in model.interaction_classes
    assert model.interaction_rule(service_reporting).parameter_datatypes["HLAreportingState"] == "HLAboolean"
    assert "HLAserviceReporting" not in model.interaction_rule(set_switches).parameters
    assert model.interaction_rule(set_switches).at_least_one_of == (
        "HLAconveyRegionDesignatorSets",
        "HLAconveyProducingFederate",
    )
    assert model.report_for_request(mim_request).endswith("HLAreportMIMdata")

    matrix = rti.backend.current_mom_summary()["mom_interaction_matrix"]
    assert matrix[service_reporting]["rti_direction"] == "rti-receives"
    assert matrix["HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"]["rti_direction"] == "rti-sends"


def test_mom_report_payload_uses_exact_mim_catalog_parameters():
    _engine, rti, fed = _joined("mom-report-catalog-v012")
    report_name = "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata"
    request_name = "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata"
    report = rti.get_interaction_class_handle(report_name)
    request = rti.get_interaction_class_handle(request_name)
    expected_names = rti.backend._mom_exposure_model(rti.backend.state.federation).parameters_for(report_name)

    rti.subscribe_interaction_class(report)
    rti.send_interaction(request, {}, b"request-mim")
    _drain(rti)

    received = [rec for rec in fed.callbacks_named("receiveInteraction") if rec.args[0] == report]
    assert received
    interaction_def = rti.backend.engine.get_or_create_interaction_class(report_name)
    actual_names = tuple(interaction_def.parameter_names[handle] for handle in received[-1].args[1])
    assert actual_names == expected_names
    assert actual_names == ("HLAMIMdata",)
    assert b"HLAstandardMIM" in next(iter(received[-1].args[1].values())) or b"HLAmanager" in next(iter(received[-1].args[1].values()))


def test_mom_receive_path_ignores_added_nonstandard_parameters_in_non_strict_mode():
    _engine, rti, fed = _joined("mom-extra-param-ignored-v012")
    service_reporting = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
    )
    sr_fed = rti.get_parameter_handle(service_reporting, "HLAfederate")
    sr_state = rti.get_parameter_handle(service_reporting, "HLAreportingState")
    extra = rti.backend.engine.get_or_create_parameter(service_reporting, "HLAignoredByRTI")
    mom_exception = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportMOMexception"
    )

    rti.subscribe_interaction_class(mom_exception)
    fed.clear()

    rti.send_interaction(
        service_reporting,
        {
            sr_fed: rti.backend.state.handle.encode(),
            sr_state: hla_mom.encode_bool(True),
            extra: b"unexpected-but-ignored",
        },
        b"extra-param",
    )
    _drain(rti)

    assert rti.backend.state.service_reporting is True
    assert not [rec for rec in fed.callbacks_named("receiveInteraction") if rec.args[0] == mom_exception]


def test_strict_mom_missing_required_parameter_reports_and_raises():
    _engine, rti, fed = _joined("mom-missing-param-v012", config=PythonRTIConfig(strict_mom_parameter_decoding=True))
    adjust = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetTiming"
    )
    federate_param = rti.get_parameter_handle(adjust, "HLAfederate")

    with pytest.raises(InteractionParameterNotDefined):
        rti.send_interaction(adjust, {federate_param: rti.backend.state.handle.encode()}, b"missing-report-period")
    _drain(rti)

    values = _decoded_exception_values(fed)
    assert "MissingMOMParameter" in values
    assert "HLAreportPeriod" in values


def test_strict_mom_rejects_invalid_boolean_payload_and_accepts_valid_service_reporting_adjust():
    _engine, rti, fed = _joined("mom-bool-param-v012", config=PythonRTIConfig(strict_mom_parameter_decoding=True))
    service_reporting = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
    )
    exception_reporting = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetExceptionReporting"
    )
    sr_fed = rti.get_parameter_handle(service_reporting, "HLAfederate")
    sr_state = rti.get_parameter_handle(service_reporting, "HLAreportingState")
    er_fed = rti.get_parameter_handle(exception_reporting, "HLAfederate")
    er_state = rti.get_parameter_handle(exception_reporting, "HLAreportingState")

    rti.send_interaction(
        service_reporting,
        {sr_fed: rti.backend.state.handle.encode(), sr_state: hla_mom.encode_bool(True)},
        b"enable-service-reporting",
    )
    assert rti.backend.state.service_reporting is True

    before_exception_reporting = rti.backend.state.exception_reporting
    with pytest.raises(InteractionParameterNotDefined):
        rti.send_interaction(
            exception_reporting,
            {er_fed: rti.backend.state.handle.encode(), er_state: b"not-a-boolean"},
            b"bad-bool",
        )
    _drain(rti)

    assert rti.backend.state.exception_reporting is before_exception_reporting
    values = _decoded_exception_values(fed)
    assert "InvalidMOMParameterEncoding" in values
    assert "HLAreportingState" in values


def test_rejected_mom_adjustment_emits_exception_but_not_service_invocation_report():
    _engine, rti, fed = _joined("mom-no-positive-report-on-reject-v012", config=PythonRTIConfig(strict_mom_parameter_decoding=True))
    service_reporting = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
    )
    exception_reporting = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetExceptionReporting"
    )
    service_report = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"
    )
    mom_exception = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportMOMexception"
    )
    sr_fed = rti.get_parameter_handle(service_reporting, "HLAfederate")
    sr_state = rti.get_parameter_handle(service_reporting, "HLAreportingState")
    er_fed = rti.get_parameter_handle(exception_reporting, "HLAfederate")
    er_state = rti.get_parameter_handle(exception_reporting, "HLAreportingState")

    rti.subscribe_interaction_class(service_report)
    rti.subscribe_interaction_class(mom_exception)
    rti.send_interaction(
        service_reporting,
        {sr_fed: rti.backend.state.handle.encode(), sr_state: hla_mom.encode_bool(True)},
        b"enable-service-reporting",
    )
    _drain(rti)

    fed.clear()
    with pytest.raises(InteractionParameterNotDefined):
        rti.send_interaction(
            exception_reporting,
            {er_fed: rti.backend.state.handle.encode(), er_state: b"not-a-boolean"},
            b"bad-bool",
        )
    _drain(rti)

    assert [rec for rec in fed.callbacks_named("receiveInteraction") if rec.args[0] == mom_exception]
    assert not [rec for rec in fed.callbacks_named("receiveInteraction") if rec.args[0] == service_report]


def test_strict_mom_rejects_federate_sent_report_interaction():
    _engine, rti, fed = _joined("mom-sent-report-v012", config=PythonRTIConfig(strict_mom_parameter_decoding=True))
    report_name = "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"
    report = rti.get_interaction_class_handle(report_name)
    mom_exception = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportMOMexception"
    )
    rti.subscribe_interaction_class(report)
    rti.subscribe_interaction_class(mom_exception)

    with pytest.raises(InteractionClassNotPublished):
        rti.send_interaction(report, {}, b"federate-should-not-send-report")
    _drain(rti)

    values = _decoded_exception_values(fed)
    assert "MOMInteractionNotReceivableByRTI" in values
    assert report_name in values
    assert [rec for rec in fed.callbacks_named("receiveInteraction") if rec.args[0] == mom_exception]
    assert not [rec for rec in fed.callbacks_named("receiveInteraction") if rec.args[0] == report]


def test_rejected_mom_report_request_does_not_emit_positive_mim_report():
    _engine, rti, fed = _joined("mom-no-positive-mim-report-on-reject-v012", config=PythonRTIConfig(strict_mom_parameter_decoding=True))
    adjust = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetTiming"
    )
    federate_param = rti.get_parameter_handle(adjust, "HLAfederate")
    mim_report = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata"
    )
    mom_exception = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportMOMexception"
    )
    rti.subscribe_interaction_class(mim_report)
    rti.subscribe_interaction_class(mom_exception)

    with pytest.raises(InteractionParameterNotDefined):
        rti.send_interaction(adjust, {federate_param: rti.backend.state.handle.encode()}, b"missing-report-period")
    _drain(rti)

    assert [rec for rec in fed.callbacks_named("receiveInteraction") if rec.args[0] == mom_exception]
    assert not [rec for rec in fed.callbacks_named("receiveInteraction") if rec.args[0] == mim_report]


def test_mom_internal_object_instances_remain_rti_owned_without_non_rti_attribute_owners():
    _engine, rti, _fed = _joined("mom-rti-owned-v012")
    federation = rti.backend.state.federation
    assert federation is not None

    federate_class = rti.get_object_class_handle(MOM_FEDERATE_CLASS)
    federation_class = rti.get_object_class_handle(MOM_FEDERATION_CLASS)
    mom_instances = [
        instance
        for instance in federation.objects.values()
        if instance.class_handle in {federate_class, federation_class}
    ]

    assert mom_instances
    assert any(instance.class_handle == federate_class for instance in mom_instances)
    assert any(instance.class_handle == federation_class for instance in mom_instances)
    for instance in mom_instances:
        assert instance.owner == RTI_FEDERATE_HANDLE
        assert set(instance.attribute_owners.values()) <= {RTI_FEDERATE_HANDLE}


def test_mom_internal_traffic_uses_receive_order_reliable_transport_and_no_time_metadata():
    _engine, rti, fed = _joined("mom-ro-transport-v012")
    cls = rti.get_object_class_handle(MOM_FEDERATE_CLASS)
    attr = rti.get_attribute_handle(cls, "HLAfederateName")
    report_name = "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata"
    request_name = "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata"
    report = rti.get_interaction_class_handle(report_name)
    request = rti.get_interaction_class_handle(request_name)

    rti.subscribe_object_class_attributes(cls, {attr})
    rti.subscribe_interaction_class(report)
    _drain(rti)
    fed.clear()

    rti.request_attribute_value_update(cls, {attr}, b"mom-ro-refresh")
    rti.send_interaction(request, {}, b"mom-ro-request")
    _drain(rti)

    reflections = fed.callbacks_named("reflectAttributeValues")
    assert reflections
    reflection = reflections[-1]
    assert reflection.args[2] == b"mom-ro-refresh"
    assert reflection.args[3] is OrderType.RECEIVE
    assert reflection.args[4] == rti.backend.engine.transportation_reliable
    assert len(reflection.args) == 6

    reports = [rec for rec in fed.callbacks_named("receiveInteraction") if rec.args[0] == report]
    assert reports
    received = reports[-1]
    assert received.args[2] == b"MOM"
    assert received.args[3] is OrderType.RECEIVE
    assert received.args[4] == rti.backend.engine.transportation_reliable
    assert len(received.args) == 6


def test_mom_runtime_uses_no_hidden_rti_side_subscriptions():
    _engine, rti, _fed = _joined("mom-no-hidden-subscriptions-v012")
    federation = rti.backend.state.federation
    assert federation is not None

    assert len(federation.federates) == 1
    joined = next(iter(federation.federates.values()))
    assert joined is rti.backend.state
    assert joined.subscribed_objects == {}
    assert joined.subscribed_interactions == set()

    assert joined.mom_federate_object is not None
    assert any(instance.owner == RTI_FEDERATE_HANDLE for instance in federation.objects.values())


def test_mom_runtime_does_not_join_as_time_managed_federate():
    _engine, rti, _fed = _joined("mom-no-time-managed-rti-v012")
    federation = rti.backend.state.federation
    assert federation is not None

    assert RTI_FEDERATE_HANDLE not in federation.federates
    assert len(federation.federates) == 1
    joined = next(iter(federation.federates.values()))
    assert joined.handle != RTI_FEDERATE_HANDLE
    assert joined.connected is True
    assert joined.federation is federation


def test_mom_classes_reject_ddm_region_services():
    _engine, rti, _fed = _joined("mom-ddm-reject-v012")
    dim = rti.get_dimension_handle("HLAdefaultRoutingSpace")
    region = rti.create_region({dim})
    federate_cls = rti.get_object_class_handle(MOM_FEDERATE_CLASS)
    federate_attr = rti.get_attribute_handle(federate_cls, "HLAfederateName")
    report = rti.get_interaction_class_handle(
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata"
    )

    with pytest.raises(InvalidRegionContext):
        rti.subscribe_object_class_attributes_with_regions(
            federate_cls,
            [{"attributes": {federate_attr}, "regions": {region}}],
        )
    with pytest.raises(InvalidRegionContext):
        rti.subscribe_interaction_class_with_regions(report, {region})


def test_mom_runtime_applies_standard_rti_characteristics_as_one_coherent_contract():
    _engine, rti, fed = _joined("mom-rti-characteristics-v012")
    federation = rti.backend.state.federation
    assert federation is not None

    assert RTI_FEDERATE_HANDLE not in federation.federates
    assert len(federation.federates) == 1
    joined = next(iter(federation.federates.values()))
    assert joined is rti.backend.state
    assert joined.subscribed_objects == {}
    assert joined.subscribed_interactions == set()

    federate_class = rti.get_object_class_handle(MOM_FEDERATE_CLASS)
    federate_attr = rti.get_attribute_handle(federate_class, "HLAfederateName")
    request_name = "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata"
    report_name = "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata"
    request = rti.get_interaction_class_handle(request_name)
    report = rti.get_interaction_class_handle(report_name)
    dim = rti.get_dimension_handle("HLAdefaultRoutingSpace")
    region = rti.create_region({dim})

    rti.subscribe_object_class_attributes(federate_class, {federate_attr})
    rti.subscribe_interaction_class(report)
    _drain(rti)
    fed.clear()

    rti.request_attribute_value_update(federate_class, {federate_attr}, b"mom-rti-refresh")
    rti.send_interaction(request, {}, b"mom-rti-request")
    _drain(rti)

    reflection = fed.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection.args[3] is OrderType.RECEIVE
    assert reflection.args[4] == rti.backend.engine.transportation_reliable
    assert len(reflection.args) == 6

    reports = [rec for rec in fed.callbacks_named("receiveInteraction") if rec.args[0] == report]
    assert reports
    received = reports[-1]
    assert received.args[3] is OrderType.RECEIVE
    assert received.args[4] == rti.backend.engine.transportation_reliable
    assert len(received.args) == 6

    with pytest.raises(InvalidRegionContext):
        rti.subscribe_object_class_attributes_with_regions(
            federate_class,
            [{"attributes": {federate_attr}, "regions": {region}}],
        )
    with pytest.raises(InvalidRegionContext):
        rti.subscribe_interaction_class_with_regions(report, {region})
