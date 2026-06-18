from __future__ import annotations

import uuid
from pathlib import Path

import pytest


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
