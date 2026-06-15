# ruff: noqa: F401,F403

import pytest

from hla2010.enums import CallbackModel, OrderType, ResignAction
from hla2010.exceptions import (
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
from hla2010.handles import (
    AttributeSetRegionSetPairList,
    MessageRetractionHandle,
    ObjectInstanceHandle,
    TransportationTypeHandle,
)
from hla2010.types import (
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
    rtis[0].createFederationExecution(name, "TargetRadarFOMmodule.xml")
    handles = [
        rti.joinFederationExecution(f"fed-{index}", f"type-{index}", name)
        for index, rti in enumerate(rtis)
    ]
    return engine, rtis, feds, handles


def test_flush_queue_request_delivers_only_grant_bound_tso_messages_and_grants_earliest_tso():
    _, sender, receiver, _sender_fed, receiver_fed, _h1, _h2 = joined_pair("flush-queue-fed")
    cls = sender.getObjectClassHandle("HLAobjectRoot.Target")
    attr = sender.getAttributeHandle(cls, "Position")
    factory = sender.getTimeFactory()

    sender.publishObjectClassAttributes(cls, {attr})
    receiver.subscribeObjectClassAttributes(cls, {attr})
    sender.enableTimeRegulation(factory.make_interval(1.0))
    receiver.enableTimeConstrained()
    drain(sender, receiver)

    obj = sender.registerObjectInstance(cls, "FlushTarget")
    drain(sender, receiver)
    receiver_fed.clear()

    sender.updateAttributeValues(obj, {attr: b"five"}, b"t5", factory.make_time(5.0))
    sender.updateAttributeValues(obj, {attr: b"three"}, b"t3", factory.make_time(3.0))
    drain(sender, receiver)
    assert not receiver_fed.callbacks_named("reflectAttributeValues")

    sender.timeAdvanceRequest(factory.make_time(10.0))
    drain(sender, receiver)
    receiver.flushQueueRequest(factory.make_time(6.0))
    drain(sender, receiver)

    reflections = receiver_fed.callbacks_named("reflectAttributeValues")
    assert [rec.args[1][attr] for rec in reflections] == [b"three"]
    grant = receiver_fed.last_callback("timeAdvanceGrant")
    assert grant is not None
    assert getattr(grant.args[0], "value") == 3.0

    sender.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    receiver.resignFederationExecution(ResignAction.NO_ACTION)
    sender.destroyFederationExecution("flush-queue-fed")


def test_flush_queue_request_without_queued_messages_is_galt_bounded():
    _, sender, receiver, _sender_fed, receiver_fed, _h1, _h2 = joined_pair("flush-queue-galt-fed")
    factory = sender.getTimeFactory()

    sender.enableTimeRegulation(factory.make_interval(1.0))
    receiver.enableTimeConstrained()
    drain(sender, receiver)

    sender.timeAdvanceRequest(factory.make_time(4.0))
    drain(sender, receiver)
    assert receiver.queryGALT().time == factory.make_time(5.0)

    receiver.flushQueueRequest(factory.make_time(6.0))
    drain(sender, receiver)

    assert not receiver_fed.callbacks_named("reflectAttributeValues")
    grant = receiver_fed.last_callback("timeAdvanceGrant")
    assert grant is not None
    assert grant.args[0] == factory.make_time(5.0)

    sender.resignFederationExecution(ResignAction.NO_ACTION)
    receiver.resignFederationExecution(ResignAction.NO_ACTION)
    sender.destroyFederationExecution("flush-queue-galt-fed")


def test_time_queries_report_invalid_when_no_time_regulating_federate_contributes():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("time-query-invalid-fed")

    galt = r1.queryGALT()
    lits = r1.queryLITS()

    assert isinstance(galt, TimeQueryReturn)
    assert isinstance(lits, TimeQueryReturn)
    assert galt.time_is_valid is False
    assert galt.time is None
    assert lits.time_is_valid is False
    assert lits.time is None

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("time-query-invalid-fed")


@pytest.mark.parametrize(
    ("method_name", "logical_time"),
    (
        ("timeAdvanceRequest", 5.0),
        ("timeAdvanceRequestAvailable", 5.0),
        ("nextMessageRequest", 5.0),
        ("nextMessageRequestAvailable", 5.0),
        ("flushQueueRequest", 5.0),
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
    with pytest.raises(InvalidLogicalTime):
        bound_method(object())

    factory = r1.getTimeFactory()
    r1.timeAdvanceRequest(factory.make_time(3.0))
    drain(r1, r2)
    with pytest.raises(LogicalTimeAlreadyPassed):
        bound_method(factory.make_time(2.0))

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution(f"{method_name}-negative-fed")


@pytest.mark.parametrize(
    "method_name",
    (
        "timeAdvanceRequest",
        "timeAdvanceRequestAvailable",
        "nextMessageRequest",
        "nextMessageRequestAvailable",
        "flushQueueRequest",
    ),
)
def test_time_advance_services_reject_save_restore_and_outstanding_advance(method_name):
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair(f"{method_name}-blocked-fed")
    method = getattr(r1, method_name)
    factory = r1.getTimeFactory()
    requested = factory.make_time(5.0)

    r1.requestFederationSave(f"{method_name}-save")
    drain(r1, r2)
    with pytest.raises(SaveInProgress):
        method(requested)

    r1.federateSaveBegun()
    r2.federateSaveBegun()
    r1.federateSaveComplete()
    r2.federateSaveComplete()
    drain(r1, r2)

    r1.requestFederationRestore(f"{method_name}-save")
    drain(r1, r2)
    with pytest.raises(RestoreInProgress):
        method(requested)

    r1.abortFederationRestore()
    drain(r1, r2)
    r1.backend.state.time_advancing = True
    with pytest.raises(InTimeAdvancingState):
        method(requested)
    r1.backend.state.time_advancing = False

    r1.resignFederationExecution(ResignAction.NO_ACTION)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution(f"{method_name}-blocked-fed")


def test_async_delivery_and_order_type_services_update_runtime_state():
    _, r1, r2, _f1, _f2, _h1, _h2 = joined_pair("time-service-switches-fed")
    cls = r1.getObjectClassHandle("HLAobjectRoot.Target")
    attr = r1.getAttributeHandle(cls, "Position")
    interaction = r1.getInteractionClassHandle("HLAinteractionRoot.TrackReport")

    obj = r1.registerObjectInstance(cls, "OrderTarget")
    drain(r1, r2)

    assert r1.backend.state.asynchronous_delivery_enabled is False
    r1.enableAsynchronousDelivery()
    assert r1.backend.state.asynchronous_delivery_enabled is True
    r1.disableAsynchronousDelivery()
    assert r1.backend.state.asynchronous_delivery_enabled is False

    r1.changeAttributeOrderType(obj, {attr}, OrderType.TIMESTAMP)
    assert r1.backend.state.attribute_order_overrides[(obj, attr)] is OrderType.TIMESTAMP

    r1.changeInteractionOrderType(interaction, OrderType.TIMESTAMP)
    assert r1.backend.state.interaction_order_overrides[interaction] is OrderType.TIMESTAMP

    r1.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("time-service-switches-fed")


def test_ddm_region_subscription_update_and_unsubscribe_lifecycle():
    _, tx, rx, tx_fed, rx_fed, _h1, _h2 = joined_pair("ddm-lifecycle-fed")
    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "Position")
    dim = tx.getDimensionHandle("HLAdefaultRoutingSpace")
    interaction = tx.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = tx.getParameterHandle(interaction, "TrackId")

    tx_region = tx.createRegion({dim})
    rx_region = rx.createRegion({dim})
    tx.setRangeBounds(tx_region, dim, RangeBounds(10, 20))
    rx.setRangeBounds(rx_region, dim, RangeBounds(15, 25))
    tx.commitRegionModifications({tx_region})
    rx.commitRegionModifications({rx_region})

    update_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({tx_region}))]
    subscription_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx_region}))]

    rx.subscribeObjectClassAttributesWithRegions(cls, subscription_pairs)
    assert rx.backend.state.object_region_subscriptions[cls][attr] == {rx_region}

    tx.publishObjectClassAttributes(cls, {attr})
    obj = tx.registerObjectInstanceWithRegions(cls, update_pairs, "DDM-Region-Object")
    drain(tx, rx)
    assert rx_fed.last_callback("discoverObjectInstance") is not None
    assert tx.backend.state.update_regions[obj][attr] == {tx_region}

    tx.unassociateRegionsForUpdates(obj, update_pairs)
    assert attr not in tx.backend.state.update_regions.get(obj, {})
    tx.associateRegionsForUpdates(obj, update_pairs)
    assert tx.backend.state.update_regions[obj][attr] == {tx_region}

    rx.requestAttributeValueUpdateWithRegions(obj, subscription_pairs, b"refresh-ddm")
    drain(tx, rx)
    provide = tx_fed.last_callback("provideAttributeValueUpdate")
    assert provide is not None
    assert provide.args[0] == obj
    assert provide.args[2] == b"refresh-ddm"

    tx.publishInteractionClass(interaction)
    rx.subscribeInteractionClassWithRegions(interaction, {rx_region})
    assert rx.backend.state.interaction_region_subscriptions[interaction] == {rx_region}

    tx.sendInteractionWithRegions(interaction, {track_id: b"match"}, {tx_region}, b"ddm-match")
    drain(tx, rx)
    received = rx_fed.last_callback("receiveInteraction")
    assert received is not None
    assert received.args[0] == interaction
    assert received.args[1][track_id] == b"match"

    rx_fed.clear()
    rx.unsubscribeInteractionClassWithRegions(interaction, {rx_region})
    assert interaction not in rx.backend.state.interaction_region_subscriptions
    tx.sendInteractionWithRegions(interaction, {track_id: b"after-unsub"}, {tx_region}, b"ddm-after-unsub")
    drain(tx, rx)
    assert not rx_fed.callbacks_named("receiveInteraction")

    rx.unsubscribeObjectClassAttributesWithRegions(cls, subscription_pairs)
    assert cls not in rx.backend.state.object_region_subscriptions

    tx.deleteRegion(tx_region)
    rx.deleteRegion(rx_region)
    assert tx_region not in tx.backend.state.regions
    assert rx_region not in rx.backend.state.regions

    tx.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("ddm-lifecycle-fed")


def test_dm_publication_and_ddm_subscriptions_route_object_updates_and_interactions():
    _, tx, rx, _tx_fed, rx_fed, _h1, _h2 = joined_pair("dm-ddm-interplay-fed")
    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "Position")
    dim = tx.getDimensionHandle("HLAdefaultRoutingSpace")
    interaction = tx.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = tx.getParameterHandle(interaction, "TrackId")

    tx_region = tx.createRegion({dim})
    rx_region = rx.createRegion({dim})
    tx.setRangeBounds(tx_region, dim, RangeBounds(10, 20))
    rx.setRangeBounds(rx_region, dim, RangeBounds(15, 25))
    tx.commitRegionModifications({tx_region})
    rx.commitRegionModifications({rx_region})

    update_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({tx_region}))]
    subscription_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx_region}))]

    tx.publishObjectClassAttributes(cls, {attr})
    rx.subscribeObjectClassAttributesWithRegions(cls, subscription_pairs)
    obj = tx.registerObjectInstanceWithRegions(cls, update_pairs, "DM-DDM-Object")
    drain(tx, rx)

    discovery = rx_fed.last_callback("discoverObjectInstance")
    assert discovery is not None
    assert discovery.args[0] == obj
    rx_fed.clear()

    tx.updateAttributeValues(obj, {attr: b"region-update"}, b"dm-ddm-update")
    drain(tx, rx)
    reflection = rx_fed.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection.args[0] == obj
    assert reflection.args[1] == {attr: b"region-update"}

    tx.publishInteractionClass(interaction)
    rx.subscribeInteractionClassWithRegions(interaction, {rx_region})
    rx_fed.clear()
    tx.sendInteractionWithRegions(interaction, {track_id: b"region-track"}, {tx_region}, b"dm-ddm-track")
    drain(tx, rx)

    received = rx_fed.last_callback("receiveInteraction")
    assert received is not None
    assert received.args[0] == interaction
    assert received.args[1][track_id] == b"region-track"

    tx.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("dm-ddm-interplay-fed")


def test_dm_ddm_subscriptions_gate_discovery_reflect_and_receive_until_declared():
    _, tx, rx, _tx_fed, rx_fed, _h1, _h2 = joined_pair("dm-ddm-gating-fed")
    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "Position")
    dim = tx.getDimensionHandle("HLAdefaultRoutingSpace")
    interaction = tx.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = tx.getParameterHandle(interaction, "TrackId")

    tx_region = tx.createRegion({dim})
    rx_region = rx.createRegion({dim})
    tx.setRangeBounds(tx_region, dim, RangeBounds(10, 20))
    rx.setRangeBounds(rx_region, dim, RangeBounds(10, 20))
    tx.commitRegionModifications({tx_region})
    rx.commitRegionModifications({rx_region})

    update_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({tx_region}))]
    subscription_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx_region}))]

    tx.publishObjectClassAttributes(cls, {attr})
    tx.publishInteractionClass(interaction)
    obj = tx.registerObjectInstanceWithRegions(cls, update_pairs, "DM-DDM-Gating-Object")
    drain(tx, rx)
    assert rx_fed.last_callback("discoverObjectInstance") is None

    tx.updateAttributeValues(obj, {attr: b"before-subscription"}, b"dm-ddm-before")
    tx.sendInteractionWithRegions(interaction, {track_id: b"before-subscription"}, {tx_region}, b"dm-ddm-before")
    drain(tx, rx)
    assert rx_fed.last_callback("reflectAttributeValues") is None
    assert rx_fed.last_callback("receiveInteraction") is None

    rx.subscribeObjectClassAttributesWithRegions(cls, subscription_pairs)
    rx.subscribeInteractionClassWithRegions(interaction, {rx_region})
    drain(tx, rx)

    discovery = rx_fed.last_callback("discoverObjectInstance")
    assert discovery is not None
    assert discovery.args[0] == obj
    rx_fed.clear()

    tx.updateAttributeValues(obj, {attr: b"after-subscription"}, b"dm-ddm-after")
    tx.sendInteractionWithRegions(interaction, {track_id: b"after-subscription"}, {tx_region}, b"dm-ddm-after")
    drain(tx, rx)

    reflection = rx_fed.last_callback("reflectAttributeValues")
    received = rx_fed.last_callback("receiveInteraction")
    assert reflection is not None
    assert reflection.args[0] == obj
    assert reflection.args[1] == {attr: b"after-subscription"}
    assert received is not None
    assert received.args[0] == interaction
    assert received.args[1][track_id] == b"after-subscription"

    tx.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("dm-ddm-gating-fed")


def test_unsubscribe_object_class_attributes_removes_interest_in_future_reflections():
    _, tx, rx, _tx_fed, rx_fed, _h1, _h2 = joined_pair("dm-unsubscribe-interest-fed")
    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "Position")

    tx.publishObjectClassAttributes(cls, {attr})
    rx.subscribeObjectClassAttributes(cls, {attr})
    obj = tx.registerObjectInstance(cls, "DM-Unsubscribe-Object")
    drain(tx, rx)
    assert rx_fed.last_callback("discoverObjectInstance") is not None

    rx.unsubscribeObjectClassAttributes(cls, {attr})
    assert cls not in rx.backend.state.subscribed_objects
    rx_fed.clear()

    tx.updateAttributeValues(obj, {attr: b"after-unsubscribe"}, b"dm-after-unsubscribe")
    drain(tx, rx)
    assert not rx_fed.callbacks_named("reflectAttributeValues")

    tx.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("dm-unsubscribe-interest-fed")


def test_unsubscribe_interaction_class_removes_interest_in_future_interactions():
    _, tx, rx, _tx_fed, rx_fed, _h1, _h2 = joined_pair("dm-unsubscribe-interaction-fed")
    interaction = tx.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = tx.getParameterHandle(interaction, "TrackId")

    tx.publishInteractionClass(interaction)
    rx.subscribeInteractionClass(interaction)
    tx.sendInteraction(interaction, {track_id: b"before-unsubscribe"}, b"dm-before-unsubscribe")
    drain(tx, rx)
    received = rx_fed.last_callback("receiveInteraction")
    assert received is not None
    assert received.args[0] == interaction
    assert received.args[1][track_id] == b"before-unsubscribe"

    rx.unsubscribeInteractionClass(interaction)
    assert interaction not in rx.backend.state.subscribed_interactions
    rx_fed.clear()

    tx.sendInteraction(interaction, {track_id: b"after-unsubscribe"}, b"dm-after-unsubscribe")
    drain(tx, rx)
    assert not rx_fed.callbacks_named("receiveInteraction")

    tx.resignFederationExecution(ResignAction.NO_ACTION)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("dm-unsubscribe-interaction-fed")


def test_ddm_object_scope_filter_blocks_out_of_scope_reflects_until_regions_overlap():
    _, tx, rx, _tx_fed, rx_fed, _h1, _h2 = joined_pair("ddm-object-scope-fed")
    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "Position")
    dim = tx.getDimensionHandle("HLAdefaultRoutingSpace")

    tx_region = tx.createRegion({dim})
    rx_region = rx.createRegion({dim})
    tx.setRangeBounds(tx_region, dim, RangeBounds(0, 10))
    rx.setRangeBounds(rx_region, dim, RangeBounds(90, 100))
    tx.commitRegionModifications({tx_region})
    rx.commitRegionModifications({rx_region})

    tx.publishObjectClassAttributes(cls, {attr})
    rx.subscribeObjectClassAttributesWithRegions(
        cls,
        [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx_region}))],
    )
    obj = tx.registerObjectInstanceWithRegions(
        cls,
        [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({tx_region}))],
        "DDM-Scope-Object",
    )
    drain(tx, rx)
    rx_fed.clear()

    tx.updateAttributeValues(obj, {attr: b"out-of-scope"}, b"ddm-out")
    drain(tx, rx)
    assert not rx_fed.callbacks_named("reflectAttributeValues")

    rx.setRangeBounds(rx_region, dim, RangeBounds(5, 15))
    rx.commitRegionModifications({rx_region})
    tx.updateAttributeValues(obj, {attr: b"in-scope"}, b"ddm-in")
    drain(tx, rx)

    reflection = rx_fed.last_callback("reflectAttributeValues")
    assert reflection is not None
    assert reflection.args[1] == {attr: b"in-scope"}

    tx.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("ddm-object-scope-fed")


def test_attributes_in_scope_and_out_of_scope_callbacks_track_region_scope_transitions():
    _, tx, rx, _tx_fed, rx_fed, _h1, _h2 = joined_pair("ddm-scope-callbacks-fed")
    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "Position")
    dim = tx.getDimensionHandle("HLAdefaultRoutingSpace")

    tx_region = tx.createRegion({dim})
    rx_region = rx.createRegion({dim})
    tx.setRangeBounds(tx_region, dim, RangeBounds(0, 10))
    rx.setRangeBounds(rx_region, dim, RangeBounds(90, 100))
    tx.commitRegionModifications({tx_region})
    rx.commitRegionModifications({rx_region})

    tx.publishObjectClassAttributes(cls, {attr})
    rx.enableAttributeScopeAdvisorySwitch()
    rx.subscribeObjectClassAttributesWithRegions(
        cls,
        [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx_region}))],
    )
    obj = tx.registerObjectInstanceWithRegions(
        cls,
        [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({tx_region}))],
        "DDM-Scope-Callbacks-Object",
    )
    drain(tx, rx)
    assert rx_fed.last_callback("discoverObjectInstance") is not None
    assert not rx_fed.callbacks_named("attributesInScope")
    assert not rx_fed.callbacks_named("attributesOutOfScope")

    rx.setRangeBounds(rx_region, dim, RangeBounds(5, 15))
    rx.commitRegionModifications({rx_region})
    drain(tx, rx)

    gained = rx_fed.last_callback("attributesInScope")
    assert gained is not None
    assert gained.args == (obj, {attr})

    rx.setRangeBounds(rx_region, dim, RangeBounds(50, 60))
    rx.commitRegionModifications({rx_region})
    drain(tx, rx)

    lost = rx_fed.last_callback("attributesOutOfScope")
    assert lost is not None
    assert lost.args == (obj, {attr})

    tx.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("ddm-scope-callbacks-fed")


def test_request_attribute_value_update_routes_only_to_relevant_object_owners():
    _, rtis, feds, _handles = _joined_group("request-avu-routing-fed", 3)
    owner_a, owner_b, requester = rtis
    owner_a_fed, owner_b_fed, requester_fed = feds
    cls = owner_a.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner_a.getAttributeHandle(cls, "Position")

    owner_a.publishObjectClassAttributes(cls, {attr})
    owner_b.publishObjectClassAttributes(cls, {attr})
    requester.subscribeObjectClassAttributes(cls, {attr})

    obj_a = owner_a.registerObjectInstance(cls, "Requester-Object-A")
    obj_b = owner_b.registerObjectInstance(cls, "Requester-Object-B")
    drain(owner_a, owner_b, requester)
    requester_fed.clear()
    owner_a_fed.clear()
    owner_b_fed.clear()

    requester.requestAttributeValueUpdate(obj_a, {attr}, b"object-only")
    drain(owner_a, owner_b, requester)
    provide_a = owner_a_fed.last_callback("provideAttributeValueUpdate")
    assert provide_a is not None
    assert provide_a.args == (obj_a, {attr}, b"object-only")
    assert owner_b_fed.last_callback("provideAttributeValueUpdate") is None

    owner_a_fed.clear()
    owner_b_fed.clear()
    requester.requestAttributeValueUpdate(cls, {attr}, b"class-wide")
    drain(owner_a, owner_b, requester)
    assert owner_a_fed.last_callback("provideAttributeValueUpdate").args == (obj_a, {attr}, b"class-wide")
    assert owner_b_fed.last_callback("provideAttributeValueUpdate").args == (obj_b, {attr}, b"class-wide")

    owner_a.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    owner_b.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    requester.resignFederationExecution(ResignAction.NO_ACTION)
    owner_a.destroyFederationExecution("request-avu-routing-fed")


def test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.sendInteractionWithRegions(object(), {}, set(), b"tag")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.sendInteractionWithRegions(object(), {}, set(), b"tag")
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("ddm-send-negative-fed")
    interaction = tx.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = tx.getParameterHandle(interaction, "TrackId")
    region = tx.createRegion({tx.getDimensionHandle("HLAdefaultRoutingSpace")})
    invalid_region = type(tx.createRegion({tx.getDimensionHandle("HLAdefaultRoutingSpace")}))(999999)
    with pytest.raises(InvalidRegion):
        tx.sendInteractionWithRegions(interaction, {track_id: b"x"}, {invalid_region}, b"tag")
    with pytest.raises(InvalidInteractionClassHandle):
        tx.sendInteractionWithRegions(type(interaction)(interaction.value + 1000), {track_id: b"x"}, {region}, b"tag")
    with pytest.raises(InteractionParameterNotDefined):
        tx.sendInteractionWithRegions(interaction, {type(track_id)(track_id.value + 1000): b"x"}, {region}, b"tag")

    tx.requestFederationSave("DDM-SEND-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        tx.sendInteractionWithRegions(interaction, {track_id: b"x"}, set(), b"tag")

    tx.federateSaveBegun()
    rx.federateSaveBegun()
    tx.federateSaveComplete()
    rx.federateSaveComplete()
    drain(tx, rx)

    tx.requestFederationRestore("DDM-SEND-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        tx.sendInteractionWithRegions(interaction, {track_id: b"x"}, set(), b"tag")

    tx.abortFederationRestore()
    drain(tx, rx)
    tx.resignFederationExecution(ResignAction.NO_ACTION)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("ddm-send-negative-fed")


def test_strict_publication_gates_registration_update_and_interaction_sends():
    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("strict-publication-fed")
    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "Position")
    rcs = tx.getAttributeHandle(cls, "RCS")
    interaction = tx.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = tx.getParameterHandle(interaction, "TrackId")
    dim = tx.getDimensionHandle("HLAdefaultRoutingSpace")
    region = tx.createRegion({dim})
    pair = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({region}))]
    unpublished_pair = [AttributeRegionAssociation(AttributeHandleSet({rcs}), RegionHandleSet({region}))]

    with pytest.raises(InvalidObjectClassHandle):
        tx.registerObjectInstance(type(cls)(cls.value + 1000), "Bad-Class")
    with pytest.raises(InvalidObjectClassHandle):
        tx.registerObjectInstanceWithRegions(type(cls)(cls.value + 1000), pair, "Bad-Class-Regions")

    obj = tx.registerObjectInstance(cls, "Strict-Update-Object")
    with pytest.raises(ObjectInstanceNameInUse):
        tx.registerObjectInstanceWithRegions(cls, pair, "Strict-Update-Object")
    tx.backend.config.strict_object_publication = True
    with pytest.raises(AttributeNotPublished):
        tx.updateAttributeValues(obj, {attr: b"strict"}, b"tag")
    with pytest.raises(AttributeNotPublished):
        tx.registerObjectInstanceWithRegions(cls, unpublished_pair, "Strict-Unpublished-Object")

    tx.backend.config.strict_object_publication = False
    tx.backend.config.strict_interaction_publication = True
    with pytest.raises(InteractionClassNotPublished):
        tx.sendInteraction(interaction, {track_id: b"no-pub"}, b"tag")
    with pytest.raises(InteractionClassNotPublished):
        tx.sendInteractionWithRegions(interaction, {track_id: b"no-pub"}, {region}, b"tag")
    with pytest.raises(InvalidInteractionClassHandle):
        tx.sendInteraction(type(interaction)(interaction.value + 1000), {track_id: b"no-pub"}, b"tag")

    tx.backend.config.strict_interaction_publication = False
    tx.requestFederationSave("STRICT-PUBLICATION-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        tx.registerObjectInstance(cls, "Strict-Save-Object")
    with pytest.raises(SaveInProgress):
        tx.registerObjectInstanceWithRegions(cls, pair, "Strict-Save-Region-Object")

    tx.federateSaveBegun()
    rx.federateSaveBegun()
    tx.federateSaveComplete()
    rx.federateSaveComplete()
    drain(tx, rx)

    tx.requestFederationRestore("STRICT-PUBLICATION-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        tx.registerObjectInstance(cls, "Strict-Restore-Object")
    with pytest.raises(RestoreInProgress):
        tx.registerObjectInstanceWithRegions(cls, pair, "Strict-Restore-Region-Object")

    tx.abortFederationRestore()
    drain(tx, rx)

    factory = tx.getTimeFactory()
    tx.enableTimeRegulation(factory.make_interval(1.0))
    rx.enableTimeConstrained()
    drain(tx, rx)

    tx.timeAdvanceRequest(factory.make_time(2.0))
    drain(tx, rx)
    with pytest.raises(InvalidLogicalTime):
        tx.updateAttributeValues(obj, {attr: b"timed"}, b"tag", factory.make_time(1.0))
    with pytest.raises(InvalidLogicalTime):
        tx.sendInteraction(interaction, {track_id: b"timed"}, b"tag", factory.make_time(1.0))
    with pytest.raises(InvalidLogicalTime):
        tx.sendInteractionWithRegions(interaction, {track_id: b"timed"}, {region}, b"tag", factory.make_time(1.0))

    tx.backend.config.strict_interaction_publication = False
    tx.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("strict-publication-fed")


def test_request_attribute_value_update_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.requestAttributeValueUpdateWithRegions(object(), [], b"tag")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.requestAttributeValueUpdateWithRegions(object(), [], b"tag")
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("ddm-ravu-negative-fed")
    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "Position")
    invalid_region = type(tx.createRegion({tx.getDimensionHandle("HLAdefaultRoutingSpace")}))(999999)
    pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({invalid_region}))]
    with pytest.raises(InvalidRegion):
        rx.requestAttributeValueUpdateWithRegions(cls, pairs, b"tag")
    bad_class = type(cls)(cls.value + 1000)
    with pytest.raises(InvalidObjectClassHandle):
        rx.requestAttributeValueUpdateWithRegions(
            bad_class,
            [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx.createRegion({rx.getDimensionHandle("HLAdefaultRoutingSpace")})}))],
            b"tag",
        )
    bad_attr = type(attr)(attr.value + 1000)
    with pytest.raises(AttributeNotDefined):
        rx.requestAttributeValueUpdateWithRegions(
            cls,
            [
                AttributeRegionAssociation(
                    AttributeHandleSet({bad_attr}), RegionHandleSet({rx.createRegion({rx.getDimensionHandle("HLAdefaultRoutingSpace")})})
                )
            ],
            b"tag",
        )

    tx.requestFederationSave("DDM-RAVU-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        rx.requestAttributeValueUpdateWithRegions(cls, [], b"tag")

    tx.federateSaveBegun()
    rx.federateSaveBegun()
    tx.federateSaveComplete()
    rx.federateSaveComplete()
    drain(tx, rx)

    tx.requestFederationRestore("DDM-RAVU-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        rx.requestAttributeValueUpdateWithRegions(cls, [], b"tag")

    tx.abortFederationRestore()
    drain(tx, rx)
    tx.resignFederationExecution(ResignAction.NO_ACTION)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("ddm-ravu-negative-fed")


def test_associate_regions_for_updates_rejects_not_connected_not_joined_unknown_object_invalid_region_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.associateRegionsForUpdates(ObjectInstanceHandle(999), [])

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.associateRegionsForUpdates(ObjectInstanceHandle(999), [])
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("associate-regions-negative-fed")
    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "Position")
    with pytest.raises(ObjectInstanceNotKnown):
        tx.associateRegionsForUpdates(ObjectInstanceHandle(999), [])

    invalid_region = type(tx.createRegion({tx.getDimensionHandle("HLAdefaultRoutingSpace")}))(999999)
    pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({invalid_region}))]
    obj = tx.registerObjectInstance(cls, "Associate-Negative")
    with pytest.raises(InvalidRegion):
        tx.associateRegionsForUpdates(obj, pairs)

    tx.requestFederationSave("ASSOC-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        tx.associateRegionsForUpdates(obj, [])

    tx.federateSaveBegun()
    rx.federateSaveBegun()
    tx.federateSaveComplete()
    rx.federateSaveComplete()
    drain(tx, rx)

    tx.requestFederationRestore("ASSOC-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        tx.associateRegionsForUpdates(obj, [])

    tx.abortFederationRestore()
    drain(tx, rx)
    tx.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("associate-regions-negative-fed")


def test_unassociate_regions_for_updates_rejects_not_connected_not_joined_unknown_object_invalid_region_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.unassociateRegionsForUpdates(ObjectInstanceHandle(999), [])

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.unassociateRegionsForUpdates(ObjectInstanceHandle(999), [])
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("unassociate-regions-negative-fed")
    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "Position")
    with pytest.raises(ObjectInstanceNotKnown):
        tx.unassociateRegionsForUpdates(ObjectInstanceHandle(999), [])

    dim = tx.getDimensionHandle("HLAdefaultRoutingSpace")
    invalid_region = type(tx.createRegion({dim}))(999999)
    tx_region = tx.createRegion({dim})
    pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({invalid_region}))]
    valid_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({tx_region}))]
    obj = tx.registerObjectInstance(cls, "Unassociate-Negative")
    tx.associateRegionsForUpdates(obj, valid_pairs)
    with pytest.raises(InvalidRegion):
        tx.unassociateRegionsForUpdates(obj, pairs)

    tx.requestFederationSave("UNASSOC-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        tx.unassociateRegionsForUpdates(obj, valid_pairs)

    tx.federateSaveBegun()
    rx.federateSaveBegun()
    tx.federateSaveComplete()
    rx.federateSaveComplete()
    drain(tx, rx)

    tx.requestFederationRestore("UNASSOC-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        tx.unassociateRegionsForUpdates(obj, valid_pairs)

    tx.abortFederationRestore()
    drain(tx, rx)
    tx.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("unassociate-regions-negative-fed")


@pytest.mark.parametrize(
    ("method_name", "kind"),
    (
        ("subscribeObjectClassAttributesWithRegions", "object"),
        ("subscribeObjectClassAttributesPassivelyWithRegions", "object"),
        ("subscribeInteractionClassWithRegions", "interaction"),
        ("subscribeInteractionClassPassivelyWithRegions", "interaction"),
    ),
)
def test_ddm_region_subscriptions_reject_not_connected_not_joined_and_invalid_region(method_name, kind):
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    if kind == "object":
        with pytest.raises(NotConnected):
            getattr(rti, method_name)(object(), [])
    else:
        with pytest.raises(NotConnected):
            getattr(rti, method_name)(object(), set())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    if kind == "object":
        with pytest.raises(FederateNotExecutionMember):
            getattr(rti, method_name)(object(), [])
    else:
        with pytest.raises(FederateNotExecutionMember):
            getattr(rti, method_name)(object(), set())
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair(f"{method_name}-negative-fed")
    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "Position")
    interaction = tx.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    dim = tx.getDimensionHandle("HLAdefaultRoutingSpace")
    region = rx.createRegion({dim})
    invalid_region = type(tx.createRegion({tx.getDimensionHandle("HLAdefaultRoutingSpace")}))(999999)
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

    tx.requestFederationSave(f"{method_name}-save")
    drain(tx, rx)
    if kind == "object":
        with pytest.raises(SaveInProgress):
            getattr(rx, method_name)(cls, [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({region}))])
    else:
        with pytest.raises(SaveInProgress):
            getattr(rx, method_name)(interaction, {region})

    tx.federateSaveBegun()
    rx.federateSaveBegun()
    tx.federateSaveComplete()
    rx.federateSaveComplete()
    drain(tx, rx)

    tx.requestFederationRestore(f"{method_name}-save")
    drain(tx, rx)
    if kind == "object":
        with pytest.raises(RestoreInProgress):
            getattr(rx, method_name)(cls, [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({region}))])
    else:
        with pytest.raises(RestoreInProgress):
            getattr(rx, method_name)(interaction, {region})

    tx.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution(f"{method_name}-negative-fed")


def test_register_object_instance_with_regions_rejects_not_connected_not_joined_and_invalid_region():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.registerObjectInstanceWithRegions(object(), [], "bad")

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.registerObjectInstanceWithRegions(object(), [], "bad")
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("register-with-regions-negative-fed")
    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "Position")
    rcs = tx.getAttributeHandle(cls, "RCS")
    tx.publishObjectClassAttributes(cls, {attr})
    invalid_region = type(tx.createRegion({tx.getDimensionHandle("HLAdefaultRoutingSpace")}))(999999)
    pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({invalid_region}))]
    with pytest.raises(InvalidRegion):
        tx.registerObjectInstanceWithRegions(cls, pairs, "bad-region-object")
    with pytest.raises(AttributeNotDefined):
        tx.registerObjectInstanceWithRegions(
            cls,
            [
                AttributeRegionAssociation(
                    AttributeHandleSet({type(attr)(attr.value + 1000)}),
                    RegionHandleSet({tx.createRegion({tx.getDimensionHandle("HLAdefaultRoutingSpace")})}),
                )
            ],
            "bad-attr-object",
        )

    tx.backend.config.strict_object_publication = True
    with pytest.raises(AttributeNotPublished):
        tx.registerObjectInstanceWithRegions(
            cls,
            [AttributeRegionAssociation(AttributeHandleSet({rcs}), RegionHandleSet({tx.createRegion({tx.getDimensionHandle("HLAdefaultRoutingSpace")})}))],
            "strict-unpublished-object",
        )

    tx.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("register-with-regions-negative-fed")


def test_unsubscribe_object_class_attributes_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.unsubscribeObjectClassAttributesWithRegions(object(), [])

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.unsubscribeObjectClassAttributesWithRegions(object(), [])
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("unsubscribe-ocar-negative-fed")
    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "Position")
    bad_attr = type(attr)(attr.value + 1000)
    invalid_region = type(tx.createRegion({tx.getDimensionHandle("HLAdefaultRoutingSpace")}))(999999)
    bad_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({invalid_region}))]
    with pytest.raises(InvalidRegion):
        rx.unsubscribeObjectClassAttributesWithRegions(cls, bad_pairs)
    with pytest.raises(AttributeNotDefined):
        rx.unsubscribeObjectClassAttributesWithRegions(
            cls,
            [
                AttributeRegionAssociation(
                    AttributeHandleSet({bad_attr}), RegionHandleSet({rx.createRegion({rx.getDimensionHandle("HLAdefaultRoutingSpace")})})
                )
            ],
        )

    rx.requestFederationSave("UNSUB-OCAR-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        rx.unsubscribeObjectClassAttributesWithRegions(cls, [])

    tx.federateSaveBegun()
    rx.federateSaveBegun()
    tx.federateSaveComplete()
    rx.federateSaveComplete()
    drain(tx, rx)

    rx.requestFederationRestore("UNSUB-OCAR-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        rx.unsubscribeObjectClassAttributesWithRegions(cls, [])

    rx.abortFederationRestore()
    drain(tx, rx)
    tx.resignFederationExecution(ResignAction.NO_ACTION)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("unsubscribe-ocar-negative-fed")


def test_unsubscribe_interaction_class_with_regions_and_delete_region_reject_not_connected_not_joined_invalid_region_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.unsubscribeInteractionClassWithRegions(object(), set())
    with pytest.raises(NotConnected):
        rti.deleteRegion(object())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.unsubscribeInteractionClassWithRegions(object(), set())
    with pytest.raises(FederateNotExecutionMember):
        rti.deleteRegion(object())
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("unsub-icwr-delete-region-negative-fed")
    interaction = tx.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    dim = rx.getDimensionHandle("HLAdefaultRoutingSpace")
    region = rx.createRegion({dim})
    invalid_region = type(region)(999999)

    with pytest.raises(InvalidRegion):
        rx.unsubscribeInteractionClassWithRegions(interaction, {invalid_region})
    with pytest.raises(InvalidRegion):
        rx.deleteRegion(invalid_region)

    rx.requestFederationSave("UNSUB-ICWR-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        rx.unsubscribeInteractionClassWithRegions(interaction, {region})
    with pytest.raises(SaveInProgress):
        rx.deleteRegion(region)

    tx.federateSaveBegun()
    rx.federateSaveBegun()
    tx.federateSaveComplete()
    rx.federateSaveComplete()
    drain(tx, rx)

    rx.requestFederationRestore("UNSUB-ICWR-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        rx.unsubscribeInteractionClassWithRegions(interaction, {region})
    with pytest.raises(RestoreInProgress):
        rx.deleteRegion(region)

    rx.abortFederationRestore()
    drain(tx, rx)
    tx.resignFederationExecution(ResignAction.NO_ACTION)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("unsub-icwr-delete-region-negative-fed")


def test_create_region_and_commit_region_modifications_reject_not_connected_not_joined_invalid_region_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.createRegion(set())
    with pytest.raises(NotConnected):
        rti.commitRegionModifications(set())

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.createRegion(set())
    with pytest.raises(FederateNotExecutionMember):
        rti.commitRegionModifications(set())
    rti.disconnect()

    _, tx, rx, _tx_fed, _rx_fed, _h1, _h2 = joined_pair("create-commit-region-negative-fed")
    dim = tx.getDimensionHandle("HLAdefaultRoutingSpace")
    region = tx.createRegion({dim})
    invalid_region = type(region)(999999)

    with pytest.raises(InvalidRegion):
        tx.commitRegionModifications({invalid_region})

    tx.requestFederationSave("REGION-SAVE")
    drain(tx, rx)
    with pytest.raises(SaveInProgress):
        tx.createRegion({dim})
    with pytest.raises(SaveInProgress):
        tx.commitRegionModifications({region})

    tx.federateSaveBegun()
    rx.federateSaveBegun()
    tx.federateSaveComplete()
    rx.federateSaveComplete()
    drain(tx, rx)

    tx.requestFederationRestore("REGION-SAVE")
    drain(tx, rx)
    with pytest.raises(RestoreInProgress):
        tx.createRegion({dim})
    with pytest.raises(RestoreInProgress):
        tx.commitRegionModifications({region})

    tx.abortFederationRestore()
    drain(tx, rx)
    tx.resignFederationExecution(ResignAction.NO_ACTION)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("create-commit-region-negative-fed")


def test_ddm_passive_region_subscriptions_behave_like_active_region_subscriptions():
    _, tx, rx, tx_fed, rx_fed, _h1, _h2 = joined_pair("ddm-passive-fed")
    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    attr = tx.getAttributeHandle(cls, "Position")
    dim = tx.getDimensionHandle("HLAdefaultRoutingSpace")
    interaction = tx.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = tx.getParameterHandle(interaction, "TrackId")

    tx_region = tx.createRegion({dim})
    rx_region = rx.createRegion({dim})
    tx.setRangeBounds(tx_region, dim, RangeBounds(10, 20))
    rx.setRangeBounds(rx_region, dim, RangeBounds(15, 25))
    tx.commitRegionModifications({tx_region})
    rx.commitRegionModifications({rx_region})

    update_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({tx_region}))]
    subscription_pairs = [AttributeRegionAssociation(AttributeHandleSet({attr}), RegionHandleSet({rx_region}))]

    rx.subscribeObjectClassAttributesPassivelyWithRegions(cls, subscription_pairs)
    tx.publishObjectClassAttributes(cls, {attr})
    obj = tx.registerObjectInstanceWithRegions(cls, update_pairs, "DDM-Passive-Object")
    drain(tx, rx)
    assert rx_fed.last_callback("discoverObjectInstance") is not None

    tx.publishInteractionClass(interaction)
    rx.subscribeInteractionClassPassivelyWithRegions(interaction, {rx_region})
    tx.sendInteractionWithRegions(interaction, {track_id: b"passive-match"}, {tx_region}, b"passive-ddm")
    drain(tx, rx)
    received = rx_fed.last_callback("receiveInteraction")
    assert received is not None
    assert received.args[0] == interaction
    assert received.args[1][track_id] == b"passive-match"
    assert tx_fed.last_callback("provideAttributeValueUpdate") is None

    rx.unsubscribeObjectClassAttributesWithRegions(cls, subscription_pairs)
    rx.unsubscribeInteractionClassWithRegions(interaction, {rx_region})

    tx.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("ddm-passive-fed")


def test_name_reservation_ddm_regions_ownership_and_time_support():
    _, r1, r2, f1, f2, h1, h2 = joined_pair("ddm-ownership-fed")
    cls = r1.getObjectClassHandle("HLAobjectRoot.Target")
    attr = r1.getAttributeHandle(cls, "Position")

    r1.reserveObjectInstanceName("ReservedTarget")
    drain(r1)
    assert f1.last_callback("objectInstanceNameReservationSucceeded").args == ("ReservedTarget",)
    r2.reserveObjectInstanceName("ReservedTarget")
    drain(r2)
    assert f2.last_callback("objectInstanceNameReservationFailed").args == ("ReservedTarget",)

    r1.publishObjectClassAttributes(cls, {attr})
    r2.publishObjectClassAttributes(cls, {attr})
    obj = r1.registerObjectInstance(cls, "ReservedTarget")
    assert r1.isAttributeOwnedByFederate(obj, attr)
    r1.unconditionalAttributeOwnershipDivestiture(obj, {attr})
    assert not r1.isAttributeOwnedByFederate(obj, attr)
    r2.attributeOwnershipAcquisitionIfAvailable(obj, {attr})
    drain(r2)
    acquired = f2.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired.args[0] == obj
    assert isinstance(acquired.args[1], AttributeHandleSet)
    assert r2.isAttributeOwnedByFederate(obj, attr)
    r1.queryAttributeOwnership(obj, attr)
    drain(r1)
    assert f1.last_callback("informAttributeOwnership").args == (obj, attr, h2)

    dim = r1.getDimensionHandle("HLAdefaultRoutingSpace")
    region = r1.createRegion({dim})
    r1.setRangeBounds(region, dim, RangeBounds(10, 20))
    assert r1.getRangeBounds(region, dim) == RangeBounds(10, 20)
    assert r1.getDimensionUpperBound(dim) > 20
    assert dim in r1.getAvailableDimensionsForClassAttribute(cls, attr)

    assert r1.getOrderName(OrderType.RECEIVE) == "RECEIVE"
    assert r1.getOrderType("HLAreceive") is OrderType.RECEIVE
    assert r1.decodeMessageRetractionHandle(MessageRetractionHandle(7).encoded()) == MessageRetractionHandle(7)
    assert isinstance(r1.queryGALT(), TimeQueryReturn)
    assert r1.normalizeFederateHandle(h1) == h1

    r1.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    r2.resignFederationExecution(ResignAction.NO_ACTION)
    r1.destroyFederationExecution("ddm-ownership-fed")


def test_support_service_roundtrips_and_callback_controls_have_exact_behavior():
    _, owner, observer, owner_fed, observer_fed, h1, h2 = joined_pair("support-controls-fed")

    assert owner.getFederateName(h1) == "alpha"
    assert owner.getFederateName(h2) == "bravo"
    assert owner.getFederateHandle("bravo") == h2

    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    assert owner.getObjectClassName(cls) == "HLAobjectRoot.Target"
    attr = owner.getAttributeHandle(cls, "Position")
    assert owner.getAttributeName(cls, attr) == "Position"

    interaction = owner.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    assert owner.getInteractionClassName(interaction) == "HLAinteractionRoot.TrackReport"
    track_id = owner.getParameterHandle(interaction, "TrackId")
    assert owner.getParameterName(interaction, track_id) == "TrackId"

    dim = owner.getDimensionHandle("HLAdefaultRoutingSpace")
    assert owner.getDimensionName(dim) == "HLAdefaultRoutingSpace"
    region = owner.createRegion({dim})
    assert dim in owner.getDimensionHandleSet(region)
    pair_list_factory = owner.getAttributeSetRegionSetPairListFactory()
    assert isinstance(pair_list_factory.create(), AttributeSetRegionSetPairList)

    owner.publishObjectClassAttributes(cls, {attr})
    observer.subscribeObjectClassAttributes(cls, {attr})

    queued = owner.registerObjectInstance(cls, "Queued-Target")
    owner.updateAttributeValues(queued, {attr: b"queued"}, b"queued-tag")
    observer.disableCallbacks()
    assert observer.evokeMultipleCallbacks(0.0, 0.0) is False
    observer.enableCallbacks()
    assert observer.evokeMultipleCallbacks(0.0, 0.0) is True
    assert observer_fed.last_callback("discoverObjectInstance") is not None
    assert observer_fed.last_callback("reflectAttributeValues").args[1] == {attr: b"queued"}

    observer_fed.clear()
    owner.updateAttributeValues(queued, {attr: b"single"}, b"single-tag")
    assert observer.evokeCallback(0.0) is False
    assert observer_fed.last_callback("reflectAttributeValues").args[1] == {attr: b"single"}

    assert owner.getObjectInstanceName(queued) == "Queued-Target"
    assert owner.getObjectInstanceHandle("Queued-Target") == queued
    assert owner.getKnownObjectClassHandle(queued) == cls
    assert owner.getHLAversion().startswith("HLA 1516-2010")
    assert owner.normalizeFederateHandle(h1) == h1

    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("support-controls-fed")


def test_time_query_tail_rejects_not_connected_not_joined_and_save_restore():
    rti = rti_ambassador(engine=InMemoryRTIEngine())
    with pytest.raises(NotConnected):
        rti.queryGALT()
    with pytest.raises(NotConnected):
        rti.queryLogicalTime()
    with pytest.raises(NotConnected):
        rti.queryLITS()

    rti.connect(RecordingFederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederateNotExecutionMember):
        rti.queryGALT()
    with pytest.raises(FederateNotExecutionMember):
        rti.queryLogicalTime()
    with pytest.raises(FederateNotExecutionMember):
        rti.queryLITS()
    rti.disconnect()

    _, owner, observer, _owner_fed, _observer_fed, _h1, _h2 = joined_pair("time-query-negative-fed")
    owner.requestFederationSave("TIME-QUERY-SAVE")
    drain(owner, observer)
    with pytest.raises(SaveInProgress):
        owner.queryGALT()
    with pytest.raises(SaveInProgress):
        owner.queryLogicalTime()
    with pytest.raises(SaveInProgress):
        owner.queryLITS()

    owner.federateSaveBegun()
    observer.federateSaveBegun()
    owner.federateSaveComplete()
    observer.federateSaveComplete()
    drain(owner, observer)

    owner.requestFederationRestore("TIME-QUERY-SAVE")
    drain(owner, observer)
    with pytest.raises(RestoreInProgress):
        owner.queryGALT()
    with pytest.raises(RestoreInProgress):
        owner.queryLogicalTime()
    with pytest.raises(RestoreInProgress):
        owner.queryLITS()

    owner.abortFederationRestore()
    drain(owner, observer)
    owner.resignFederationExecution(ResignAction.NO_ACTION)
    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.destroyFederationExecution("time-query-negative-fed")


def test_hla_immediate_callback_model_delivers_object_callbacks_inline_without_evocation():
    engine = InMemoryRTIEngine()
    owner = rti_ambassador(engine=engine)
    observer = rti_ambassador(engine=engine)
    owner_fed = RecordingFederateAmbassador()
    observer_fed = RecordingFederateAmbassador()

    owner.connect(owner_fed, CallbackModel.HLA_EVOKED)
    observer.connect(observer_fed, CallbackModel.HLA_IMMEDIATE)
    owner.createFederationExecution("immediate-callback-fed", "TargetRadarFOMmodule.xml")
    owner.joinFederationExecution("alpha", "type-a", "immediate-callback-fed")
    observer.joinFederationExecution("bravo", "type-b", "immediate-callback-fed")

    cls = owner.getObjectClassHandle("HLAobjectRoot.Target")
    attr = owner.getAttributeHandle(cls, "Position")
    owner.publishObjectClassAttributes(cls, {attr})
    observer.subscribeObjectClassAttributes(cls, {attr})

    obj = owner.registerObjectInstance(cls, "ImmediateTarget")
    owner.updateAttributeValues(obj, {attr: b"now"}, b"tag")

    assert observer_fed.last_callback("discoverObjectInstance") is not None
    assert observer_fed.last_callback("reflectAttributeValues").args[1] == {attr: b"now"}
    assert observer.evokeMultipleCallbacks(0.0, 0.0) is False

    observer.resignFederationExecution(ResignAction.NO_ACTION)
    owner.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    owner.destroyFederationExecution("immediate-callback-fed")


def test_hla_immediate_time_enable_callbacks_expose_pending_request_exceptions():
    engine = InMemoryRTIEngine()
    regulator = rti_ambassador(engine=engine)
    constrained = rti_ambassador(engine=engine)
    regulator_fed = _ImmediateRegulationPendingAmbassador(regulator)
    constrained_fed = _ImmediateConstrainedPendingAmbassador(constrained)

    regulator.connect(regulator_fed, CallbackModel.HLA_IMMEDIATE)
    constrained.connect(constrained_fed, CallbackModel.HLA_IMMEDIATE)
    regulator.createFederationExecution("immediate-time-fed", "TargetRadarFOMmodule.xml")
    regulator.joinFederationExecution("alpha", "type-a", "immediate-time-fed")
    constrained.joinFederationExecution("bravo", "type-b", "immediate-time-fed")

    regulator.enableTimeRegulation(regulator.getTimeFactory().make_interval(1.0))
    constrained.enableTimeConstrained()

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

    constrained.resignFederationExecution(ResignAction.NO_ACTION)
    regulator.resignFederationExecution(ResignAction.NO_ACTION)
    regulator.destroyFederationExecution("immediate-time-fed")
