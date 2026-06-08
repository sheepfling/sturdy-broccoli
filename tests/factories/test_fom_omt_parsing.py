from __future__ import annotations

from pathlib import Path

import pytest

from hla2010.encoding import HLAboolean, HLAfixedArray, HLAfixedRecord, HLAinteger32BE
from hla2010.exceptions import CouldNotDecode
from hla2010.fom import (
    BasicDatatypeSpec,
    FOMMergeError,
    FOMModule,
    FOMResolutionError,
    InteractionClassSpec,
    ObjectClassSpec,
    SimpleDatatypeSpec,
    merge_fom_modules,
    parse_fom_xml,
    serialize_fom_module,
    validate_encoded_datatype_value,
    validate_fom_xml_schema,
)


def test_parse_fom_xml_extracts_identification_names_and_reference_datatypes():
    module = parse_fom_xml("hla2010/resources/foms/TargetRadarFOMmodule.xml")

    assert module.name == "Target Radar FOM Module"
    assert module.model_type == "FOM"
    assert module.model_identification["version"] == "0.2"
    assert module.model_identification["securityClassification"] == "Unclassified"
    assert module.model_identification["applicationDomain"] == "HLA API development and integration testing"
    assert module.is_mim is False
    assert module.inferred_time_implementation == "HLAfloat64Time"
    assert module.time_stamp_datatype == "HLAfloat64BE"
    assert module.lookahead_datatype == "HLAfloat64BE"
    assert module.transportation_names == ("HLAreliable",)
    assert "Vec3Float64BE" in module.datatype_names

    target = next(spec for spec in module.object_classes if spec.full_name == "HLAobjectRoot.Target")
    track = next(spec for spec in module.object_classes if spec.full_name == "HLAobjectRoot.Track")
    report = next(spec for spec in module.interaction_classes if spec.full_name == "HLAinteractionRoot.TrackReport")

    assert target.attribute_datatypes["Position"] == "Vec3Float64BE"
    assert target.attribute_datatypes["RCS"] == "HLAfloat64BE"
    assert track.attribute_datatypes["TargetName"] == "HLAunicodeString"
    assert report.parameter_datatypes["TrackId"] == "HLAunicodeString"
    assert report.parameter_datatypes["Position"] == "Vec3Float64BE"


def test_parse_fom_xml_extracts_transportation_update_rate_and_datatype_tables(tmp_path: Path):
    xml_path = tmp_path / "omt-transport-update-rate.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification>
    <name>Transport Update Rate SOM</name>
    <type>SOM</type>
  </modelIdentification>
  <time>
    <timeStamp><dataType>HLAfloat64BE</dataType></timeStamp>
    <lookahead><dataType>HLAfloat64BE</dataType></lookahead>
  </time>
  <transportations>
    <transportation><name>HLAreliable</name></transportation>
    <transportation><name>HLAbestEffort</name></transportation>
  </transportations>
  <updateRates>
    <updateRate><name>HLAdefault</name><rate>0.0</rate></updateRate>
    <updateRate><name>Fast</name><rate>10.0</rate></updateRate>
  </updateRates>
  <dataTypes>
    <simpleDataTypes>
      <simpleData><name>HLAfloat64BE</name></simpleData>
    </simpleDataTypes>
    <fixedRecordDataTypes>
      <fixedRecordData><name>Vec2</name></fixedRecordData>
    </fixedRecordDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )

    module = parse_fom_xml(xml_path)
    assert module.model_type == "SOM"
    assert module.time_stamp_datatype == "HLAfloat64BE"
    assert module.lookahead_datatype == "HLAfloat64BE"
    assert module.transportation_names == ("HLAreliable", "HLAbestEffort")
    assert module.update_rates == {"HLAdefault": "0.0", "Fast": "10.0"}
    assert module.datatype_names == ("HLAfloat64BE", "Vec2")
    assert module.is_mim is False


def test_parse_standard_mim_xml_exposes_mim_content_and_merge_summary():
    mim_module = parse_fom_xml("hla2010/resources/foms/HLAstandardMIM.xml")
    target_module = parse_fom_xml("hla2010/resources/foms/TargetRadarFOMmodule.xml")
    catalog = merge_fom_modules((target_module,), mim_module=mim_module)

    assert mim_module.is_mim is True
    assert "HLAreliable" in mim_module.transportation_names
    assert "HLAbestEffort" in mim_module.transportation_names
    assert "HLAfloat64Time" in mim_module.datatype_names
    assert "HLAobjectRoot.HLAmanager.HLAfederate" in catalog.object_classes
    assert "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata" in catalog.interaction_classes
    assert "HLAfederate" in catalog.dimensions
    assert "HLAserviceGroup" in catalog.dimensions
    assert "HLAreliable" in catalog.transportation_names
    assert "HLAbestEffort" in catalog.transportation_names
    assert "Vec3Float64BE" in catalog.datatype_names


def test_parse_fom_xml_requires_and_preserves_model_identification_metadata(tmp_path: Path):
    xml_path = tmp_path / "missing-identification.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <objects>
    <objectClass><name>HLAobjectRoot</name></objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="missing required modelIdentification"):
        parse_fom_xml(xml_path)

    restaurant = parse_fom_xml("CERTI/xml/ieee1516-2010/1516_2-2010/RestaurantFOMmodule.xml")
    assert restaurant.model_identification["name"] == "Restaurant FOM Module Example"
    assert restaurant.model_identification["type"] == "FOM"
    assert restaurant.model_identification["version"] == "3.0"
    assert restaurant.model_identification["securityClassification"] == "Unclassified"
    assert restaurant.model_identification["applicationDomain"] == "Restaurant operations"
    assert "pocs" in restaurant.model_identification


def test_parse_standard_mim_xml_extracts_structured_datatype_definitions():
    mim_module = parse_fom_xml("hla2010/resources/foms/HLAstandardMIM.xml")

    assert mim_module.basic_datatypes["HLAinteger16BE"].size == "16"
    assert mim_module.basic_datatypes["HLAinteger16BE"].endian == "Big"
    assert mim_module.simple_datatypes["HLAASCIIchar"].representation == "HLAoctet"
    assert mim_module.enumerated_datatypes["HLAboolean"].representation == "HLAinteger32BE"
    assert [enum.name for enum in mim_module.enumerated_datatypes["HLAboolean"].enumerators] == ["HLAfalse", "HLAtrue"]
    assert mim_module.enumerated_datatypes["HLAboolean"].enumerators[0].values == ("0",)
    assert mim_module.array_datatypes["HLAASCIIstring"].encoding == "HLAvariableArray"
    assert mim_module.array_datatypes["HLAASCIIstring"].cardinality == "Dynamic"
    assert mim_module.fixed_record_datatypes["HLAinteractionSubscription"].fields[0].name == "HLAinteractionClass"
    assert mim_module.fixed_record_datatypes["HLAinteractionSubscription"].fields[1].data_type == "HLAboolean"


def test_merge_with_standard_mim_preserves_mom_table_definitions_without_alteration():
    mim_module = parse_fom_xml("hla2010/resources/foms/HLAstandardMIM.xml")
    target_module = parse_fom_xml("hla2010/resources/foms/TargetRadarFOMmodule.xml")
    catalog = merge_fom_modules((target_module,), mim_module=mim_module)

    assert catalog.mim_module is mim_module
    assert mim_module.is_mim is True

    for spec in mim_module.object_classes:
        merged = catalog.object_classes[spec.full_name]
        assert merged.parent_name == spec.parent_name
        assert merged.declared_attributes == spec.declared_attributes
        assert merged.attribute_datatypes == spec.attribute_datatypes

    for spec in mim_module.interaction_classes:
        merged = catalog.interaction_classes[spec.full_name]
        assert merged.parent_name == spec.parent_name
        assert merged.declared_parameters == spec.declared_parameters
        assert merged.parameter_datatypes == spec.parameter_datatypes

    assert set(mim_module.dimensions) <= set(catalog.dimensions)
    assert set(mim_module.transportation_names) <= set(catalog.transportation_names)
    assert set(mim_module.datatype_names) <= set(catalog.datatype_names)


def test_merge_with_standard_mim_preserves_standard_mom_definitions_and_catalog_metadata():
    mim_module = parse_fom_xml("hla2010/resources/foms/HLAstandardMIM.xml")
    target_module = parse_fom_xml("hla2010/resources/foms/TargetRadarFOMmodule.xml")
    catalog = merge_fom_modules((target_module,), mim_module=mim_module)

    assert catalog.mim_module is mim_module
    assert catalog.mim_module.model_identification == mim_module.model_identification
    assert catalog.mim_module.notes == mim_module.notes
    assert catalog.mim_module.service_utilization == mim_module.service_utilization
    assert catalog.mim_module.switch_settings == mim_module.switch_settings
    assert catalog.time_stamp_datatype == mim_module.time_stamp_datatype
    assert catalog.lookahead_datatype == mim_module.lookahead_datatype

    for spec in mim_module.object_classes:
        merged = catalog.object_classes[spec.full_name]
        assert merged == spec

    for spec in mim_module.interaction_classes:
        merged = catalog.interaction_classes[spec.full_name]
        assert merged == spec

    for name, spec in mim_module.basic_datatypes.items():
        assert catalog.basic_datatypes[name] == spec
    for name, spec in mim_module.simple_datatypes.items():
        assert catalog.simple_datatypes[name] == spec
    for name, spec in mim_module.enumerated_datatypes.items():
        assert catalog.enumerated_datatypes[name] == spec
    for name, spec in mim_module.array_datatypes.items():
        assert catalog.array_datatypes[name] == spec
    for name, spec in mim_module.fixed_record_datatypes.items():
        assert catalog.fixed_record_datatypes[name] == spec
    for name, spec in mim_module.variant_record_datatypes.items():
        assert catalog.variant_record_datatypes[name] == spec
    for name, spec in mim_module.tag_representations.items():
        assert catalog.tag_representations[name] == spec
    for name, spec in mim_module.update_rates.items():
        assert catalog.update_rates[name] == spec
    for name, spec in mim_module.synchronization_points.items():
        assert catalog.synchronization_points[name] == spec


def test_merge_allows_extending_standard_mom_classes_with_subclasses_and_attributes(tmp_path: Path):
    extension_path = tmp_path / "mom-extension.xml"
    extension_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification>
    <name>MOM Extension Module</name>
    <type>FOM</type>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>HLAmanager</name>
        <objectClass>
          <name>HLAfederate</name>
          <attribute>
            <name>HLAcustomAuditFlag</name>
            <dataType>HLAunicodeString</dataType>
          </attribute>
          <objectClass>
            <name>HLAextendedFederate</name>
          </objectClass>
        </objectClass>
      </objectClass>
    </objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )

    mim_module = parse_fom_xml("hla2010/resources/foms/HLAstandardMIM.xml")
    target_module = parse_fom_xml("hla2010/resources/foms/TargetRadarFOMmodule.xml")
    extension_module = parse_fom_xml(extension_path)
    catalog = merge_fom_modules((target_module, extension_module), mim_module=mim_module)

    federate = catalog.object_classes["HLAobjectRoot.HLAmanager.HLAfederate"]
    extended = catalog.object_classes["HLAobjectRoot.HLAmanager.HLAfederate.HLAextendedFederate"]

    assert "HLAcustomAuditFlag" in federate.attributes
    assert "HLAcustomAuditFlag" in federate.declared_attributes
    assert federate.attribute_datatypes["HLAcustomAuditFlag"] == "HLAunicodeString"
    assert extended.parent_name == "HLAobjectRoot.HLAmanager.HLAfederate"
    assert any(note.startswith("MOM1:") for note in mim_module.notes)
    assert any(note.startswith("MOM1:") for note in catalog.notes)


def test_parse_fom_xml_distinguishes_fom_som_and_mim_types_and_preserves_notes(tmp_path: Path):
    som_path = tmp_path / "omt-notes-som.xml"
    som_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification>
    <name>Example SOM</name>
    <type>SOM</type>
  </modelIdentification>
  <notes>
    <note>
      <label>N1</label>
      <semantics>Example note semantics.</semantics>
    </note>
  </notes>
</objectModel>
""",
        encoding="utf-8",
    )

    fom_module = parse_fom_xml("hla2010/resources/foms/TargetRadarFOMmodule.xml")
    som_module = parse_fom_xml(som_path)
    mim_module = parse_fom_xml("hla2010/resources/foms/HLAstandardMIM.xml")

    assert fom_module.model_type == "FOM"
    assert fom_module.is_mim is False
    assert som_module.model_type == "SOM"
    assert som_module.is_mim is False
    assert som_module.notes == ("N1: Example note semantics.",)
    assert mim_module.model_type == "FOM"
    assert mim_module.is_mim is True
    assert any("Dimension Upper Bound entry for the Federate dimension" in note for note in mim_module.notes)


def test_parse_fom_xml_recognizes_standard_omt_component_tables_across_fom_som_and_mim():
    som_module = parse_fom_xml("CERTI/xml/ieee1516-2010/1516_2-2010/RestaurantSOMmodule.xml")
    fom_module = parse_fom_xml("CERTI/xml/ieee1516-2010/1516_2-2010/RestaurantFOMmodule.xml")
    mim_module = parse_fom_xml("hla2010/resources/foms/HLAstandardMIM.xml")

    assert som_module.model_identification["type"] == "SOM"
    assert som_module.service_utilization["joinFederationExecution"]["isUsed"] == "true"
    assert som_module.service_utilization["getInteractionClassHandle"]["section"] == "10.15"
    assert "HLAobjectRoot.Customer" in {spec.full_name for spec in som_module.object_classes}
    assert "HLAobjectRoot.Employee.Waiter" in {spec.full_name for spec in som_module.object_classes}
    assert "HLAinteractionRoot.CustomerTransactions.OrderTaken" in {
        spec.full_name for spec in som_module.interaction_classes
    }
    assert "WaiterId" in som_module.dimensions
    assert som_module.time_stamp_datatype is not None
    assert som_module.tag_representations
    assert som_module.transportation_names
    assert som_module.switch_settings
    assert som_module.update_rates
    assert som_module.datatype_names
    assert som_module.notes

    assert fom_module.synchronization_points
    assert mim_module.is_mim is True


def test_parse_fom_xml_distinguishes_required_optional_and_conditionally_required_omt_entries(tmp_path: Path):
    valid_minimal = tmp_path / "valid-minimal.xml"
    valid_minimal.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification>
    <name>Minimal</name>
    <type>FOM</type>
  </modelIdentification>
</objectModel>
""",
        encoding="utf-8",
    )

    module = parse_fom_xml(valid_minimal)
    assert module.name == "Minimal"
    assert module.object_classes == ()
    assert module.service_utilization == {}

    invalid_conditional = tmp_path / "invalid-conditional.xml"
    invalid_conditional.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification>
    <name>Conditional</name>
    <type>FOM</type>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Broken</name>
        <attribute>
          <name>Payload</name>
          <transportation>MissingTransport</transportation>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="references undefined transportation type"):
        parse_fom_xml(invalid_conditional)


def test_parse_fom_xml_extracts_switch_table_settings_and_merge_summary():
    module = parse_fom_xml("hla2010/resources/foms/VendorSmokeFOM.xml")
    catalog = merge_fom_modules((module,))

    assert module.model_type == "FOM"
    assert module.switch_settings["autoProvide"] == "false"
    assert module.switch_settings["interactionRelevanceAdvisory"] == "false"
    assert module.switch_settings["automaticResignAction"] == "CancelThenDeleteThenDivest"
    assert catalog.switch_settings["serviceReporting"] == "false"
    assert catalog.switch_settings["automaticResignAction"] == "CancelThenDeleteThenDivest"
    assert catalog.as_summary()["switch_settings"]["autoProvide"] == "false"


def test_parse_fom_xml_extracts_synchronization_table_and_merge_summary(tmp_path: Path):
    xml_path = tmp_path / "omt-synchronization-som.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification>
    <name>Synchronization SOM</name>
    <type>SOM</type>
  </modelIdentification>
  <synchronizations>
    <synchronization>
      <label>ReadyToRun</label>
      <tagDatatype>NA</tagDatatype>
      <capability>RegisterAchieve</capability>
      <semantics>Startup barrier for launch.</semantics>
    </synchronization>
    <synchronization>
      <label>Shutdown</label>
      <tagDatatype>HLAunicodeString</tagDatatype>
      <capability>Achieve</capability>
      <semantics>Clean shutdown barrier.</semantics>
    </synchronization>
  </synchronizations>
</objectModel>
""",
        encoding="utf-8",
    )

    module = parse_fom_xml(xml_path)
    catalog = merge_fom_modules((module,))

    assert module.model_type == "SOM"
    assert module.synchronization_points["ReadyToRun"] == {
        "tag_datatype": "NA",
        "capability": "RegisterAchieve",
        "semantics": "Startup barrier for launch.",
    }
    assert module.synchronization_points["Shutdown"]["tag_datatype"] == "HLAunicodeString"
    assert catalog.synchronization_points["Shutdown"]["capability"] == "Achieve"
    assert catalog.as_summary()["synchronization_points"]["ReadyToRun"]["semantics"] == "Startup barrier for launch."


def test_parse_fom_xml_extracts_tag_table_and_merge_summary():
    target_module = parse_fom_xml("hla2010/resources/foms/TargetRadarFOMmodule.xml")
    vendor_module = parse_fom_xml("hla2010/resources/foms/VendorSmokeFOM.xml")
    catalog = merge_fom_modules((target_module, vendor_module))

    assert target_module.tag_representations["updateReflectTag"] == {
        "datatype": "HLAunicodeString",
        "semantics": "Update tag.",
    }
    assert target_module.tag_representations["sendReceiveTag"] == {
        "datatype": "HLAunicodeString",
        "semantics": "Interaction tag.",
    }
    assert vendor_module.tag_representations["deleteRemoveTag"]["datatype"] == "NA"
    assert catalog.tag_representations["acquisitionRequestTag"]["semantics"] == "NA"
    assert catalog.as_summary()["tag_representations"]["sendReceiveTag"]["datatype"] == "HLAunicodeString"


def test_parse_fom_xml_rejects_duplicate_synchronization_point_labels(tmp_path: Path):
    xml_path = tmp_path / "duplicate-sync.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Duplicate Sync</name><type>FOM</type></modelIdentification>
  <synchronizations>
    <synchronization><label>ReadyToRun</label></synchronization>
    <synchronization><label>ReadyToRun</label></synchronization>
  </synchronizations>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Duplicate synchronization point definition"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_duplicate_transportation_names(tmp_path: Path):
    xml_path = tmp_path / "duplicate-transport.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Duplicate Transport</name><type>FOM</type></modelIdentification>
  <transportations>
    <transportation><name>HLAreliable</name></transportation>
    <transportation><name>HLAreliable</name></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Duplicate transportation type definition"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_duplicate_update_rate_names(tmp_path: Path):
    xml_path = tmp_path / "duplicate-update-rate.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Duplicate Update Rate</name><type>FOM</type></modelIdentification>
  <updateRates>
    <updateRate><name>Fast</name><rate>1.0</rate></updateRate>
    <updateRate><name>Fast</name><rate>2.0</rate></updateRate>
  </updateRates>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Duplicate update rate definition"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_duplicate_datatype_names(tmp_path: Path):
    xml_path = tmp_path / "duplicate-datatype.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Duplicate Datatype</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <simpleDataTypes>
      <simpleData><name>TypeA</name></simpleData>
      <simpleData><name>TypeA</name></simpleData>
    </simpleDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Duplicate datatype definition"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_duplicate_enumeration_values(tmp_path: Path):
    xml_path = tmp_path / "duplicate-enum-values.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Duplicate Enum Values</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <enumeratedDataTypes>
      <enumeratedData>
        <name>Boolish</name>
        <representation>HLAinteger32BE</representation>
        <enumerator><name>False</name><value>0</value></enumerator>
        <enumerator><name>Nope</name><value>0</value></enumerator>
      </enumeratedData>
    </enumeratedDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Duplicate enumeration value definition"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_duplicate_enumerated_datatype_names(tmp_path: Path):
    xml_path = tmp_path / "duplicate-enum-name.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Duplicate Enum Name</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <enumeratedDataTypes>
      <enumeratedData><name>Choice</name><representation>HLAinteger32BE</representation></enumeratedData>
      <enumeratedData><name>Choice</name><representation>HLAinteger32BE</representation></enumeratedData>
    </enumeratedDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Duplicate datatype definition"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_invalid_fixed_array_cardinality(tmp_path: Path):
    xml_path = tmp_path / "invalid-array-cardinality.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Invalid Array</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <arrayDataTypes>
      <arrayData>
        <name>BrokenArray</name>
        <dataType>HLAinteger32BE</dataType>
        <cardinality>abc</cardinality>
        <encoding>HLAfixedArray</encoding>
      </arrayData>
    </arrayDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="invalid cardinality"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_extracts_variant_record_mappings_and_rejects_duplicate_alternatives(tmp_path: Path):
    good = tmp_path / "variant-good.xml"
    bad = tmp_path / "variant-bad.xml"
    variant_xml = """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Variant FOM</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <basicDataRepresentations>
      <basicData><name>HLAinteger32BE</name><size>32</size><endian>Big</endian><encoding>int</encoding></basicData>
    </basicDataRepresentations>
    <enumeratedDataTypes>
      <enumeratedData>
        <name>ChoiceEnum</name>
        <representation>HLAinteger32BE</representation>
        <enumerator><name>A</name><value>1</value></enumerator>
        <enumerator><name>B</name><value>2</value></enumerator>
      </enumeratedData>
    </enumeratedDataTypes>
    <variantRecordDataTypes>
      <variantRecordData>
        <name>ChoiceRecord</name>
        <discriminant>choice</discriminant>
        <dataType>ChoiceEnum</dataType>
        <alternative><enumerator>A</enumerator><name>alpha</name><dataType>HLAinteger32BE</dataType></alternative>
        {duplicate_or_unique}
        <encoding>HLAvariantRecord</encoding>
      </variantRecordData>
    </variantRecordDataTypes>
  </dataTypes>
</objectModel>
"""
    good.write_text(variant_xml.format(duplicate_or_unique="<alternative><enumerator>B</enumerator><name>beta</name><dataType>HLAinteger32BE</dataType></alternative>"), encoding="utf-8")
    bad.write_text(variant_xml.format(duplicate_or_unique="<alternative><enumerator>A</enumerator><name>beta</name><dataType>HLAinteger32BE</dataType></alternative>"), encoding="utf-8")

    module = parse_fom_xml(good)
    assert module.variant_record_datatypes["ChoiceRecord"].discriminant == "choice"
    assert [alt.enumerator for alt in module.variant_record_datatypes["ChoiceRecord"].alternatives] == ["A", "B"]

    with pytest.raises(FOMResolutionError, match="Duplicate discriminant alternative definition"):
        parse_fom_xml(bad)


def test_parse_fom_xml_rejects_undefined_datatype_references(tmp_path: Path):
    xml_path = tmp_path / "undefined-datatype-ref.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Bad Datatype Reference</name><type>FOM</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>BadObject</name>
        <attribute><name>Payload</name><dataType>MissingType</dataType></attribute>
      </objectClass>
    </objectClass>
  </objects>
  <dataTypes>
    <simpleDataTypes>
      <simpleData>
        <name>AliasType</name>
        <representation>MissingBase</representation>
      </simpleData>
    </simpleDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="references undefined datatype"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_unknown_object_model_namespace(tmp_path: Path):
    xml_path = tmp_path / "bad-namespace.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://example.com/not-hla">
  <modelIdentification><name>Bad Namespace</name><type>FOM</type></modelIdentification>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Unsupported objectModel namespace"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_unknown_switch_definition(tmp_path: Path):
    xml_path = tmp_path / "bad-switch.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Bad Switch</name><type>FOM</type></modelIdentification>
  <switches>
    <unsupportedSwitch isEnabled="true"/>
  </switches>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Unknown switch definition"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_undefined_attribute_transportation_reference(tmp_path: Path):
    xml_path = tmp_path / "bad-attribute-transport.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Bad Attribute Transport</name><type>FOM</type></modelIdentification>
  <transportations>
    <transportation><name>HLAreliable</name></transportation>
  </transportations>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>RateObject</name>
        <attribute>
          <name>Payload</name>
          <dataType>HLAunicodeString</dataType>
          <transportation>MissingTransport</transportation>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="references undefined transportation type"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_undefined_interaction_transportation_reference(tmp_path: Path):
    xml_path = tmp_path / "bad-interaction-transport.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Bad Interaction Transport</name><type>FOM</type></modelIdentification>
  <transportations>
    <transportation><name>HLAreliable</name></transportation>
  </transportations>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>BadInteraction</name>
        <transportation>MissingTransport</transportation>
      </interactionClass>
    </interactionClass>
  </interactions>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="references undefined transportation type"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_undefined_update_rate_reference(tmp_path: Path):
    xml_path = tmp_path / "bad-update-rate-ref.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Bad Update Rate Reference</name><type>FOM</type></modelIdentification>
  <updateRates>
    <updateRate><name>Fast</name><rate>2.0</rate></updateRate>
  </updateRates>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>RateObject</name>
        <attribute>
          <name>Payload</name>
          <dataType>HLAunicodeString</dataType>
          <updateRate>MissingRate</updateRate>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="references undefined update rate designator"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_unresolved_simple_array_fixed_and_variant_datatype_references(tmp_path: Path):
    xml_path = tmp_path / "bad-datatype-refs.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Bad Datatype Refs</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <simpleDataTypes>
      <simpleData><name>AliasType</name><representation>MissingBase</representation></simpleData>
    </simpleDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Simple datatype AliasType references undefined datatype"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_unresolved_array_and_fixed_record_datatype_references(tmp_path: Path):
    xml_path = tmp_path / "bad-array-fixed-refs.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Bad Array Fixed Refs</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <arrayDataTypes>
      <arrayData><name>BrokenArray</name><dataType>MissingType</dataType><cardinality>Dynamic</cardinality><encoding>HLAvariableArray</encoding></arrayData>
    </arrayDataTypes>
    <fixedRecordDataTypes>
      <fixedRecordData><name>BrokenRecord</name><encoding>HLAfixedRecord</encoding><field><name>a</name><dataType>MissingFieldType</dataType></field></fixedRecordData>
    </fixedRecordDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Array datatype BrokenArray references undefined datatype"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_unresolved_variant_record_datatype_references(tmp_path: Path):
    xml_path = tmp_path / "bad-variant-refs.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Bad Variant Refs</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <variantRecordDataTypes>
      <variantRecordData>
        <name>BrokenVariant</name>
        <discriminant>choice</discriminant>
        <dataType>MissingDiscriminantType</dataType>
        <alternative><enumerator>A</enumerator><dataType>MissingAltType</dataType></alternative>
      </variantRecordData>
    </variantRecordDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Variant record discriminant BrokenVariant references undefined datatype"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_accepts_namespaced_object_model_and_preserves_ordered_unique_metadata(tmp_path: Path):
    xml_path = tmp_path / "namespaced-omt.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification>
    <name>Namespaced FOM</name>
    <type>FOM</type>
  </modelIdentification>
  <transportations>
    <transportation><name>HLAreliable</name></transportation>
    <transportation><name>HLAbestEffort</name></transportation>
  </transportations>
  <updateRates>
    <updateRate><name>Slow</name><rate>1.0</rate></updateRate>
  </updateRates>
  <dataTypes>
    <simpleDataTypes>
      <simpleData><name>Simple1</name></simpleData>
      <simpleData><name>Simple2</name></simpleData>
    </simpleDataTypes>
    <fixedRecordDataTypes>
      <fixedRecordData><name>Record1</name></fixedRecordData>
    </fixedRecordDataTypes>
  </dataTypes>
  <notes>
    <note><label>N1</label><semantics>alpha</semantics></note>
    <note><semantics>beta</semantics></note>
  </notes>
</objectModel>
""",
        encoding="utf-8",
    )

    module = parse_fom_xml(xml_path)

    assert module.name == "Namespaced FOM"
    assert module.model_type == "FOM"
    assert module.transportation_names == ("HLAreliable", "HLAbestEffort")
    assert module.update_rates == {"Slow": "1.0"}
    assert module.datatype_names == ("Simple1", "Simple2", "Record1")
    assert module.notes == ("N1: alpha", "beta")


def test_parse_fom_xml_rejects_duplicate_dimension_names(tmp_path: Path):
    xml_path = tmp_path / "duplicate-dimension.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Duplicate Dimension</name><type>FOM</type></modelIdentification>
  <dimensions>
    <dimension><name>RegionX</name></dimension>
    <dimension><name>RegionX</name></dimension>
  </dimensions>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Duplicate dimension definition"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_duplicate_object_class_names_in_same_hierarchy(tmp_path: Path):
    xml_path = tmp_path / "duplicate-object-class.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Duplicate Object Class</name><type>FOM</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass><name>Vehicle</name></objectClass>
      <objectClass><name>Vehicle</name></objectClass>
    </objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Duplicate object class definition"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_duplicate_interaction_class_names_in_same_hierarchy(tmp_path: Path):
    xml_path = tmp_path / "duplicate-interaction-class.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Duplicate Interaction Class</name><type>FOM</type></modelIdentification>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass><name>Fire</name></interactionClass>
      <interactionClass><name>Fire</name></interactionClass>
    </interactionClass>
  </interactions>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Duplicate interaction class definition"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_multiple_top_level_object_classes(tmp_path: Path):
    xml_path = tmp_path / "multiple-object-roots.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Bad Object Roots</name><type>FOM</type></modelIdentification>
  <objects>
    <objectClass><name>HLAobjectRoot</name></objectClass>
    <objectClass><name>OrphanRoot</name></objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="must declare exactly one top-level HLAobjectRoot class"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_multiple_top_level_interaction_classes(tmp_path: Path):
    xml_path = tmp_path / "multiple-interaction-roots.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Bad Interaction Roots</name><type>FOM</type></modelIdentification>
  <interactions>
    <interactionClass><name>HLAinteractionRoot</name></interactionClass>
    <interactionClass><name>OrphanRoot</name></interactionClass>
  </interactions>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="must declare exactly one top-level HLAinteractionRoot class"):
        parse_fom_xml(xml_path)


def test_merge_fom_modules_combines_transport_update_rate_datatype_and_note_metadata(tmp_path: Path):
    first = tmp_path / "first.xml"
    second = tmp_path / "second.xml"
    first.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>First</name><type>FOM</type></modelIdentification>
  <transportations>
    <transportation><name>HLAreliable</name></transportation>
  </transportations>
  <updateRates>
    <updateRate><name>Shared</name><rate>1.0</rate></updateRate>
    <updateRate><name>FirstOnly</name><rate>2.0</rate></updateRate>
  </updateRates>
  <dataTypes>
    <simpleDataTypes><simpleData><name>TypeA</name></simpleData></simpleDataTypes>
  </dataTypes>
  <notes><note><label>N1</label><semantics>first</semantics></note></notes>
</objectModel>
""",
        encoding="utf-8",
    )
    second.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Second</name><type>FOM</type></modelIdentification>
  <transportations>
    <transportation><name>HLAbestEffort</name></transportation>
    <transportation><name>HLAreliable</name></transportation>
  </transportations>
  <updateRates>
    <updateRate><name>Shared</name><rate>9.0</rate></updateRate>
    <updateRate><name>SecondOnly</name><rate>3.0</rate></updateRate>
  </updateRates>
  <dataTypes>
    <simpleDataTypes><simpleData><name>TypeB</name></simpleData></simpleDataTypes>
  </dataTypes>
  <notes>
    <note><label>N1</label><semantics>first</semantics></note>
    <note><label>N2</label><semantics>second</semantics></note>
  </notes>
</objectModel>
""",
        encoding="utf-8",
    )

    catalog = merge_fom_modules((parse_fom_xml(first), parse_fom_xml(second)))
    summary = catalog.as_summary()

    assert summary["transportation_names"] == ["HLAbestEffort", "HLAreliable"]
    assert summary["datatype_names"] == ["TypeA", "TypeB"]
    assert summary["update_rates"] == {"FirstOnly": "2.0", "SecondOnly": "3.0", "Shared": "1.0"}
    assert summary["notes"] == ["N1: first", "N2: second"]


def test_merge_fom_modules_preserves_class_datatype_and_dimension_consistency(tmp_path: Path):
    first = tmp_path / "merge-first.xml"
    second = tmp_path / "merge-second.xml"
    first.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>First</name><type>FOM</type></modelIdentification>
  <dimensions><dimension><name>DimA</name></dimension></dimensions>
  <objects><objectClass><name>HLAobjectRoot</name><objectClass><name>A</name></objectClass></objectClass></objects>
  <dataTypes><simpleDataTypes><simpleData><name>TypeA</name><representation>HLAinteger32BE</representation></simpleData></simpleDataTypes></dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )
    second.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Second</name><type>FOM</type></modelIdentification>
  <dimensions><dimension><name>DimB</name></dimension></dimensions>
  <interactions><interactionClass><name>HLAinteractionRoot</name><interactionClass><name>B</name></interactionClass></interactionClass></interactions>
  <dataTypes><simpleDataTypes><simpleData><name>TypeB</name><representation>HLAinteger32BE</representation></simpleData></simpleDataTypes></dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )

    catalog = merge_fom_modules((parse_fom_xml(first), parse_fom_xml(second)))

    assert "HLAobjectRoot.A" in catalog.object_classes
    assert "HLAinteractionRoot.B" in catalog.interaction_classes
    assert catalog.dimensions == frozenset({"DimA", "DimB"})
    assert set(catalog.simple_datatypes) == {"TypeA", "TypeB"}


def test_merge_fom_modules_rejects_conflicting_duplicate_datatype_definitions(tmp_path: Path):
    first = tmp_path / "merge-conflict-a.xml"
    second = tmp_path / "merge-conflict-b.xml"
    xml_template = """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>{name}</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <simpleDataTypes>
      <simpleData><name>SharedType</name><representation>{representation}</representation></simpleData>
    </simpleDataTypes>
  </dataTypes>
</objectModel>
"""
    first.write_text(xml_template.format(name="A", representation="HLAinteger32BE"), encoding="utf-8")
    second.write_text(xml_template.format(name="B", representation="HLAinteger64BE"), encoding="utf-8")

    with pytest.raises(FOMMergeError, match="Conflicting simple datatype definition"):
        merge_fom_modules((parse_fom_xml(first), parse_fom_xml(second)))


def test_serialize_fom_module_preserves_metadata_subset_across_round_trip(tmp_path: Path):
    module = FOMModule(
        source="synthetic",
        uri="synthetic:omt",
        name="Round Trip FOM",
        model_type="FOM",
        basic_datatypes={
            "HLAinteger32BE": BasicDatatypeSpec(
                name="HLAinteger32BE",
                size="32",
                interpretation="Integer",
                endian="Big",
                encoding="32-bit signed",
            )
        },
        simple_datatypes={
            "Simple1": SimpleDatatypeSpec(
                name="Simple1",
                representation="HLAinteger32BE",
                units="NA",
                resolution="1",
                accuracy="Perfect",
                semantics="Primary simple datatype.",
            ),
            "Record1": SimpleDatatypeSpec(
                name="Record1",
                representation="HLAinteger32BE",
                units="NA",
                resolution="1",
                accuracy="Perfect",
                semantics="Compatibility placeholder datatype.",
            ),
        },
        tag_representations={
            "sendReceiveTag": {"datatype": "Simple1", "semantics": "Interaction tag."},
        },
        transportation_names=("HLAreliable", "HLAbestEffort"),
        update_rates={"Fast": "10.0"},
        synchronization_points={
            "ReadyToRun": {
                "tag_datatype": "Simple1",
                "capability": "RegisterAchieve",
                "semantics": "Startup barrier.",
            },
        },
        switch_settings={"autoProvide": "false", "automaticResignAction": "CancelThenDeleteThenDivest"},
        notes=("N1: alpha", "beta"),
    )

    xml_text = serialize_fom_module(module)
    xml_path = tmp_path / "round-trip.xml"
    xml_path.write_text(xml_text, encoding="utf-8")

    reparsed = parse_fom_xml(xml_path)

    assert 'xmlns="http://standards.ieee.org/IEEE1516-2010"' in xml_text
    assert reparsed.name == module.name
    assert reparsed.model_type == module.model_type
    assert {"Simple1", "Record1"}.issubset(set(reparsed.datatype_names))
    assert reparsed.tag_representations == module.tag_representations
    assert reparsed.transportation_names == module.transportation_names
    assert reparsed.update_rates == module.update_rates
    assert reparsed.synchronization_points == module.synchronization_points
    for name, value in module.switch_settings.items():
        assert reparsed.switch_settings[name] == value
    assert reparsed.notes == module.notes


def test_parse_fom_xml_with_schema_validation_accepts_standard_target_radar_module():
    module = parse_fom_xml("hla2010/resources/foms/TargetRadarFOMmodule.xml", validate_schema=True)
    assert module.name == "Target Radar FOM Module"


def test_parse_fom_xml_with_schema_validation_rejects_schema_invalid_document(tmp_path: Path):
    xml_path = tmp_path / "schema-invalid.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Bad Schema</name><type>FOM</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Child</name>
        <attribute><dataType>HLAunicodeString</dataType></attribute>
      </objectClass>
    </objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Schema-invalid DIF XML"):
        parse_fom_xml(xml_path, validate_schema=True)


def test_serialize_fom_module_emits_schema_valid_xml_and_preserves_identification(tmp_path: Path):
    module = FOMModule(
        source="schema",
        uri="schema",
        name="Schema Valid FOM",
        model_type="FOM",
        basic_datatypes={
            "HLAinteger32BE": BasicDatatypeSpec(
                name="HLAinteger32BE",
                size="32",
                interpretation="Integer",
                endian="Big",
                encoding="32-bit signed",
            )
        },
        simple_datatypes={
            "ClockType": SimpleDatatypeSpec(
                name="ClockType",
                representation="HLAinteger32BE",
                units="NA",
                resolution="1",
                accuracy="NA",
                semantics="Alias",
            )
        },
        time_stamp_datatype="ClockType",
        lookahead_datatype="ClockType",
    )
    xml_text = serialize_fom_module(module)
    xml_path = tmp_path / "schema-valid.xml"
    xml_path.write_text(xml_text, encoding="utf-8")

    validate_fom_xml_schema(xml_path, profile="dif")
    reparsed = parse_fom_xml(xml_path, validate_schema=True)
    assert reparsed.name == "Schema Valid FOM"
    assert reparsed.model_type == "FOM"


def test_serialize_fom_module_round_trips_object_interaction_and_dimension_tables(tmp_path: Path):
    module = FOMModule(
        source="tables",
        uri="tables",
        name="Structured FOM",
        model_type="FOM",
        object_classes=(
            ObjectClassSpec("HLAobjectRoot"),
            ObjectClassSpec(
                "HLAobjectRoot.Vehicle",
                attributes=("Position",),
                parent_name="HLAobjectRoot",
                declared_attributes=("Position",),
                attribute_datatypes={"Position": "ClockType"},
                attribute_transportations={"Position": "HLAreliable"},
            ),
            ObjectClassSpec(
                "HLAobjectRoot.Vehicle.Car",
                attributes=("Position", "Speed"),
                parent_name="HLAobjectRoot.Vehicle",
                declared_attributes=("Speed",),
                attribute_datatypes={"Position": "ClockType", "Speed": "ClockType"},
                attribute_transportations={"Speed": "HLAreliable"},
            ),
        ),
        interaction_classes=(
            InteractionClassSpec("HLAinteractionRoot"),
            InteractionClassSpec(
                "HLAinteractionRoot.Report",
                parameters=("Payload",),
                parent_name="HLAinteractionRoot",
                declared_parameters=("Payload",),
                parameter_datatypes={"Payload": "ClockType"},
                transportation="HLAreliable",
            ),
            InteractionClassSpec(
                "HLAinteractionRoot.Report.Nested",
                parameters=("Payload", "Extra"),
                parent_name="HLAinteractionRoot.Report",
                declared_parameters=("Extra",),
                parameter_datatypes={"Payload": "ClockType", "Extra": "ClockType"},
                transportation="HLAreliable",
            ),
        ),
        dimensions=("RouteDim",),
        simple_datatypes={
            "ClockType": SimpleDatatypeSpec(
                name="ClockType",
                representation="HLAinteger32BE",
                units="NA",
                resolution="1",
                accuracy="Perfect",
            )
        },
        transportation_names=("HLAreliable",),
    )

    xml_text = serialize_fom_module(module)
    xml_path = tmp_path / "structured-round-trip.xml"
    xml_path.write_text(xml_text, encoding="utf-8")

    validate_fom_xml_schema(xml_path, profile="dif")
    reparsed = parse_fom_xml(xml_path, validate_schema=True)

    assert "HLAobjectRoot.Vehicle" in {spec.full_name for spec in reparsed.object_classes}
    assert "HLAobjectRoot.Vehicle.Car" in {spec.full_name for spec in reparsed.object_classes}
    assert reparsed.object_classes[1].declared_attributes == ("Position",)
    assert reparsed.object_classes[2].parent_name == "HLAobjectRoot.Vehicle"
    assert reparsed.object_classes[2].attribute_datatypes["Speed"] == "ClockType"
    assert reparsed.object_classes[2].attribute_transportations["Speed"] == "HLAreliable"
    assert "HLAinteractionRoot.Report.Nested" in {spec.full_name for spec in reparsed.interaction_classes}
    assert reparsed.interaction_classes[2].declared_parameters == ("Extra",)
    assert reparsed.interaction_classes[2].parameter_datatypes["Extra"] == "ClockType"
    assert reparsed.interaction_classes[2].transportation == "HLAreliable"
    assert reparsed.dimensions == ("RouteDim",)


def test_parse_fom_xml_extracts_richer_datatype_semantics_and_merge_summary():
    module = parse_fom_xml("CERTI/xml/ieee1516-2010/1516_2-2010/RestaurantFOMmodule.xml")
    catalog = merge_fom_modules((module,))

    assert module.simple_datatypes["RateScale"].representation == "HLAinteger32BE"
    assert module.simple_datatypes["RateScale"].accuracy == "Perfect"
    assert [item.name for item in module.enumerated_datatypes["WaiterTasks"].enumerators] == [
        "TakingOrder",
        "Serving",
        "Cleaning",
        "CalculatingBill",
        "Other",
    ]
    assert module.array_datatypes["Employees"].encoding == "HLAfixedArray"
    assert module.array_datatypes["AddressBook"].cardinality == "Dynamic"
    assert [field.name for field in module.fixed_record_datatypes["AddressType"].fields] == [
        "Name",
        "Street",
        "City",
        "State",
        "Zip",
    ]
    assert module.variant_record_datatypes["WaiterValue"].discriminant == "ValIndex"
    assert module.variant_record_datatypes["WaiterValue"].alternatives[1].enumerator == "[Apprentice .. Senior], Master"
    assert catalog.as_summary()["enumerated_datatypes"]["WaiterTasks"]["enumerators"][0]["name"] == "TakingOrder"
    assert catalog.as_summary()["variant_record_datatypes"]["WaiterValue"]["alternatives"][2]["enumerator"] == "HLAother"


def test_validate_encoded_datatype_value_supports_enumerations_arrays_records_and_variants():
    catalog = merge_fom_modules((parse_fom_xml("CERTI/xml/ieee1516-2010/1516_2-2010/RestaurantFOMmodule.xml"),))

    validate_encoded_datatype_value(HLAinteger32BE(2).encode(), "WaiterTasks", catalog)
    validate_encoded_datatype_value(
        HLAfixedArray([HLAinteger32BE(index) for index in range(10)]).encode(),
        "Employees",
        catalog,
    )
    validate_encoded_datatype_value(
        HLAfixedRecord([HLAboolean(True), HLAboolean(False), HLAboolean(True)]).encode(),
        "ServiceStat",
        catalog,
    )
    validate_encoded_datatype_value(HLAinteger32BE(0).encode() + HLAboolean(True).encode(), "WaiterValue", catalog)
    validate_encoded_datatype_value(HLAinteger32BE(3).encode() + HLAinteger32BE(7).encode(), "WaiterValue", catalog)


def test_validate_encoded_datatype_value_rejects_invalid_enumerator_and_array_payload():
    catalog = merge_fom_modules((parse_fom_xml("CERTI/xml/ieee1516-2010/1516_2-2010/RestaurantFOMmodule.xml"),))

    with pytest.raises(CouldNotDecode, match="not valid for enumeration"):
        validate_encoded_datatype_value(HLAinteger32BE(999).encode(), "WaiterTasks", catalog)
    with pytest.raises(CouldNotDecode, match="trailing payload remains"):
        validate_encoded_datatype_value(
            HLAfixedArray([HLAinteger32BE(index) for index in range(11)]).encode(),
            "Employees",
            catalog,
        )


def test_parse_fom_xml_rejects_duplicate_enumeration_names_and_values(tmp_path: Path):
    xml_path = tmp_path / "duplicate-enumerator.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Duplicate Enumerators</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <enumeratedDataTypes>
      <enumeratedData>
        <name>EnumA</name>
        <representation>HLAinteger32BE</representation>
        <enumerator><name>Alpha</name><value>1</value></enumerator>
        <enumerator><name>Alpha</name><value>2</value></enumerator>
      </enumeratedData>
    </enumeratedDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )
    with pytest.raises(FOMResolutionError, match="Duplicate enumeration name definition"):
        parse_fom_xml(xml_path)

    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Duplicate Enumeration Values</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <enumeratedDataTypes>
      <enumeratedData>
        <name>EnumA</name>
        <representation>HLAinteger32BE</representation>
        <enumerator><name>Alpha</name><value>1</value></enumerator>
        <enumerator><name>Bravo</name><value>1</value></enumerator>
      </enumeratedData>
    </enumeratedDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )
    with pytest.raises(FOMResolutionError, match="Duplicate enumeration value definition"):
        parse_fom_xml(xml_path)


def test_parse_fom_xml_rejects_invalid_array_cardinality_and_duplicate_variant_alternatives(tmp_path: Path):
    xml_path = tmp_path / "bad-array-cardinality.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Bad Cardinality</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <arrayDataTypes>
      <arrayData>
        <name>BadArray</name>
        <dataType>HLAinteger32BE</dataType>
        <cardinality>bad</cardinality>
        <encoding>HLAfixedArray</encoding>
      </arrayData>
    </arrayDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )
    with pytest.raises(FOMResolutionError, match="invalid cardinality"):
        parse_fom_xml(xml_path)

    xml_path = tmp_path / "duplicate-variant-alt.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Duplicate Variant Alternatives</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <enumeratedDataTypes>
      <enumeratedData>
        <name>Selector</name>
        <representation>HLAinteger32BE</representation>
        <enumerator><name>Alpha</name><value>1</value></enumerator>
      </enumeratedData>
    </enumeratedDataTypes>
    <variantRecordDataTypes>
      <variantRecordData>
        <name>VariantA</name>
        <discriminant>Kind</discriminant>
        <dataType>Selector</dataType>
        <alternative><enumerator>Alpha</enumerator><dataType>HLAinteger32BE</dataType></alternative>
        <alternative><enumerator>Alpha</enumerator><dataType>HLAinteger32BE</dataType></alternative>
        <encoding>HLAvariantRecord</encoding>
      </variantRecordData>
    </variantRecordDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )
    with pytest.raises(FOMResolutionError, match="Duplicate discriminant alternative definition"):
        parse_fom_xml(xml_path)


def test_merge_fom_modules_preserves_dimension_and_datatype_consistency(tmp_path: Path):
    first = tmp_path / "first-merge.xml"
    second = tmp_path / "second-merge.xml"
    first.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>First</name><type>FOM</type></modelIdentification>
  <dimensions><dimension><name>RegionX</name></dimension></dimensions>
  <dataTypes>
    <enumeratedDataTypes>
      <enumeratedData>
        <name>Mode</name><representation>HLAinteger32BE</representation>
        <enumerator><name>Alpha</name><value>1</value></enumerator>
      </enumeratedData>
    </enumeratedDataTypes>
  </dataTypes>
  <objects><objectClass><name>HLAobjectRoot</name><objectClass><name>Vehicle</name></objectClass></objectClass></objects>
</objectModel>
""",
        encoding="utf-8",
    )
    second.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Second</name><type>FOM</type></modelIdentification>
  <dimensions><dimension><name>RegionY</name></dimension></dimensions>
  <dataTypes>
    <enumeratedDataTypes>
      <enumeratedData>
        <name>Mode</name><representation>HLAinteger32BE</representation>
        <enumerator><name>Alpha</name><value>1</value></enumerator>
      </enumeratedData>
    </enumeratedDataTypes>
  </dataTypes>
  <objects><objectClass><name>HLAobjectRoot</name><objectClass><name>Vehicle</name><objectClass><name>Car</name></objectClass></objectClass></objectClass></objects>
</objectModel>
""",
        encoding="utf-8",
    )

    catalog = merge_fom_modules((parse_fom_xml(first), parse_fom_xml(second)))
    summary = catalog.as_summary()

    assert summary["dimensions"] == ["RegionX", "RegionY"]
    assert summary["enumerated_datatypes"]["Mode"]["enumerators"] == [{"name": "Alpha", "values": ["1"]}]
    assert "HLAobjectRoot.Vehicle" in summary["object_classes"]
    assert "HLAobjectRoot.Vehicle.Car" in summary["object_classes"]


def test_parse_fom_xml_with_omt_schema_validation_accepts_restaurant_reference_module_and_rejects_invalid_document(tmp_path: Path):
    valid = tmp_path / "valid-omt.xml"
    valid.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification>
    <name>Valid OMT</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-07</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Schema-valid minimal OMT document.</description>
    <poc><pocType>Sponsor</pocType><pocName>Codex</pocName></poc>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <sharing>Neither</sharing>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <sharing>Neither</sharing>
      <transportation>HLAreliable</transportation>
      <order>Receive</order>
    </interactionClass>
  </interactions>
  <dimensions>
    <dimension>
      <name>RouteDim</name>
      <dataType>DimValue</dataType>
      <upperBound>100</upperBound>
      <normalization>Linear</normalization>
    </dimension>
  </dimensions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
    <transportation><name>HLAbestEffort</name><reliable>No</reliable></transportation>
  </transportations>
  <switches>
    <autoProvide isEnabled="false"/>
    <conveyRegionDesignatorSets isEnabled="false"/>
    <conveyProducingFederate isEnabled="false"/>
    <attributeScopeAdvisory isEnabled="false"/>
    <attributeRelevanceAdvisory isEnabled="false"/>
    <objectClassRelevanceAdvisory isEnabled="false"/>
    <interactionRelevanceAdvisory isEnabled="false"/>
    <serviceReporting isEnabled="false"/>
    <exceptionReporting isEnabled="false"/>
    <delaySubscriptionEvaluation isEnabled="false"/>
    <automaticResignAction resignAction="NoAction"/>
  </switches>
  <dataTypes>
    <basicDataRepresentations>
      <basicData>
        <name>HLAinteger32BE</name>
        <size>32</size>
        <interpretation>Integer</interpretation>
        <endian>Big</endian>
        <encoding>32-bit signed</encoding>
      </basicData>
    </basicDataRepresentations>
    <simpleDataTypes>
      <simpleData>
        <name>DimValue</name>
        <representation>HLAinteger32BE</representation>
        <units>NA</units>
        <resolution>1</resolution>
        <accuracy>Perfect</accuracy>
      </simpleData>
    </simpleDataTypes>
    <enumeratedDataTypes/>
    <arrayDataTypes/>
    <fixedRecordDataTypes/>
    <variantRecordDataTypes/>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )
    valid_module = parse_fom_xml(valid, validate_schema="omt")
    assert valid_module.name == "Valid OMT"

    invalid = tmp_path / "invalid-omt.xml"
    invalid.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>Broken</name><type>FOM</type></modelIdentification>
</objectModel>
""",
        encoding="utf-8",
    )

    with pytest.raises(FOMResolutionError, match="Schema-invalid OMT XML"):
        parse_fom_xml(invalid, validate_schema="omt")


def test_1516_2_hierarchy_doc_declares_omt_lexicon_and_conformance_boundary():
    text = (
        Path(__file__).resolve().parents[2] / "docs" / "verification" / "requirements_hierarchy.md"
    ).read_text(encoding="utf-8")

    assert "## OMT Lexicon" in text
    assert "`FOM module`" in text
    assert "`SOM module`" in text
    assert "`MIM`" in text
    assert "`FDD`" in text
    assert "## Conformance Claim Boundary" in text
    assert "does not claim full IEEE 1516.2-2010 conformance" in text
    assert "`mapped` requirement rows identify the implemented and executable OMT subset only" in text
    assert "`planned` requirement rows identify unimplemented" in text
