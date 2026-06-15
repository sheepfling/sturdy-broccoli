
from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010_rti_python import InMemoryRTIEngine, rti_ambassador
from hla2010.enums import (
    CallbackModel,
)
from hla2010.exceptions import (
    CallNotAllowedFromWithinCallback,
)
from hla2010.time import HLAfloat64TimeFactory


def drain(*rtis):
    for _ in range(20):
        for rti in rtis:
            rti.evokeMultipleCallbacks(0.0, 0.0)


def joined_pair(name="extended-fed"):
    engine = InMemoryRTIEngine()
    r1 = rti_ambassador(engine=engine)
    r2 = rti_ambassador(engine=engine)
    f1 = RecordingFederateAmbassador()
    f2 = RecordingFederateAmbassador()
    r1.connect(f1, CallbackModel.HLA_EVOKED)
    r2.connect(f2, CallbackModel.HLA_EVOKED)
    r1.createFederationExecution(name, "TargetRadarFOMmodule.xml")
    h1 = r1.joinFederationExecution("alpha", "type-a", name)
    h2 = r2.joinFederationExecution("bravo", "type-b", name)
    return engine, r1, r2, f1, f2, h1, h2


class _ImmediateRegulationPendingAmbassador(RecordingFederateAmbassador):
    def __init__(self, rti):
        super().__init__()
        self.rti = rti
        self.captured: list[type[BaseException]] = []

    def _capture(self, exc_type, fn):
        try:
            fn()
        except exc_type:
            self.captured.append(exc_type)
        else:  # pragma: no cover - defensive
            raise AssertionError(f"expected {exc_type.__name__}")

    def timeRegulationEnabled(self, time):
        super().timeRegulationEnabled(time)
        factory = HLAfloat64TimeFactory()
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.enableTimeRegulation(factory.make_interval(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.timeAdvanceRequest(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.timeAdvanceRequestAvailable(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.nextMessageRequest(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.nextMessageRequestAvailable(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.flushQueueRequest(factory.make_time(1.0)),
        )


class _ImmediateConstrainedPendingAmbassador(RecordingFederateAmbassador):
    def __init__(self, rti):
        super().__init__()
        self.rti = rti
        self.captured: list[type[BaseException]] = []

    def _capture(self, exc_type, fn):
        try:
            fn()
        except exc_type:
            self.captured.append(exc_type)
        else:  # pragma: no cover - defensive
            raise AssertionError(f"expected {exc_type.__name__}")

    def timeConstrainedEnabled(self, time):
        super().timeConstrainedEnabled(time)
        factory = HLAfloat64TimeFactory()
        self._capture(CallNotAllowedFromWithinCallback, self.rti.enableTimeConstrained)
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.timeAdvanceRequest(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.timeAdvanceRequestAvailable(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.nextMessageRequest(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.nextMessageRequestAvailable(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.flushQueueRequest(factory.make_time(1.0)),
        )
