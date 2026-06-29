import pytest

from hla.fom import FOMResolver, merge_fom_modules, validate_encoded_datatype_value
from hla.rti1516e import NullFederateAmbassador
from hla.backends.python1516e import InMemoryRTIEngine, rti_ambassador
from hla.rti1516e.encoding import HLAunicodeString
from hla.rti1516e.enums import CallbackModel, OrderType, ResignAction
from hla.rti1516e.exceptions import CouldNotDecode
from hla.rti1516e.handles import ObjectInstanceHandle


class Receiver(NullFederateAmbassador):
    def __init__(self):
        self.discoveries = []
        self.reflections = []
        self.interactions = []

    def discover_object_instance(self, the_object, the_object_class, object_name, *extra):
        self.discoveries.append((the_object, the_object_class, object_name, extra))

    def discoverObjectInstance(self, theObject, theObjectClass, objectName, *extra):
        self.discover_object_instance(theObject, theObjectClass, objectName, *extra)

    def reflect_attribute_values(self, the_object, the_attributes, user_supplied_tag, sent_ordering, transport, *extra):
        self.reflections.append((the_object, the_attributes, user_supplied_tag, sent_ordering, transport, extra))

    def reflectAttributeValues(self, theObject, theAttributes, userSuppliedTag, sentOrdering, transport, *extra):
        self.reflect_attribute_values(theObject, theAttributes, userSuppliedTag, sentOrdering, transport, *extra)

    def receive_interaction(self, interaction_class, parameters, user_supplied_tag, sent_ordering, transport, *extra):
        self.interactions.append((interaction_class, parameters, user_supplied_tag, sent_ordering, transport, extra))

    def receiveInteraction(self, interactionClass, parameters, userSuppliedTag, sentOrdering, transport, *extra):
        self.receive_interaction(interactionClass, parameters, userSuppliedTag, sentOrdering, transport, *extra)


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


def test_validate_encoded_datatype_value_accepts_rpr_null_terminated_user_tag(tmp_path) -> None:
    fom_path = tmp_path / "RPRUserDefinedTagFOM.xml"
    fom_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>RPR User Tag</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <arrayDataTypes>
      <arrayData>
        <name>RPRUserDefinedTag</name>
        <dataType>HLAASCIIchar</dataType>
        <cardinality>[8..255]</cardinality>
        <encoding>null-terminated-array</encoding>
      </arrayData>
    </arrayDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )
    catalog = merge_fom_modules((FOMResolver().resolve(fom_path),))

    validate_encoded_datatype_value(b"00000000\x00", "RPRUserDefinedTag", catalog)
    validate_encoded_datatype_value(b"00000000EXTRA\x00", "RPRUserDefinedTag", catalog)
    with pytest.raises(CouldNotDecode, match="missing its terminator"):
        validate_encoded_datatype_value(b"00000000", "RPRUserDefinedTag", catalog)
    with pytest.raises(CouldNotDecode, match="requires at least 8 bytes"):
        validate_encoded_datatype_value(b"1234\x00", "RPRUserDefinedTag", catalog)


def test_validate_encoded_datatype_value_accepts_alignment_padding_arrays(tmp_path) -> None:
    fom_path = tmp_path / "PaddingArrayFOM.xml"
    fom_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Padding Array FOM</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <simpleDataTypes>
      <simpleData><name>Octet</name><representation>HLAoctet</representation></simpleData>
    </simpleDataTypes>
    <arrayDataTypes>
      <arrayData><name>Pad32</name><dataType>Octet</dataType><cardinality>Dynamic</cardinality><encoding>RPRpaddingTo32Array</encoding></arrayData>
      <arrayData><name>Pad64</name><dataType>Octet</dataType><cardinality>Dynamic</cardinality><encoding>RPRpaddingTo64Array</encoding></arrayData>
    </arrayDataTypes>
    <fixedRecordDataTypes>
      <fixedRecordData>
        <name>Aligned32Struct</name>
        <encoding>HLAfixedRecord</encoding>
        <field><name>Prefix</name><dataType>HLAinteger16BE</dataType></field>
        <field><name>Padding</name><dataType>Pad32</dataType></field>
        <field><name>Value</name><dataType>HLAinteger32BE</dataType></field>
      </fixedRecordData>
      <fixedRecordData>
        <name>Aligned64Struct</name>
        <encoding>HLAfixedRecord</encoding>
        <field><name>Prefix</name><dataType>HLAinteger16BE</dataType></field>
        <field><name>Padding</name><dataType>Pad64</dataType></field>
        <field><name>Value</name><dataType>HLAinteger64BE</dataType></field>
      </fixedRecordData>
    </fixedRecordDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )
    catalog = merge_fom_modules((FOMResolver().resolve(fom_path),))

    validate_encoded_datatype_value(b"\x12\x34\x00\x00\xde\xad\xbe\xef", "Aligned32Struct", catalog)
    validate_encoded_datatype_value(
        b"\x12\x34\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08",
        "Aligned64Struct",
        catalog,
    )
    with pytest.raises(CouldNotDecode, match="requires 2 padding octets"):
        validate_encoded_datatype_value(b"\x12\x34\x00", "Aligned32Struct", catalog)
    with pytest.raises(CouldNotDecode, match="requires 6 padding octets"):
        validate_encoded_datatype_value(
            b"\x12\x34\x00\x00\x00\x00\x00",
            "Aligned64Struct",
            catalog,
        )
