from __future__ import annotations

import uuid
from pathlib import Path

import pytest


OMT_2025_SCHEMA = Path("docs/requirements/ieee-1516-2025/encoding_auth_work_packet/09-standards-subset/IEEE1516-OMT-2025.xsd")


STRICT_OMT_2025_FIXTURE = """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification><name>Schema Valid Probe</name><type>FOM</type><version>1.0</version><modificationDate>2026-06-18</modificationDate><securityClassification>Unclassified</securityClassification><applicationDomain>Training</applicationDomain><description>Probe.</description><poc><pocType>Sponsor</pocType><pocName>Test</pocName></poc><reference><type>URL</type><identification>https://example.invalid/ref</identification></reference></modelIdentification>
  <objects><objectClass><name>HLAobjectRoot</name><sharing>Neither</sharing><semantics>Root</semantics><attribute><name>Status</name><dataType>HLAunicodeString</dataType><updateType>Static</updateType><valueRequired>true</valueRequired><ownership>NoTransfer</ownership><sharing>PublishSubscribe</sharing><transportation>HLAreliable</transportation><order>Receive</order><semantics>Status</semantics></attribute></objectClass></objects>
  <interactions><interactionClass><name>HLAinteractionRoot</name><sharing>Neither</sharing><transportation>HLAreliable</transportation><order>Receive</order><semantics>Root</semantics><parameter><name>Message</name><dataType>HLAunicodeString</dataType><semantics>Message</semantics></parameter></interactionClass></interactions>
  <dimensions><dimension><name>RoutingSpace</name><inputDataTypes><dataType>RouteEnum</dataType></inputDataTypes><inputDataDescription>Route</inputDataDescription><upperBound>1</upperBound><normalization>None</normalization><outputDataSemantics>None</outputDataSemantics><value>[0..1)</value></dimension></dimensions>
  <synchronizations><synchronizationPoint><label>Ready</label><dataType>HLAunicodeString</dataType><capability>RegisterAchieve</capability><semantics>Ready</semantics></synchronizationPoint></synchronizations>
  <transportations><transportation><name>HLAreliable</name><reliable>Yes</reliable><semantics>Reliable</semantics></transportation></transportations>
  <switches><automaticResignAction resignAction="NoAction"/></switches>
  <updateRates><updateRate><name>DefaultRate</name><rate>1</rate><semantics>Rate</semantics></updateRate></updateRates>
  <dataTypes><basicDataRepresentations><basicData><name>HLAinteger32BE</name><size>32</size><interpretation>integer</interpretation><endian>Big</endian><encoding>HLAinteger32BE</encoding></basicData><basicData><name>HLAunicodeString</name><size>0</size><interpretation>string</interpretation><endian>Big</endian><encoding>HLAunicodeString</encoding></basicData></basicDataRepresentations><simpleDataTypes><simpleData><name>RouteSimple</name><representation>HLAinteger32BE</representation><semantics>Route</semantics></simpleData></simpleDataTypes><referenceDataTypes><referenceDataType><name>StatusRef</name><representation>HLAunicodeString</representation><referenceClass>HLAobjectRoot</referenceClass><referencedAttribute>Status</referencedAttribute><semantics>Status ref</semantics></referenceDataType></referenceDataTypes><enumeratedDataTypes><enumeratedData><name>RouteEnum</name><representation>HLAinteger32BE</representation><semantics>Route enum</semantics><enumerator><name>A</name><value>0</value></enumerator></enumeratedData></enumeratedDataTypes><arrayDataTypes></arrayDataTypes><fixedRecordDataTypes><fixedRecordData><name>FixedPayload</name><encoding>HLAfixedRecord</encoding><semantics>Fixed</semantics><field><name>FieldA</name><dataType>HLAunicodeString</dataType><semantics>Field</semantics></field></fixedRecordData></fixedRecordDataTypes><variantRecordDataTypes><variantRecordData><name>VariantPayload</name><discriminant>Kind</discriminant><dataType>RouteEnum</dataType><alternative><enumerator>A</enumerator><name>Text</name><dataType>HLAunicodeString</dataType><semantics>Text</semantics></alternative><encoding>HLAvariantRecord</encoding><semantics>Variant</semantics></variantRecordData></variantRecordDataTypes></dataTypes>
</objectModel>
"""


def _write_strict_omt_fixture(tmp_path: Path, text: str = STRICT_OMT_2025_FIXTURE) -> Path:
    source = tmp_path / f"strict-omt-{uuid.uuid4().hex[:8]}.xml"
    source.write_text(text, encoding="utf-8")
    return source


def _schema_issue_requirements(tmp_path: Path, text: str) -> set[str]:
    from hla.fom.validation import validate_omt_xml_schema

    return {issue.requirement for issue in validate_omt_xml_schema(_write_strict_omt_fixture(tmp_path, text), OMT_2025_SCHEMA)}


def _wrap_omt_2025_fragment(body: str, *, extra_root_attrs: str = "") -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025"{extra_root_attrs}>\n'
        f"{body}\n"
        "</objectModel>\n"
    )


@pytest.mark.requirements(
    "HLA2025-OMT-CV-015",
    "HLA2025-OMT-CV-016",
    "HLA2025-OMT-CV-017",
    "HLA2025-OMT-CV-018",
    "HLA2025-OMT-CV-019",
    "HLA2025-OMT-CV-020",
    "HLA2025-OMT-CV-021",
    "HLA2025-OMT-CV-022",
    "HLA2025-OMT-CV-023",
    "HLA2025-OMT-CV-024",
    "HLA2025-OMT-CV-025",
    "HLA2025-OMT-CV-026",
    "HLA2025-OMT-CV-027",
    "HLA2025-OMT-CV-028",
    "HLA2025-OMT-CV-029",
)
@pytest.mark.parametrize(
    ("expected_requirement", "old", "new"),
    [
        ("HLA2025-OMT-CV-015", 'resignAction="NoAction"', 'resignAction="BadResign"'),
        ("HLA2025-OMT-CV-016", "<reliable>Yes</reliable>", "<reliable>Maybe</reliable>"),
        ("HLA2025-OMT-CV-017", "<sharing>Neither</sharing>", "<sharing>BadSharing</sharing>"),
        ("HLA2025-OMT-CV-018", "<order>Receive</order>", "<order>BadOrder</order>"),
        ("HLA2025-OMT-CV-019", "<endian>Big</endian>", "<endian>Middle</endian>"),
        ("HLA2025-OMT-CV-020", "<type>FOM</type>", "<type>BadModel</type>"),
        ("HLA2025-OMT-CV-021", "<capability>RegisterAchieve</capability>", "<capability>BadCapability</capability>"),
        ("HLA2025-OMT-CV-022", "<updateType>Static</updateType>", "<updateType>BadUpdate</updateType>"),
        ("HLA2025-OMT-CV-023", "<ownership>NoTransfer</ownership>", "<ownership>BadOwnership</ownership>"),
        ("HLA2025-OMT-CV-024", "<valueRequired>true</valueRequired>", "<valueRequired>maybe</valueRequired>"),
        ("HLA2025-OMT-CV-025", "<securityClassification>Unclassified</securityClassification>", "<securityClassification>BadSecurity</securityClassification>"),
        ("HLA2025-OMT-CV-026", "<applicationDomain>Training</applicationDomain>", "<applicationDomain>BadDomain</applicationDomain>"),
        ("HLA2025-OMT-CV-027", "<encoding>HLAfixedRecord</encoding>", "<encoding>BadFixedRecord</encoding>"),
        ("HLA2025-OMT-CV-028", "<encoding>HLAvariantRecord</encoding>", "<encoding>BadVariantRecord</encoding>"),
        ("HLA2025-OMT-CV-029", "<pocType>Sponsor</pocType>", "<pocType>BadPoc</pocType>"),
    ],
)
def test_2025_omt_schema_validation_rejects_enumeration_domains(
    tmp_path: Path,
    expected_requirement: str,
    old: str,
    new: str,
) -> None:
    from hla.fom.validation import validate_omt_xml_schema

    assert validate_omt_xml_schema(_write_strict_omt_fixture(tmp_path), OMT_2025_SCHEMA) == []

    requirements = _schema_issue_requirements(tmp_path, STRICT_OMT_2025_FIXTURE.replace(old, new, 1))

    assert expected_requirement in requirements


@pytest.mark.requirements(
    "HLA2025-OMT-CV-001",
    "HLA2025-OMT-CV-002",
    "HLA2025-OMT-CV-003",
    "HLA2025-OMT-CV-004",
    "HLA2025-OMT-CV-005",
    "HLA2025-OMT-CV-006",
    "HLA2025-OMT-CV-007",
    "HLA2025-OMT-CV-008",
    "HLA2025-OMT-CV-009",
    "HLA2025-OMT-CV-010",
    "HLA2025-OMT-CV-011",
    "HLA2025-OMT-CV-012",
    "HLA2025-OMT-CV-013",
    "HLA2025-OMT-CV-014",
)
def test_2025_omt_schema_validation_rejects_named_keyref_and_unique_constraints(tmp_path: Path) -> None:
    from hla.fom.validation import validate_omt_xml_schema

    schema_text = OMT_2025_SCHEMA.read_text(encoding="utf-8")
    for constraint_name in (
        "dimensionDataTypeKey",
        "dimensionDataTypeRef",
        "representationKey",
        "representationRef",
        "dataTypeKey",
        "dataTypeRef",
        "dimensionKey",
        "dimensionRef",
        "transportationKey",
        "transportationRef",
        "className",
        "attributeName",
        "interactionName",
        "parameterName",
    ):
        assert constraint_name in schema_text

    assert validate_omt_xml_schema(_write_strict_omt_fixture(tmp_path), OMT_2025_SCHEMA) == []
    negative_cases = [
        ("HLA2025-OMT-CV-006", "<dataType>HLAunicodeString</dataType>", "<dataType>MissingDataType</dataType>"),
        ("HLA2025-OMT-CV-010", "<transportation>HLAreliable</transportation>", "<transportation>MissingTransport</transportation>"),
        (
            "HLA2025-OMT-CV-012",
            "<attribute><name>Status</name>",
            "<attribute><name>Status</name><dataType>HLAunicodeString</dataType><updateType>Static</updateType><ownership>NoTransfer</ownership><sharing>PublishSubscribe</sharing><transportation>HLAreliable</transportation><order>Receive</order></attribute><attribute><name>Status</name>",
        ),
    ]

    for expected_requirement, old, new in negative_cases:
        requirements = _schema_issue_requirements(tmp_path, STRICT_OMT_2025_FIXTURE.replace(old, new, 1))
        assert expected_requirement in requirements


@pytest.mark.requirements(
    "HLA2025-MOD-010",
    "HLA2025-VER-002",
    "HLA2025-OMT-002",
    "HLA2025-OMT-COMP-192",
    "HLA2025-OMT-COMP-196",
)
def test_2025_parser_round_trips_logical_time_xml_names(tmp_path: Path) -> None:
    from hla.fom import parse_fom_xml, serialize_fom_module

    source = tmp_path / "logical-time-2025.xml"
    source.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Logical Time 2025 FOM</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>2025 logical time naming fixture.</description>
    <poc><pocName>Test</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects><objectClass><name>HLAobjectRoot</name></objectClass></objects>
  <time>
    <logicalTime><dataType>HLAinteger64Time</dataType><semantics>Logical time semantics.</semantics></logicalTime>
    <logicalTimeInterval><dataType>HLAinteger64Time</dataType><semantics>Lookahead semantics.</semantics></logicalTimeInterval>
  </time>
</objectModel>
""",
        encoding="utf-8",
    )

    module = parse_fom_xml(source)
    assert module.time_stamp_datatype == "HLAinteger64Time"
    assert module.lookahead_datatype == "HLAinteger64Time"
    assert module.time_stamp_semantics == "Logical time semantics."
    assert module.lookahead_semantics == "Lookahead semantics."
    assert module.inferred_time_implementation == "HLAinteger64Time"

    xml_text = serialize_fom_module(module, edition="2025")
    assert "http://standards.ieee.org/IEEE1516-2025" in xml_text
    assert "<logicalTime>" in xml_text
    assert "<logicalTimeInterval>" in xml_text
    assert "<timeStamp>" not in xml_text
    assert "<lookahead>" not in xml_text

    roundtrip = tmp_path / "logical-time-roundtrip-2025.xml"
    roundtrip.write_text(xml_text, encoding="utf-8")
    reparsed = parse_fom_xml(roundtrip)
    assert reparsed.time_stamp_datatype == "HLAinteger64Time"
    assert reparsed.lookahead_datatype == "HLAinteger64Time"
    assert reparsed.time_stamp_semantics == "Logical time semantics."
    assert reparsed.lookahead_semantics == "Lookahead semantics."


@pytest.mark.requirements("HLA2025-NEW-006", "HLA2025-OMT-002", "HLA2025-OMT-006")
def test_2025_parser_preserves_reference_datatypes_and_value_required_metadata(tmp_path: Path) -> None:
    from hla.fom.validation import validate_fom_module
    from hla.fom import parse_fom_xml, serialize_fom_module

    source = tmp_path / "reference-value-required.xml"
    source.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Reference Value Required FOM</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Reference datatype and valueRequired validation fixture.</description>
    <poc><pocName>Test</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Entity</name>
        <attribute>
          <name>EntityId</name>
          <dataType>HLAunicodeString</dataType>
          <valueRequired>true</valueRequired>
        </attribute>
        <attribute>
          <name>OptionalLabel</name>
          <dataType>HLAunicodeString</dataType>
          <valueRequired>false</valueRequired>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <dataTypes>
    <referenceDataTypes>
      <referenceDataType>
        <name>EntityIdReference</name>
        <representation>HLAunicodeString</representation>
        <referenceClass>HLAobjectRoot.Entity</referenceClass>
        <referencedAttribute>EntityId</referencedAttribute>
        <semantics>Reference to an Entity object by EntityId.</semantics>
      </referenceDataType>
    </referenceDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )

    module = parse_fom_xml(source)
    entity = next(spec for spec in module.object_classes if spec.full_name == "HLAobjectRoot.Entity")
    reference = module.reference_datatypes["EntityIdReference"]

    assert entity.attribute_value_required == {"EntityId": "true", "OptionalLabel": "false"}
    assert reference.representation == "HLAunicodeString"
    assert reference.reference_class == "HLAobjectRoot.Entity"
    assert reference.referenced_attribute == "EntityId"
    assert validate_fom_module(module) == []

    roundtrip = tmp_path / "roundtrip.xml"
    roundtrip.write_text(serialize_fom_module(module), encoding="utf-8")
    reparsed = parse_fom_xml(roundtrip)
    reparsed_entity = next(spec for spec in reparsed.object_classes if spec.full_name == "HLAobjectRoot.Entity")

    assert "EntityIdReference" in reparsed.reference_datatypes
    assert reparsed_entity.attribute_value_required == {"EntityId": "true", "OptionalLabel": "false"}


@pytest.mark.requirements("HLA2025-OMT-001", "HLA2025-MOD-010", "HLA2025-FR-003", "HLA2025-FR-004")
def test_2025_validation_allows_standard_mim_hla_attribute_and_parameter_names(tmp_path: Path) -> None:
    from hla.fom.validation import validate_fom_modules
    from hla.fom import FOMResolver

    source = tmp_path / "ddm-mim-probe.xml"
    source.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>DDM MIM Probe</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-22</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Probe fixture merged with standard MIM.</description>
    <poc><pocName>Test</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Target</name>
        <sharing>PublishSubscribe</sharing>
        <attribute>
          <name>Position</name>
          <dataType>HLAunicodeString</dataType>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
          <dimension>HLAdefaultRoutingSpace</dimension>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>TrackReport</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <dimension>HLAdefaultRoutingSpace</dimension>
        <parameter><name>TrackId</name><dataType>HLAunicodeString</dataType></parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation>
  </transportations>
</objectModel>
""",
        encoding="utf-8",
    )

    modules = FOMResolver(require_local_parse=True).resolve_many((str(source), "HLAstandardMIM.xml"))
    assert validate_fom_modules(modules) == []


@pytest.mark.requirements("HLA2025-NEW-006", "HLA2025-OMT-006")
def test_2025_validation_rejects_invalid_value_required_metadata(tmp_path: Path) -> None:
    from hla.fom.validation import validate_fom_module
    from hla.fom import parse_fom_xml

    source = tmp_path / "invalid-value-required.xml"
    source.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Invalid Value Required FOM</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Invalid valueRequired validation fixture.</description>
    <poc><pocName>Test</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Entity</name>
        <attribute><name>EntityId</name><dataType>HLAunicodeString</dataType><valueRequired>maybe</valueRequired></attribute>
      </objectClass>
    </objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )

    issues = validate_fom_module(parse_fom_xml(source))

    assert [issue.requirement for issue in issues] == ["HLA2025-NEW-006"]
    assert issues[0].table == "attributeTable"
    assert issues[0].field == "valueRequired"
    assert issues[0].value == "maybe"


@pytest.mark.requirements(
    "HLA2025-OMT-COMP-004",
    "HLA2025-OMT-COMP-013",
    "HLA2025-OMT-COMP-030",
    "HLA2025-OMT-COMP-140",
    "HLA2025-OMT-COMP-141",
    "HLA2025-OMT-COMP-142",
    "HLA2025-OMT-COMP-143",
    "HLA2025-OMT-COMP-144",
    "HLA2025-OMT-COMP-146",
    "HLA2025-OMT-COMP-150",
    "HLA2025-OMT-COMP-151",
    "HLA2025-OMT-COMP-152",
    "HLA2025-OMT-COMP-215",
)
def test_2025_parser_round_trips_typed_omt_metadata_subset(tmp_path: Path) -> None:
    from hla.fom import parse_fom_xml, serialize_fom_module

    source = tmp_path / "typed-omt-metadata.xml"
    source.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Typed OMT Metadata</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Typed OMT metadata roundtrip fixture.</description>
    <poc><pocName>Test</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Entity</name>
        <attribute>
          <name>EntityId</name>
          <dataType>HLAunicodeString</dataType>
          <valueRequired>true</valueRequired>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <dataTypes>
    <basicDataRepresentations>
      <basicData>
        <name>HLAinteger32BE</name>
        <size>32</size>
        <interpretation>Integer</interpretation>
        <endian>Big</endian>
        <encoding>32-bit signed</encoding>
      </basicData>
      <basicData>
        <name>HLAunicodeString</name>
        <size>0</size>
        <interpretation>String</interpretation>
        <endian>Big</endian>
        <encoding>Unicode</encoding>
      </basicData>
      <basicData>
        <name>HLAoctet</name>
        <size>8</size>
        <interpretation>Octet</interpretation>
        <endian>Big</endian>
        <encoding>8-bit unsigned</encoding>
      </basicData>
    </basicDataRepresentations>
    <simpleDataTypes>
      <simpleData>
        <name>RouteSimple</name>
        <representation>HLAinteger32BE</representation>
        <units>NA</units>
        <resolution>1</resolution>
        <accuracy>Perfect</accuracy>
      </simpleData>
    </simpleDataTypes>
    <referenceDataTypes>
      <referenceDataType>
        <name>EntityIdReference</name>
        <representation>HLAunicodeString</representation>
        <referenceClass>HLAobjectRoot.Entity</referenceClass>
        <referencedAttribute>EntityId</referencedAttribute>
        <semantics>Reference to an Entity object by EntityId.</semantics>
      </referenceDataType>
    </referenceDataTypes>
    <enumeratedDataTypes>
      <enumeratedData>
        <name>ChoiceEnum</name>
        <representation>HLAinteger32BE</representation>
        <enumerator><name>A</name><value>1</value></enumerator>
      </enumeratedData>
    </enumeratedDataTypes>
    <arrayDataTypes>
      <arrayData>
        <name>ByteVector</name>
        <dataType>HLAoctet</dataType>
        <cardinality>Dynamic</cardinality>
        <encoding>HLAvariableArray</encoding>
      </arrayData>
    </arrayDataTypes>
    <variantRecordDataTypes>
      <variantRecordData>
        <name>ChoiceRecord</name>
        <discriminant>choice</discriminant>
        <dataType>ChoiceEnum</dataType>
        <alternative><enumerator>A</enumerator><name>alpha</name><dataType>ByteVector</dataType></alternative>
        <encoding>HLAvariantRecord</encoding>
      </variantRecordData>
    </variantRecordDataTypes>
  </dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )

    module = parse_fom_xml(source)
    entity = next(spec for spec in module.object_classes if spec.full_name == "HLAobjectRoot.Entity")
    assert entity.attribute_value_required == {"EntityId": "true"}
    assert module.reference_datatypes["EntityIdReference"].representation == "HLAunicodeString"
    assert module.reference_datatypes["EntityIdReference"].reference_class == "HLAobjectRoot.Entity"
    assert module.reference_datatypes["EntityIdReference"].referenced_attribute == "EntityId"
    assert module.reference_datatypes["EntityIdReference"].semantics == "Reference to an Entity object by EntityId."
    assert module.simple_datatypes["RouteSimple"].units == "NA"
    assert module.simple_datatypes["RouteSimple"].resolution == "1"
    assert module.simple_datatypes["RouteSimple"].accuracy == "Perfect"
    assert module.array_datatypes["ByteVector"].encoding == "variable-array"
    assert module.array_datatypes["ByteVector"].source_encoding == "HLAvariableArray"
    assert [alt.enumerator for alt in module.variant_record_datatypes["ChoiceRecord"].alternatives] == ["A"]

    xml_text = serialize_fom_module(module, edition="2025")
    roundtrip = tmp_path / "typed-omt-metadata-roundtrip.xml"
    roundtrip.write_text(xml_text, encoding="utf-8")
    reparsed = parse_fom_xml(roundtrip)

    reparsed_entity = next(spec for spec in reparsed.object_classes if spec.full_name == "HLAobjectRoot.Entity")
    assert reparsed_entity.attribute_value_required == {"EntityId": "true"}
    assert reparsed.reference_datatypes["EntityIdReference"].representation == "HLAunicodeString"
    assert reparsed.reference_datatypes["EntityIdReference"].reference_class == "HLAobjectRoot.Entity"
    assert reparsed.reference_datatypes["EntityIdReference"].referenced_attribute == "EntityId"
    assert reparsed.reference_datatypes["EntityIdReference"].semantics == "Reference to an Entity object by EntityId."
    assert reparsed.simple_datatypes["RouteSimple"].units == "NA"
    assert reparsed.simple_datatypes["RouteSimple"].resolution == "1"
    assert reparsed.simple_datatypes["RouteSimple"].accuracy == "Perfect"
    assert reparsed.array_datatypes["ByteVector"].encoding == "variable-array"
    assert reparsed.array_datatypes["ByteVector"].source_encoding == "HLAvariableArray"
    assert [alt.enumerator for alt in reparsed.variant_record_datatypes["ChoiceRecord"].alternatives] == ["A"]


@pytest.mark.requirements(
    "HLA2025-MOD-010",
    "HLA2025-OMT-COMP-078",
    "HLA2025-OMT-COMP-084",
    "HLA2025-OMT-COMP-085",
    "HLA2025-OMT-COMP-087",
    "HLA2025-OMT-COMP-090",
    "HLA2025-OMT-COMP-094",
    "HLA2025-OMT-COMP-125",
    "HLA2025-OMT-COMP-157",
    "HLA2025-OMT-COMP-158",
    "HLA2025-OMT-COMP-159",
    "HLA2025-OMT-COMP-160",
    "HLA2025-OMT-COMP-161",
    "HLA2025-OMT-COMP-162",
    "HLA2025-OMT-COMP-163",
    "HLA2025-OMT-COMP-164",
    "HLA2025-OMT-COMP-165",
    "HLA2025-OMT-COMP-167",
    "HLA2025-OMT-COMP-190",
    "HLA2025-OMT-COMP-191",
    "HLA2025-OMT-COMP-194",
    "HLA2025-OMT-COMP-195",
)
def test_2025_parser_round_trips_metadata_switches_transport_and_time_subset(tmp_path: Path) -> None:
    from hla.fom import parse_fom_xml, serialize_fom_module

    source = tmp_path / "metadata-switches-time.xml"
    source.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Metadata Switches Time</name>
    <type>FOM</type>
    <version>7.5</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <copyright>Example Copyright</copyright>
    <description>Metadata and switch roundtrip fixture.</description>
    <keyword>alpha</keyword>
    <keyword>omega</keyword>
    <poc><pocName>Test</pocName></poc>
    <reference><identification>NA</identification></reference>
  </modelIdentification>
  <objects><objectClass><name>HLAobjectRoot</name><sharing>Neither</sharing></objectClass></objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <sharing>Neither</sharing>
      <transportation>HLAreliable</transportation>
      <order>Receive</order>
    </interactionClass>
  </interactions>
  <time>
    <logicalTime><dataType>HLAinteger64Time</dataType></logicalTime>
    <logicalTimeInterval><dataType>HLAinteger64Time</dataType></logicalTimeInterval>
  </time>
  <switches>
    <autoProvide isEnabled="false"/>
    <conveyRegionDesignatorSets isEnabled="false"/>
    <attributeScopeAdvisory isEnabled="false"/>
    <attributeRelevanceAdvisory isEnabled="false"/>
    <objectClassRelevanceAdvisory isEnabled="false"/>
    <interactionRelevanceAdvisory isEnabled="false"/>
    <serviceReporting isEnabled="false"/>
    <exceptionReporting isEnabled="false"/>
    <delaySubscriptionEvaluation isEnabled="false"/>
    <automaticResignAction resignAction="CancelThenDeleteThenDivest"/>
  </switches>
</objectModel>
""",
        encoding="utf-8",
    )

    module = parse_fom_xml(source)
    assert module.model_identification["name"] == "Metadata Switches Time"
    assert module.model_identification["version"] == "7.5"
    assert module.model_identification["copyright"] == "Example Copyright"
    assert module.model_identification["description"] == "Metadata and switch roundtrip fixture."
    assert module.model_identification["keywords"] == ("alpha", "omega")
    assert module.interaction_classes[0].transportation == "HLAreliable"
    assert module.switch_settings == {
        "autoProvide": "false",
        "conveyRegionDesignatorSets": "false",
        "attributeScopeAdvisory": "false",
        "attributeRelevanceAdvisory": "false",
        "objectClassRelevanceAdvisory": "false",
        "interactionRelevanceAdvisory": "false",
        "serviceReporting": "false",
        "exceptionReporting": "false",
        "delaySubscriptionEvaluation": "false",
        "automaticResignAction": "CancelThenDeleteThenDivest",
    }
    assert module.time_stamp_datatype == "HLAinteger64Time"
    assert module.lookahead_datatype == "HLAinteger64Time"

    xml_text = serialize_fom_module(module, edition="2025")
    roundtrip = tmp_path / "metadata-switches-time-roundtrip.xml"
    roundtrip.write_text(xml_text, encoding="utf-8")
    reparsed = parse_fom_xml(roundtrip)

    assert reparsed.model_identification["name"] == "Metadata Switches Time"
    assert reparsed.model_identification["version"] == "7.5"
    assert reparsed.model_identification["copyright"] == "Example Copyright"
    assert reparsed.model_identification["description"] == "Metadata and switch roundtrip fixture."
    assert reparsed.model_identification["keywords"] == ("alpha", "omega")
    assert reparsed.interaction_classes[0].transportation == "HLAreliable"
    assert reparsed.switch_settings == {
        "autoProvide": "false",
        "conveyRegionDesignatorSets": "false",
        "conveyProducingFederate": "false",
        "attributeScopeAdvisory": "false",
        "attributeRelevanceAdvisory": "false",
        "objectClassRelevanceAdvisory": "false",
        "interactionRelevanceAdvisory": "false",
        "serviceReporting": "false",
        "exceptionReporting": "false",
        "delaySubscriptionEvaluation": "false",
        "nonRegulatedGrant": "false",
        "allowRelaxedDDM": "false",
        "advisoriesUseKnownClass": "false",
        "sendServiceReportsToFile": "false",
        "automaticResignAction": "CancelThenDeleteThenDivest",
    }
    assert reparsed.time_stamp_datatype == "HLAinteger64Time"
    assert reparsed.lookahead_datatype == "HLAinteger64Time"


@pytest.mark.requirements(
    "HLA2025-MOD-010",
    "HLA2025-OMT-COMP-001",
    "HLA2025-OMT-COMP-002",
    "HLA2025-OMT-COMP-003",
    "HLA2025-OMT-COMP-005",
    "HLA2025-OMT-COMP-007",
    "HLA2025-OMT-COMP-009",
    "HLA2025-OMT-COMP-010",
    "HLA2025-OMT-COMP-016",
    "HLA2025-OMT-COMP-020",
    "HLA2025-OMT-COMP-022",
    "HLA2025-OMT-COMP-023",
    "HLA2025-OMT-COMP-024",
    "HLA2025-OMT-COMP-025",
    "HLA2025-OMT-COMP-026",
    "HLA2025-OMT-COMP-028",
    "HLA2025-OMT-COMP-029",
    "HLA2025-OMT-COMP-031",
    "HLA2025-OMT-COMP-032",
    "HLA2025-OMT-COMP-033",
    "HLA2025-OMT-COMP-034",
    "HLA2025-OMT-COMP-036",
    "HLA2025-OMT-COMP-046",
    "HLA2025-OMT-COMP-050",
    "HLA2025-OMT-COMP-051",
    "HLA2025-OMT-COMP-052",
    "HLA2025-OMT-COMP-053",
    "HLA2025-OMT-COMP-054",
    "HLA2025-OMT-COMP-055",
    "HLA2025-OMT-COMP-058",
    "HLA2025-OMT-COMP-060",
    "HLA2025-OMT-COMP-061",
    "HLA2025-OMT-COMP-062",
    "HLA2025-OMT-COMP-063",
    "HLA2025-OMT-COMP-064",
    "HLA2025-OMT-COMP-065",
    "HLA2025-OMT-COMP-066",
    "HLA2025-OMT-COMP-069",
    "HLA2025-OMT-COMP-071",
    "HLA2025-OMT-COMP-072",
    "HLA2025-OMT-COMP-073",
    "HLA2025-OMT-COMP-086",
    "HLA2025-OMT-COMP-088",
    "HLA2025-OMT-COMP-089",
    "HLA2025-OMT-COMP-091",
    "HLA2025-OMT-COMP-092",
    "HLA2025-OMT-COMP-093",
    "HLA2025-OMT-COMP-095",
    "HLA2025-OMT-COMP-096",
    "HLA2025-OMT-COMP-097",
    "HLA2025-OMT-COMP-098",
    "HLA2025-OMT-COMP-099",
    "HLA2025-OMT-COMP-100",
    "HLA2025-OMT-COMP-101",
    "HLA2025-OMT-COMP-103",
    "HLA2025-OMT-COMP-104",
    "HLA2025-OMT-COMP-105",
    "HLA2025-OMT-COMP-108",
    "HLA2025-OMT-COMP-116",
    "HLA2025-OMT-COMP-117",
    "HLA2025-OMT-COMP-118",
    "HLA2025-OMT-COMP-119",
    "HLA2025-OMT-COMP-120",
    "HLA2025-OMT-COMP-121",
    "HLA2025-OMT-COMP-122",
    "HLA2025-OMT-COMP-123",
    "HLA2025-OMT-COMP-124",
    "HLA2025-OMT-COMP-126",
    "HLA2025-OMT-COMP-127",
    "HLA2025-OMT-COMP-128",
    "HLA2025-OMT-COMP-131",
    "HLA2025-OMT-COMP-132",
    "HLA2025-OMT-COMP-135",
    "HLA2025-OMT-COMP-136",
    "HLA2025-OMT-COMP-137",
    "HLA2025-OMT-COMP-138",
    "HLA2025-OMT-COMP-139",
    "HLA2025-OMT-COMP-148",
    "HLA2025-OMT-COMP-149",
    "HLA2025-OMT-COMP-153",
    "HLA2025-OMT-COMP-155",
    "HLA2025-OMT-COMP-172",
    "HLA2025-OMT-COMP-173",
    "HLA2025-OMT-COMP-174",
    "HLA2025-OMT-COMP-175",
    "HLA2025-OMT-COMP-177",
    "HLA2025-OMT-COMP-179",
    "HLA2025-OMT-COMP-180",
    "HLA2025-OMT-COMP-182",
    "HLA2025-OMT-COMP-183",
    "HLA2025-OMT-COMP-184",
    "HLA2025-OMT-COMP-185",
    "HLA2025-OMT-COMP-186",
    "HLA2025-OMT-COMP-187",
    "HLA2025-OMT-COMP-188",
    "HLA2025-OMT-COMP-199",
    "HLA2025-OMT-COMP-203",
    "HLA2025-OMT-COMP-205",
    "HLA2025-OMT-COMP-206",
    "HLA2025-OMT-COMP-209",
    "HLA2025-OMT-COMP-211",
    "HLA2025-OMT-COMP-212",
    "HLA2025-OMT-COMP-213",
    "HLA2025-OMT-COMP-214",
    "HLA2025-OMT-COMP-216",
    "HLA2025-OMT-COMP-217",
    "HLA2025-OMT-COMP-218",
    "HLA2025-OMT-COMP-220",
    "HLA2025-OMT-COMP-221",
    "HLA2025-OMT-COMP-223",
)
def test_2025_parser_round_trips_extended_omt_supported_subset(tmp_path: Path) -> None:
    from hla.fom import parse_fom_xml, serialize_fom_module

    source = tmp_path / "extended-omt-supported-subset.xml"
    source.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Extended Supported Subset</name>
    <type>FOM</type>
    <version>2.5</version>
    <modificationDate>2026-06-19</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <releaseRestriction>Internal</releaseRestriction>
    <purpose>Roundtrip coverage.</purpose>
    <applicationDomain>Training</applicationDomain>
    <description>Extended OMT supported-subset fixture.</description>
    <useLimitation>Lab use only.</useLimitation>
    <useHistory>Derived from regression corpus.</useHistory>
    <other>Other metadata.</other>
    <glyph>glyph-01</glyph>
    <keyword>alpha</keyword>
    <keyword>omega</keyword>
    <poc>
      <pocType>Sponsor</pocType>
      <pocName>Test User</pocName>
      <pocOrg>Example Org</pocOrg>
      <pocTelephone>555-0100</pocTelephone>
      <pocEmail>test@example.invalid</pocEmail>
    </poc>
    <reference>
      <type>URL</type>
      <identification>https://example.invalid/spec</identification>
    </reference>
  </modelIdentification>
  <serviceUtilization>
    <connect advisor="true" mode="strict" />
    <registerObjectInstance optional="false" />
  </serviceUtilization>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Entity</name>
        <attribute>
          <name>EntityId</name>
          <dataType>HLAunicodeString</dataType>
          <transportation>HLAreliable</transportation>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>Report</name>
        <parameter>
          <name>Payload</name>
          <dataType>HLAunicodeString</dataType>
        </parameter>
      </interactionClass>
    </interactionClass>
  </interactions>
  <dimensions>
    <dimension><name>RouteDim</name></dimension>
  </dimensions>
  <time>
    <logicalTime><dataType>HLAinteger64Time</dataType></logicalTime>
    <logicalTimeInterval><dataType>HLAinteger64Time</dataType></logicalTimeInterval>
  </time>
  <tags>
    <updateReflectTag><dataType>HLAunicodeString</dataType><semantics>Update tag.</semantics></updateReflectTag>
    <sendReceiveTag><dataType>HLAunicodeString</dataType><semantics>Interaction tag.</semantics></sendReceiveTag>
    <deleteRemoveTag><dataType>NA</dataType><semantics>Delete tag.</semantics></deleteRemoveTag>
    <divestitureRequestTag><dataType>NA</dataType><semantics>Divest request.</semantics></divestitureRequestTag>
    <divestitureCompletionTag><dataType>NA</dataType><semantics>Divest completion.</semantics></divestitureCompletionTag>
    <acquisitionRequestTag><dataType>NA</dataType><semantics>Acquire request.</semantics></acquisitionRequestTag>
    <requestUpdateTag><dataType>NA</dataType><semantics>Request update.</semantics></requestUpdateTag>
  </tags>
  <synchronizations>
    <synchronizationPoint>
      <label>ReadyToRun</label>
      <dataType>HLAunicodeString</dataType>
      <capability>RegisterAchieve</capability>
      <semantics>Startup barrier.</semantics>
    </synchronizationPoint>
  </synchronizations>
  <transportations>
    <transportation><name>HLAreliable</name></transportation>
    <transportation><name>HLAbestEffort</name></transportation>
  </transportations>
  <updateRates>
    <updateRate><name>Fast</name><rate>10.0</rate></updateRate>
  </updateRates>
  <dataTypes>
    <basicDataRepresentations>
      <basicData>
        <name>HLAinteger32BE</name>
        <size>32</size>
        <interpretation>Integer</interpretation>
        <endian>Big</endian>
        <encoding>32-bit signed</encoding>
      </basicData>
      <basicData>
        <name>HLAunicodeString</name>
        <size>0</size>
        <interpretation>String</interpretation>
        <endian>Big</endian>
        <encoding>Unicode</encoding>
      </basicData>
      <basicData>
        <name>HLAoctet</name>
        <size>8</size>
        <interpretation>Octet</interpretation>
        <endian>Big</endian>
        <encoding>8-bit unsigned</encoding>
      </basicData>
    </basicDataRepresentations>
    <simpleDataTypes>
      <simpleData>
        <name>RouteSimple</name>
        <representation>HLAinteger32BE</representation>
        <semantics>Route type.</semantics>
      </simpleData>
    </simpleDataTypes>
    <enumeratedDataTypes>
      <enumeratedData>
        <name>ChoiceEnum</name>
        <representation>HLAinteger32BE</representation>
        <semantics>Choice enum.</semantics>
        <enumerator><name>A</name><value>1</value></enumerator>
      </enumeratedData>
    </enumeratedDataTypes>
    <arrayDataTypes>
      <arrayData>
        <name>ByteVector</name>
        <dataType>HLAoctet</dataType>
        <cardinality>Dynamic</cardinality>
        <encoding>HLAvariableArray</encoding>
        <semantics>Opaque bytes.</semantics>
      </arrayData>
    </arrayDataTypes>
    <fixedRecordDataTypes>
      <fixedRecordData>
        <name>Vector3</name>
        <encoding>HLAfixedRecord</encoding>
        <semantics>Cartesian vector.</semantics>
        <field><name>X</name><dataType>HLAinteger32BE</dataType><semantics>x</semantics></field>
      </fixedRecordData>
    </fixedRecordDataTypes>
    <variantRecordDataTypes>
      <variantRecordData>
        <name>MeasurementValue</name>
        <discriminant>ChoiceEnum</discriminant>
        <dataType>ChoiceEnum</dataType>
        <alternative><enumerator>A</enumerator><name>Text</name><dataType>HLAunicodeString</dataType><semantics>text</semantics></alternative>
        <encoding>HLAvariantRecord</encoding>
        <semantics>Tagged payload.</semantics>
      </variantRecordData>
    </variantRecordDataTypes>
  </dataTypes>
  <notes>
    <note><label>N1</label><semantics>alpha</semantics></note>
  </notes>
</objectModel>
""",
        encoding="utf-8",
    )

    module = parse_fom_xml(source)
    entity = next(spec for spec in module.object_classes if spec.full_name == "HLAobjectRoot.Entity")
    report = next(spec for spec in module.interaction_classes if spec.full_name == "HLAinteractionRoot.Report")

    assert module.model_identification["type"] == "FOM"
    assert module.model_identification["modificationDate"] == "2026-06-19"
    assert module.model_identification["securityClassification"] == "Unclassified"
    assert module.model_identification["releaseRestriction"] == "Internal"
    assert module.model_identification["purpose"] == "Roundtrip coverage."
    assert module.model_identification["applicationDomain"] == "Training"
    assert module.model_identification["useLimitation"] == "Lab use only."
    assert module.model_identification["useHistory"] == "Derived from regression corpus."
    assert module.model_identification["other"] == "Other metadata."
    assert module.model_identification["glyph"] == "glyph-01"
    assert module.model_identification["keywords"] == ("alpha", "omega")
    assert module.model_identification["pocs"] == (
        {
            "pocType": "Sponsor",
            "pocName": "Test User",
            "pocOrg": "Example Org",
            "pocTelephone": "555-0100",
            "pocEmail": "test@example.invalid",
        },
    )
    assert module.model_identification["references"] == (
        {"type": "URL", "identification": "https://example.invalid/spec"},
    )
    assert module.service_utilization == {
        "connect": {"advisor": "true", "mode": "strict"},
        "registerObjectInstance": {"optional": "false"},
    }
    assert entity.declared_attributes == ("EntityId",)
    assert entity.attribute_datatypes["EntityId"] == "HLAunicodeString"
    assert entity.attribute_transportations["EntityId"] == "HLAreliable"
    assert report.declared_parameters == ("Payload",)
    assert report.parameter_datatypes["Payload"] == "HLAunicodeString"
    assert module.dimensions == ("RouteDim",)
    assert module.time_stamp_datatype == "HLAinteger64Time"
    assert module.lookahead_datatype == "HLAinteger64Time"
    assert module.tag_representations["updateReflectTag"] == {
        "datatype": "HLAunicodeString",
        "semantics": "Update tag.",
    }
    assert module.tag_representations["sendReceiveTag"]["datatype"] == "HLAunicodeString"
    assert module.synchronization_points["ReadyToRun"] == {
        "tag_datatype": "HLAunicodeString",
        "capability": "RegisterAchieve",
        "semantics": "Startup barrier.",
    }
    assert module.transportation_names == ("HLAreliable", "HLAbestEffort")
    assert module.update_rates == {"Fast": "10.0"}
    assert module.basic_datatypes["HLAinteger32BE"].encoding == "32-bit signed"
    assert module.simple_datatypes["RouteSimple"].representation == "HLAinteger32BE"
    assert module.simple_datatypes["RouteSimple"].semantics == "Route type."
    assert module.enumerated_datatypes["ChoiceEnum"].representation == "HLAinteger32BE"
    assert [item.name for item in module.enumerated_datatypes["ChoiceEnum"].enumerators] == ["A"]
    assert module.array_datatypes["ByteVector"].data_type == "HLAoctet"
    assert module.array_datatypes["ByteVector"].cardinality == "Dynamic"
    assert module.array_datatypes["ByteVector"].semantics == "Opaque bytes."
    assert module.fixed_record_datatypes["Vector3"].encoding == "HLAfixedRecord"
    assert [(field.name, field.data_type, field.semantics) for field in module.fixed_record_datatypes["Vector3"].fields] == [
        ("X", "HLAinteger32BE", "x"),
    ]
    assert module.variant_record_datatypes["MeasurementValue"].discriminant == "ChoiceEnum"
    assert module.variant_record_datatypes["MeasurementValue"].encoding == "variant-record"
    assert module.variant_record_datatypes["MeasurementValue"].source_encoding == "HLAvariantRecord"
    assert [
        (alt.enumerator, alt.name, alt.data_type, alt.semantics)
        for alt in module.variant_record_datatypes["MeasurementValue"].alternatives
    ] == [("A", "Text", "HLAunicodeString", "text")]
    assert module.notes == ("N1: alpha",)

    roundtrip = tmp_path / "extended-omt-supported-subset-roundtrip.xml"
    roundtrip.write_text(serialize_fom_module(module, edition="2025"), encoding="utf-8")
    reparsed = parse_fom_xml(roundtrip)

    assert reparsed.model_identification == module.model_identification
    assert reparsed.service_utilization == module.service_utilization
    assert reparsed.dimensions == module.dimensions
    assert reparsed.time_stamp_datatype == module.time_stamp_datatype
    assert reparsed.lookahead_datatype == module.lookahead_datatype
    assert reparsed.tag_representations == module.tag_representations
    assert reparsed.synchronization_points == module.synchronization_points
    assert reparsed.transportation_names == module.transportation_names
    assert reparsed.update_rates == module.update_rates
    for key, value in module.basic_datatypes.items():
        assert reparsed.basic_datatypes[key] == value
    for key, value in module.simple_datatypes.items():
        assert reparsed.simple_datatypes[key] == value
    for key, value in module.enumerated_datatypes.items():
        assert reparsed.enumerated_datatypes[key] == value
    for key, value in module.array_datatypes.items():
        assert reparsed.array_datatypes[key] == value
    for key, value in module.fixed_record_datatypes.items():
        assert reparsed.fixed_record_datatypes[key] == value
    for key, value in module.variant_record_datatypes.items():
        assert reparsed.variant_record_datatypes[key] == value
    assert reparsed.notes == module.notes

    reparsed_entity = next(spec for spec in reparsed.object_classes if spec.full_name == "HLAobjectRoot.Entity")
    reparsed_report = next(spec for spec in reparsed.interaction_classes if spec.full_name == "HLAinteractionRoot.Report")
    assert reparsed_entity.declared_attributes == ("EntityId",)
    assert reparsed_entity.attribute_datatypes["EntityId"] == "HLAunicodeString"
    assert reparsed_entity.attribute_transportations["EntityId"] == "HLAreliable"
    assert reparsed_report.declared_parameters == ("Payload",)
    assert reparsed_report.parameter_datatypes["Payload"] == "HLAunicodeString"


@pytest.mark.requirements(
    "HLA2025-OMT-COMP-083",
    "HLA2025-OMT-COMP-200",
    "HLA2025-OMT-COMP-201",
)
def test_2025_parser_intentionally_narrows_unmodeled_omt_fields(tmp_path: Path) -> None:
    from hla.fom import parse_fom_xml, serialize_fom_module

    source = tmp_path / "narrow-omt-fields.xml"
    source.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Narrow OMT Fields</name>
    <type>FOM</type>
    <keyword taxonomy="domain">alpha</keyword>
    <poc><pocName>Test</pocName></poc>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <sharing>PublishSubscribe</sharing>
      <semantics>Root semantics</semantics>
      <objectClass>
        <name>Entity</name>
        <attribute>
          <name>Status</name>
          <dataType>HLAunicodeString</dataType>
          <updateType>Static</updateType>
          <updateCondition>Conditional</updateCondition>
          <ownership>NoTransfer</ownership>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Timestamp</order>
          <semantics>Status semantics</semantics>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <sharing>PublishSubscribe</sharing>
      <transportation>HLAreliable</transportation>
      <order>Timestamp</order>
      <semantics>Interaction semantics</semantics>
      <parameter>
        <name>Payload</name>
        <dataType>HLAunicodeString</dataType>
        <semantics>Payload semantics</semantics>
      </parameter>
    </interactionClass>
  </interactions>
  <dimensions>
    <dimension>
      <name>RouteDim</name>
      <upperBound>100</upperBound>
      <value>[0..1)</value>
    </dimension>
  </dimensions>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable><semantics>Reliable semantics</semantics></transportation>
  </transportations>
  <updateRates>
    <updateRate><name>Fast</name><rate>10.0</rate><semantics>Fast semantics</semantics></updateRate>
  </updateRates>
</objectModel>
""",
        encoding="utf-8",
    )

    module = parse_fom_xml(source)
    entity = next(spec for spec in module.object_classes if spec.full_name == "HLAobjectRoot.Entity")
    assert entity.attribute_datatypes["Status"] == "HLAunicodeString"
    assert entity.attribute_transportations["Status"] == "HLAreliable"
    assert entity.attribute_update_types["Status"] == "Static"
    assert entity.attribute_update_conditions["Status"] == "Conditional"
    assert entity.attribute_ownership["Status"] == "NoTransfer"
    assert entity.attribute_sharing["Status"] == "PublishSubscribe"
    assert entity.attribute_order["Status"] == "Timestamp"
    assert entity.attribute_semantics["Status"] == "Status semantics"
    root_object = next(spec for spec in module.object_classes if spec.full_name == "HLAobjectRoot")
    root_interaction = next(spec for spec in module.interaction_classes if spec.full_name == "HLAinteractionRoot")
    assert root_object.sharing == "PublishSubscribe"
    assert root_object.semantics == "Root semantics"
    assert root_interaction.sharing == "PublishSubscribe"
    assert root_interaction.order == "Timestamp"
    assert root_interaction.semantics == "Interaction semantics"
    assert root_interaction.parameter_semantics["Payload"] == "Payload semantics"
    assert module.dimension_specs["RouteDim"].upper_bound == "100"
    assert module.dimension_specs["RouteDim"].value == "[0..1)"
    assert module.model_identification["keywords"] == ("alpha",)
    assert module.model_identification["keyword_taxonomies"] == ("domain",)
    assert module.transportation_specs["HLAreliable"].reliable == "Yes"
    assert module.transportation_specs["HLAreliable"].semantics == "Reliable semantics"

    xml_text = serialize_fom_module(module, edition="2025")
    assert 'taxonomy="domain"' in xml_text
    assert "<updateType>Static</updateType>" in xml_text
    assert "<updateCondition>Conditional</updateCondition>" in xml_text
    assert "<ownership>NoTransfer</ownership>" in xml_text
    assert "<sharing>PublishSubscribe</sharing>" in xml_text
    assert "<order>Timestamp</order>" in xml_text
    assert "Status semantics" in xml_text
    assert "Interaction semantics" in xml_text
    assert "Payload semantics" in xml_text
    assert "<upperBound>100</upperBound>" in xml_text
    assert "<value>[0..1)</value>" in xml_text
    assert "Reliable semantics" in xml_text
    assert "Fast semantics" in xml_text


@pytest.mark.requirements(
    "HLA2025-OMT-COMP-074",
    "HLA2025-OMT-COMP-079",
    "HLA2025-OMT-COMP-080",
    "HLA2025-OMT-COMP-109",
    "HLA2025-OMT-COMP-114",
    "HLA2025-OMT-COMP-133",
)
def test_2025_class_and_parameter_metadata_round_trips(tmp_path: Path) -> None:
    from hla.fom import parse_fom_xml, serialize_fom_module

    source = tmp_path / "class-parameter-metadata.xml"
    source.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification><name>Class Metadata</name><type>FOM</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <sharing>PublishSubscribe</sharing>
      <semantics>Root semantics</semantics>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <sharing>PublishSubscribe</sharing>
      <transportation>HLAreliable</transportation>
      <order>Timestamp</order>
      <semantics>Interaction semantics</semantics>
      <parameter><name>Payload</name><dataType>HLAunicodeString</dataType><semantics>Payload semantics</semantics></parameter>
    </interactionClass>
  </interactions>
  <transportations><transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation></transportations>
  <dataTypes><simpleDataTypes><simpleData><name>HLAunicodeString</name></simpleData></simpleDataTypes></dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )

    module = parse_fom_xml(source)
    root_object = next(spec for spec in module.object_classes if spec.full_name == "HLAobjectRoot")
    root_interaction = next(spec for spec in module.interaction_classes if spec.full_name == "HLAinteractionRoot")

    assert root_object.sharing == "PublishSubscribe"
    assert root_object.semantics == "Root semantics"
    assert root_interaction.sharing == "PublishSubscribe"
    assert root_interaction.order == "Timestamp"
    assert root_interaction.semantics == "Interaction semantics"
    assert root_interaction.parameter_semantics["Payload"] == "Payload semantics"

    reparsed_path = tmp_path / "reparsed.xml"
    reparsed_path.write_text(serialize_fom_module(module, edition="2025"), encoding="utf-8")
    reparsed = parse_fom_xml(reparsed_path)
    reparsed_object = next(spec for spec in reparsed.object_classes if spec.full_name == "HLAobjectRoot")
    reparsed_interaction = next(spec for spec in reparsed.interaction_classes if spec.full_name == "HLAinteractionRoot")

    assert reparsed_object.sharing == root_object.sharing
    assert reparsed_object.semantics == root_object.semantics
    assert reparsed_interaction.sharing == root_interaction.sharing
    assert reparsed_interaction.order == root_interaction.order
    assert reparsed_interaction.semantics == root_interaction.semantics
    assert reparsed_interaction.parameter_semantics == root_interaction.parameter_semantics


@pytest.mark.requirements(
    "HLA2025-OMT-COMP-011",
    "HLA2025-OMT-COMP-012",
    "HLA2025-OMT-COMP-014",
    "HLA2025-OMT-COMP-015",
    "HLA2025-OMT-COMP-017",
    "HLA2025-OMT-COMP-018",
)
def test_2025_attribute_metadata_round_trips(tmp_path: Path) -> None:
    from hla.fom import parse_fom_xml, serialize_fom_module

    source = tmp_path / "attribute-metadata.xml"
    source.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification><name>Attribute Metadata</name><type>FOM</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>Entity</name>
        <attribute>
          <name>Status</name>
          <dataType>HLAunicodeString</dataType>
          <updateType>Static</updateType>
          <updateCondition>On change</updateCondition>
          <ownership>NoTransfer</ownership>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Timestamp</order>
          <valueRequired>true</valueRequired>
          <semantics>Status semantics</semantics>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
  <transportations><transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation></transportations>
  <dataTypes><simpleDataTypes><simpleData><name>HLAunicodeString</name></simpleData></simpleDataTypes></dataTypes>
</objectModel>
""",
        encoding="utf-8",
    )

    module = parse_fom_xml(source)
    entity = next(spec for spec in module.object_classes if spec.full_name == "HLAobjectRoot.Entity")
    assert entity.attribute_update_types["Status"] == "Static"
    assert entity.attribute_update_conditions["Status"] == "On change"
    assert entity.attribute_ownership["Status"] == "NoTransfer"
    assert entity.attribute_sharing["Status"] == "PublishSubscribe"
    assert entity.attribute_order["Status"] == "Timestamp"
    assert entity.attribute_semantics["Status"] == "Status semantics"

    reparsed_path = tmp_path / "reparsed.xml"
    reparsed_path.write_text(serialize_fom_module(module, edition="2025"), encoding="utf-8")
    reparsed = parse_fom_xml(reparsed_path)
    reparsed_entity = next(spec for spec in reparsed.object_classes if spec.full_name == "HLAobjectRoot.Entity")

    assert reparsed_entity.attribute_update_types == entity.attribute_update_types
    assert reparsed_entity.attribute_update_conditions == entity.attribute_update_conditions
    assert reparsed_entity.attribute_ownership == entity.attribute_ownership
    assert reparsed_entity.attribute_sharing == entity.attribute_sharing
    assert reparsed_entity.attribute_order == entity.attribute_order
    assert reparsed_entity.attribute_semantics == entity.attribute_semantics


@pytest.mark.requirements(
    "HLA2025-OMT-COMP-200",
    "HLA2025-OMT-COMP-201",
    "HLA2025-OMT-COMP-207",
)
def test_2025_transportation_and_update_rate_metadata_round_trips(tmp_path: Path) -> None:
    from hla.fom import parse_fom_xml, serialize_fom_module

    source = tmp_path / "transport-update-rate-metadata.xml"
    source.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification><name>Metadata</name><type>FOM</type></modelIdentification>
  <transportations>
    <transportation><name>HLAreliable</name><reliable>Yes</reliable><semantics>Reliable semantics</semantics></transportation>
    <transportation><name>HLAbestEffort</name><reliable>No</reliable><semantics>Best effort semantics</semantics></transportation>
  </transportations>
  <updateRates>
    <updateRate><name>Fast</name><rate>10.0</rate><semantics>Fast semantics</semantics></updateRate>
  </updateRates>
</objectModel>
""",
        encoding="utf-8",
    )

    module = parse_fom_xml(source)
    assert module.transportation_specs["HLAreliable"].reliable == "Yes"
    assert module.transportation_specs["HLAreliable"].semantics == "Reliable semantics"
    assert module.transportation_specs["HLAbestEffort"].reliable == "No"
    assert module.transportation_specs["HLAbestEffort"].semantics == "Best effort semantics"
    assert module.update_rate_specs["Fast"].rate == "10.0"
    assert module.update_rate_specs["Fast"].semantics == "Fast semantics"

    reparsed_path = tmp_path / "reparsed.xml"
    reparsed_path.write_text(serialize_fom_module(module, edition="2025"), encoding="utf-8")
    reparsed = parse_fom_xml(reparsed_path)

    assert reparsed.transportation_specs == module.transportation_specs
    assert reparsed.update_rate_specs == module.update_rate_specs


@pytest.mark.requirements(
    "HLA2025-OMT-COMP-006",
    "HLA2025-OMT-COMP-008",
    "HLA2025-OMT-COMP-019",
    "HLA2025-OMT-COMP-021",
    "HLA2025-OMT-COMP-027",
    "HLA2025-OMT-COMP-035",
    "HLA2025-OMT-COMP-039",
    "HLA2025-OMT-COMP-045",
    "HLA2025-OMT-COMP-047",
    "HLA2025-OMT-COMP-056",
    "HLA2025-OMT-COMP-057",
    "HLA2025-OMT-COMP-059",
    "HLA2025-OMT-COMP-067",
    "HLA2025-OMT-COMP-068",
    "HLA2025-OMT-COMP-070",
    "HLA2025-OMT-COMP-077",
    "HLA2025-OMT-COMP-081",
    "HLA2025-OMT-COMP-082",
    "HLA2025-OMT-COMP-102",
    "HLA2025-OMT-COMP-106",
    "HLA2025-OMT-COMP-107",
    "HLA2025-OMT-COMP-113",
    "HLA2025-OMT-COMP-115",
    "HLA2025-OMT-COMP-129",
    "HLA2025-OMT-COMP-130",
    "HLA2025-OMT-COMP-134",
    "HLA2025-OMT-COMP-145",
    "HLA2025-OMT-COMP-147",
    "HLA2025-OMT-COMP-154",
    "HLA2025-OMT-COMP-156",
    "HLA2025-OMT-COMP-171",
    "HLA2025-OMT-COMP-176",
    "HLA2025-OMT-COMP-178",
    "HLA2025-OMT-COMP-181",
    "HLA2025-OMT-COMP-189",
    "HLA2025-OMT-COMP-193",
    "HLA2025-OMT-COMP-197",
    "HLA2025-OMT-COMP-198",
    "HLA2025-OMT-COMP-202",
    "HLA2025-OMT-COMP-204",
    "HLA2025-OMT-COMP-208",
    "HLA2025-OMT-COMP-210",
    "HLA2025-OMT-COMP-219",
    "HLA2025-OMT-COMP-222",
    "HLA2025-OMT-COMP-224",
)
@pytest.mark.parametrize(
    ("case_name", "body"),
    [
        (
            "array-data-xs-any",
            """
  <modelIdentification><name>Ext</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <basicDataRepresentations>
      <basicData><name>HLAinteger32BE</name><size>32</size><interpretation>Integer</interpretation><endian>Big</endian><encoding>32-bit</encoding></basicData>
    </basicDataRepresentations>
    <arrayDataTypes>
      <arrayData><name>ArrayValue</name><dataType>HLAinteger32BE</dataType><cardinality>1</cardinality><ext:item /></arrayData>
      <ext:arrayDataTypes />
    </arrayDataTypes>
  </dataTypes>
""",
        ),
        (
            "attribute-xs-any",
            """
  <modelIdentification><name>Ext</name><type>FOM</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <attribute><name>Status</name><dataType>HLAunicodeString</dataType><ext:attribute /></attribute>
    </objectClass>
  </objects>
""",
        ),
        (
            "basic-data-xs-any",
            """
  <modelIdentification><name>Ext</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <basicDataRepresentations>
      <basicData><name>HLAinteger32BE</name><size>32</size><interpretation>Integer</interpretation><endian>Big</endian><encoding>32-bit</encoding><ext:basic /></basicData>
      <ext:basicDataRepresentations />
    </basicDataRepresentations>
    <ext:dataTypes />
  </dataTypes>
""",
        ),
        (
            "dimension-xs-any",
            """
  <modelIdentification><name>Ext</name><type>FOM</type></modelIdentification>
  <dimensions>
    <dimension>
      <name>RouteDim</name>
      <inputDataTypes><dataType>HLAinteger32BE</dataType><ext:inputDataTypes /></inputDataTypes>
      <upperBound>1</upperBound>
      <ext:dimension />
    </dimension>
    <ext:dimensions />
  </dimensions>
""",
        ),
        (
            "enumerated-xs-any",
            """
  <modelIdentification><name>Ext</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <basicDataRepresentations>
      <basicData><name>HLAinteger32BE</name><size>32</size><interpretation>Integer</interpretation><endian>Big</endian><encoding>32-bit</encoding></basicData>
    </basicDataRepresentations>
    <enumeratedDataTypes>
      <enumeratedData><name>Choice</name><representation>HLAinteger32BE</representation><enumerator><name>A</name><value>1</value><ext:enumerator /></enumerator><ext:enumeratedData /></enumeratedData>
      <ext:enumeratedDataTypes />
    </enumeratedDataTypes>
  </dataTypes>
""",
        ),
        (
            "fixed-record-xs-any",
            """
  <modelIdentification><name>Ext</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <basicDataRepresentations>
      <basicData><name>HLAinteger32BE</name><size>32</size><interpretation>Integer</interpretation><endian>Big</endian><encoding>32-bit</encoding></basicData>
    </basicDataRepresentations>
    <fixedRecordDataTypes>
      <fixedRecordData><name>Vector</name><field><name>X</name><dataType>HLAinteger32BE</dataType><ext:field /></field><ext:fixedRecordData /></fixedRecordData>
      <ext:fixedRecordDataTypes />
    </fixedRecordDataTypes>
  </dataTypes>
""",
        ),
        (
            "interaction-and-parameter-xs-any",
            """
  <modelIdentification><name>Ext</name><type>FOM</type></modelIdentification>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <dimensions><dimension>RouteDim</dimension><ext:dimensions /></dimensions>
      <parameter><name>Payload</name><dataType>HLAunicodeString</dataType><ext:parameter /></parameter>
      <ext:interactionClass />
    </interactionClass>
    <ext:interactions />
  </interactions>
""",
        ),
        (
            "model-identification-and-notes-xs-any",
            """
  <modelIdentification><name>Ext</name><type>FOM</type><ext:modelIdentification /></modelIdentification>
  <notes><note><label>N1</label><semantics>alpha</semantics><ext:note /></note><ext:notes /></notes>
""",
        ),
        (
            "object-model-and-objects-xs-any",
            """
  <modelIdentification><name>Ext</name><type>FOM</type></modelIdentification>
  <objects>
    <objectClass><name>HLAobjectRoot</name><dimensions><dimension>ObjDim</dimension><ext:dimensions /></dimensions><ext:objectClass /></objectClass>
    <ext:objects />
  </objects>
  <ext:objectModel />
""",
        ),
        (
            "reference-and-simple-data-xs-any",
            """
  <modelIdentification><name>Ext</name><type>FOM</type></modelIdentification>
  <objects><objectClass><name>HLAobjectRoot</name></objectClass></objects>
  <dataTypes>
    <basicDataRepresentations>
      <basicData><name>HLAunicodeString</name><size>0</size><interpretation>String</interpretation><endian>Big</endian><encoding>Unicode</encoding></basicData>
    </basicDataRepresentations>
    <simpleDataTypes><simpleData><name>RouteSimple</name><representation>HLAunicodeString</representation><ext:simpleData /></simpleData><ext:simpleDataTypes /></simpleDataTypes>
    <referenceDataTypes><referenceDataType><name>StatusRef</name><representation>HLAunicodeString</representation><referenceClass>HLAobjectRoot</referenceClass><referencedAttribute>Status</referencedAttribute><ext:referenceDataType /></referenceDataType><ext:referenceDataTypes /></referenceDataTypes>
  </dataTypes>
""",
        ),
        (
            "switch-sync-tag-xs-any",
            """
  <modelIdentification><name>Ext</name><type>FOM</type></modelIdentification>
  <switches><ext:switches /></switches>
  <synchronizations><synchronizationPoint><label>Ready</label><dataType>NA</dataType><capability>RegisterAchieve</capability><ext:synchronizationPoint /></synchronizationPoint><ext:synchronizations /></synchronizations>
  <tags><updateReflectTag><dataType>NA</dataType><semantics>tag</semantics><ext:tag /></updateReflectTag><ext:tags /></tags>
""",
        ),
        (
            "time-transport-update-xs-any",
            """
  <modelIdentification><name>Ext</name><type>FOM</type></modelIdentification>
  <time>
    <logicalTime><dataType>HLAinteger64Time</dataType><ext:logicalTime /></logicalTime>
    <logicalTimeInterval><dataType>HLAinteger64Time</dataType><ext:logicalTimeInterval /></logicalTimeInterval>
    <ext:time />
  </time>
  <transportations><transportation><name>HLAreliable</name><reliable>Yes</reliable><ext:transportation /></transportation><ext:transportations /></transportations>
  <updateRates><updateRate><name>Fast</name><rate>1</rate><ext:updateRate /></updateRate><ext:updateRates /></updateRates>
""",
        ),
        (
            "nested-extension-payload-xs-any",
            """
  <modelIdentification><name>Ext</name><type>FOM</type><ext:vendorProfile ext:version="2">payload-text<ext:nested flag="yes">nested-text</ext:nested></ext:vendorProfile></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <attribute>
        <name>Status</name>
        <dataType>HLAunicodeString</dataType>
        <ext:attributeExtension ext:kind="diagnostic">attribute-payload<ext:child>attribute-child</ext:child></ext:attributeExtension>
      </attribute>
    </objectClass>
  </objects>
  <dataTypes>
    <basicDataRepresentations>
      <basicData><name>HLAunicodeString</name><size>0</size><interpretation>String</interpretation><endian>Big</endian><encoding>Unicode</encoding><ext:basicDataExtension ext:kind="text">basic-payload</ext:basicDataExtension></basicData>
    </basicDataRepresentations>
  </dataTypes>
""",
        ),
        (
            "variant-record-xs-any",
            """
  <modelIdentification><name>Ext</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <basicDataRepresentations>
      <basicData><name>HLAinteger32BE</name><size>32</size><interpretation>Integer</interpretation><endian>Big</endian><encoding>32-bit</encoding></basicData>
      <basicData><name>HLAunicodeString</name><size>0</size><interpretation>String</interpretation><endian>Big</endian><encoding>Unicode</encoding></basicData>
    </basicDataRepresentations>
    <enumeratedDataTypes><enumeratedData><name>Choice</name><representation>HLAinteger32BE</representation><enumerator><name>A</name><value>1</value></enumerator></enumeratedData></enumeratedDataTypes>
    <simpleDataTypes><simpleData><name>Payload</name><representation>HLAunicodeString</representation></simpleData></simpleDataTypes>
    <variantRecordDataTypes><variantRecordData><name>ChoiceRecord</name><discriminant>Choice</discriminant><dataType>Choice</dataType><alternative><enumerator>A</enumerator><name>Alpha</name><dataType>Payload</dataType><ext:alternative /></alternative><ext:variantRecordData /></variantRecordData><ext:variantRecordDataTypes /></variantRecordDataTypes>
  </dataTypes>
""",
        ),
    ],
)
def test_2025_parser_accepts_isolates_and_preserves_foreign_namespace_extension_points(
    tmp_path: Path,
    case_name: str,
    body: str,
) -> None:
    from hla.fom import parse_fom_xml, serialize_fom_module

    source = tmp_path / f"{case_name}.xml"
    source.write_text(_wrap_omt_2025_fragment(body, extra_root_attrs=' xmlns:ext="urn:ext"'), encoding="utf-8")

    module = parse_fom_xml(source)
    xml_text = serialize_fom_module(module, edition="2025")

    assert module.name == "Ext"
    assert module.foreign_extensions
    assert all("urn:ext" in extension.xml for extension in module.foreign_extensions)
    if case_name == "nested-extension-payload-xs-any":
        extension_xml = "\n".join(extension.xml for extension in module.foreign_extensions)
        assert "payload-text" in extension_xml
        assert "nested-text" in extension_xml
        assert "attribute-child" in extension_xml
        assert "basic-payload" in extension_xml
    assert "urn:ext" in xml_text
    assert any(local_name in xml_text for local_name in ("modelIdentification", "objects", "interactionClass", "variantRecordData"))
    if case_name == "nested-extension-payload-xs-any":
        assert "payload-text" in xml_text
        assert "nested-text" in xml_text
        assert "attribute-child" in xml_text
        assert "basic-payload" in xml_text
    reparsed_source = tmp_path / f"{case_name}-roundtrip.xml"
    reparsed_source.write_text(xml_text, encoding="utf-8")
    reparsed = parse_fom_xml(reparsed_source)
    assert len(reparsed.foreign_extensions) == len(module.foreign_extensions)


@pytest.mark.requirements(
    "HLA2025-OMT-COMP-048",
    "HLA2025-OMT-COMP-049",
    "HLA2025-OMT-COMP-075",
    "HLA2025-OMT-COMP-076",
    "HLA2025-OMT-COMP-110",
    "HLA2025-OMT-COMP-111",
    "HLA2025-OMT-COMP-112",
)
def test_2025_parser_round_trips_structural_association_omt_fields(tmp_path: Path) -> None:
    from hla.fom import parse_fom_xml, serialize_fom_module

    source = tmp_path / "structural-association-omt.xml"
    source.write_text(
        _wrap_omt_2025_fragment(
            """
  <modelIdentification><name>Probe</name><type>FOM</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <sharing>PublishSubscribe</sharing>
      <objectClass>
        <name>Entity</name>
        <attribute><name>Status</name><dataType>HLAunicodeString</dataType><sharing>Subscribe</sharing></attribute>
      </objectClass>
      <directedInteraction><name>Ping</name><sharing>Subscribe</sharing></directedInteraction>
      <dimensions><dimension>ObjDim</dimension></dimensions>
    </objectClass>
  </objects>
  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <sharing>PublishSubscribe</sharing>
      <dimensions><dimension>IntDim</dimension></dimensions>
      <order>Timestamp</order>
      <transportation>HLAreliable</transportation>
    </interactionClass>
  </interactions>
  <time>
    <logicalTime><dataType>HLAinteger64Time</dataType><semantics>LT sem</semantics></logicalTime>
    <logicalTimeInterval><dataType>HLAinteger64Time</dataType><semantics>LTI sem</semantics></logicalTimeInterval>
  </time>
  <transportations><transportation><name>HLAreliable</name><reliable>Yes</reliable></transportation></transportations>
  <dataTypes><basicDataRepresentations><basicData><name>HLAunicodeString</name><size>0</size><interpretation>String</interpretation><endian>Big</endian><encoding>Unicode</encoding></basicData></basicDataRepresentations></dataTypes>
"""
        ),
        encoding="utf-8",
    )

    module = parse_fom_xml(source)
    root_object = next(spec for spec in module.object_classes if spec.full_name == "HLAobjectRoot")
    entity = next(spec for spec in module.object_classes if spec.full_name == "HLAobjectRoot.Entity")
    root_interaction = next(spec for spec in module.interaction_classes if spec.full_name == "HLAinteractionRoot")

    assert root_object.directed_interactions == ("Ping",)
    assert root_object.directed_interaction_sharing["Ping"] == "Subscribe"
    assert root_object.dimensions == ("ObjDim",)
    assert entity.attribute_datatypes["Status"] == "HLAunicodeString"
    assert root_interaction.dimensions == ("IntDim",)
    assert set(module.dimensions) == {"IntDim", "ObjDim"}
    assert module.time_stamp_datatype == "HLAinteger64Time"
    assert module.lookahead_datatype == "HLAinteger64Time"

    xml_text = serialize_fom_module(module, edition="2025")
    round_trip_source = tmp_path / "structural-association-roundtrip.xml"
    round_trip_source.write_text(xml_text, encoding="utf-8")
    reparsed = parse_fom_xml(round_trip_source)
    reparsed_root_object = next(spec for spec in reparsed.object_classes if spec.full_name == "HLAobjectRoot")
    reparsed_root_interaction = next(
        spec for spec in reparsed.interaction_classes if spec.full_name == "HLAinteractionRoot"
    )

    assert "<directedInteraction><name>Ping</name><sharing>Subscribe</sharing></directedInteraction>" in xml_text
    assert "<dimensions><dimension>ObjDim</dimension></dimensions>" in xml_text
    assert "<dimensions><dimension>IntDim</dimension></dimensions>" in xml_text
    assert "<attribute><name>Status</name><dataType>HLAunicodeString</dataType><sharing>Subscribe</sharing></attribute>" in xml_text
    assert reparsed_root_object.directed_interactions == ("Ping",)
    assert reparsed_root_object.directed_interaction_sharing["Ping"] == "Subscribe"
    assert reparsed_root_object.dimensions == ("ObjDim",)
    assert reparsed_root_interaction.dimensions == ("IntDim",)
    assert "<interactionClass><name>HLAinteractionRoot</name><sharing>PublishSubscribe</sharing>" in xml_text
    assert "<order>Timestamp</order>" in xml_text
    assert "LT sem" in xml_text
    assert "LTI sem" in xml_text


@pytest.mark.requirements(
    "HLA2025-OMT-COMP-166",
    "HLA2025-OMT-COMP-168",
    "HLA2025-OMT-COMP-169",
    "HLA2025-OMT-COMP-170",
)
def test_2025_parser_round_trips_additional_switch_metadata(tmp_path: Path) -> None:
    from hla.fom import parse_fom_xml, serialize_fom_module

    source = tmp_path / "additional-switches.xml"
    source.write_text(
        _wrap_omt_2025_fragment(
            """
  <modelIdentification><name>Probe</name><type>FOM</type></modelIdentification>
  <switches>
    <nonRegulatedGrant isEnabled="true" />
    <allowRelaxedDDM isEnabled="true" />
    <advisoriesUseKnownClass isEnabled="false" />
    <sendServiceReportsToFile isEnabled="true" />
  </switches>
"""
        ),
        encoding="utf-8",
    )

    module = parse_fom_xml(source)
    assert module.switch_settings["nonRegulatedGrant"] == "true"
    assert module.switch_settings["allowRelaxedDDM"] == "true"
    assert module.switch_settings["advisoriesUseKnownClass"] == "false"
    assert module.switch_settings["sendServiceReportsToFile"] == "true"

    reparsed_path = tmp_path / "additional-switches-roundtrip.xml"
    reparsed_path.write_text(serialize_fom_module(module, edition="2025"), encoding="utf-8")
    reparsed = parse_fom_xml(reparsed_path)
    assert reparsed.switch_settings["nonRegulatedGrant"] == "true"
    assert reparsed.switch_settings["allowRelaxedDDM"] == "true"
    assert reparsed.switch_settings["advisoriesUseKnownClass"] == "false"
    assert reparsed.switch_settings["sendServiceReportsToFile"] == "true"

    xml_text = reparsed_path.read_text(encoding="utf-8")
    assert '<nonRegulatedGrant isEnabled="true"' in xml_text
    assert '<allowRelaxedDDM isEnabled="true"' in xml_text
    assert '<advisoriesUseKnownClass isEnabled="false"' in xml_text
    assert '<sendServiceReportsToFile isEnabled="true"' in xml_text

@pytest.mark.requirements("HLA2025-OMT-001", "HLA2025-OMT-006")
def test_validate_hla_name_reports_structured_2025_omt_failures() -> None:
    from hla.fom.validation import validate_hla_name

    issues = validate_hla_name("hla.Bad:Name", table="objectClassStructure")

    assert all(issue.requirement == "HLA2025-OMT-001" for issue in issues)
    assert {issue.field for issue in issues} == {"name"}
    assert len(issues) >= 3
    assert any("periods" in issue.message for issue in issues)
    assert any("Colons" in issue.message for issue in issues)
    assert any("reserved" in issue.message for issue in issues)


@pytest.mark.requirements("HLA2025-OMT-001", "HLA2025-OMT-005", "HLA2025-OMT-006")
def test_validate_fom_module_returns_structured_issue_payloads() -> None:
    from hla.fom.validation import validate_fom_module
    from hla.fom import FOMModule, ObjectClassSpec

    module = FOMModule(
        source="synthetic",
        uri="synthetic:bad-fom",
        name="Synthetic Bad FOM",
        model_type="FOM",
        model_identification={
            "name": "Synthetic Bad FOM",
            "type": "FOM",
            "version": "1.0",
            "modificationDate": "2026-06-18",
            "securityClassification": "Unclassified",
            "description": "Validation test",
        },
        object_classes=(ObjectClassSpec(full_name="HLAobjectRoot.hlaBadEntity", declared_attributes=("Bad.Field",)),),
    )

    issues = validate_fom_module(module, strict_identification=True)
    payloads = [issue.as_dict() for issue in issues]

    assert any(issue["requirement"] == "HLA2025-OMT-005" and issue["field"] == "pocs" for issue in payloads)
    assert any(issue["requirement"] == "HLA2025-OMT-005" and issue["field"] == "references" for issue in payloads)
    assert any(issue["requirement"] == "HLA2025-OMT-001" and issue["table"] == "objectClassStructure" for issue in payloads)
    assert any(issue["requirement"] == "HLA2025-OMT-001" and issue["table"] == "attributeTable" for issue in payloads)


@pytest.mark.requirements("HLA2025-OMT-001")
@pytest.mark.parametrize("name", ("HLAdefaultRoutingSpace", "HLAfederate", "HLAserviceGroup"))
def test_validate_hla_name_allows_standard_mim_dimension_names(name: str) -> None:
    from hla.fom.validation import validate_hla_name

    assert validate_hla_name(name, table="dimensionTable") == []


@pytest.mark.requirements("HLA2025-FI-008", "HLA2025-OMT-001", "HLA2025-OMT-006")
def test_2025_python2025_rejects_fom_with_invalid_hla_user_defined_names(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel
    from hla.rti1516_2025.exceptions import InvalidFOM
    from hla.runtime.rti1516_2025_factory import create_hla_factory

    invalid_fom = tmp_path / "invalid-2025-name.xml"
    invalid_fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Invalid Name FOM</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Validation test module.</description>
    <poc><pocName>Test</pocName></poc>
    <references><reference>NA</reference></references>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>hlaBadEntity</name>
        <attribute>
          <name>GoodField</name>
          <dataType>HLAunicodeString</dataType>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )

    factory = create_hla_factory(provider="python1516_2025")
    result = factory.load_fom([invalid_fom])
    assert result.status == "invalid"
    assert any(entry == "validation_issues=1" for entry in result.diagnostics)

    federation_name = f"invalid-name-fed-{uuid.uuid4().hex[:8]}"
    rti = factory.create_rti_ambassador()
    rti.connect(object(), CallbackModel.HLA_EVOKED)

    with pytest.raises(InvalidFOM, match="reserved"):
        rti.createFederationExecution(federationName=federation_name, fomModule=str(invalid_fom))

    rti.disconnect()


@pytest.mark.requirements("HLA2025-OMT-005", "HLA2025-OMT-006")
def test_2025_factory_load_fom_reports_strict_identification_failures(tmp_path: Path) -> None:
    from hla.runtime.rti1516_2025_factory import create_hla_factory

    invalid_fom = tmp_path / "missing-identification-rows.xml"
    invalid_fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification>
    <name>Minimal Strict Failure</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-18</modificationDate>
    <securityClassification>Unclassified</securityClassification>
    <description>Missing POC and References rows.</description>
  </modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>StrictEntity</name>
        <attribute>
          <name>GoodField</name>
          <dataType>HLAunicodeString</dataType>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )

    result = create_hla_factory(provider="python1516_2025").load_fom(
        [invalid_fom],
        strict_identification=True,
    )

    assert result.status == "invalid"
    assert result.strict_identification is True
    assert any(entry == "strict_identification=true" for entry in result.diagnostics)
    assert any(entry == "validation_issues=2" for entry in result.diagnostics)
    assert {issue["field"] for issue in result.validation_issues if issue["requirement"] == "HLA2025-OMT-005"} == {
        "pocs",
        "references",
    }
    assert all(issue["status"] == "fail" for issue in result.validation_issues)
