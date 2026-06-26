# ruff: noqa: F401,F403

import pytest

from hla.backends.common.base import BackendConversionError
from hla.rti1516e.enums import CallbackModel, OrderType, ResignAction
from hla.rti1516e.exceptions import (
    AttributeNotDefined,
    AttributeNotPublished,
    FederateNotExecutionMember,
    InTimeAdvancingState,
    InteractionClassNotPublished,
    InteractionParameterNotDefined,
    InvalidInteractionClassHandle,
    InvalidLogicalTime,
    InvalidObjectClassHandle,
    InvalidRegion,
    InvalidUpdateRateDesignator,
    LogicalTimeAlreadyPassed,
    NotConnected,
    ObjectInstanceNameInUse,
    ObjectInstanceNotKnown,
    RestoreInProgress,
    SaveInProgress,
)
from hla.rti1516e.handles import (
    AttributeHandle,
    AttributeSetRegionSetPairList,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    RegionHandle,
    TransportationTypeHandle,
)
from hla.rti1516e.datatypes import (
    AttributeHandleSet,
    AttributeRegionAssociation,
    RangeBounds,
    RegionHandleSet,
    TimeQueryReturn,
)

from tests.backends.python_backend_extended_support import *
from tests.backends.python_backend_extended_support import (
    _ImmediateConstrainedPendingAmbassador,
    _ImmediateRegulationPendingAmbassador,
)


def _joined_group(name: str, count: int):
    engine = InMemoryRTIEngine()
    rtis = [rti_ambassador(engine=engine) for _ in range(count)]
    feds = [RecordingFederateAmbassador() for _ in range(count)]
    for rti, fed in zip(rtis, feds):
        rti.connect(fed, CallbackModel.HLA_EVOKED)
    rtis[0].create_federation_execution(name, "TargetRadarFOMmodule.xml")
    handles = [
        rti.join_federation_execution(f"fed-{index}", f"type-{index}", name)
        for index, rti in enumerate(rtis)
    ]
    return engine, rtis, feds, handles


def _region_pairs(attribute: AttributeHandle, region: RegionHandle) -> list[AttributeRegionAssociation]:
    return [AttributeRegionAssociation(AttributeHandleSet({attribute}), RegionHandleSet({region}))]


def test_flush_queue_request_delivers_only_grant_bound_tso_messages_and_grants_earliest_tso():
    _, sender, receiver, _sender_fed, receiver_fed, _h1, _h2 = joined_pair("flush-queue-fed")
    cls = sender.get_object_class_handle("HLAobjectRoot.Target")
    attr = sender.get_attribute_handle(cls, "Position")
    factory = sender.get_time_factory()

    sender.publish_object_class_attributes(cls, {attr})
    receiver.subscribe_object_class_attributes(cls, {attr})
    sender.enable_time_regulation(factory.make_interval(1.0))
    receiver.enable_time_constrained()
    drain(sender, receiver)

    obj = sender.register_object_instance(cls, "FlushTarget")
    drain(sender, receiver)
    receiver_fed.clear()

    sender.update_attribute_values(obj, {attr: b"five"}, b"t5", factory.make_time(5.0))
    sender.update_attribute_values(obj, {attr: b"three"}, b"t3", factory.make_time(3.0))
    drain(sender, receiver)
    assert not receiver_fed.callbacks_named("reflectAttributeValues")

    sender.time_advance_request(factory.make_time(10.0))
    drain(sender, receiver)
    receiver.flush_queue_request(factory.make_time(6.0))
    drain(sender, receiver)

    reflections = receiver_fed.callbacks_named("reflectAttributeValues")
    assert [rec.args[1][attr] for rec in reflections] == [b"three"]
    grant = receiver_fed.last_callback("timeAdvanceGrant")
    assert grant is not None
    assert getattr(grant.args[0], "value") == 3.0

    sender.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    receiver.resign_federation_execution(ResignAction.NO_ACTION)
    sender.destroy_federation_execution("flush-queue-fed")


def test_flush_queue_request_without_queued_messages_is_galt_bounded():
    _, sender, receiver, _sender_fed, receiver_fed, _h1, _h2 = joined_pair("flush-queue-galt-fed")
    factory = sender.get_time_factory()

    sender.enable_time_regulation(factory.make_interval(1.0))
    receiver.enable_time_constrained()
    drain(sender, receiver)

    sender.time_advance_request(factory.make_time(4.0))
    drain(sender, receiver)
    assert receiver.query_galt().time == factory.make_time(5.0)

    receiver.flush_queue_request(factory.make_time(6.0))
    drain(sender, receiver)

    assert not receiver_fed.callbacks_named("reflectAttributeValues")
    grant = receiver_fed.last_callback("timeAdvanceGrant")
    assert grant is not None
    assert grant.args[0] == factory.make_time(5.0)

    sender.resign_federation_execution(ResignAction.NO_ACTION)
    receiver.resign_federation_execution(ResignAction.NO_ACTION)
    sender.destroy_federation_execution("flush-queue-galt-fed")


def test_time_queries_report_invalid_when_no_time_regulating_federate_contributes():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("time-query-invalid-fed")

    galt = r1.query_galt()
    lits = r1.query_lits()

    assert isinstance(galt, TimeQueryReturn)
    assert isinstance(lits, TimeQueryReturn)
    assert galt.time_is_valid is False
    assert galt.time is None
    assert lits.time_is_valid is False
    assert lits.time is None

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("time-query-invalid-fed")


@pytest.mark.parametrize(
    ("method_name", "logical_time"),
    (
        ("time_advance_request", 5.0),
        ("time_advance_request_available", 5.0),
        ("next_message_request", 5.0),
        ("next_message_request_available", 5.0),
        ("flush_queue_request", 5.0),
    ),
)
def test_time_advance_services_reject_not_connected_not_joined_invalid_and_past_time(method_name, logical_time):
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    method = getattr(rti, method_name)
    with pytest.raises(NotConnected):
        method(logical_time)

    fed = RecordingFederateAmbassador()
    rti.connect(fed, CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        method(logical_time)
    rti.disconnect()

    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair(f"{method_name}-negative-fed")
    bound_method = getattr(r1, method_name)
    with pytest.raises(BackendConversionError):
        bound_method(object())

    factory = r1.get_time_factory()
    r1.time_advance_request(factory.make_time(3.0))
    drain(r1, r2)
    with pytest.raises(LogicalTimeAlreadyPassed):
        bound_method(factory.make_time(2.0))

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution(f"{method_name}-negative-fed")


@pytest.mark.parametrize(
    "method_name",
    (
        "time_advance_request",
        "time_advance_request_available",
        "next_message_request",
        "next_message_request_available",
        "flush_queue_request",
    ),
)
def test_time_advance_services_reject_save_restore_and_outstanding_advance(method_name):
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair(f"{method_name}-blocked-fed")
    method = getattr(r1, method_name)
    factory = r1.get_time_factory()
    requested = factory.make_time(5.0)

    r1.request_federation_save(f"{method_name}-save")
    drain(r1, r2)
    with pytest.raises(SaveInProgress):
        method(requested)

    r1.federate_save_begun()
    r2.federate_save_begun()
    r1.federate_save_complete()
    r2.federate_save_complete()
    drain(r1, r2)

    r1.request_federation_restore(f"{method_name}-save")
    drain(r1, r2)
    with pytest.raises(RestoreInProgress):
        method(requested)

    r1.abort_federation_restore()
    drain(r1, r2)
    r1.backend.state.time_advancing = True
    with pytest.raises(InTimeAdvancingState):
        method(requested)
    r1.backend.state.time_advancing = False

    r1.resign_federation_execution(ResignAction.NO_ACTION)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution(f"{method_name}-blocked-fed")


def test_async_delivery_and_order_type_services_update_runtime_state():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("time-service-switches-fed")
    cls = r1.get_object_class_handle("HLAobjectRoot.Target")
    attr = r1.get_attribute_handle(cls, "Position")
    interaction = r1.get_interaction_class_handle("HLAinteractionRoot.TrackReport")

    obj = r1.register_object_instance(cls, "OrderTarget")
    drain(r1, r2)

    assert r1.backend.state.asynchronous_delivery_enabled is False
    r1.enable_asynchronous_delivery()
    assert r1.backend.state.asynchronous_delivery_enabled is True
    r1.disable_asynchronous_delivery()
    assert r1.backend.state.asynchronous_delivery_enabled is False

    r1.change_attribute_order_type(obj, {attr}, OrderType.TIMESTAMP)
    assert r1.backend.state.attribute_order_overrides[(obj, attr)] is OrderType.TIMESTAMP

    r1.change_interaction_order_type(interaction, OrderType.TIMESTAMP)
    assert r1.backend.state.interaction_order_overrides[interaction] is OrderType.TIMESTAMP

    r1.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("time-service-switches-fed")


def test_ddm_region_subscription_update_and_unsubscribe_lifecycle():
    _, tx, rx, tx_fed, rx_fed, _h1, _h2 = joined_pair("ddm-lifecycle-fed")
    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "Position")
    dim = tx.get_dimension_handle("HLAdefaultRoutingSpace")
    interaction = tx.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    track_id = tx.get_parameter_handle(interaction, "TrackId")

    tx_region = tx.create_region({dim})
    rx_region = rx.create_region({dim})
    tx.set_range_bounds(tx_region, dim, RangeBounds(10, 20))
    rx.set_range_bounds(rx_region, dim, RangeBounds(15, 25))
    tx.commit_region_modifications({tx_region})
    rx.commit_region_modifications({rx_region})

    update_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({tx_region}))]
    subscription_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx_region}))]

    rx.subscribe_object_class_attributes_with_regions(cls, subscription_pairs)
    assert rx.backend.state.object_region_subscriptions[cls][attr] == {rx_region}

    tx.publish_object_class_attributes(cls, {attr})
    obj = tx.register_object_instance_with_regions(cls, update_pairs, "DDM-Region-Object")
    drain(tx, rx)
    assert rx_fed.last_callback("discoverObjectInstance") is not None
    assert tx.backend.state.update_regions[obj][attr] == {tx_region}

    tx.unassociate_regions_for_updates(obj, update_pairs)
    assert attr not in tx.backend.state.update_regions.get(obj, {})
    tx.associate_regions_for_updates(obj, update_pairs)
    assert tx.backend.state.update_regions[obj][attr] == {tx_region}

    rx.request_attribute_value_update_with_regions(cls, subscription_pairs, b"refresh-ddm")
    drain(tx, rx)
    provide = tx_fed.last_callback("provideAttributeValueUpdate")
    assert provide is not None
    assert provide.args[0] == obj
    assert provide.args[2] == b"refresh-ddm"

    tx.publish_interaction_class(interaction)
    rx.subscribe_interaction_class_with_regions(interaction, {rx_region})
    assert rx.backend.state.interaction_region_subscriptions[interaction] == {rx_region}

    tx.send_interaction_with_regions(interaction, {track_id: b"match"}, {tx_region}, b"ddm-match")
    drain(tx, rx)
    received = rx_fed.last_callback("receiveInteraction")
    assert received is not None
    assert received.args[0] == interaction
    assert received.args[1][track_id] == b"match"

    rx_fed.clear()
    rx.unsubscribe_interaction_class_with_regions(interaction, {rx_region})
    assert interaction not in rx.backend.state.interaction_region_subscriptions
    tx.send_interaction_with_regions(interaction, {track_id: b"after-unsub"}, {tx_region}, b"ddm-after-unsub")
    drain(tx, rx)
    assert not rx_fed.callbacks_named("receiveInteraction")

    rx.unsubscribe_object_class_attributes_with_regions(cls, subscription_pairs)
    assert cls not in rx.backend.state.object_region_subscriptions

    tx.delete_region(tx_region)
    rx.delete_region(rx_region)
    assert tx_region not in tx.backend.state.regions
    assert rx_region not in rx.backend.state.regions

    tx.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("ddm-lifecycle-fed")


def test_dm_publication_and_ddm_subscriptions_route_object_updates_and_interactions():
    _, tx, rx, _tx_fed, rx_fed, _h1, _h2 = joined_pair("dm-ddm-interplay-fed")
    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "Position")
    dim = tx.get_dimension_handle("HLAdefaultRoutingSpace")
    interaction = tx.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    track_id = tx.get_parameter_handle(interaction, "TrackId")

    tx_region = tx.create_region({dim})
    rx_region = rx.create_region({dim})
    tx.set_range_bounds(tx_region, dim, RangeBounds(10, 20))
    rx.set_range_bounds(rx_region, dim, RangeBounds(15, 25))
    tx.commit_region_modifications({tx_region})
    rx.commit_region_modifications({rx_region})

    update_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({tx_region}))]
    subscription_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx_region}))]

    tx.publish_object_class_attributes(cls, {attr})
    rx.subscribe_object_class_attributes_with_regions(cls, subscription_pairs)
    obj = tx.register_object_instance_with_regions(cls, update_pairs, "DM-DDM-Object")
    drain(tx, rx)

    discovery = rx_fed.last_callback("discoverObjectInstance")
    assert discovery is not None
    assert discovery.args[0] == obj
    rx_fed.clear()

    tx.update_attribute_values(obj, {attr: b"region-update"}, b"dm-ddm-update")
    drain(tx, rx)
    reflection = rx_fed.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection.args[0] == obj
    assert reflection.args[1] == {attr: b"region-update"}

    tx.publish_interaction_class(interaction)
    rx.subscribe_interaction_class_with_regions(interaction, {rx_region})
    rx_fed.clear()
    tx.send_interaction_with_regions(interaction, {track_id: b"region-track"}, {tx_region}, b"dm-ddm-track")
    drain(tx, rx)

    received = rx_fed.last_callback("receiveInteraction")
    assert received is not None
    assert received.args[0] == interaction
    assert received.args[1][track_id] == b"region-track"

    tx.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("dm-ddm-interplay-fed")


def test_dm_ddm_subscriptions_gate_discovery_reflect_and_receive_until_declared():
    _, tx, rx, _tx_fed, rx_fed, _h1, _h2 = joined_pair("dm-ddm-gating-fed")
    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "Position")
    dim = tx.get_dimension_handle("HLAdefaultRoutingSpace")
    interaction = tx.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    track_id = tx.get_parameter_handle(interaction, "TrackId")

    tx_region = tx.create_region({dim})
    rx_region = rx.create_region({dim})
    tx.set_range_bounds(tx_region, dim, RangeBounds(10, 20))
    rx.set_range_bounds(rx_region, dim, RangeBounds(10, 20))
    tx.commit_region_modifications({tx_region})
    rx.commit_region_modifications({rx_region})

    update_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({tx_region}))]
    subscription_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx_region}))]

    tx.publish_object_class_attributes(cls, {attr})
    tx.publish_interaction_class(interaction)
    obj = tx.register_object_instance_with_regions(cls, update_pairs, "DM-DDM-Gating-Object")
    drain(tx, rx)
    assert rx_fed.last_callback("discoverObjectInstance") is None

    tx.update_attribute_values(obj, {attr: b"before-subscription"}, b"dm-ddm-before")
    tx.send_interaction_with_regions(interaction, {track_id: b"before-subscription"}, {tx_region}, b"dm-ddm-before")
    drain(tx, rx)
    assert rx_fed.last_callback("reflectAttributeValues") is None
    assert rx_fed.last_callback("receiveInteraction") is None

    rx.subscribe_object_class_attributes_with_regions(cls, subscription_pairs)
    rx.subscribe_interaction_class_with_regions(interaction, {rx_region})
    drain(tx, rx)

    discovery = rx_fed.last_callback("discoverObjectInstance")
    assert discovery is not None
    assert discovery.args[0] == obj
    rx_fed.clear()

    tx.update_attribute_values(obj, {attr: b"after-subscription"}, b"dm-ddm-after")
    tx.send_interaction_with_regions(interaction, {track_id: b"after-subscription"}, {tx_region}, b"dm-ddm-after")
    drain(tx, rx)

    reflection = rx_fed.last_callback("reflectAttributeValues")
    received = rx_fed.last_callback("receiveInteraction")
    assert reflection is not None
    assert reflection.args[0] == obj
    assert reflection.args[1] == {attr: b"after-subscription"}
    assert received is not None
    assert received.args[0] == interaction
    assert received.args[1][track_id] == b"after-subscription"

    tx.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("dm-ddm-gating-fed")


def test_unsubscribe_object_class_attributes_removes_interest_in_future_reflections():
    _, tx, rx, _tx_fed, rx_fed, _h1, _h2 = joined_pair("dm-unsubscribe-interest-fed")
    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "Position")

    tx.publish_object_class_attributes(cls, {attr})
    rx.subscribe_object_class_attributes(cls, {attr})
    obj = tx.register_object_instance(cls, "DM-Unsubscribe-Object")
    drain(tx, rx)
    assert rx_fed.last_callback("discoverObjectInstance") is not None

    rx.unsubscribe_object_class_attributes(cls, {attr})
    assert cls not in rx.backend.state.subscribed_objects
    rx_fed.clear()

    tx.update_attribute_values(obj, {attr: b"after-unsubscribe"}, b"dm-after-unsubscribe")
    drain(tx, rx)
    assert not rx_fed.callbacks_named("reflectAttributeValues")

    tx.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("dm-unsubscribe-interest-fed")


def test_unsubscribe_interaction_class_removes_interest_in_future_interactions():
    _, tx, rx, _tx_fed, rx_fed, _h1, _h2 = joined_pair("dm-unsubscribe-interaction-fed")
    interaction = tx.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    track_id = tx.get_parameter_handle(interaction, "TrackId")

    tx.publish_interaction_class(interaction)
    rx.subscribe_interaction_class(interaction)
    tx.send_interaction(interaction, {track_id: b"before-unsubscribe"}, b"dm-before-unsubscribe")
    drain(tx, rx)
    received = rx_fed.last_callback("receiveInteraction")
    assert received is not None
    assert received.args[0] == interaction
    assert received.args[1][track_id] == b"before-unsubscribe"

    rx.unsubscribe_interaction_class(interaction)
    assert interaction not in rx.backend.state.subscribed_interactions
    rx_fed.clear()

    tx.send_interaction(interaction, {track_id: b"after-unsubscribe"}, b"dm-after-unsubscribe")
    drain(tx, rx)
    assert not rx_fed.callbacks_named("receiveInteraction")

    tx.resign_federation_execution(ResignAction.NO_ACTION)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("dm-unsubscribe-interaction-fed")


def test_ddm_object_scope_filter_blocks_out_of_scope_reflects_until_regions_overlap():
    _, tx, rx, _tx_fed, rx_fed, _h1, _h2 = joined_pair("ddm-object-scope-fed")
    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "Position")
    dim = tx.get_dimension_handle("HLAdefaultRoutingSpace")

    tx_region = tx.create_region({dim})
    rx_region = rx.create_region({dim})
    tx.set_range_bounds(tx_region, dim, RangeBounds(0, 10))
    rx.set_range_bounds(rx_region, dim, RangeBounds(90, 100))
    tx.commit_region_modifications({tx_region})
    rx.commit_region_modifications({rx_region})

    tx.publish_object_class_attributes(cls, {attr})
    rx.subscribe_object_class_attributes_with_regions(
        cls,
        [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx_region}))],
    )
    obj = tx.register_object_instance_with_regions(
        cls,
        [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({tx_region}))],
        "DDM-Scope-Object",
    )
    drain(tx, rx)
    rx_fed.clear()

    tx.update_attribute_values(obj, {attr: b"out-of-scope"}, b"ddm-out")
    drain(tx, rx)
    assert not rx_fed.callbacks_named("reflectAttributeValues")

    rx.set_range_bounds(rx_region, dim, RangeBounds(5, 15))
    rx.commit_region_modifications({rx_region})
    tx.update_attribute_values(obj, {attr: b"in-scope"}, b"ddm-in")
    drain(tx, rx)

    reflection = rx_fed.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection.args[1] == {attr: b"in-scope"}

    tx.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("ddm-object-scope-fed")


def test_attributes_in_scope_and_out_of_scope_callbacks_track_region_scope_transitions():
    _, tx, rx, _tx_fed, rx_fed, _h1, _h2 = joined_pair("ddm-scope-callbacks-fed")
    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "Position")
    dim = tx.get_dimension_handle("HLAdefaultRoutingSpace")

    tx_region = tx.create_region({dim})
    rx_region = rx.create_region({dim})
    tx.set_range_bounds(tx_region, dim, RangeBounds(0, 10))
    rx.set_range_bounds(rx_region, dim, RangeBounds(90, 100))
    tx.commit_region_modifications({tx_region})
    rx.commit_region_modifications({rx_region})

    tx.publish_object_class_attributes(cls, {attr})
    rx.enable_attribute_scope_advisory_switch()
    rx.subscribe_object_class_attributes_with_regions(
        cls,
        [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx_region}))],
    )
    obj = tx.register_object_instance_with_regions(
        cls,
        [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({tx_region}))],
        "DDM-Scope-Callbacks-Object",
    )
    drain(tx, rx)
    assert rx_fed.last_callback("discoverObjectInstance") is not None
    assert not rx_fed.callbacks_named("attributesInScope")
    assert not rx_fed.callbacks_named("attributesOutOfScope")

    rx.set_range_bounds(rx_region, dim, RangeBounds(5, 15))
    rx.commit_region_modifications({rx_region})
    drain(tx, rx)

    gained = rx_fed.last_callback("attributesInScope")
    assert gained is not None
    assert gained.args == (obj, {attr})

    rx.set_range_bounds(rx_region, dim, RangeBounds(50, 60))
    rx.commit_region_modifications({rx_region})
    drain(tx, rx)

    lost = rx_fed.last_callback("attributesOutOfScope")
    assert lost is not None
    assert lost.args == (obj, {attr})

    tx.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("ddm-scope-callbacks-fed")


def test_request_attribute_value_update_routes_only_to_relevant_object_owners():
    _, rtis, feds, _handles = _joined_group("request-avu-routing-fed", 3)
    owner_a, owner_b, requester = rtis
    owner_a_fed, owner_b_fed, requester_fed = feds
    cls = owner_a.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner_a.get_attribute_handle(cls, "Position")

    owner_a.publish_object_class_attributes(cls, {attr})
    owner_b.publish_object_class_attributes(cls, {attr})
    requester.subscribe_object_class_attributes(cls, {attr})

    obj_a = owner_a.register_object_instance(cls, "Requester-Object-A")
    obj_b = owner_b.register_object_instance(cls, "Requester-Object-B")
    drain(owner_a, owner_b, requester)
    requester_fed.clear()
    owner_a_fed.clear()
    owner_b_fed.clear()

    requester.request_attribute_value_update(obj_a, {attr}, b"object-only")
    drain(owner_a, owner_b, requester)
    provide_a = owner_a_fed.last_callback("provideAttributeValueUpdate")
    assert provide_a is not None
    assert provide_a.args == (obj_a, {attr}, b"object-only")
    assert owner_b_fed.last_callback("provideAttributeValueUpdate") is None

    owner_a_fed.clear()
    owner_b_fed.clear()
    requester.request_attribute_value_update(cls, {attr}, b"class-wide")
    drain(owner_a, owner_b, requester)
    assert owner_a_fed.last_callback("provideAttributeValueUpdate").args == (obj_a, {attr}, b"class-wide")
    assert owner_b_fed.last_callback("provideAttributeValueUpdate").args == (obj_b, {attr}, b"class-wide")

    owner_a.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    owner_b.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    requester.resign_federation_execution(ResignAction.NO_ACTION)
    owner_a.destroy_federation_execution("request-avu-routing-fed")


def test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    invalid_interaction = InteractionClassHandle(999999)
    invalid_regions = {RegionHandle(999999)}
    with pytest.raises(NotConnected):
        rti.send_interaction_with_regions(invalid_interaction, {}, invalid_regions, b"tag")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.send_interaction_with_regions(invalid_interaction, {}, invalid_regions, b"tag")
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("ddm-send-negative-fed")
    interaction = tx.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    track_id = tx.get_parameter_handle(interaction, "TrackId")
    region = tx.create_region({tx.get_dimension_handle("HLAdefaultRoutingSpace")})
    invalid_region = type(tx.create_region({tx.get_dimension_handle("HLAdefaultRoutingSpace")}))(999999)
    with pytest.raises(InvalidRegion):
        tx.send_interaction_with_regions(interaction, {track_id: b"x"}, {invalid_region}, b"tag")
    with pytest.raises(InvalidInteractionClassHandle):
        tx.send_interaction_with_regions(type(interaction)(interaction.value + 1000), {track_id: b"x"}, {region}, b"tag")
    with pytest.raises(InteractionParameterNotDefined):
        tx.send_interaction_with_regions(interaction, {type(track_id)(track_id.value + 1000): b"x"}, {region}, b"tag")

    tx.request_federation_save("DDM-SEND-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        tx.send_interaction_with_regions(interaction, {track_id: b"x"}, set(), b"tag")

    tx.federate_save_begun()
    rx.federate_save_begun()
    tx.federate_save_complete()
    rx.federate_save_complete()
    drain(tx, rx)

    tx.request_federation_restore("DDM-SEND-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        tx.send_interaction_with_regions(interaction, {track_id: b"x"}, set(), b"tag")

    tx.abort_federation_restore()
    drain(tx, rx)
    tx.resign_federation_execution(ResignAction.NO_ACTION)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("ddm-send-negative-fed")


def test_strict_publication_gates_registration_update_and_interaction_sends():
    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("strict-publication-fed")
    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "Position")
    rcs = tx.get_attribute_handle(cls, "RCS")
    interaction = tx.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    track_id = tx.get_parameter_handle(interaction, "TrackId")
    dim = tx.get_dimension_handle("HLAdefaultRoutingSpace")
    region = tx.create_region({dim})
    pair = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({region}))]
    unpublished_pair = [AttributeRegionAssociation(AttributeHandleSet({rcs}), RegionHandleSet({region}))]

    with pytest.raises(InvalidObjectClassHandle):
        tx.register_object_instance(type(cls)(cls.value + 1000), "Bad-Class")
    with pytest.raises(InvalidObjectClassHandle):
        tx.register_object_instance_with_regions(type(cls)(cls.value + 1000), pair, "Bad-Class-Regions")

    obj = tx.register_object_instance(cls, "Strict-Update-Object")
    with pytest.raises(ObjectInstanceNameInUse):
        tx.register_object_instance_with_regions(cls, pair, "Strict-Update-Object")
    tx.backend.config.strict_object_publication = True
    with pytest.raises(AttributeNotPublished):
        tx.update_attribute_values(obj, {attr: b"strict"}, b"tag")
    with pytest.raises(AttributeNotPublished):
        tx.register_object_instance_with_regions(cls, unpublished_pair, "Strict-Unpublished-Object")

    tx.backend.config.strict_object_publication = False
    tx.backend.config.strict_interaction_publication = True
    with pytest.raises(InteractionClassNotPublished):
        tx.send_interaction(interaction, {track_id: b"no-pub"}, b"tag")
    with pytest.raises(InteractionClassNotPublished):
        tx.send_interaction_with_regions(interaction, {track_id: b"no-pub"}, {region}, b"tag")
    with pytest.raises(InvalidInteractionClassHandle):
        tx.send_interaction(type(interaction)(interaction.value + 1000), {track_id: b"no-pub"}, b"tag")

    tx.backend.config.strict_interaction_publication = False
    tx.request_federation_save("STRICT-PUBLICATION-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        tx.register_object_instance(cls, "Strict-Save-Object")
    with pytest.raises(SaveInProgress):
        tx.register_object_instance_with_regions(cls, pair, "Strict-Save-Region-Object")

    tx.federate_save_begun()
    rx.federate_save_begun()
    tx.federate_save_complete()
    rx.federate_save_complete()
    drain(tx, rx)

    tx.request_federation_restore("STRICT-PUBLICATION-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        tx.register_object_instance(cls, "Strict-Restore-Object")
    with pytest.raises(RestoreInProgress):
        tx.register_object_instance_with_regions(cls, pair, "Strict-Restore-Region-Object")

    tx.abort_federation_restore()
    drain(tx, rx)

    factory = tx.get_time_factory()
    tx.enable_time_regulation(factory.make_interval(1.0))
    rx.enable_time_constrained()
    drain(tx, rx)

    tx.time_advance_request(factory.make_time(2.0))
    drain(tx, rx)
    with pytest.raises(InvalidLogicalTime):
        tx.update_attribute_values(obj, {attr: b"timed"}, b"tag", factory.make_time(1.0))
    with pytest.raises(InvalidLogicalTime):
        tx.send_interaction(interaction, {track_id: b"timed"}, b"tag", factory.make_time(1.0))
    with pytest.raises(InvalidLogicalTime):
        tx.send_interaction_with_regions(interaction, {track_id: b"timed"}, {region}, b"tag", factory.make_time(1.0))

    tx.backend.config.strict_interaction_publication = False
    tx.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("strict-publication-fed")


def test_request_attribute_value_update_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    invalid_pairs = _region_pairs(AttributeHandle(999999), RegionHandle(999999))
    with pytest.raises(NotConnected):
        rti.request_attribute_value_update_with_regions(ObjectClassHandle(999999), invalid_pairs, b"tag")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.request_attribute_value_update_with_regions(ObjectClassHandle(999999), invalid_pairs, b"tag")
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("ddm-ravu-negative-fed")
    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "Position")
    invalid_region = type(tx.create_region({tx.get_dimension_handle("HLAdefaultRoutingSpace")}))(999999)
    pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({invalid_region}))]
    with pytest.raises(InvalidRegion):
        rx.request_attribute_value_update_with_regions(cls, pairs, b"tag")
    bad_class = type(cls)(cls.value + 1000)
    with pytest.raises(InvalidObjectClassHandle):
        rx.request_attribute_value_update_with_regions(
            bad_class,
            [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx.create_region({rx.get_dimension_handle("HLAdefaultRoutingSpace")})}))],
            b"tag",
        )
    bad_attr = type(attr)(attr.value + 1000)
    with pytest.raises(AttributeNotDefined):
        rx.request_attribute_value_update_with_regions(
            cls,
            [
                AttributeRegionAssociation(
                    AttributeHandleSet({bad_attr}), RegionHandleSet({rx.create_region({rx.get_dimension_handle("HLAdefaultRoutingSpace")})})
                )
            ],
            b"tag",
        )

    tx.request_federation_save("DDM-RAVU-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        rx.request_attribute_value_update_with_regions(cls, [], b"tag")

    tx.federate_save_begun()
    rx.federate_save_begun()
    tx.federate_save_complete()
    rx.federate_save_complete()
    drain(tx, rx)

    tx.request_federation_restore("DDM-RAVU-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        rx.request_attribute_value_update_with_regions(cls, [], b"tag")

    tx.abort_federation_restore()
    drain(tx, rx)
    tx.resign_federation_execution(ResignAction.NO_ACTION)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("ddm-ravu-negative-fed")


def test_associate_regions_for_updates_rejects_not_connected_not_joined_unknown_object_invalid_region_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.associate_regions_for_updates(ObjectInstanceHandle(999), [])

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.associate_regions_for_updates(ObjectInstanceHandle(999), [])
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("associate-regions-negative-fed")
    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "Position")
    with pytest.raises(ObjectInstanceNotKnown):
        tx.associate_regions_for_updates(ObjectInstanceHandle(999), [])

    invalid_region = type(tx.create_region({tx.get_dimension_handle("HLAdefaultRoutingSpace")}))(999999)
    pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({invalid_region}))]
    obj = tx.register_object_instance(cls, "Associate-Negative")
    with pytest.raises(InvalidRegion):
        tx.associate_regions_for_updates(obj, pairs)

    tx.request_federation_save("ASSOC-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        tx.associate_regions_for_updates(obj, [])

    tx.federate_save_begun()
    rx.federate_save_begun()
    tx.federate_save_complete()
    rx.federate_save_complete()
    drain(tx, rx)

    tx.request_federation_restore("ASSOC-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        tx.associate_regions_for_updates(obj, [])

    tx.abort_federation_restore()
    drain(tx, rx)
    tx.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("associate-regions-negative-fed")


def test_unassociate_regions_for_updates_rejects_not_connected_not_joined_unknown_object_invalid_region_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.unassociate_regions_for_updates(ObjectInstanceHandle(999), [])

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.unassociate_regions_for_updates(ObjectInstanceHandle(999), [])
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("unassociate-regions-negative-fed")
    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "Position")
    with pytest.raises(ObjectInstanceNotKnown):
        tx.unassociate_regions_for_updates(ObjectInstanceHandle(999), [])

    dim = tx.get_dimension_handle("HLAdefaultRoutingSpace")
    invalid_region = type(tx.create_region({dim}))(999999)
    tx_region = tx.create_region({dim})
    pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({invalid_region}))]
    valid_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({tx_region}))]
    obj = tx.register_object_instance(cls, "Unassociate-Negative")
    tx.associate_regions_for_updates(obj, valid_pairs)
    with pytest.raises(InvalidRegion):
        tx.unassociate_regions_for_updates(obj, pairs)

    tx.request_federation_save("UNASSOC-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        tx.unassociate_regions_for_updates(obj, valid_pairs)

    tx.federate_save_begun()
    rx.federate_save_begun()
    tx.federate_save_complete()
    rx.federate_save_complete()
    drain(tx, rx)

    tx.request_federation_restore("UNASSOC-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        tx.unassociate_regions_for_updates(obj, valid_pairs)

    tx.abort_federation_restore()
    drain(tx, rx)
    tx.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("unassociate-regions-negative-fed")


@pytest.mark.parametrize(
    ("method_name", "kind"),
    (
        ("subscribe_object_class_attributes_with_regions", "object"),
        ("subscribe_object_class_attributes_passively_with_regions", "object"),
        ("subscribe_interaction_class_with_regions", "interaction"),
        ("subscribe_interaction_class_passively_with_regions", "interaction"),
    ),
)
def test_ddm_region_subscriptions_reject_not_connected_not_joined_and_invalid_region(method_name, kind):
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    if kind == "object":
        invalid_pairs = _region_pairs(AttributeHandle(999999), RegionHandle(999999))
        with pytest.raises(NotConnected):
            getattr(rti, method_name)(ObjectClassHandle(999999), invalid_pairs)
    else:
        invalid_regions = {RegionHandle(999999)}
        with pytest.raises(NotConnected):
            getattr(rti, method_name)(InteractionClassHandle(999999), invalid_regions)

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    if kind == "object":
        with pytest.raises(FederateNotExecutionMember):
            getattr(rti, method_name)(ObjectClassHandle(999999), invalid_pairs)
    else:
        with pytest.raises(FederateNotExecutionMember):
            getattr(rti, method_name)(InteractionClassHandle(999999), invalid_regions)
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair(f"{method_name}-negative-fed")
    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "Position")
    interaction = tx.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    dim = tx.get_dimension_handle("HLAdefaultRoutingSpace")
    region = rx.create_region({dim})
    invalid_region = type(tx.create_region({tx.get_dimension_handle("HLAdefaultRoutingSpace")}))(999999)
    if kind == "object":
        pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({invalid_region}))]
        with pytest.raises(InvalidRegion):
            getattr(rx, method_name)(cls, pairs)
        bad_class = type(cls)(cls.value + 1000)
        with pytest.raises(InvalidObjectClassHandle):
            getattr(rx, method_name)(bad_class, [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({region}))])
        bad_attr = type(attr)(attr.value + 1000)
        with pytest.raises(AttributeNotDefined):
            getattr(rx, method_name)(cls, [AttributeRegionAssociation(AttributeHandleSet({bad_attr}), RegionHandleSet({region}))])
        with pytest.raises(InvalidUpdateRateDesignator):
            getattr(rx, method_name)(cls, [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({region}))], "bad-rate")
    else:
        with pytest.raises(InvalidRegion):
            getattr(rx, method_name)(interaction, {invalid_region})
        bad_interaction = type(interaction)(interaction.value + 1000)
        with pytest.raises(InvalidInteractionClassHandle):
            getattr(rx, method_name)(bad_interaction, {region})

    tx.request_federation_save(f"{method_name}-save")
    drain(tx, rx)
    if kind == "object":
        with pytest.raises(SaveInProgress):
            getattr(rx, method_name)(cls, [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({region}))])
    else:
        with pytest.raises(SaveInProgress):
            getattr(rx, method_name)(interaction, {region})

    tx.federate_save_begun()
    rx.federate_save_begun()
    tx.federate_save_complete()
    rx.federate_save_complete()
    drain(tx, rx)

    tx.request_federation_restore(f"{method_name}-save")
    drain(tx, rx)
    if kind == "object":
        with pytest.raises(RestoreInProgress):
            getattr(rx, method_name)(cls, [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({region}))])
    else:
        with pytest.raises(RestoreInProgress):
            getattr(rx, method_name)(interaction, {region})

    tx.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution(f"{method_name}-negative-fed")


def test_register_object_instance_with_regions_rejects_not_connected_not_joined_and_invalid_region():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    invalid_pairs = _region_pairs(AttributeHandle(999999), RegionHandle(999999))
    with pytest.raises(NotConnected):
        rti.register_object_instance_with_regions(ObjectClassHandle(999999), invalid_pairs, "bad")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.register_object_instance_with_regions(ObjectClassHandle(999999), invalid_pairs, "bad")
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("register-with-regions-negative-fed")
    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "Position")
    rcs = tx.get_attribute_handle(cls, "RCS")
    tx.publish_object_class_attributes(cls, {attr})
    invalid_region = type(tx.create_region({tx.get_dimension_handle("HLAdefaultRoutingSpace")}))(999999)
    pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({invalid_region}))]
    with pytest.raises(InvalidRegion):
        tx.register_object_instance_with_regions(cls, pairs, "bad-region-object")
    with pytest.raises(AttributeNotDefined):
        tx.register_object_instance_with_regions(
            cls,
            [
                AttributeRegionAssociation(
                    AttributeHandleSet({type(attr)(attr.value + 1000)}),
                    RegionHandleSet({tx.create_region({tx.get_dimension_handle("HLAdefaultRoutingSpace")})}),
                )
            ],
            "bad-attr-object",
        )

    tx.backend.config.strict_object_publication = True
    with pytest.raises(AttributeNotPublished):
        tx.register_object_instance_with_regions(
            cls,
            [AttributeRegionAssociation(AttributeHandleSet({rcs}), RegionHandleSet({tx.create_region({tx.get_dimension_handle("HLAdefaultRoutingSpace")})}))],
            "strict-unpublished-object",
        )

    tx.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("register-with-regions-negative-fed")


def test_unsubscribe_object_class_attributes_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    invalid_pairs = _region_pairs(AttributeHandle(999999), RegionHandle(999999))
    with pytest.raises(NotConnected):
        rti.unsubscribe_object_class_attributes_with_regions(ObjectClassHandle(999999), invalid_pairs)

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.unsubscribe_object_class_attributes_with_regions(ObjectClassHandle(999999), invalid_pairs)
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("unsubscribe-ocar-negative-fed")
    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "Position")
    bad_attr = type(attr)(attr.value + 1000)
    invalid_region = type(tx.create_region({tx.get_dimension_handle("HLAdefaultRoutingSpace")}))(999999)
    bad_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({invalid_region}))]
    with pytest.raises(InvalidRegion):
        rx.unsubscribe_object_class_attributes_with_regions(cls, bad_pairs)
    with pytest.raises(AttributeNotDefined):
        rx.unsubscribe_object_class_attributes_with_regions(
            cls,
            [
                AttributeRegionAssociation(
                    AttributeHandleSet({bad_attr}), RegionHandleSet({rx.create_region({rx.get_dimension_handle("HLAdefaultRoutingSpace")})})
                )
            ],
        )

    rx.request_federation_save("UNSUB-OCAR-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        rx.unsubscribe_object_class_attributes_with_regions(cls, [])

    tx.federate_save_begun()
    rx.federate_save_begun()
    tx.federate_save_complete()
    rx.federate_save_complete()
    drain(tx, rx)

    rx.request_federation_restore("UNSUB-OCAR-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        rx.unsubscribe_object_class_attributes_with_regions(cls, [])

    rx.abort_federation_restore()
    drain(tx, rx)
    tx.resign_federation_execution(ResignAction.NO_ACTION)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("unsubscribe-ocar-negative-fed")


def test_unsubscribe_interaction_class_with_regions_and_delete_region_reject_not_connected_not_joined_invalid_region_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    invalid_regions = {RegionHandle(999999)}
    invalid_region = RegionHandle(999999)
    with pytest.raises(NotConnected):
        rti.unsubscribe_interaction_class_with_regions(InteractionClassHandle(999999), invalid_regions)
    with pytest.raises(NotConnected):
        rti.delete_region(invalid_region)

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.unsubscribe_interaction_class_with_regions(InteractionClassHandle(999999), invalid_regions)
    with pytest.raises(FederateNotExecutionMember):
        rti.delete_region(invalid_region)
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("unsub-icwr-delete-region-negative-fed")
    interaction = tx.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    dim = rx.get_dimension_handle("HLAdefaultRoutingSpace")
    region = rx.create_region({dim})
    invalid_region = type(region)(999999)

    with pytest.raises(InvalidRegion):
        rx.unsubscribe_interaction_class_with_regions(interaction, {invalid_region})
    with pytest.raises(InvalidRegion):
        rx.delete_region(invalid_region)

    rx.request_federation_save("UNSUB-ICWR-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        rx.unsubscribe_interaction_class_with_regions(interaction, {region})
    with pytest.raises(SaveInProgress):
        rx.delete_region(region)

    tx.federate_save_begun()
    rx.federate_save_begun()
    tx.federate_save_complete()
    rx.federate_save_complete()
    drain(tx, rx)

    rx.request_federation_restore("UNSUB-ICWR-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        rx.unsubscribe_interaction_class_with_regions(interaction, {region})
    with pytest.raises(RestoreInProgress):
        rx.delete_region(region)

    rx.abort_federation_restore()
    drain(tx, rx)
    tx.resign_federation_execution(ResignAction.NO_ACTION)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("unsub-icwr-delete-region-negative-fed")


def test_create_region_and_commit_region_modifications_reject_not_connected_not_joined_invalid_region_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.create_region(set())
    with pytest.raises(NotConnected):
        rti.commit_region_modifications(set())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.create_region(set())
    with pytest.raises(FederateNotExecutionMember):
        rti.commit_region_modifications(set())
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("create-commit-region-negative-fed")
    dim = tx.get_dimension_handle("HLAdefaultRoutingSpace")
    region = tx.create_region({dim})
    invalid_region = type(region)(999999)

    with pytest.raises(InvalidRegion):
        tx.commit_region_modifications({invalid_region})

    tx.request_federation_save("REGION-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        tx.create_region({dim})
    with pytest.raises(SaveInProgress):
        tx.commit_region_modifications({region})

    tx.federate_save_begun()
    rx.federate_save_begun()
    tx.federate_save_complete()
    rx.federate_save_complete()
    drain(tx, rx)

    tx.request_federation_restore("REGION-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        tx.create_region({dim})
    with pytest.raises(RestoreInProgress):
        tx.commit_region_modifications({region})

    tx.abort_federation_restore()
    drain(tx, rx)
    tx.resign_federation_execution(ResignAction.NO_ACTION)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("create-commit-region-negative-fed")


def test_ddm_passive_region_subscriptions_behave_like_active_region_subscriptions():
    _, tx, rx, tx_fed, rx_fed, _h1, _h2 = joined_pair("ddm-passive-fed")
    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    attr = tx.get_attribute_handle(cls, "Position")
    dim = tx.get_dimension_handle("HLAdefaultRoutingSpace")
    interaction = tx.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    track_id = tx.get_parameter_handle(interaction, "TrackId")

    tx_region = tx.create_region({dim})
    rx_region = rx.create_region({dim})
    tx.set_range_bounds(tx_region, dim, RangeBounds(10, 20))
    rx.set_range_bounds(rx_region, dim, RangeBounds(15, 25))
    tx.commit_region_modifications({tx_region})
    rx.commit_region_modifications({rx_region})

    update_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({tx_region}))]
    subscription_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx_region}))]

    rx.subscribe_object_class_attributes_passively_with_regions(cls, subscription_pairs)
    tx.publish_object_class_attributes(cls, {attr})
    obj = tx.register_object_instance_with_regions(cls, update_pairs, "DDM-Passive-Object")
    drain(tx, rx)
    assert rx_fed.last_callback("discoverObjectInstance") is not None

    tx.publish_interaction_class(interaction)
    rx.subscribe_interaction_class_passively_with_regions(interaction, {rx_region})
    tx.send_interaction_with_regions(interaction, {track_id: b"passive-match"}, {tx_region}, b"passive-ddm")
    drain(tx, rx)
    received = rx_fed.last_callback("receiveInteraction")
    assert received is not None
    assert received.args[0] == interaction
    assert received.args[1][track_id] == b"passive-match"
    assert tx_fed.last_callback("provideAttributeValueUpdate") is None

    rx.unsubscribe_object_class_attributes_with_regions(cls, subscription_pairs)
    rx.unsubscribe_interaction_class_with_regions(interaction, {rx_region})

    tx.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("ddm-passive-fed")


def test_name_reservation_ddm_regions_ownership_and_time_support():
    _, r1, r2, f1, f2, h1, h2 = joined_pair("ddm-ownership-fed")
    cls = r1.get_object_class_handle("HLAobjectRoot.Target")
    attr = r1.get_attribute_handle(cls, "Position")

    r1.reserve_object_instance_name("ReservedTarget")
    drain(r1)
    assert f1.last_callback("objectInstanceNameReservationSucceeded").args == ("ReservedTarget",)
    r2.reserve_object_instance_name("ReservedTarget")
    drain(r2)
    assert f2.last_callback("objectInstanceNameReservationFailed").args == ("ReservedTarget",)

    r1.publish_object_class_attributes(cls, {attr})
    r2.publish_object_class_attributes(cls, {attr})
    obj = r1.register_object_instance(cls, "ReservedTarget")
    assert r1.is_attribute_owned_by_federate(obj, attr)
    r1.unconditional_attribute_ownership_divestiture(obj, {attr})
    assert not r1.is_attribute_owned_by_federate(obj, attr)
    r2.attribute_ownership_acquisition_if_available(obj, {attr})
    drain(r2)
    acquired = f2.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired.args[0] == obj
    assert isinstance(acquired.args[1], AttributeHandleSet)
    assert r2.is_attribute_owned_by_federate(obj, attr)
    r1.query_attribute_ownership(obj, attr)
    drain(r1)
    assert f1.last_callback("informAttributeOwnership").args == (obj, attr, h2)

    dim = r1.get_dimension_handle("HLAdefaultRoutingSpace")
    region = r1.create_region({dim})
    r1.set_range_bounds(region, dim, RangeBounds(10, 20))
    assert r1.get_range_bounds(region, dim) == RangeBounds(10, 20)
    assert r1.get_dimension_upper_bound(dim) > 20
    assert dim in r1.get_available_dimensions_for_class_attribute(cls, attr)

    assert r1.get_order_name(OrderType.RECEIVE) == "RECEIVE"
    assert r1.get_order_type("HLAreceive") is OrderType.RECEIVE
    assert r1.decode_message_retraction_handle(MessageRetractionHandle(7).encoded()) == MessageRetractionHandle(7)
    assert isinstance(r1.query_galt(), TimeQueryReturn)
    assert r1.normalize_federate_handle(h1) == h1

    r1.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    r2.resign_federation_execution(ResignAction.NO_ACTION)
    r1.destroy_federation_execution("ddm-ownership-fed")


def test_support_service_roundtrips_and_callback_controls_have_exact_behavior():
    _, owner, observer, owner_fed, observer_fed, h1, h2 = joined_pair("support-controls-fed")

    assert owner.get_federate_name(h1) == "alpha"
    assert owner.get_federate_name(h2) == "bravo"
    assert owner.get_federate_handle("bravo") == h2

    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    assert owner.get_object_class_name(cls) == "HLAobjectRoot.Target"
    attr = owner.get_attribute_handle(cls, "Position")
    assert owner.get_attribute_name(cls, attr) == "Position"

    interaction = owner.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    assert owner.get_interaction_class_name(interaction) == "HLAinteractionRoot.TrackReport"
    track_id = owner.get_parameter_handle(interaction, "TrackId")
    assert owner.get_parameter_name(interaction, track_id) == "TrackId"

    dim = owner.get_dimension_handle("HLAdefaultRoutingSpace")
    assert owner.get_dimension_name(dim) == "HLAdefaultRoutingSpace"
    region = owner.create_region({dim})
    assert dim in owner.get_dimension_handle_set(region)
    pair_list_factory = owner.get_attribute_set_region_set_pair_list_factory()
    assert isinstance(pair_list_factory.create(), AttributeSetRegionSetPairList)

    owner.publish_object_class_attributes(cls, {attr})
    observer.subscribe_object_class_attributes(cls, {attr})

    queued = owner.register_object_instance(cls, "Queued-Target")
    owner.update_attribute_values(queued, {attr: b"queued"}, b"queued-tag")
    observer.disable_callbacks()
    assert observer.evoke_multiple_callbacks(0.0, 0.0) is False
    observer.enable_callbacks()
    assert observer.evoke_multiple_callbacks(0.0, 0.0) is True
    assert observer_fed.last_callback("discoverObjectInstance") is not None
    assert observer_fed.last_callback("reflectAttributeValues").args[1] == {attr: b"queued"}

    observer_fed.clear()
    owner.update_attribute_values(queued, {attr: b"single"}, b"single-tag")
    assert observer.evoke_callback(0.0) is False
    assert observer_fed.last_callback("reflectAttributeValues").args[1] == {attr: b"single"}

    assert owner.get_object_instance_name(queued) == "Queued-Target"
    assert owner.get_object_instance_handle("Queued-Target") == queued
    assert owner.get_known_object_class_handle(queued) == cls
    assert owner.get_hla_version().startswith("HLA 1516-2010")
    assert owner.normalize_federate_handle(h1) == h1

    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("support-controls-fed")


def test_time_query_tail_rejects_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.query_galt()
    with pytest.raises(NotConnected):
        rti.query_logical_time()
    with pytest.raises(NotConnected):
        rti.query_lits()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.query_galt()
    with pytest.raises(FederateNotExecutionMember):
        rti.query_logical_time()
    with pytest.raises(FederateNotExecutionMember):
        rti.query_lits()
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("time-query-negative-fed")
    owner.request_federation_save("TIME-QUERY-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.query_galt()
    with pytest.raises(SaveInProgress):
        owner.query_logical_time()
    with pytest.raises(SaveInProgress):
        owner.query_lits()

    owner.federate_save_begun()
    observer.federate_save_begun()
    owner.federate_save_complete()
    observer.federate_save_complete()
    drain(owner, observer)

    owner.request_federation_restore("TIME-QUERY-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.query_galt()
    with pytest.raises(RestoreInProgress):
        owner.query_logical_time()
    with pytest.raises(RestoreInProgress):
        owner.query_lits()

    owner.abort_federation_restore()
    drain(owner, observer)
    owner.resign_federation_execution(ResignAction.NO_ACTION)
    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.destroy_federation_execution("time-query-negative-fed")


def test_hla_immediate_callback_model_delivers_object_callbacks_inline_without_evocation():
    engine = InMemoryRTIEngine()
    owner = rti_ambassador(engine=engine)
    observer = rti_ambassador(engine=engine)
    owner_fed = RecordingFederateAmbassador()
    observer_fed = RecordingFederateAmbassador()

    owner.connect(owner_fed, CallbackModel.HLA_EVOKED)
    observer.connect(observer_fed, CallbackModel.HLA_IMMEDIATE)
    owner.create_federation_execution("immediate-callback-fed", "TargetRadarFOMmodule.xml")
    owner.join_federation_execution("alpha", "type-a", "immediate-callback-fed")
    observer.join_federation_execution("bravo", "type-b", "immediate-callback-fed")

    cls = owner.get_object_class_handle("HLAobjectRoot.Target")
    attr = owner.get_attribute_handle(cls, "Position")
    owner.publish_object_class_attributes(cls, {attr})
    observer.subscribe_object_class_attributes(cls, {attr})

    obj = owner.register_object_instance(cls, "ImmediateTarget")
    owner.update_attribute_values(obj, {attr: b"now"}, b"tag")

    assert observer_fed.last_callback("discoverObjectInstance") is not None
    assert observer_fed.last_callback("reflectAttributeValues").args[1] == {attr: b"now"}
    assert observer.evoke_multiple_callbacks(0.0, 0.0) is False

    observer.resign_federation_execution(ResignAction.NO_ACTION)
    owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    owner.destroy_federation_execution("immediate-callback-fed")


def test_hla_immediate_time_enable_callbacks_expose_pending_request_exceptions():
    engine = InMemoryRTIEngine()
    regulator = rti_ambassador(engine=engine)
    constrained = rti_ambassador(engine=engine)
    regulator_fed = _ImmediateRegulationPendingAmbassador(regulator)
    constrained_fed = _ImmediateConstrainedPendingAmbassador(constrained)

    regulator.connect(regulator_fed, CallbackModel.HLA_IMMEDIATE)
    constrained.connect(constrained_fed, CallbackModel.HLA_IMMEDIATE)
    regulator.create_federation_execution("immediate-time-fed", "TargetRadarFOMmodule.xml")
    regulator.join_federation_execution("alpha", "type-a", "immediate-time-fed")
    constrained.join_federation_execution("bravo", "type-b", "immediate-time-fed")

    regulator.enable_time_regulation(regulator.get_time_factory().make_interval(1.0))
    constrained.enable_time_constrained()

    assert regulator_fed.last_callback("timeRegulationEnabled") is not None
    assert constrained_fed.last_callback("timeConstrainedEnabled") is not None
    assert regulator_fed.captured == [
        CallNotAllowedFromWithinCallback,
        CallNotAllowedFromWithinCallback,
        CallNotAllowedFromWithinCallback,
        CallNotAllowedFromWithinCallback,
        CallNotAllowedFromWithinCallback,
        CallNotAllowedFromWithinCallback,
    ]
    assert constrained_fed.captured == [
        CallNotAllowedFromWithinCallback,
        CallNotAllowedFromWithinCallback,
        CallNotAllowedFromWithinCallback,
        CallNotAllowedFromWithinCallback,
        CallNotAllowedFromWithinCallback,
        CallNotAllowedFromWithinCallback,
    ]

    constrained.resign_federation_execution(ResignAction.NO_ACTION)
    regulator.resign_federation_execution(ResignAction.NO_ACTION)
    regulator.destroy_federation_execution("immediate-time-fed")
