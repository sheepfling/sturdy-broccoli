"""Reusable Section 8 backend-matrix scenarios."""
from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from typing import Any

from hla.rti1516e.enums import CallbackModel, OrderType, ResignAction
from hla.rti1516e.exceptions import InvalidLogicalTime, TimeConstrainedAlreadyEnabled, TimeRegulationAlreadyEnabled
from hla.rti1516e.types import MessageRetractionReturn
from hla.backends.common import RecordingFederateAmbassador


def vendor_smoke_fom_path() -> str:
    return str(resources.files("hla.rti1516e").joinpath("resources", "foms", "VendorSmokeFOM.xml"))


@dataclass(frozen=True)
class Section8MatrixConfig:
    federation_name: str
    logical_time_implementation_name: str
    lookahead: Any
    modified_lookahead: Any
    first_timestamp: Any
    second_timestamp: Any
    sender_advance_time: Any
    receiver_window_time: Any
    fom_modules: tuple[str, ...] = ()
    publisher_name: str = "Publisher"
    subscriber_name: str = "Subscriber"
    federate_type: str = "TimeFederate"
    interaction_class_name: str = "HLAinteractionRoot.SmokeInteraction"
    parameter_name: str = "Message"
    object_class_name: str = "HLAobjectRoot.SmokeObject"
    attribute_name: str = "Payload"
    order_interaction_class_name: str = "HLAinteractionRoot.SmokeInteraction"
    order_parameter_name: str = "Message"
    object_instance_name: str = "SmokeObject-1"
    first_payload: bytes = b"t3"
    second_payload: bytes = b"t2"
    retracted_payload: bytes = b"withdrawn"
    first_tag: bytes = b"tag3"
    second_tag: bytes = b"tag2"
    retracted_tag: bytes = b"withdraw"


def section8_matrix_config(federation_name: str, time_factory_name: str) -> Section8MatrixConfig:
    fom_modules = (vendor_smoke_fom_path(),)
    if time_factory_name == "HLAinteger64Time":
        from hla.rti1516e.time import HLAinteger64Interval, HLAinteger64Time

        return Section8MatrixConfig(
            federation_name=federation_name,
            logical_time_implementation_name=time_factory_name,
            lookahead=HLAinteger64Interval(1),
            modified_lookahead=HLAinteger64Interval(2),
            first_timestamp=HLAinteger64Time(3),
            second_timestamp=HLAinteger64Time(2),
            sender_advance_time=HLAinteger64Time(4),
            receiver_window_time=HLAinteger64Time(5),
            fom_modules=fom_modules,
        )
    if time_factory_name == "HLAfloat64Time":
        from hla.rti1516e.time import HLAfloat64Interval, HLAfloat64Time

        return Section8MatrixConfig(
            federation_name=federation_name,
            logical_time_implementation_name=time_factory_name,
            lookahead=HLAfloat64Interval(1.0),
            modified_lookahead=HLAfloat64Interval(2.0),
            first_timestamp=HLAfloat64Time(3.0),
            second_timestamp=HLAfloat64Time(2.0),
            sender_advance_time=HLAfloat64Time(4.0),
            receiver_window_time=HLAfloat64Time(5.0),
            fom_modules=fom_modules,
        )
    raise AssertionError(f"unexpected time factory {time_factory_name}")


def drain_callbacks(*rtis: Any, iterations: int = 20, max_time: float = 0.0) -> None:
    for _ in range(iterations):
        for rti in rtis:
            rti.evoke_multiple_callbacks(0.0, max_time)


def connect_section8_pair(
    publisher: Any,
    subscriber: Any,
    *,
    config: Section8MatrixConfig,
    publisher_federate: RecordingFederateAmbassador | None = None,
    subscriber_federate: RecordingFederateAmbassador | None = None,
    publisher_callback_model: CallbackModel = CallbackModel.HLA_EVOKED,
    subscriber_callback_model: CallbackModel = CallbackModel.HLA_EVOKED,
) -> tuple[RecordingFederateAmbassador, RecordingFederateAmbassador]:
    publisher_federate = publisher_federate or RecordingFederateAmbassador()
    subscriber_federate = subscriber_federate or RecordingFederateAmbassador()
    publisher.connect(publisher_federate, publisher_callback_model)
    subscriber.connect(subscriber_federate, subscriber_callback_model)
    publisher.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    publisher.join_federation_execution(config.publisher_name, config.federate_type, config.federation_name)
    subscriber.join_federation_execution(config.subscriber_name, config.federate_type, config.federation_name)
    return publisher_federate, subscriber_federate


def cleanup_section8_pair(publisher: Any, subscriber: Any, federation_name: str) -> None:
    try:
        subscriber.resign_federation_execution(ResignAction.NO_ACTION)
    except Exception:
        pass
    try:
        publisher.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    except Exception:
        try:
            publisher.resign_federation_execution(ResignAction.NO_ACTION)
        except Exception:
            pass
    try:
        publisher.destroy_federation_execution(federation_name)
    except Exception:
        pass
    for rti in (subscriber, publisher):
        try:
            rti.disconnect()
        except Exception:
            pass
        close = getattr(rti, "close", None)
        if callable(close):
            close()


def run_section8_state_services_case(
    publisher: Any,
    subscriber: Any,
    *,
    config: Section8MatrixConfig,
    publisher_federate: RecordingFederateAmbassador | None = None,
    subscriber_federate: RecordingFederateAmbassador | None = None,
) -> dict[str, Any]:
    publisher_federate, subscriber_federate = connect_section8_pair(
        publisher,
        subscriber,
        config=config,
        publisher_federate=publisher_federate,
        subscriber_federate=subscriber_federate,
    )
    try:
        publisher.enable_time_regulation(config.lookahead)
        subscriber.enable_time_constrained()
        drain_callbacks(publisher, subscriber)

        publisher_initial_time = publisher.query_logical_time()
        subscriber_initial_time = subscriber.query_logical_time()
        initial_lookahead = publisher.query_lookahead()
        publisher.modify_lookahead(config.modified_lookahead)
        modified_lookahead = publisher.query_lookahead()

        publisher.enable_asynchronous_delivery()
        publisher.disable_asynchronous_delivery()
        publisher.disable_time_regulation()
        subscriber.disable_time_constrained()

        return {
            "publisher_federate": publisher_federate,
            "subscriber_federate": subscriber_federate,
            "initial_time": publisher_initial_time,
            "publisher_initial_time": publisher_initial_time,
            "subscriber_initial_time": subscriber_initial_time,
            "initial_lookahead": initial_lookahead,
            "modified_lookahead": modified_lookahead,
        }
    finally:
        cleanup_section8_pair(publisher, subscriber, config.federation_name)


def run_section8_early_timestamp_send_case(
    publisher: Any,
    subscriber: Any,
    *,
    config: Section8MatrixConfig,
    publisher_federate: RecordingFederateAmbassador | None = None,
    subscriber_federate: RecordingFederateAmbassador | None = None,
) -> dict[str, Any]:
    publisher_federate, subscriber_federate = connect_section8_pair(
        publisher,
        subscriber,
        config=config,
        publisher_federate=publisher_federate,
        subscriber_federate=subscriber_federate,
    )
    try:
        publisher_object_class = publisher.get_object_class_handle(config.object_class_name)
        publisher_attribute = publisher.get_attribute_handle(publisher_object_class, config.attribute_name)
        publisher_interaction = publisher.get_interaction_class_handle(config.order_interaction_class_name)
        publisher_parameter = publisher.get_parameter_handle(publisher_interaction, config.order_parameter_name)
        subscriber_object_class = subscriber.get_object_class_handle(config.object_class_name)
        subscriber_attribute = subscriber.get_attribute_handle(subscriber_object_class, config.attribute_name)
        subscriber_interaction = subscriber.get_interaction_class_handle(config.order_interaction_class_name)

        publisher.publish_object_class_attributes(publisher_object_class, {publisher_attribute})
        subscriber.subscribe_object_class_attributes(subscriber_object_class, {subscriber_attribute})
        publisher.publish_interaction_class(publisher_interaction)
        subscriber.subscribe_interaction_class(subscriber_interaction)

        publisher.enable_time_regulation(config.lookahead)
        subscriber.enable_time_constrained()
        drain_callbacks(publisher, subscriber)

        publisher_initial_lookahead = publisher.query_lookahead()
        publisher.modify_lookahead(config.modified_lookahead)
        modified_lookahead = publisher.query_lookahead()
        instance = publisher.register_object_instance(publisher_object_class, config.object_instance_name)

        zero_time = type(config.first_timestamp)(0 if config.logical_time_implementation_name == "HLAinteger64Time" else 0.0)

        update_error = None
        try:
            publisher.update_attribute_values(
                instance,
                {publisher_attribute: config.first_payload},
                config.first_tag,
                zero_time,
            )
        except InvalidLogicalTime as exc:
            update_error = exc

        interaction_error = None
        try:
            publisher.send_interaction(
                publisher_interaction,
                {publisher_parameter: config.second_payload},
                config.second_tag,
                zero_time,
            )
        except InvalidLogicalTime as exc:
            interaction_error = exc

        return {
            "publisher_federate": publisher_federate,
            "subscriber_federate": subscriber_federate,
            "publisher_initial_lookahead": publisher_initial_lookahead,
            "modified_lookahead": modified_lookahead,
            "instance": instance,
            "update_error": update_error,
            "interaction_error": interaction_error,
        }
    finally:
        cleanup_section8_pair(publisher, subscriber, config.federation_name)


def run_section8_ordering_and_query_case(
    publisher: Any,
    subscriber: Any,
    *,
    config: Section8MatrixConfig,
    publisher_federate: RecordingFederateAmbassador | None = None,
    subscriber_federate: RecordingFederateAmbassador | None = None,
) -> dict[str, Any]:
    publisher_federate, subscriber_federate = connect_section8_pair(
        publisher,
        subscriber,
        config=config,
        publisher_federate=publisher_federate,
        subscriber_federate=subscriber_federate,
    )
    try:
        publisher_interaction = publisher.get_interaction_class_handle(config.interaction_class_name)
        publisher_parameter = publisher.get_parameter_handle(publisher_interaction, config.parameter_name)
        subscriber_interaction = subscriber.get_interaction_class_handle(config.interaction_class_name)
        subscriber_parameter = subscriber.get_parameter_handle(subscriber_interaction, config.parameter_name)
        publisher.publish_interaction_class(publisher_interaction)
        subscriber.subscribe_interaction_class(subscriber_interaction)

        publisher.enable_time_regulation(config.lookahead)
        subscriber.enable_time_constrained()
        drain_callbacks(publisher, subscriber)

        publisher.send_interaction(publisher_interaction, {publisher_parameter: config.first_payload}, config.first_tag, config.first_timestamp)
        publisher.send_interaction(publisher_interaction, {publisher_parameter: config.second_payload}, config.second_tag, config.second_timestamp)
        drain_callbacks(publisher, subscriber)

        initial_galt = subscriber.query_galt()
        initial_lits = subscriber.query_lits()

        publisher.time_advance_request(config.sender_advance_time)
        drain_callbacks(publisher, subscriber)
        sender_grant = publisher_federate.last_callback("timeAdvanceGrant")

        subscriber.next_message_request(config.receiver_window_time)
        drain_callbacks(publisher, subscriber)
        first_receive = subscriber_federate.callbacks_named("receiveInteraction")[-1]
        first_grant = subscriber_federate.last_callback("timeAdvanceGrant")

        subscriber.next_message_request(config.receiver_window_time)
        drain_callbacks(publisher, subscriber)
        second_receive = subscriber_federate.callbacks_named("receiveInteraction")[-1]
        second_grant = subscriber_federate.last_callback("timeAdvanceGrant")

        return {
            "publisher_federate": publisher_federate,
            "subscriber_federate": subscriber_federate,
            "parameter": subscriber_parameter,
            "initial_galt": initial_galt,
            "initial_lits": initial_lits,
            "sender_grant": sender_grant,
            "first_receive": first_receive,
            "first_grant": first_grant,
            "second_receive": second_receive,
            "second_grant": second_grant,
        }
    finally:
        cleanup_section8_pair(publisher, subscriber, config.federation_name)


def run_section8_time_bound_query_case(
    publisher: Any,
    subscriber: Any,
    *,
    config: Section8MatrixConfig,
    publisher_federate: RecordingFederateAmbassador | None = None,
    subscriber_federate: RecordingFederateAmbassador | None = None,
) -> dict[str, Any]:
    publisher_federate, subscriber_federate = connect_section8_pair(
        publisher,
        subscriber,
        config=config,
        publisher_federate=publisher_federate,
        subscriber_federate=subscriber_federate,
    )
    try:
        publisher_interaction = publisher.get_interaction_class_handle(config.interaction_class_name)
        publisher_parameter = publisher.get_parameter_handle(publisher_interaction, config.parameter_name)
        subscriber_interaction = subscriber.get_interaction_class_handle(config.interaction_class_name)
        subscriber_parameter = subscriber.get_parameter_handle(subscriber_interaction, config.parameter_name)
        publisher.publish_interaction_class(publisher_interaction)
        subscriber.subscribe_interaction_class(subscriber_interaction)

        publisher.enable_time_regulation(config.lookahead)
        subscriber.enable_time_constrained()
        drain_callbacks(publisher, subscriber)

        publisher.send_interaction(publisher_interaction, {publisher_parameter: config.first_payload}, config.first_tag, config.first_timestamp)
        publisher.send_interaction(publisher_interaction, {publisher_parameter: config.second_payload}, config.second_tag, config.second_timestamp)
        drain_callbacks(publisher, subscriber)

        initial_galt = subscriber.query_galt()
        initial_lits = subscriber.query_lits()

        return {
            "publisher_federate": publisher_federate,
            "subscriber_federate": subscriber_federate,
            "parameter": subscriber_parameter,
            "initial_galt": initial_galt,
            "initial_lits": initial_lits,
        }
    finally:
        cleanup_section8_pair(publisher, subscriber, config.federation_name)


def run_section8_available_and_retraction_case(
    publisher: Any,
    subscriber: Any,
    *,
    config: Section8MatrixConfig,
    publisher_federate: RecordingFederateAmbassador | None = None,
    subscriber_federate: RecordingFederateAmbassador | None = None,
) -> dict[str, Any]:
    publisher_federate, subscriber_federate = connect_section8_pair(
        publisher,
        subscriber,
        config=config,
        publisher_federate=publisher_federate,
        subscriber_federate=subscriber_federate,
    )
    try:
        publisher_interaction = publisher.get_interaction_class_handle(config.interaction_class_name)
        publisher_parameter = publisher.get_parameter_handle(publisher_interaction, config.parameter_name)
        subscriber_interaction = subscriber.get_interaction_class_handle(config.interaction_class_name)
        subscriber_parameter = subscriber.get_parameter_handle(subscriber_interaction, config.parameter_name)
        publisher.publish_interaction_class(publisher_interaction)
        subscriber.subscribe_interaction_class(subscriber_interaction)

        publisher.enable_time_regulation(config.lookahead)
        subscriber.enable_time_constrained()
        drain_callbacks(publisher, subscriber)

        retraction = publisher.send_interaction(
            publisher_interaction,
            {publisher_parameter: config.retracted_payload},
            config.retracted_tag,
            config.second_timestamp,
        )
        assert isinstance(retraction, MessageRetractionReturn)
        publisher.retract(retraction.handle)

        publisher.time_advance_request(config.sender_advance_time)
        drain_callbacks(publisher, subscriber)

        subscriber.time_advance_request_available(config.receiver_window_time)
        drain_callbacks(publisher, subscriber)
        available_grant = subscriber_federate.last_callback("timeAdvanceGrant")

        subscriber.next_message_request_available(config.receiver_window_time)
        drain_callbacks(publisher, subscriber)
        after_retract_callbacks = subscriber_federate.callbacks_named("receiveInteraction")

        subscriber.flush_queue_request(config.receiver_window_time)
        drain_callbacks(publisher, subscriber)
        flush_grant = subscriber_federate.last_callback("timeAdvanceGrant")

        return {
            "publisher_federate": publisher_federate,
            "subscriber_federate": subscriber_federate,
            "parameter": subscriber_parameter,
            "available_grant": available_grant,
            "after_retract_callbacks": after_retract_callbacks,
            "flush_grant": flush_grant,
        }
    finally:
        cleanup_section8_pair(publisher, subscriber, config.federation_name)


def run_section8_available_and_flush_case(
    publisher: Any,
    subscriber: Any,
    *,
    config: Section8MatrixConfig,
    publisher_federate: RecordingFederateAmbassador | None = None,
    subscriber_federate: RecordingFederateAmbassador | None = None,
) -> dict[str, Any]:
    publisher_federate, subscriber_federate = connect_section8_pair(
        publisher,
        subscriber,
        config=config,
        publisher_federate=publisher_federate,
        subscriber_federate=subscriber_federate,
    )
    try:
        publisher_interaction = publisher.get_interaction_class_handle(config.interaction_class_name)
        publisher_parameter = publisher.get_parameter_handle(publisher_interaction, config.parameter_name)
        subscriber_interaction = subscriber.get_interaction_class_handle(config.interaction_class_name)
        subscriber_parameter = subscriber.get_parameter_handle(subscriber_interaction, config.parameter_name)
        publisher.publish_interaction_class(publisher_interaction)
        subscriber.subscribe_interaction_class(subscriber_interaction)

        publisher.enable_time_regulation(config.lookahead)
        subscriber.enable_time_constrained()
        drain_callbacks(publisher, subscriber)

        publisher.send_interaction(
            publisher_interaction,
            {publisher_parameter: config.second_payload},
            config.second_tag,
            config.second_timestamp,
        )
        publisher.time_advance_request(config.sender_advance_time)
        drain_callbacks(publisher, subscriber)

        subscriber.time_advance_request_available(config.receiver_window_time)
        drain_callbacks(publisher, subscriber)
        available_grant = subscriber_federate.last_callback("timeAdvanceGrant")

        subscriber.flush_queue_request(config.receiver_window_time)
        drain_callbacks(publisher, subscriber)
        flush_grant = subscriber_federate.last_callback("timeAdvanceGrant")
        flushed_receive = subscriber_federate.last_callback("receiveInteraction")

        return {
            "publisher_federate": publisher_federate,
            "subscriber_federate": subscriber_federate,
            "parameter": subscriber_parameter,
            "available_grant": available_grant,
            "flush_grant": flush_grant,
            "flushed_receive": flushed_receive,
        }
    finally:
        cleanup_section8_pair(publisher, subscriber, config.federation_name)


def run_section8_order_override_case(
    publisher: Any,
    subscriber: Any,
    *,
    config: Section8MatrixConfig,
    publisher_federate: RecordingFederateAmbassador | None = None,
    subscriber_federate: RecordingFederateAmbassador | None = None,
) -> dict[str, Any]:
    publisher_federate, subscriber_federate = connect_section8_pair(
        publisher,
        subscriber,
        config=config,
        publisher_federate=publisher_federate,
        subscriber_federate=subscriber_federate,
    )
    try:
        publisher_object_class = publisher.get_object_class_handle(config.object_class_name)
        publisher_attribute = publisher.get_attribute_handle(publisher_object_class, config.attribute_name)
        publisher_interaction = publisher.get_interaction_class_handle(config.order_interaction_class_name)
        publisher_parameter = publisher.get_parameter_handle(publisher_interaction, config.order_parameter_name)
        subscriber_object_class = subscriber.get_object_class_handle(config.object_class_name)
        subscriber_attribute = subscriber.get_attribute_handle(subscriber_object_class, config.attribute_name)
        subscriber_interaction = subscriber.get_interaction_class_handle(config.order_interaction_class_name)
        subscriber_parameter = subscriber.get_parameter_handle(subscriber_interaction, config.order_parameter_name)

        publisher.publish_object_class_attributes(publisher_object_class, {publisher_attribute})
        subscriber.subscribe_object_class_attributes(subscriber_object_class, {subscriber_attribute})
        publisher.publish_interaction_class(publisher_interaction)
        subscriber.subscribe_interaction_class(subscriber_interaction)

        publisher.enable_time_regulation(config.lookahead)
        subscriber.enable_time_constrained()
        drain_callbacks(publisher, subscriber)

        instance = publisher.register_object_instance(publisher_object_class)
        drain_callbacks(publisher, subscriber)

        publisher.change_attribute_order_type(instance, {publisher_attribute}, OrderType.RECEIVE)
        publisher.change_interaction_order_type(publisher_interaction, OrderType.RECEIVE)

        publisher.update_attribute_values(
            instance,
            {publisher_attribute: config.first_payload},
            config.first_tag,
            config.first_timestamp,
        )
        publisher.send_interaction(
            publisher_interaction,
            {publisher_parameter: config.second_payload},
            config.second_tag,
            config.second_timestamp,
        )
        drain_callbacks(publisher, subscriber)

        reflect = subscriber_federate.last_callback("reflectAttributeValues")
        receive = subscriber_federate.last_callback("receiveInteraction")

        return {
            "publisher_federate": publisher_federate,
            "subscriber_federate": subscriber_federate,
            "attribute": subscriber_attribute,
            "parameter": subscriber_parameter,
            "reflect": reflect,
            "receive": receive,
        }
    finally:
        cleanup_section8_pair(publisher, subscriber, config.federation_name)


def run_section8_request_retraction_case(
    publisher: Any,
    subscriber: Any,
    *,
    config: Section8MatrixConfig,
    publisher_federate: RecordingFederateAmbassador | None = None,
    subscriber_federate: RecordingFederateAmbassador | None = None,
) -> dict[str, Any]:
    publisher_federate, subscriber_federate = connect_section8_pair(
        publisher,
        subscriber,
        config=config,
        publisher_federate=publisher_federate,
        subscriber_federate=subscriber_federate,
    )
    try:
        publisher_interaction = publisher.get_interaction_class_handle(config.interaction_class_name)
        publisher_parameter = publisher.get_parameter_handle(publisher_interaction, config.parameter_name)
        subscriber_interaction = subscriber.get_interaction_class_handle(config.interaction_class_name)
        subscriber_parameter = subscriber.get_parameter_handle(subscriber_interaction, config.parameter_name)
        publisher.publish_interaction_class(publisher_interaction)
        subscriber.subscribe_interaction_class(subscriber_interaction)

        publisher.enable_time_regulation(config.lookahead)
        subscriber.enable_time_constrained()
        drain_callbacks(publisher, subscriber)

        sent = publisher.send_interaction(
            publisher_interaction,
            {publisher_parameter: config.first_payload},
            config.first_tag,
            config.first_timestamp,
        )
        assert isinstance(sent, MessageRetractionReturn)

        publisher.time_advance_request(config.sender_advance_time)
        drain_callbacks(publisher, subscriber)

        subscriber.next_message_request(config.receiver_window_time)
        drain_callbacks(publisher, subscriber)
        received = subscriber_federate.last_callback("receiveInteraction")

        publisher.retract(sent.handle)
        drain_callbacks(publisher, subscriber)
        request_retraction = subscriber_federate.last_callback("requestRetraction")

        return {
            "publisher_federate": publisher_federate,
            "subscriber_federate": subscriber_federate,
            "parameter": subscriber_parameter,
            "sent": sent,
            "received": received,
            "request_retraction": request_retraction,
        }
    finally:
        cleanup_section8_pair(publisher, subscriber, config.federation_name)


def run_section8_duplicate_enable_rejection_case(
    publisher: Any,
    subscriber: Any,
    *,
    config: Section8MatrixConfig,
    publisher_federate: RecordingFederateAmbassador | None = None,
    subscriber_federate: RecordingFederateAmbassador | None = None,
) -> dict[str, Any]:
    publisher_federate, subscriber_federate = connect_section8_pair(
        publisher,
        subscriber,
        config=config,
        publisher_federate=publisher_federate,
        subscriber_federate=subscriber_federate,
    )
    try:
        publisher.enable_time_regulation(config.lookahead)
        subscriber.enable_time_constrained()
        drain_callbacks(publisher, subscriber)

        initial_regulation_callback_count = len(publisher_federate.callbacks_named("timeRegulationEnabled"))
        initial_constrained_callback_count = len(subscriber_federate.callbacks_named("timeConstrainedEnabled"))

        regulation_error = None
        try:
            publisher.enable_time_regulation(config.lookahead)
        except TimeRegulationAlreadyEnabled as exc:
            regulation_error = exc

        constrained_error = None
        try:
            subscriber.enable_time_constrained()
        except TimeConstrainedAlreadyEnabled as exc:
            constrained_error = exc

        drain_callbacks(publisher, subscriber)

        return {
            "regulation_error": regulation_error,
            "constrained_error": constrained_error,
            "initial_regulation_callback_count": initial_regulation_callback_count,
            "initial_constrained_callback_count": initial_constrained_callback_count,
            "final_regulation_callback_count": len(publisher_federate.callbacks_named("timeRegulationEnabled")),
            "final_constrained_callback_count": len(subscriber_federate.callbacks_named("timeConstrainedEnabled")),
        }
    finally:
        cleanup_section8_pair(publisher, subscriber, config.federation_name)


def run_section8_tar_galt_boundary_case(
    publisher: Any,
    subscriber: Any,
    *,
    config: Section8MatrixConfig,
    publisher_federate: RecordingFederateAmbassador | None = None,
    subscriber_federate: RecordingFederateAmbassador | None = None,
) -> dict[str, Any]:
    publisher_federate, subscriber_federate = connect_section8_pair(
        publisher,
        subscriber,
        config=config,
        publisher_federate=publisher_federate,
        subscriber_federate=subscriber_federate,
    )
    try:
        publisher.enable_time_regulation(config.lookahead)
        subscriber.enable_time_constrained()
        drain_callbacks(publisher, subscriber)

        publisher.time_advance_request(config.sender_advance_time)
        drain_callbacks(publisher, subscriber)
        equal_galt = subscriber.query_galt()

        subscriber.time_advance_request(equal_galt.time)
        drain_callbacks(publisher, subscriber)

        return {
            "equal_galt": equal_galt,
            "grant": subscriber_federate.last_callback("timeAdvanceGrant"),
        }
    finally:
        cleanup_section8_pair(publisher, subscriber, config.federation_name)


__all__ = [
    "Section8MatrixConfig",
    "run_section8_available_and_flush_case",
    "cleanup_section8_pair",
    "connect_section8_pair",
    "drain_callbacks",
    "run_section8_available_and_retraction_case",
    "run_section8_duplicate_enable_rejection_case",
    "run_section8_early_timestamp_send_case",
    "run_section8_order_override_case",
    "run_section8_ordering_and_query_case",
    "run_section8_tar_galt_boundary_case",
    "run_section8_time_bound_query_case",
    "run_section8_request_retraction_case",
    "run_section8_state_services_case",
    "section8_matrix_config",
    "vendor_smoke_fom_path",
]
