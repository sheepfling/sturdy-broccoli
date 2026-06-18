from __future__ import annotations

import uuid
from pathlib import Path

import pytest


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
