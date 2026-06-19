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
    from hla.rti1516_2025.validation import validate_omt_xml_schema

    return {issue.requirement for issue in validate_omt_xml_schema(_write_strict_omt_fixture(tmp_path, text), OMT_2025_SCHEMA)}


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
    from hla.rti1516_2025.validation import validate_omt_xml_schema

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
    from hla.rti1516_2025.validation import validate_omt_xml_schema

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


@pytest.mark.requirements("HLA2025-MOD-010", "HLA2025-VER-002", "HLA2025-OMT-002")
def test_2025_parser_round_trips_logical_time_xml_names(tmp_path: Path) -> None:
    from hla.rti1516e.fom import parse_fom_xml, serialize_fom_module

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
    <logicalTime><dataType>HLAinteger64Time</dataType></logicalTime>
    <logicalTimeInterval><dataType>HLAinteger64Time</dataType></logicalTimeInterval>
  </time>
</objectModel>
""",
        encoding="utf-8",
    )

    module = parse_fom_xml(source)
    assert module.time_stamp_datatype == "HLAinteger64Time"
    assert module.lookahead_datatype == "HLAinteger64Time"
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


@pytest.mark.requirements("HLA2025-NEW-006", "HLA2025-OMT-002", "HLA2025-OMT-006")
def test_2025_parser_preserves_reference_datatypes_and_value_required_metadata(tmp_path: Path) -> None:
    from hla.rti1516_2025.validation import validate_fom_module
    from hla.rti1516e.fom import parse_fom_xml, serialize_fom_module

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


@pytest.mark.requirements("HLA2025-NEW-006", "HLA2025-OMT-006")
def test_2025_validation_rejects_invalid_value_required_metadata(tmp_path: Path) -> None:
    from hla.rti1516_2025.validation import validate_fom_module
    from hla.rti1516e.fom import parse_fom_xml

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


@pytest.mark.requirements("HLA2025-OMT-001", "HLA2025-OMT-006")
def test_validate_hla_name_reports_structured_2025_omt_failures() -> None:
    from hla.rti1516_2025.validation import validate_hla_name

    issues = validate_hla_name("hla.Bad:Name", table="objectClassStructure")

    assert all(issue.requirement == "HLA2025-OMT-001" for issue in issues)
    assert {issue.field for issue in issues} == {"name"}
    assert len(issues) >= 3
    assert any("periods" in issue.message for issue in issues)
    assert any("Colons" in issue.message for issue in issues)
    assert any("reserved" in issue.message for issue in issues)


@pytest.mark.requirements("HLA2025-OMT-001", "HLA2025-OMT-005", "HLA2025-OMT-006")
def test_validate_fom_module_returns_structured_issue_payloads() -> None:
    from hla.rti1516_2025.validation import validate_fom_module
    from hla.rti1516e.fom import FOMModule, ObjectClassSpec

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


@pytest.mark.requirements("HLA2025-FI-008", "HLA2025-OMT-001", "HLA2025-OMT-006")
def test_2025_shim_rejects_fom_with_invalid_hla_user_defined_names(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel
    from hla.rti1516_2025.exceptions import InvalidFOM
    from hla.rti1516_2025.factory import create_hla_factory

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

    factory = create_hla_factory(provider="shim")
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
    from hla.rti1516_2025.factory import create_hla_factory

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

    result = create_hla_factory(provider="shim").load_fom(
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
