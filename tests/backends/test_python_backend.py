import pytest

from hla2010.spec import FederateAmbassadorSpec
from hla2010_rti_python import InMemoryRTIEngine, rti_ambassador
from hla2010.encoding import HLAunicodeString
from hla2010.enums import CallbackModel, OrderType, ResignAction
from hla2010.exceptions import CouldNotDecode
from hla2010.handles import ObjectInstanceHandle


class Receiver(FederateAmbassadorSpec):
    def __init__(self):
        self.discoveries = []
        self.reflections = []
        self.interactions = []

    def discover_object_instance(self, the_object, the_object_class, object_name, *extra):
        self.discoveries.append((the_object, the_object_class, object_name, extra))

    def reflect_attribute_values(self, the_object, the_attributes, user_supplied_tag, sent_ordering, transport, *extra):
        self.reflections.append((the_object, the_attributes, user_supplied_tag, sent_ordering, transport, extra))

    def receive_interaction(self, interaction_class, parameters, user_supplied_tag, sent_ordering, transport, *extra):
        self.interactions.append((interaction_class, parameters, user_supplied_tag, sent_ordering, transport, extra))


def drain(*rtis):
    for _ in range(10):
        for rti in rtis:
            rti.evokeMultipleCallbacks(0.0, 0.0)


def test_two_python_federates_share_in_memory_rti():
    engine = InMemoryRTIEngine()
    tx = rti_ambassador(engine=engine)
    rx = rti_ambassador(engine=engine)
    tx_fed = Receiver()
    rx_fed = Receiver()

    tx.connect(tx_fed, CallbackModel.HLA_EVOKED)
    rx.connect(rx_fed, CallbackModel.HLA_EVOKED)
    tx.createFederationExecution("unit-fed", "TargetRadarFOMmodule.xml")
    tx.joinFederationExecution("target", "target-type", "unit-fed")
    rx.joinFederationExecution("radar", "radar-type", "unit-fed")

    cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    pos = tx.getAttributeHandle(cls, "Position")
    rx.subscribeObjectClassAttributes(cls, {pos})
    tx.publishObjectClassAttributes(cls, {pos})

    obj = tx.registerObjectInstance(cls, "Target-1")
    assert isinstance(obj, ObjectInstanceHandle)
    drain(tx, rx)
    assert rx_fed.discoveries[-1][2] == "Target-1"

    tx.updateAttributeValues(obj, {pos: b"12345678"}, b"tag")
    drain(tx, rx)
    reflected = rx_fed.reflections[-1]
    assert reflected[0] == obj
    assert reflected[1] == {pos: b"12345678"}
    assert reflected[2] == b"tag"
    assert reflected[3] is OrderType.RECEIVE

    query = tx.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    request_id = tx.getParameterHandle(query, "TrackId")
    tx.publishInteractionClass(query)
    rx.subscribeInteractionClass(query)
    tx.sendInteraction(query, {request_id: b"Q1"}, b"iq")
    drain(tx, rx)
    assert rx_fed.interactions[-1][0] == query
    assert rx_fed.interactions[-1][1] == {request_id: b"Q1"}

    tx.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    rx.resignFederationExecution(ResignAction.NO_ACTION)
    tx.destroyFederationExecution("unit-fed")


def test_python_backend_validates_declared_user_tag_encoding_for_updates_and_interactions():
    engine = InMemoryRTIEngine()
    tx = rti_ambassador(engine=engine)
    rx = rti_ambassador(engine=engine)
    tx.connect(Receiver(), CallbackModel.HLA_EVOKED)
    rx.connect(Receiver(), CallbackModel.HLA_EVOKED)
    tx.createFederationExecution("tag-fed", "TargetRadarFOMmodule.xml")
    tx.joinFederationExecution("target", "target-type", "tag-fed")
    rx.joinFederationExecution("radar", "radar-type", "tag-fed")

    obj_cls = tx.getObjectClassHandle("HLAobjectRoot.Target")
    pos = tx.getAttributeHandle(obj_cls, "Position")
    tx.publishObjectClassAttributes(obj_cls, {pos})
    obj = tx.registerObjectInstance(obj_cls, "Tagged-1")
    good_tag = HLAunicodeString("ok").encode()

    tx.updateAttributeValues(obj, {pos: b"12345678"}, good_tag)
    with pytest.raises(CouldNotDecode, match="updateReflectTag"):
        tx.updateAttributeValues(obj, {pos: b"12345678"}, b"\xff")

    interaction = tx.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    track_id = tx.getParameterHandle(interaction, "TrackId")
    tx.publishInteractionClass(interaction)
    tx.sendInteraction(interaction, {track_id: b"T-1"}, good_tag)
    with pytest.raises(CouldNotDecode, match="sendReceiveTag"):
        tx.sendInteraction(interaction, {track_id: b"T-1"}, b"\xff")
