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
            rti.evoke_multiple_callbacks(0.0, 0.0)


def test_two_python_federates_share_in_memory_rti():
    engine = InMemoryRTIEngine()
    tx = rti_ambassador(engine=engine)
    rx = rti_ambassador(engine=engine)
    tx_fed = Receiver()
    rx_fed = Receiver()

    tx.connect(tx_fed, CallbackModel.HLA_EVOKED)
    rx.connect(rx_fed, CallbackModel.HLA_EVOKED)
    tx.create_federation_execution("unit-fed", "TargetRadarFOMmodule.xml")
    tx.join_federation_execution("target", "target-type", "unit-fed")
    rx.join_federation_execution("radar", "radar-type", "unit-fed")

    cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    pos = tx.get_attribute_handle(cls, "Position")
    rx.subscribe_object_class_attributes(cls, {pos})
    tx.publish_object_class_attributes(cls, {pos})

    obj = tx.register_object_instance(cls, "Target-1")
    assert isinstance(obj, ObjectInstanceHandle)
    drain(tx, rx)
    assert rx_fed.discoveries[-1][2] == "Target-1"

    tx.update_attribute_values(obj, {pos: b"12345678"}, b"tag")
    drain(tx, rx)
    reflected = rx_fed.reflections[-1]
    assert reflected[0] == obj
    assert reflected[1] == {pos: b"12345678"}
    assert reflected[2] == b"tag"
    assert reflected[3] is OrderType.RECEIVE

    query = tx.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    request_id = tx.get_parameter_handle(query, "TrackId")
    tx.publish_interaction_class(query)
    rx.subscribe_interaction_class(query)
    tx.send_interaction(query, {request_id: b"Q1"}, b"iq")
    drain(tx, rx)
    assert rx_fed.interactions[-1][0] == query
    assert rx_fed.interactions[-1][1] == {request_id: b"Q1"}

    tx.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    rx.resign_federation_execution(ResignAction.NO_ACTION)
    tx.destroy_federation_execution("unit-fed")


def test_python_backend_validates_declared_user_tag_encoding_for_updates_and_interactions():
    engine = InMemoryRTIEngine()
    tx = rti_ambassador(engine=engine)
    rx = rti_ambassador(engine=engine)
    tx.connect(Receiver(), CallbackModel.HLA_EVOKED)
    rx.connect(Receiver(), CallbackModel.HLA_EVOKED)
    tx.create_federation_execution("tag-fed", "TargetRadarFOMmodule.xml")
    tx.join_federation_execution("target", "target-type", "tag-fed")
    rx.join_federation_execution("radar", "radar-type", "tag-fed")

    obj_cls = tx.get_object_class_handle("HLAobjectRoot.Target")
    pos = tx.get_attribute_handle(obj_cls, "Position")
    tx.publish_object_class_attributes(obj_cls, {pos})
    obj = tx.register_object_instance(obj_cls, "Tagged-1")
    good_tag = HLAunicodeString("ok").encode()

    tx.update_attribute_values(obj, {pos: b"12345678"}, good_tag)
    with pytest.raises(CouldNotDecode, match="updateReflectTag"):
        tx.update_attribute_values(obj, {pos: b"12345678"}, b"\xff")

    interaction = tx.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    track_id = tx.get_parameter_handle(interaction, "TrackId")
    tx.publish_interaction_class(interaction)
    tx.send_interaction(interaction, {track_id: b"T-1"}, good_tag)
    with pytest.raises(CouldNotDecode, match="sendReceiveTag"):
        tx.send_interaction(interaction, {track_id: b"T-1"}, b"\xff")
