
from hla.backends.common import RecordingFederateAmbassador
from hla.backends.python1516e import InMemoryRTIEngine, rti_ambassador
from hla.rti1516e.enums import (
    CallbackModel,
    OrderType,
)
from hla.rti1516e.exceptions import (
    CallNotAllowedFromWithinCallback,
)
from hla.rti1516e.time import HLAfloat64TimeFactory


def drain(*rtis):
    for _ in range(20):
        for rti in rtis:
            rti.evoke_multiple_callbacks(0.0, 0.0)


def joined_pair(name="extended-fed"):
    engine = InMemoryRTIEngine()
    r1 = rti_ambassador(engine=engine)
    r2 = rti_ambassador(engine=engine)
    f1 = RecordingFederateAmbassador()
    f2 = RecordingFederateAmbassador()
    r1.connect(f1, CallbackModel.HLA_EVOKED)
    r2.connect(f2, CallbackModel.HLA_EVOKED)
    r1.create_federation_execution(name, "TargetRadarFOMmodule.xml")
    h1 = r1.join_federation_execution("alpha", "type-a", name)
    h2 = r2.join_federation_execution("bravo", "type-b", name)
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
            lambda: self.rti.enable_time_regulation(factory.make_interval(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.time_advance_request(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.time_advance_request_available(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.next_message_request(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.next_message_request_available(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.flush_queue_request(factory.make_time(1.0)),
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
        self._capture(CallNotAllowedFromWithinCallback, self.rti.enable_time_constrained)
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.time_advance_request(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.time_advance_request_available(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.next_message_request(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.next_message_request_available(factory.make_time(1.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.flush_queue_request(factory.make_time(1.0)),
        )


class _ImmediateTimeAdvanceGrantAmbassador(RecordingFederateAmbassador):
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

    def timeAdvanceGrant(self, time):
        super().timeAdvanceGrant(time)
        factory = HLAfloat64TimeFactory()
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.time_advance_request(factory.make_time(6.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.time_advance_request_available(factory.make_time(6.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.next_message_request(factory.make_time(6.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.next_message_request_available(factory.make_time(6.0)),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.flush_queue_request(factory.make_time(6.0)),
        )


class _ImmediateAsyncDeliveryAmbassador(RecordingFederateAmbassador):
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

    def synchronizationPointRegistrationSucceeded(self, label):
        super().synchronizationPointRegistrationSucceeded(label)
        self._capture(CallNotAllowedFromWithinCallback, self.rti.enable_asynchronous_delivery)
        self._capture(CallNotAllowedFromWithinCallback, self.rti.disable_asynchronous_delivery)


class _ImmediateOrderTypeAmbassador(RecordingFederateAmbassador):
    def __init__(self, rti, obj=None, attr=None, interaction=None):
        super().__init__()
        self.rti = rti
        self.obj = obj
        self.attr = attr
        self.interaction = interaction
        self.captured: list[type[BaseException]] = []

    def _capture(self, exc_type, fn):
        try:
            fn()
        except exc_type:
            self.captured.append(exc_type)
        else:  # pragma: no cover - defensive
            raise AssertionError(f"expected {exc_type.__name__}")

    def synchronizationPointRegistrationSucceeded(self, label):
        super().synchronizationPointRegistrationSucceeded(label)
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.change_attribute_order_type(self.obj, {self.attr}, OrderType.TIMESTAMP),
        )
        self._capture(
            CallNotAllowedFromWithinCallback,
            lambda: self.rti.change_interaction_order_type(self.interaction, OrderType.TIMESTAMP),
        )
