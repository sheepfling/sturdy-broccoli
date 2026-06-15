"""Minimal publisher/subscriber HLA smoke scenario."""
from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from typing import Any, Callable, Iterable, Mapping, Protocol

from hla2010.enums import CallbackModel, OrderType, ResignAction, TransportationType
from hla2010.exceptions import FederatesCurrentlyJoined, FederationExecutionAlreadyExists, FederationExecutionDoesNotExist, RTIexception
from hla2010.handles import AttributeHandle, InteractionClassHandle, ObjectClassHandle, ObjectInstanceHandle, ParameterHandle
from hla2010.spec import FederateAmbassadorSpec

DEMO_OBJECT_CLASS = "HLAobjectRoot.DemoObject"
DEMO_INTERACTION_CLASS = "HLAinteractionRoot.DemoAnnouncement"
MESSAGE_ATTRIBUTE = "Message"
SENDER_PARAMETER = "Sender"
MESSAGE_PARAMETER = "Message"


@dataclass(frozen=True)
class MinimalObjectUpdate:
    object_name: str
    message: str


@dataclass(frozen=True)
class MinimalInteraction:
    sender: str
    message: str


@dataclass
class MinimalScenarioResult:
    federation_name: str
    backend_kinds: tuple[str, str]
    object_updates: list[MinimalObjectUpdate]
    interactions: list[MinimalInteraction]
    publisher_events: list[tuple[str, Any]] = field(default_factory=list)
    subscriber_events: list[tuple[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "federation_name": self.federation_name,
            "backend_kinds": self.backend_kinds,
            "object_updates": [
                {"object_name": item.object_name, "message": item.message}
                for item in self.object_updates
            ],
            "interactions": [
                {"sender": item.sender, "message": item.message}
                for item in self.interactions
            ],
            "publisher_events": [(name, repr(payload)) for name, payload in self.publisher_events],
            "subscriber_events": [(name, repr(payload)) for name, payload in self.subscriber_events],
        }


class RTIAmbassadorLike(Protocol):
    def connect(self, *args: Any, **kwargs: Any) -> Any: ...
    def create_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...
    def join_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...
    def resign_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...
    def disconnect(self, *args: Any, **kwargs: Any) -> Any: ...
    def destroy_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...
    def evoke_multiple_callbacks(self, *args: Any, **kwargs: Any) -> Any: ...


RtiFactory = Callable[[str], RTIAmbassadorLike]


def encode_text(value: str) -> bytes:
    return value.encode("utf-8")


def decode_text(data: bytes) -> str:
    return bytes(data).decode("utf-8")


class PublisherFederate(FederateAmbassadorSpec):
    """Federate that publishes one object update and one interaction."""

    def __init__(self, *, name: str = "Publisher-1") -> None:
        self.name = name
        self.rti: Any | None = None
        self.object_class: ObjectClassHandle | None = None
        self.message_attr: AttributeHandle | None = None
        self.interaction_class: InteractionClassHandle | None = None
        self.sender_param: ParameterHandle | None = None
        self.message_param: ParameterHandle | None = None
        self.object_handle: ObjectInstanceHandle | None = None
        self.events: list[tuple[str, Any]] = []

    def setup(self, rti: Any) -> None:
        self.rti = rti
        self.object_class = rti.getObjectClassHandle(DEMO_OBJECT_CLASS)
        self.message_attr = rti.getAttributeHandle(self.object_class, MESSAGE_ATTRIBUTE)
        self.interaction_class = rti.getInteractionClassHandle(DEMO_INTERACTION_CLASS)
        self.sender_param = rti.getParameterHandle(self.interaction_class, SENDER_PARAMETER)
        self.message_param = rti.getParameterHandle(self.interaction_class, MESSAGE_PARAMETER)
        rti.publishObjectClassAttributes(self.object_class, {self.message_attr})
        rti.publishInteractionClass(self.interaction_class)
        self.object_handle = rti.registerObjectInstance(self.object_class, self.name)
        self.events.append(("registerObjectInstance", self.name))

    def publish(self, *, object_message: str, interaction_message: str) -> None:
        assert self.rti is not None
        assert self.object_handle is not None
        assert self.message_attr is not None
        assert self.interaction_class is not None
        assert self.sender_param is not None
        assert self.message_param is not None

        self.rti.updateAttributeValues(
            self.object_handle,
            {self.message_attr: encode_text(object_message)},
            b"minimal-demo-object",
        )
        self.events.append(("updateAttributeValues", object_message))

        self.rti.sendInteraction(
            self.interaction_class,
            {
                self.sender_param: encode_text(self.name),
                self.message_param: encode_text(interaction_message),
            },
            b"minimal-demo-interaction",
        )
        self.events.append(("sendInteraction", interaction_message))


class SubscriberFederate(FederateAmbassadorSpec):
    """Federate that subscribes to the minimal object and interaction."""

    def __init__(self, *, name: str = "Subscriber-1") -> None:
        self.name = name
        self.rti: Any | None = None
        self.object_class: ObjectClassHandle | None = None
        self.message_attr: AttributeHandle | None = None
        self.interaction_class: InteractionClassHandle | None = None
        self.sender_param: ParameterHandle | None = None
        self.message_param: ParameterHandle | None = None
        self.object_names: dict[ObjectInstanceHandle, str] = {}
        self.object_updates: list[MinimalObjectUpdate] = []
        self.interactions: list[MinimalInteraction] = []
        self.events: list[tuple[str, Any]] = []

    def setup(self, rti: Any) -> None:
        self.rti = rti
        self.object_class = rti.getObjectClassHandle(DEMO_OBJECT_CLASS)
        self.message_attr = rti.getAttributeHandle(self.object_class, MESSAGE_ATTRIBUTE)
        self.interaction_class = rti.getInteractionClassHandle(DEMO_INTERACTION_CLASS)
        self.sender_param = rti.getParameterHandle(self.interaction_class, SENDER_PARAMETER)
        self.message_param = rti.getParameterHandle(self.interaction_class, MESSAGE_PARAMETER)
        rti.subscribeObjectClassAttributes(self.object_class, {self.message_attr})
        rti.subscribeInteractionClass(self.interaction_class)

    def discover_object_instance(self, the_object: ObjectInstanceHandle, the_object_class: ObjectClassHandle, object_name: str, *extra: Any) -> None:
        if self.object_class is not None and the_object_class == self.object_class:
            self.object_names[the_object] = str(object_name)
            self.events.append(("discover_object_instance", object_name))

    def reflect_attribute_values(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: Mapping[AttributeHandle, bytes],
        user_supplied_tag: bytes,
        sent_ordering: Any = OrderType.RECEIVE,
        transportation_type: Any = TransportationType.RELIABLE,
        *extra: Any,
    ) -> None:
        if self.message_attr is None or self.message_attr not in the_attributes:
            return
        update = MinimalObjectUpdate(
            object_name=self.object_names.get(the_object, f"Object-{the_object.value}"),
            message=decode_text(the_attributes[self.message_attr]),
        )
        self.object_updates.append(update)
        self.events.append(("reflect_attribute_values", (update.object_name, update.message, user_supplied_tag)))

    def receive_interaction(
        self,
        interaction_class: InteractionClassHandle,
        the_parameters: Mapping[ParameterHandle, bytes],
        user_supplied_tag: bytes,
        sent_ordering: Any = OrderType.RECEIVE,
        transportation_type: Any = TransportationType.RELIABLE,
        *extra: Any,
    ) -> None:
        if self.interaction_class is None or interaction_class != self.interaction_class:
            return
        assert self.sender_param is not None
        assert self.message_param is not None
        interaction = MinimalInteraction(
            sender=decode_text(the_parameters[self.sender_param]),
            message=decode_text(the_parameters[self.message_param]),
        )
        self.interactions.append(interaction)
        self.events.append(("receive_interaction", (interaction.sender, interaction.message, user_supplied_tag)))


def create_python_minimal_demo_pair() -> tuple[Any, Any]:
    """Create publisher/subscriber RTI ambassadors sharing one Python engine."""

    return import_module("hla2010_rti_python").create_python_pair()


def _python_pair_factory() -> RtiFactory:
    pair_by_role: dict[str, RTIAmbassadorLike] = {}

    def factory(role: str) -> RTIAmbassadorLike:
        if role not in pair_by_role:
            publisher_rti, subscriber_rti = create_python_minimal_demo_pair()
            pair_by_role.update({"publisher": publisher_rti, "subscriber": subscriber_rti})
        return pair_by_role[role]

    return factory


def _call_factory(factory: RtiFactory, role: str) -> RTIAmbassadorLike:
    try:
        return factory(role)
    except TypeError:
        return factory()  # type: ignore[misc]


def _drain_callbacks(*rtis: Any, cycles: int = 6) -> None:
    for _ in range(cycles):
        for rti in rtis:
            rti.evokeMultipleCallbacks(0.0, 0.1)


def run_minimal_demo_scenario(
    rti_factory: RtiFactory | None = None,
    *,
    federation_name: str = "MinimalDemoFederation",
    object_message: str = "hello-object",
    interaction_message: str = "hello-interaction",
    publisher: PublisherFederate | None = None,
    subscriber: SubscriberFederate | None = None,
    fom_modules: Iterable[Any] | None = None,
    cleanup: bool = True,
) -> MinimalScenarioResult:
    """Run the minimal publisher/subscriber scenario with any backend-neutral RTI pair."""

    if rti_factory is None:
        rti_factory = _python_pair_factory()

    publisher = publisher or PublisherFederate()
    subscriber = subscriber or SubscriberFederate()
    publisher_rti = _call_factory(rti_factory, "publisher")
    subscriber_rti = _call_factory(rti_factory, "subscriber")

    publisher_rti.connect(publisher, CallbackModel.HLA_EVOKED)
    subscriber_rti.connect(subscriber, CallbackModel.HLA_EVOKED)

    try:
        publisher_rti.createFederationExecution(federation_name, list(fom_modules or []))
    except FederationExecutionAlreadyExists:
        pass

    publisher_rti.joinFederationExecution("Publisher", "minimal-demo-publisher", federation_name)
    subscriber_rti.joinFederationExecution("Subscriber", "minimal-demo-subscriber", federation_name)

    subscriber.setup(subscriber_rti)
    publisher.setup(publisher_rti)
    _drain_callbacks(publisher_rti, subscriber_rti)

    publisher.publish(object_message=object_message, interaction_message=interaction_message)
    _drain_callbacks(publisher_rti, subscriber_rti)

    backend_kinds = (
        getattr(getattr(publisher_rti, "backend_info", None), "kind", "unknown"),
        getattr(getattr(subscriber_rti, "backend_info", None), "kind", "unknown"),
    )
    result = MinimalScenarioResult(
        federation_name=federation_name,
        backend_kinds=backend_kinds,
        object_updates=list(subscriber.object_updates),
        interactions=list(subscriber.interactions),
        publisher_events=list(publisher.events),
        subscriber_events=list(subscriber.events),
    )

    if cleanup:
        for rti in (subscriber_rti, publisher_rti):
            try:
                rti.resignFederationExecution(ResignAction.NO_ACTION)
            except RTIexception:
                pass
        try:
            publisher_rti.destroyFederationExecution(federation_name)
        except (FederationExecutionDoesNotExist, FederatesCurrentlyJoined, RTIexception):
            pass
        for rti in (subscriber_rti, publisher_rti):
            try:
                rti.disconnect()
            except RTIexception:
                pass
        for rti in (subscriber_rti, publisher_rti):
            close = getattr(rti, "close", None)
            if callable(close):
                close()

    return result


__all__ = [
    "MinimalInteraction",
    "MinimalObjectUpdate",
    "MinimalScenarioResult",
    "PublisherFederate",
    "SubscriberFederate",
    "create_python_minimal_demo_pair",
    "decode_text",
    "encode_text",
    "run_minimal_demo_scenario",
]
