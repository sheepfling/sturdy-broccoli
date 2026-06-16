from __future__ import annotations

import pytest

from hla.rti1516e import mom as hla_mom
from hla.rti1516e.ambassadors import RecordingFederateAmbassador
from hla.rti1516e.backends.python_rti import InMemoryRTIEngine, PythonRTIConfig
from hla.rti1516e.enums import CallbackModel
from hla.rti1516e.exceptions import InteractionClassNotPublished, InteractionParameterNotDefined
from hla.rti1516e.rti import create_rti_ambassador


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


def test_strict_mom_rejects_federate_sent_report_interaction():
    _engine, rti, fed = _joined("mom-sent-report-v012", config=PythonRTIConfig(strict_mom_parameter_decoding=True))
    report_name = "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"
    report = rti.get_interaction_class_handle(report_name)

    with pytest.raises(InteractionClassNotPublished):
        rti.send_interaction(report, {}, b"federate-should-not-send-report")
    _drain(rti)

    values = _decoded_exception_values(fed)
    assert "MOMInteractionNotReceivableByRTI" in values
    assert report_name in values
