from __future__ import annotations

from hla.rti1516e import mom as hla_mom
from hla.backends.common import RecordingFederateAmbassador
from hla.rti1516e.enums import CallbackModel, ResignAction
from hla.backends.inmemory import InMemoryRTIEngine, PythonRTIConfig, rti_ambassador


def _drain(*rtis, limit: int = 25) -> None:
    for _ in range(limit):
        for rti in rtis:
            rti.evokeMultipleCallbacks(0.0, 0.0)


def _build_two_federates(name: str):
    engine = InMemoryRTIEngine()
    reporter = rti_ambassador(engine=engine, config=PythonRTIConfig())
    observer = rti_ambassador(engine=engine, config=PythonRTIConfig())
    reporter_fed = RecordingFederateAmbassador()
    observer_fed = RecordingFederateAmbassador()
    reporter.connect(reporter_fed, CallbackModel.HLA_EVOKED)
    observer.connect(observer_fed, CallbackModel.HLA_EVOKED)
    reporter.createFederationExecution(name, "TargetRadarFOMmodule.xml")
    reporter.joinFederationExecution("reporter", "reporter-type", name)
    observer.joinFederationExecution("observer", "observer-type", name)
    _drain(reporter, observer)
    return reporter, observer, reporter_fed, observer_fed


def _cleanup(name: str, *rtis) -> None:
    for rti in rtis:
        try:
            rti.resignFederationExecution(ResignAction.NO_ACTION)
        except Exception:
            pass
    try:
        rtis[0].destroyFederationExecution(name)
    except Exception:
        pass


def test_mom_observer_slice_reconstructs_federate_object_discovery_and_reflection():
    name = "mom-observer-object-v013"
    reporter, observer, _reporter_fed, observer_fed = _build_two_federates(name)
    try:
        cls = observer.getObjectClassHandle("HLAobjectRoot.HLAmanager.HLAfederate")
        attr = observer.getAttributeHandle(cls, "HLAfederateName")
        observer.subscribeObjectClassAttributes(cls, {attr})
        _drain(reporter, observer)

        discoveries = observer_fed.callbacks_named("discoverObjectInstance")
        assert any("HLAmanager.HLAfederate" in rec.args[2] for rec in discoveries)

        observer.requestAttributeValueUpdate(cls, {attr}, b"mom-observer-snapshot")
        _drain(reporter, observer)
        reflections = observer_fed.callbacks_named("reflectAttributeValues")
        assert any(attr in rec.args[1] and rec.args[2] == b"mom-observer-snapshot" for rec in reflections)
    finally:
        _cleanup(name, reporter, observer)


def test_mom_observer_slice_reconstructs_mim_request_report_exchange():
    name = "mom-observer-mim-v013"
    reporter, observer, _reporter_fed, observer_fed = _build_two_federates(name)
    try:
        report = observer.getInteractionClassHandle(
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata"
        )
        request = reporter.getInteractionClassHandle(
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata"
        )
        data_param = observer.getParameterHandle(report, "HLAMIMdata")
        observer.subscribeInteractionClass(report)
        reporter.sendInteraction(request, {}, b"mom-observer-request-mim")
        _drain(reporter, observer)

        received = [rec for rec in observer_fed.callbacks_named("receiveInteraction") if rec.args[0] == report]
        assert received
        assert data_param in received[-1].args[1]
        assert b"HLAstandardMIM" in received[-1].args[1][data_param] or b"HLAmanager" in received[-1].args[1][data_param]
    finally:
        _cleanup(name, reporter, observer)


def test_mom_observer_slice_reconstructs_service_invocation_reporting():
    name = "mom-observer-service-report-v013"
    reporter, observer, _reporter_fed, observer_fed = _build_two_federates(name)
    try:
        report = observer.getInteractionClassHandle(
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"
        )
        adjust = reporter.getInteractionClassHandle(
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting"
        )
        federate_param = reporter.getParameterHandle(adjust, "HLAfederate")
        state_param = reporter.getParameterHandle(adjust, "HLAreportingState")
        service_param = observer.getParameterHandle(report, "HLAservice")
        observer.subscribeInteractionClass(report)
        reporter.sendInteraction(
            adjust,
            {
                federate_param: reporter.backend.state.handle.encode(),
                state_param: hla_mom.encode_bool(True),
            },
            b"mom-observer-enable-service-reporting",
        )
        _drain(reporter, observer)
        reporter.queryLogicalTime()
        _drain(reporter, observer)

        received = [rec for rec in observer_fed.callbacks_named("receiveInteraction") if rec.args[0] == report]
        assert received
        assert any(service_param in rec.args[1] for rec in received)
    finally:
        _cleanup(name, reporter, observer)
