"""Reusable backend-neutral smoke scenarios for HLA RTI adapters."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from ..api import FederateAmbassador
from ..enums import CallbackModel, OrderType, ResignAction
from ..handles import (
    AttributeHandle,
    DimensionHandle,
    FederateHandle,
    InteractionClassHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    RegionHandle,
)
from ..exceptions import RTIexception
from ..time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time


@dataclass
class DemoFederate(FederateAmbassador):
    """Federate used by shim/integration tests.

    The event names are intentionally backend-neutral.  The payloads are Python
    handles, dictionaries, bytes, enums, and logical-time objects after adapter
    conversion.
    """

    events: list[tuple[str, Any]] = field(default_factory=list)

    def discover_object_instance(self, the_object, the_object_class, object_name, *extra):
        self.events.append(("discover", (the_object, the_object_class, object_name, extra)))

    def reflect_attribute_values(
        self,
        the_object,
        the_attributes,
        user_supplied_tag,
        sent_ordering,
        the_transport,
        *extra,
    ):
        self.events.append(
            (
                "reflect",
                (the_object, the_attributes, user_supplied_tag, sent_ordering, the_transport, extra),
            )
        )

    def receive_interaction(
        self,
        interaction_class,
        the_parameters,
        user_supplied_tag,
        sent_ordering,
        the_transport,
        *extra,
    ):
        self.events.append(
            (
                "interaction",
                (interaction_class, the_parameters, user_supplied_tag, sent_ordering, the_transport, extra),
            )
        )

    def time_regulation_enabled(self, time):
        self.events.append(("time_regulation_enabled", time))

    def time_constrained_enabled(self, time):
        self.events.append(("time_constrained_enabled", time))

    def time_advance_grant(self, the_time):
        self.events.append(("time_advance_grant", the_time))


def drain_callbacks(rti: Any) -> None:
    """Drain queued callbacks through the HLA evoke API."""

    while rti.evoke_callback(0.0):
        pass
    rti.evoke_multiple_callbacks(0.0, 0.1)


def drain_callbacks_pair(*rtis: Any, loops: int = 8) -> None:
    for _ in range(loops):
        delivered = False
        for rti in rtis:
            if rti.evoke_callback(0.0):
                delivered = True
        for rti in rtis:
            if rti.evoke_multiple_callbacks(0.0, 0.05):
                delivered = True
        if not delivered:
            return


def wait_for_callback(rti: Any, federate: Any, method_name: str, *, loops: int = 24) -> Any:
    for _ in range(loops):
        rti.evoke_callback(0.0)
        record = federate.last_callback(method_name)
        if record is not None:
            return record
    rti.evoke_multiple_callbacks(0.0, 0.1)
    return federate.last_callback(method_name)


def wait_for_callback_count(rti: Any, federate: Any, method_name: str, expected_count: int, *, loops: int = 24) -> list[Any]:
    for _ in range(loops):
        rti.evoke_callback(0.0)
        records = federate.callbacks_named(method_name)
        if len(records) >= expected_count:
            return records
    rti.evoke_multiple_callbacks(0.0, 0.1)
    return federate.callbacks_named(method_name)


def wait_for_callback_count_pair(
    publisher_rti: Any,
    subscriber_rti: Any,
    federate: Any,
    method_name: str,
    expected_count: int,
    *,
    loops: int = 24,
) -> list[Any]:
    for _ in range(loops):
        publisher_rti.evoke_callback(0.0)
        subscriber_rti.evoke_callback(0.0)
        records = federate.callbacks_named(method_name)
        if len(records) >= expected_count:
            return records
    publisher_rti.evoke_multiple_callbacks(0.0, 0.1)
    subscriber_rti.evoke_multiple_callbacks(0.0, 0.1)
    return federate.callbacks_named(method_name)


def _advance_time_beyond(publisher_rti: Any, subscriber_rti: Any, target_time: Any) -> None:
    raw = float(getattr(target_time, "value", target_time))
    if isinstance(target_time, HLAinteger64Time):
        advance_to = type(target_time)(int(raw) + 1)
    else:
        advance_to = type(target_time)(raw + 1.0)
    publisher_rti.time_advance_request(advance_to)
    subscriber_rti.time_advance_request(advance_to)
    drain_callbacks_pair(publisher_rti, subscriber_rti, loops=24)


def _order_value(value: Any) -> int:
    return int(getattr(value, "value", value))


@dataclass(frozen=True)
class TwoFederateExchangeConfig:
    federation_name: str = "VendorExchangeFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    publisher_name: str = "Publisher"
    subscriber_name: str = "Subscriber"
    federate_type: str = "SmokeFederate"
    object_class_name: str = "HLAobjectRoot.DemoObject"
    attribute_name: str = "Payload"
    interaction_class_name: str = "HLAinteractionRoot.DemoInteraction"
    parameter_name: str = "Message"
    object_instance_name: str = "DemoObject-1"
    attribute_payload: bytes = b"attribute-bytes"
    attribute_tag: bytes = b"update-tag"
    interaction_payload: bytes = b"hello"
    interaction_tag: bytes = b"interaction-tag"
    enable_time_management: bool = False
    lookahead: Any = HLAinteger64Interval(1)
    advance_time: Any = HLAinteger64Time(10)
    timestamped_attribute_payload: bytes = b"attribute-tso"
    timestamped_attribute_tag: bytes = b"update-tso"
    timestamped_attribute_time: Any = HLAinteger64Time(5)
    timestamped_interaction_payload: bytes = b"hello-tso"
    timestamped_interaction_tag: bytes = b"interaction-tso"
    timestamped_interaction_time: Any = HLAinteger64Time(6)


@dataclass(frozen=True)
class ExchangeRoundConfig:
    attribute_payload: bytes
    attribute_tag: bytes
    interaction_payload: bytes
    interaction_tag: bytes
    attribute_time: Any | None = None
    interaction_time: Any | None = None


@dataclass(frozen=True)
class SynchronizationScenarioConfig:
    federation_name: str = "JavaProfileSyncFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    leader_name: str = "Leader"
    wing_name: str = "Wing"
    federate_type: str = "Participant"
    label: str = "ReadyToRun"
    tag: bytes = b"startup"


@dataclass(frozen=True)
class OwnershipScenarioConfig:
    federation_name: str = "JavaProfileOwnershipFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    owner_name: str = "Owner"
    acquirer_name: str = "Acquirer"
    federate_type: str = "Participant"
    object_class_name: str = "HLAobjectRoot.DemoObject"
    attribute_name: str = "Payload"
    object_instance_name: str = "OwnedObject-1"


@dataclass(frozen=True)
class NegotiatedOwnershipScenarioConfig:
    federation_name: str = "JavaProfileNegotiatedOwnershipFederation"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    owner_name: str = "Owner"
    acquirer_name: str = "Acquirer"
    federate_type: str = "Participant"
    object_class_name: str = "HLAobjectRoot.DemoObject"
    attribute_name: str = "Payload"
    object_instance_name: str = "NegotiatedOwnedObject-1"
    assumption_tag: bytes = b"assume-offer"
    request_tag: bytes = b"acquire-request"
    cancel_tag: bytes = b"cancel-request"


def run_two_federate_exchange_scenario(
    publisher_rti: Any,
    subscriber_rti: Any,
    *,
    config: TwoFederateExchangeConfig,
    publisher_federate: Any,
    subscriber_federate: Any,
) -> dict[str, Any]:
    publisher_rti.connect(publisher_federate, CallbackModel.HLA_EVOKED)
    subscriber_rti.connect(subscriber_federate, CallbackModel.HLA_EVOKED)
    publisher_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    publisher_handle = publisher_rti.join_federation_execution(config.publisher_name, config.federate_type, config.federation_name)
    subscriber_handle = subscriber_rti.join_federation_execution(config.subscriber_name, config.federate_type, config.federation_name)
    assert isinstance(publisher_handle, FederateHandle)
    assert isinstance(subscriber_handle, FederateHandle)

    publisher_class = publisher_rti.get_object_class_handle(config.object_class_name)
    subscriber_class = subscriber_rti.get_object_class_handle(config.object_class_name)
    publisher_attr = publisher_rti.get_attribute_handle(publisher_class, config.attribute_name)
    subscriber_attr = subscriber_rti.get_attribute_handle(subscriber_class, config.attribute_name)
    publisher_rti.publish_object_class_attributes(publisher_class, {publisher_attr})
    subscriber_rti.subscribe_object_class_attributes(the_class=subscriber_class, attribute_list={subscriber_attr})

    publisher_interaction = publisher_rti.get_interaction_class_handle(config.interaction_class_name)
    subscriber_interaction = subscriber_rti.get_interaction_class_handle(config.interaction_class_name)
    publisher_param = publisher_rti.get_parameter_handle(publisher_interaction, config.parameter_name)
    subscriber_param = subscriber_rti.get_parameter_handle(subscriber_interaction, config.parameter_name)
    publisher_rti.publish_interaction_class(publisher_interaction)
    subscriber_rti.subscribe_interaction_class(subscriber_interaction)
    drain_callbacks_pair(publisher_rti, subscriber_rti)

    object_instance = publisher_rti.register_object_instance(publisher_class, config.object_instance_name)
    discover = wait_for_callback(subscriber_rti, subscriber_federate, "discoverObjectInstance")
    assert discover is not None
    discovered_object, discovered_class, discovered_name = discover.args
    assert discovered_class == subscriber_class
    assert discovered_name == config.object_instance_name
    assert subscriber_rti.get_object_instance_handle(config.object_instance_name) == discovered_object
    assert subscriber_rti.get_known_object_class_handle(discovered_object) == subscriber_class

    publisher_rti.update_attribute_values(object_instance, {publisher_attr: config.attribute_payload}, config.attribute_tag)
    reflect = wait_for_callback(subscriber_rti, subscriber_federate, "reflectAttributeValues")
    assert reflect is not None
    reflected_object = reflect.args[0]
    reflected_attrs = reflect.args[1]
    reflected_tag = reflect.args[2]
    reflected_order = reflect.args[3]
    reflected_transport = reflect.args[4]
    assert reflected_object == discovered_object
    assert reflected_attrs == {subscriber_attr: config.attribute_payload}
    assert reflected_tag == config.attribute_tag
    assert _order_value(reflected_order) == OrderType.RECEIVE.value
    assert int(reflected_transport.value) >= 1

    publisher_rti.send_interaction(publisher_interaction, {publisher_param: config.interaction_payload}, config.interaction_tag)
    interaction = wait_for_callback(subscriber_rti, subscriber_federate, "receiveInteraction")
    assert interaction is not None
    received_interaction = interaction.args[0]
    received_params = interaction.args[1]
    received_tag = interaction.args[2]
    received_order = interaction.args[3]
    received_transport = interaction.args[4]
    assert received_interaction == subscriber_interaction
    assert received_params == {subscriber_param: config.interaction_payload}
    assert received_tag == config.interaction_tag
    assert int(received_transport.value) >= 1

    summary: dict[str, Any] = {
        "publisher_handle": publisher_handle,
        "subscriber_handle": subscriber_handle,
        "object_instance": object_instance,
        "discovered_object": discovered_object,
        "publisher_class": publisher_class,
        "subscriber_class": subscriber_class,
        "publisher_attribute": publisher_attr,
        "subscriber_attribute": subscriber_attr,
        "publisher_interaction": publisher_interaction,
        "subscriber_interaction": subscriber_interaction,
        "publisher_parameter": publisher_param,
        "subscriber_parameter": subscriber_param,
        "discover": discover,
        "reflect": reflect,
        "interaction": interaction,
    }

    if config.enable_time_management:
        publisher_rti.enable_time_regulation(config.lookahead)
        subscriber_rti.enable_time_constrained()
        drain_callbacks_pair(publisher_rti, subscriber_rti, loops=16)

        time_regulation = publisher_federate.last_callback("timeRegulationEnabled")
        time_constrained = subscriber_federate.last_callback("timeConstrainedEnabled")
        assert time_regulation is not None
        assert time_constrained is not None

        publisher_rti.update_attribute_values(
            object_instance,
            {publisher_attr: config.timestamped_attribute_payload},
            config.timestamped_attribute_tag,
            config.timestamped_attribute_time,
        )
        publisher_rti.send_interaction(
            publisher_interaction,
            {publisher_param: config.timestamped_interaction_payload},
            config.timestamped_interaction_tag,
            config.timestamped_interaction_time,
        )
        publisher_rti.time_advance_request(config.advance_time)
        subscriber_rti.time_advance_request(config.advance_time)
        drain_callbacks_pair(publisher_rti, subscriber_rti, loops=24)

        timed_reflects = subscriber_federate.callbacks_named("reflectAttributeValues")
        timed_reflect = timed_reflects[-1]
        assert timed_reflect.args[1] == {subscriber_attr: config.timestamped_attribute_payload}
        assert timed_reflect.args[2] == config.timestamped_attribute_tag
        assert _order_value(timed_reflect.args[3]) == OrderType.TIMESTAMP.value
        assert timed_reflect.args[5] == config.timestamped_attribute_time

        timed_interactions = subscriber_federate.callbacks_named("receiveInteraction")
        timed_interaction = timed_interactions[-1]
        assert timed_interaction.args[1] == {subscriber_param: config.timestamped_interaction_payload}
        assert timed_interaction.args[2] == config.timestamped_interaction_tag
        assert _order_value(timed_interaction.args[3]) == OrderType.TIMESTAMP.value
        assert timed_interaction.args[5] == config.timestamped_interaction_time

        advance_grant = subscriber_federate.last_callback("timeAdvanceGrant")
        assert advance_grant is not None
        assert advance_grant.args[0] == config.advance_time
        summary.update(
            {
                "time_regulation": time_regulation,
                "time_constrained": time_constrained,
                "timed_reflect": timed_reflect,
                "timed_interaction": timed_interaction,
                "advance_grant": advance_grant,
            }
        )

    return summary


def assert_two_federate_exchange_callback_history(
    summary: Mapping[str, Any],
    *,
    publisher_federate: Any,
    subscriber_federate: Any,
    config: TwoFederateExchangeConfig,
    require_timed_delivery: bool = True,
) -> dict[str, Any]:
    discovers = subscriber_federate.callbacks_named("discoverObjectInstance")
    reflects = subscriber_federate.callbacks_named("reflectAttributeValues")
    interactions = subscriber_federate.callbacks_named("receiveInteraction")
    time_regulations = publisher_federate.callbacks_named("timeRegulationEnabled")
    time_constrained = subscriber_federate.callbacks_named("timeConstrainedEnabled")
    grants = subscriber_federate.callbacks_named("timeAdvanceGrant")

    receive_reflect = next(record for record in reflects if record.args[2] == config.attribute_tag)
    receive_interaction = next(record for record in interactions if record.args[2] == config.interaction_tag)

    assert len(discovers) == 1
    assert len(reflects) >= 1
    assert len(interactions) >= 1
    if config.enable_time_management:
        assert len(time_regulations) == 1
        assert len(time_constrained) == 1

    assert discovers[0].args[2] == config.object_instance_name

    assert receive_reflect.args[1] == {summary["subscriber_attribute"]: config.attribute_payload}
    assert receive_reflect.args[2] == config.attribute_tag
    assert receive_reflect.args[3] is OrderType.RECEIVE

    assert receive_interaction.args[1] == {summary["subscriber_parameter"]: config.interaction_payload}
    assert receive_interaction.args[2] == config.interaction_tag

    timestamp_reflect = None
    timestamp_interaction = None
    if require_timed_delivery:
        timestamp_reflect = next(record for record in reflects if record.args[2] == config.timestamped_attribute_tag)
        timestamp_interaction = next(record for record in interactions if record.args[2] == config.timestamped_interaction_tag)
        assert len(reflects) >= 2
        assert len(interactions) >= 2
        assert timestamp_reflect.args[1] == {summary["subscriber_attribute"]: config.timestamped_attribute_payload}
        assert timestamp_reflect.args[2] == config.timestamped_attribute_tag
        assert timestamp_reflect.args[3] is OrderType.TIMESTAMP
        assert timestamp_reflect.args[5] == config.timestamped_attribute_time
        assert timestamp_interaction.args[1] == {summary["subscriber_parameter"]: config.timestamped_interaction_payload}
        assert timestamp_interaction.args[2] == config.timestamped_interaction_tag
        assert timestamp_interaction.args[3] is OrderType.TIMESTAMP
        assert timestamp_interaction.args[5] == config.timestamped_interaction_time

    if config.enable_time_management:
        assert time_regulations[0] == summary["time_regulation"]
        assert time_constrained[0] == summary["time_constrained"]
        assert grants[-1].args[0] == config.advance_time

    return {
        "discovers": discovers,
        "reflects": reflects,
        "interactions": interactions,
        "time_regulations": time_regulations,
        "time_constrained": time_constrained,
        "grants": grants,
        "receive_reflect": receive_reflect,
        "timestamp_reflect": timestamp_reflect,
        "receive_interaction": receive_interaction,
        "timestamp_interaction": timestamp_interaction,
    }


def run_exchange_round(
    publisher_rti: Any,
    subscriber_rti: Any,
    *,
    summary: Mapping[str, Any],
    subscriber_federate: Any,
    config: ExchangeRoundConfig,
) -> dict[str, Any]:
    object_instance = summary["object_instance"]
    discovered_object = summary["discovered_object"]
    publisher_attribute = summary["publisher_attribute"]
    subscriber_attribute = summary["subscriber_attribute"]
    publisher_interaction = summary["publisher_interaction"]
    subscriber_interaction = summary["subscriber_interaction"]
    publisher_parameter = summary["publisher_parameter"]
    subscriber_parameter = summary["subscriber_parameter"]

    baseline_reflects = len(subscriber_federate.callbacks_named("reflectAttributeValues"))
    baseline_interactions = len(subscriber_federate.callbacks_named("receiveInteraction"))

    if config.attribute_time is None:
        publisher_rti.update_attribute_values(object_instance, {publisher_attribute: config.attribute_payload}, config.attribute_tag)
    else:
        publisher_rti.update_attribute_values(
            object_instance,
            {publisher_attribute: config.attribute_payload},
            config.attribute_tag,
            config.attribute_time,
        )

    if config.interaction_time is None:
        publisher_rti.send_interaction(
            publisher_interaction,
            {publisher_parameter: config.interaction_payload},
            config.interaction_tag,
        )
    else:
        publisher_rti.send_interaction(
            publisher_interaction,
            {publisher_parameter: config.interaction_payload},
            config.interaction_tag,
            config.interaction_time,
        )

    if config.attribute_time is not None or config.interaction_time is not None:
        target_time = config.interaction_time if config.interaction_time is not None else config.attribute_time
        _advance_time_beyond(publisher_rti, subscriber_rti, target_time)

    reflect_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        subscriber_federate,
        "reflectAttributeValues",
        baseline_reflects + 1,
    )
    assert len(reflect_records) == baseline_reflects + 1
    latest_reflect = reflect_records[-1]
    assert latest_reflect.args[0] == discovered_object
    assert latest_reflect.args[1] == {subscriber_attribute: config.attribute_payload}
    assert latest_reflect.args[2] == config.attribute_tag
    expected_reflect_order = OrderType.TIMESTAMP if config.attribute_time is not None else OrderType.RECEIVE
    assert _order_value(latest_reflect.args[3]) == expected_reflect_order.value
    if config.attribute_time is not None:
        assert latest_reflect.args[5] == config.attribute_time

    interaction_records = wait_for_callback_count_pair(
        publisher_rti,
        subscriber_rti,
        subscriber_federate,
        "receiveInteraction",
        baseline_interactions + 1,
    )
    assert len(interaction_records) == baseline_interactions + 1
    latest_interaction = interaction_records[-1]
    assert latest_interaction.args[0] == subscriber_interaction
    assert latest_interaction.args[1] == {subscriber_parameter: config.interaction_payload}
    assert latest_interaction.args[2] == config.interaction_tag
    expected_interaction_order = OrderType.TIMESTAMP if config.interaction_time is not None else OrderType.RECEIVE
    assert _order_value(latest_interaction.args[3]) == expected_interaction_order.value
    if config.interaction_time is not None:
        assert latest_interaction.args[5] == config.interaction_time

    return {
        "reflect": latest_reflect,
        "interaction": latest_interaction,
        "reflect_count": len(reflect_records),
        "interaction_count": len(interaction_records),
    }


def run_synchronization_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: SynchronizationScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    leader_handle = leader_rti.join_federation_execution(config.leader_name, config.federate_type, config.federation_name)
    wing_handle = wing_rti.join_federation_execution(config.wing_name, config.federate_type, config.federation_name)

    leader_rti.register_federation_synchronization_point(config.label, config.tag)
    drain_callbacks_pair(leader_rti, wing_rti, loops=12)

    leader_announce = leader_federate.last_callback("announceSynchronizationPoint")
    wing_announce = wing_federate.last_callback("announceSynchronizationPoint")
    assert leader_announce is not None
    assert wing_announce is not None
    assert leader_announce.args[:2] == (config.label, config.tag)
    assert wing_announce.args[:2] == (config.label, config.tag)

    leader_rti.synchronization_point_achieved(config.label)
    wing_rti.synchronization_point_achieved(config.label)
    drain_callbacks_pair(leader_rti, wing_rti, loops=12)

    leader_sync = leader_federate.last_callback("federationSynchronized")
    wing_sync = wing_federate.last_callback("federationSynchronized")
    assert leader_sync is not None
    assert wing_sync is not None
    assert leader_sync.args[0] == config.label
    assert wing_sync.args[0] == config.label

    return {
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
        "leader_announce": leader_announce,
        "wing_announce": wing_announce,
        "leader_sync": leader_sync,
        "wing_sync": wing_sync,
    }


def run_attribute_ownership_scenario(
    owner_rti: Any,
    acquirer_rti: Any,
    *,
    config: OwnershipScenarioConfig,
    owner_federate: Any,
    acquirer_federate: Any,
) -> dict[str, Any]:
    owner_rti.connect(owner_federate, CallbackModel.HLA_EVOKED)
    acquirer_rti.connect(acquirer_federate, CallbackModel.HLA_EVOKED)
    owner_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    owner_handle = owner_rti.join_federation_execution(config.owner_name, config.federate_type, config.federation_name)
    acquirer_handle = acquirer_rti.join_federation_execution(config.acquirer_name, config.federate_type, config.federation_name)

    owner_class = owner_rti.get_object_class_handle(config.object_class_name)
    acquirer_class = acquirer_rti.get_object_class_handle(config.object_class_name)
    owner_attr = owner_rti.get_attribute_handle(owner_class, config.attribute_name)
    acquirer_attr = acquirer_rti.get_attribute_handle(acquirer_class, config.attribute_name)

    owner_rti.publish_object_class_attributes(owner_class, {owner_attr})
    acquirer_rti.publish_object_class_attributes(acquirer_class, {acquirer_attr})
    acquirer_rti.subscribe_object_class_attributes(acquirer_class, {acquirer_attr})
    object_instance = owner_rti.register_object_instance(owner_class, config.object_instance_name)
    discover = wait_for_callback(acquirer_rti, acquirer_federate, "discoverObjectInstance")
    assert discover is not None
    acquirer_object = acquirer_rti.get_object_instance_handle(config.object_instance_name)
    assert owner_rti.is_attribute_owned_by_federate(object_instance, owner_attr)

    owner_rti.unconditional_attribute_ownership_divestiture(object_instance, {owner_attr})
    assert not owner_rti.is_attribute_owned_by_federate(object_instance, owner_attr)

    owner_rti.query_attribute_ownership(object_instance, owner_attr)
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    not_owned = owner_federate.last_callback("attributeIsNotOwned")
    assert not_owned is not None
    assert not_owned.args == (object_instance, owner_attr)

    acquirer_rti.attribute_ownership_acquisition_if_available(acquirer_object, {acquirer_attr})
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)

    acquired = acquirer_federate.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired is not None
    assert acquired.args[0] == acquirer_object
    assert acquirer_attr in acquired.args[1]
    assert acquirer_rti.is_attribute_owned_by_federate(acquirer_object, acquirer_attr)

    owner_rti.query_attribute_ownership(object_instance, owner_attr)
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    informed = owner_federate.last_callback("informAttributeOwnership")
    assert informed is not None
    assert informed.args[0] == object_instance
    assert informed.args[1] == owner_attr
    assert isinstance(informed.args[2], FederateHandle)

    return {
        "owner_handle": owner_handle,
        "acquirer_handle": acquirer_handle,
        "object_instance": object_instance,
        "acquirer_object_instance": acquirer_object,
        "owner_class": owner_class,
        "acquirer_class": acquirer_class,
        "owner_attribute": owner_attr,
        "acquirer_attribute": acquirer_attr,
        "not_owned": not_owned,
        "acquired": acquired,
        "informed": informed,
    }


def run_negotiated_attribute_ownership_scenario(
    owner_rti: Any,
    acquirer_rti: Any,
    *,
    config: NegotiatedOwnershipScenarioConfig,
    owner_federate: Any,
    acquirer_federate: Any,
) -> dict[str, Any]:
    owner_rti.connect(owner_federate, CallbackModel.HLA_EVOKED)
    acquirer_rti.connect(acquirer_federate, CallbackModel.HLA_EVOKED)
    owner_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    owner_handle = owner_rti.join_federation_execution(config.owner_name, config.federate_type, config.federation_name)
    acquirer_handle = acquirer_rti.join_federation_execution(config.acquirer_name, config.federate_type, config.federation_name)

    owner_class = owner_rti.get_object_class_handle(config.object_class_name)
    acquirer_class = acquirer_rti.get_object_class_handle(config.object_class_name)
    owner_attr = owner_rti.get_attribute_handle(owner_class, config.attribute_name)
    acquirer_attr = acquirer_rti.get_attribute_handle(acquirer_class, config.attribute_name)

    owner_rti.publish_object_class_attributes(owner_class, {owner_attr})
    acquirer_rti.publish_object_class_attributes(acquirer_class, {acquirer_attr})
    acquirer_rti.subscribe_object_class_attributes(acquirer_class, {acquirer_attr})
    object_instance = owner_rti.register_object_instance(owner_class, config.object_instance_name)
    discover = wait_for_callback(acquirer_rti, acquirer_federate, "discoverObjectInstance")
    assert discover is not None
    acquirer_object = acquirer_rti.get_object_instance_handle(config.object_instance_name)
    assert owner_rti.is_attribute_owned_by_federate(object_instance, owner_attr)

    assumption = None
    negotiated_divestiture_supported = False
    try:
        owner_rti.negotiated_attribute_ownership_divestiture(object_instance, {owner_attr}, config.assumption_tag)
        drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
        assumption = acquirer_federate.last_callback("requestAttributeOwnershipAssumption")
        negotiated_divestiture_supported = assumption is not None
    except RTIexception:
        assumption = None

    acquirer_rti.attribute_ownership_acquisition(acquirer_object, {acquirer_attr}, config.request_tag)
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    release = owner_federate.last_callback("requestAttributeOwnershipRelease")
    assert release is not None
    assert release.args[0] == object_instance
    assert release.args[1] == {owner_attr}
    assert release.args[2] == config.request_tag

    acquirer_rti.cancel_attribute_ownership_acquisition(acquirer_object, {acquirer_attr})
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    cancellation = acquirer_federate.last_callback("confirmAttributeOwnershipAcquisitionCancellation")
    assert cancellation is not None
    assert cancellation.args[0] == acquirer_object
    assert cancellation.args[1] == {acquirer_attr}

    acquirer_rti.attribute_ownership_acquisition(acquirer_object, {acquirer_attr}, config.cancel_tag)
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    release = owner_federate.last_callback("requestAttributeOwnershipRelease")
    assert release is not None
    assert release.args[0] == object_instance
    assert release.args[1] == {owner_attr}
    assert release.args[2] == config.cancel_tag

    divested = owner_rti.attribute_ownership_divestiture_if_wanted(object_instance, {owner_attr})
    assert divested == {owner_attr}
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)

    acquired = acquirer_federate.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired is not None
    assert acquired.args[0] == acquirer_object
    assert acquired.args[1] == {acquirer_attr}
    assert acquirer_rti.is_attribute_owned_by_federate(acquirer_object, acquirer_attr)

    owner_rti.query_attribute_ownership(object_instance, owner_attr)
    drain_callbacks_pair(owner_rti, acquirer_rti, loops=12)
    informed = owner_federate.last_callback("informAttributeOwnership")
    assert informed is not None
    assert informed.args[0] == object_instance
    assert informed.args[1] == owner_attr
    assert isinstance(informed.args[2], FederateHandle)

    return {
        "owner_handle": owner_handle,
        "acquirer_handle": acquirer_handle,
        "object_instance": object_instance,
        "acquirer_object_instance": acquirer_object,
        "owner_attribute": owner_attr,
        "acquirer_attribute": acquirer_attr,
        "assumption": assumption,
        "negotiated_divestiture_supported": negotiated_divestiture_supported,
        "release": release,
        "cancellation": cancellation,
        "divested": divested,
        "acquired": acquired,
        "informed": informed,
    }


def run_basic_federate_scenario(
    rti_factory: Callable[[], Any],
    *,
    federation_name: str = "PythonShimFederation",
) -> dict[str, Any]:
    """Run a small HLA scenario using only backend-neutral Python calls.

    The same function is used for the in-process JPype-profile shim, the
    in-process Py4J-profile shim, and optional real JPype/Py4J bridge smoke
    tests.  It deliberately touches the main adapter paths:

    * connection and federate ambassador callback adaptation
    * federation create/join/resign/destroy lifecycle
    * handle return conversion and pass-back conversion
    * object class and attribute support services
    * publish/subscribe/register/update object flow
    * interaction class and parameter flow
    * callback delivery and callback argument conversion
    * basic time-management callbacks
    """

    rti = rti_factory()
    federate = DemoFederate()
    summary: dict[str, Any] = {"backend": getattr(rti, "backend_info", None)}

    rti.connect(federate, CallbackModel.HLA_EVOKED)
    rti.create_federation_execution(federation_name, "DemoFOMmodule.xml")
    federate_handle = rti.join_federation_execution("python-federate", "demo", federation_name)
    assert isinstance(federate_handle, FederateHandle)
    assert rti.get_federate_name(federate_handle) == "python-federate"
    assert rti.get_federate_handle("python-federate") == federate_handle

    object_class = rti.get_object_class_handle("HLAobjectRoot.DemoObject")
    assert isinstance(object_class, ObjectClassHandle)
    assert rti.get_object_class_name(object_class) == "HLAobjectRoot.DemoObject"

    attribute = rti.get_attribute_handle(object_class, "Payload")
    assert isinstance(attribute, AttributeHandle)
    assert rti.get_attribute_name(object_class, attribute) == "Payload"

    # Mix positional and keyword forms so keyword-to-Java-overload resolution is
    # exercised without leaking Java details into the scenario.
    rti.publish_object_class_attributes(object_class, {attribute})
    rti.subscribe_object_class_attributes(the_class=object_class, attribute_list={attribute})

    object_instance = rti.register_object_instance(object_class, "DemoObject-1")
    assert isinstance(object_instance, ObjectInstanceHandle)
    assert rti.get_object_instance_handle("DemoObject-1") == object_instance
    assert rti.get_object_instance_name(object_instance) == "DemoObject-1"
    assert rti.get_known_object_class_handle(object_instance) == object_class
    drain_callbacks(rti)

    rti.update_attribute_values(object_instance, {attribute: b"attribute-bytes"}, b"update-tag")
    drain_callbacks(rti)

    interaction_class = rti.get_interaction_class_handle("HLAinteractionRoot.DemoInteraction")
    assert isinstance(interaction_class, InteractionClassHandle)
    assert rti.get_interaction_class_name(interaction_class) == "HLAinteractionRoot.DemoInteraction"

    parameter = rti.get_parameter_handle(interaction_class, "Message")
    assert isinstance(parameter, ParameterHandle)
    assert rti.get_parameter_name(interaction_class, parameter) == "Message"
    rti.publish_interaction_class(interaction_class)
    rti.subscribe_interaction_class(interaction_class)
    rti.send_interaction(interaction_class, {parameter: b"hello"}, b"interaction-tag")
    drain_callbacks(rti)

    rti.enable_time_regulation(HLAinteger64Interval(1))
    rti.enable_time_constrained()
    rti.time_advance_request(HLAinteger64Time(10))
    drain_callbacks(rti)

    dimension = rti.get_dimension_handle("RoutingSpace")
    assert isinstance(dimension, DimensionHandle)
    assert rti.get_dimension_name(dimension) == "RoutingSpace"
    region = rti.create_region({dimension})
    assert isinstance(region, RegionHandle)
    rti.commit_region_modifications({region})
    rti.delete_region(region)

    event_names = [name for name, _ in federate.events]
    assert "discover" in event_names
    assert "reflect" in event_names
    assert "interaction" in event_names
    assert "time_regulation_enabled" in event_names
    assert "time_constrained_enabled" in event_names
    assert "time_advance_grant" in event_names

    reflect_events = [payload for name, payload in federate.events if name == "reflect"]
    reflected_object, reflected_attrs, reflected_tag, reflected_order, *_ = reflect_events[-1]
    assert reflected_object == object_instance
    assert reflected_attrs == {attribute: b"attribute-bytes"}
    assert reflected_tag == b"update-tag"
    assert reflected_order is OrderType.RECEIVE

    interaction_events = [payload for name, payload in federate.events if name == "interaction"]
    received_interaction, received_params, received_tag, received_order, *_ = interaction_events[-1]
    assert received_interaction == interaction_class
    assert received_params == {parameter: b"hello"}
    assert received_tag == b"interaction-tag"
    assert received_order is OrderType.RECEIVE

    time_grants = [payload for name, payload in federate.events if name == "time_advance_grant"]
    assert time_grants[-1] == HLAinteger64Time(10)

    summary.update(
        {
            "federate_handle": federate_handle,
            "object_class": object_class,
            "attribute": attribute,
            "object_instance": object_instance,
            "interaction_class": interaction_class,
            "parameter": parameter,
            "dimension": dimension,
            "region": region,
            "events": federate.events,
            "event_names": event_names,
        }
    )

    rti.resign_federation_execution(ResignAction.NO_ACTION)
    rti.destroy_federation_execution(federation_name)
    rti.disconnect()
    rti.close()
    return summary


__all__ = [
    "assert_two_federate_exchange_callback_history",
    "DemoFederate",
    "ExchangeRoundConfig",
    "OwnershipScenarioConfig",
    "SynchronizationScenarioConfig",
    "TwoFederateExchangeConfig",
    "drain_callbacks",
    "drain_callbacks_pair",
    "run_basic_federate_scenario",
    "run_attribute_ownership_scenario",
    "run_exchange_round",
    "run_synchronization_scenario",
    "run_two_federate_exchange_scenario",
    "wait_for_callback",
    "wait_for_callback_count",
    "wait_for_callback_count_pair",
]
