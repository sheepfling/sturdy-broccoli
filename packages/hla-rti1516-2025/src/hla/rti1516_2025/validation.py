"""IEEE 1516.2-2025-oriented validation helpers for HLA names and FOM modules."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

try:
    from lxml import etree as LET
except ModuleNotFoundError:  # pragma: no cover - depends on optional runtime extra
    LET = None

_XML_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
_RESERVED_STANDARD_NAMES = frozenset(
    {
        "HLAobjectRoot",
        "HLAinteractionRoot",
        "HLAreliable",
        "HLAbestEffort",
        "HLAdefault",
        "HLAinteger64Time",
        "HLAfloat64Time",
    }
)
_IDENTIFICATION_FIELDS = (
    "name",
    "type",
    "version",
    "modificationDate",
    "securityClassification",
    "description",
    "pocs",
    "references",
)
_OMT_CV_REQUIREMENTS_BY_CONSTRAINT = {
    "dimensionDataTypeKey": "HLA2025-OMT-CV-001",
    "dimensionDataTypeRef": "HLA2025-OMT-CV-002",
    "representationKey": "HLA2025-OMT-CV-003",
    "representationRef": "HLA2025-OMT-CV-004",
    "dataTypeKey": "HLA2025-OMT-CV-005",
    "dataTypeRef": "HLA2025-OMT-CV-006",
    "dimensionKey": "HLA2025-OMT-CV-007",
    "dimensionRef": "HLA2025-OMT-CV-008",
    "transportationKey": "HLA2025-OMT-CV-009",
    "transportationRef": "HLA2025-OMT-CV-010",
    "className": "HLA2025-OMT-CV-011",
    "attributeName": "HLA2025-OMT-CV-012",
    "interactionName": "HLA2025-OMT-CV-013",
    "parameterName": "HLA2025-OMT-CV-014",
}
_OMT_CV_REQUIREMENTS_BY_ENUM_FIELD = {
    "resignAction": "HLA2025-OMT-CV-015",
    "reliable": "HLA2025-OMT-CV-016",
    "sharing": "HLA2025-OMT-CV-017",
    "order": "HLA2025-OMT-CV-018",
    "endian": "HLA2025-OMT-CV-019",
    "type": "HLA2025-OMT-CV-020",
    "capability": "HLA2025-OMT-CV-021",
    "updateType": "HLA2025-OMT-CV-022",
    "ownership": "HLA2025-OMT-CV-023",
    "valueRequired": "HLA2025-OMT-CV-024",
    "securityClassification": "HLA2025-OMT-CV-025",
    "applicationDomain": "HLA2025-OMT-CV-026",
    "pocType": "HLA2025-OMT-CV-029",
}
_OMT_NAMESPACE = "http://standards.ieee.org/IEEE1516-2025"
_STRICT_OMT_ENUM_SPECS = (
    ("//ns:automaticResignAction/@resignAction", "resignAction", {"UnconditionallyDivestAttributes", "DeleteObjects", "CancelPendingOwnershipAcquisitions", "DeleteObjectsThenDivest", "CancelThenDeleteThenDivest", "NoAction"}, "HLA2025-OMT-CV-015"),
    ("//ns:transportation/ns:reliable/text()", "reliable", {"Yes", "No"}, "HLA2025-OMT-CV-016"),
    ("//ns:sharing/text()", "sharing", {"Publish", "Subscribe", "PublishSubscribe", "Neither"}, "HLA2025-OMT-CV-017"),
    ("//ns:order/text()", "order", {"Receive", "TimeStamp"}, "HLA2025-OMT-CV-018"),
    ("//ns:endian/text()", "endian", {"Big", "Little"}, "HLA2025-OMT-CV-019"),
    ("/ns:objectModel/ns:modelIdentification/ns:type/text()", "type", {"FOM", "SOM"}, "HLA2025-OMT-CV-020"),
    ("//ns:synchronizationPoint/ns:capability/text()", "capability", {"Register", "Achieve", "RegisterAchieve", "NoSynch", "NA"}, "HLA2025-OMT-CV-021"),
    ("//ns:updateType/text()", "updateType", {"Static", "Periodic", "Conditional", "NA"}, "HLA2025-OMT-CV-022"),
    ("//ns:ownership/text()", "ownership", {"Divest", "Acquire", "DivestAcquire", "NoTransfer"}, "HLA2025-OMT-CV-023"),
    ("//ns:valueRequired/text()", "valueRequired", {"true", "false"}, "HLA2025-OMT-CV-024"),
    ("//ns:securityClassification/text()", "securityClassification", {"Unclassified", "Confidential", "Secret", "Top Secret"}, "HLA2025-OMT-CV-025"),
    ("//ns:applicationDomain/text()", "applicationDomain", {"Analysis", "Training", "Test and Evaluation", "Engineering", "Acquisition"}, "HLA2025-OMT-CV-026"),
    ("//ns:fixedRecordData/ns:encoding/text()", "encoding", {"HLAfixedRecord"}, "HLA2025-OMT-CV-027"),
    ("//ns:variantRecordData/ns:encoding/text()", "encoding", {"HLAvariantRecord", "HLAextendableVariantRecord"}, "HLA2025-OMT-CV-028"),
    ("//ns:pocType/text()", "pocType", {"Primary author", "Contributor", "Proponent", "Sponsor", "Release authority", "Technical POC"}, "HLA2025-OMT-CV-029"),
)


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    requirement: str
    table: str
    field: str
    value: str
    status: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def validate_hla_name(
    name: str,
    *,
    table: str,
    field: str = "name",
    allow_standard: bool = False,
) -> list[ValidationIssue]:
    """Validate one HLA user-defined name against the 2025 naming subset."""

    issues: list[ValidationIssue] = []
    text = name if isinstance(name, str) else repr(name)
    if not isinstance(name, str) or not name:
        return [
            ValidationIssue(
                requirement="HLA2025-OMT-001",
                table=table,
                field=field,
                value=text,
                status="fail",
                message="HLA names must be non-empty strings",
            )
        ]
    if not _XML_NAME_RE.fullmatch(name):
        issues.append(
            ValidationIssue(
                requirement="HLA2025-OMT-001",
                table=table,
                field=field,
                value=name,
                status="fail",
                message="Name must follow the XML naming subset used by the validator",
            )
        )
    if "." in name:
        issues.append(
            ValidationIssue(
                requirement="HLA2025-OMT-001",
                table=table,
                field=field,
                value=name,
                status="fail",
                message="User-defined HLA names shall not contain periods",
            )
        )
    if ":" in name:
        issues.append(
            ValidationIssue(
                requirement="HLA2025-OMT-001",
                table=table,
                field=field,
                value=name,
                status="fail",
                message="Colons should not be used in HLA names",
            )
        )
    if name in {"NA", "na"}:
        issues.append(
            ValidationIssue(
                requirement="HLA2025-OMT-001",
                table=table,
                field=field,
                value=name,
                status="fail",
                message="NA/na is reserved as the not-applicable marker",
            )
        )
    if name.lower().startswith("hla") and not (allow_standard or name in _RESERVED_STANDARD_NAMES):
        issues.append(
            ValidationIssue(
                requirement="HLA2025-OMT-001",
                table=table,
                field=field,
                value=name,
                status="fail",
                message="Names beginning with hla/HLA are reserved",
            )
        )
    return issues


def validate_fom_module(module: Any, *, strict_identification: bool = False) -> list[ValidationIssue]:
    """Return structured 2025 OMT validation issues for one parsed FOM module."""

    issues: list[ValidationIssue] = []
    if strict_identification:
        issues.extend(_validate_identification_table(getattr(module, "model_identification", {})))
    issues.extend(_validate_object_classes(module))
    issues.extend(_validate_interaction_classes(module))
    issues.extend(_validate_name_collection(getattr(module, "dimensions", ()), table="dimensionTable"))
    issues.extend(
        _validate_name_collection(
            getattr(module, "transportation_names", ()),
            table="transportationTypeTable",
            allow_standard_names=True,
        )
    )
    issues.extend(
        _validate_name_collection(
            getattr(module, "update_rates", {}).keys(),
            table="updateRateTable",
            allow_standard_names=True,
        )
    )
    issues.extend(_validate_name_collection(getattr(module, "switch_settings", {}).keys(), table="switchesTable"))
    issues.extend(_validate_name_collection(getattr(module, "synchronization_points", {}).keys(), table="synchronizationPoints"))
    issues.extend(_validate_datatypes(module))
    return issues


def validate_fom_modules(modules: Iterable[Any], *, strict_identification: bool = False) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for module in modules:
        issues.extend(validate_fom_module(module, strict_identification=strict_identification))
    return issues


def validate_omt_xml_schema(xml_path: str | Path, schema_path: str | Path) -> list[ValidationIssue]:
    """Validate one object-model document against the supplied IEEE 1516.2 OMT XSD."""

    if LET is None:
        raise RuntimeError("lxml is required for IEEE 1516.2 OMT XML Schema validation")
    schema = LET.XMLSchema(LET.parse(str(schema_path)))
    xml_document = LET.parse(str(xml_path))
    strict_issues = _strict_omt_enumeration_issues(xml_document)
    if schema.validate(xml_document):
        return strict_issues
    return [_schema_error_to_issue(error) for error in schema.error_log] + strict_issues


def _validate_identification_table(metadata: Mapping[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for field in _IDENTIFICATION_FIELDS:
        value = metadata.get(field)
        if value in (None, ""):
            issues.append(
                ValidationIssue(
                    requirement="HLA2025-OMT-005",
                    table="objectModelIdentification",
                    field=field,
                    value="" if value is None else str(value),
                    status="fail",
                    message="Required identification row is missing or empty",
                )
            )
    return issues


def _schema_error_to_issue(error: Any) -> ValidationIssue:
    message = str(error.message)
    path = str(getattr(error, "path", "") or "")
    return ValidationIssue(
        requirement=_schema_error_requirement(message, path),
        table="omtXmlSchema",
        field=_schema_error_field(message, path),
        value=message,
        status="fail",
        message=message,
    )


def _schema_error_requirement(message: str, path: str) -> str:
    for constraint, requirement in _OMT_CV_REQUIREMENTS_BY_CONSTRAINT.items():
        if constraint in message:
            return requirement
    if "fixedRecordData" in path and "encoding" in path:
        return "HLA2025-OMT-CV-027"
    if "variantRecordData" in path and "encoding" in path:
        return "HLA2025-OMT-CV-028"
    field = _schema_error_field(message, path)
    return _OMT_CV_REQUIREMENTS_BY_ENUM_FIELD.get(field, "HLA2025-OMT-CV")


def _schema_error_field(message: str, path: str) -> str:
    attribute_match = re.search(r"attribute '([^']+)'", message)
    if attribute_match:
        return attribute_match.group(1)
    element_match = re.search(r"Element '\{[^}]+\}([^']+)'", message)
    if element_match:
        return element_match.group(1)
    for part in reversed(path.split("/")):
        if part:
            return part.split(":")[-1]
    return "schema"


def _strict_omt_enumeration_issues(xml_document: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    namespaces = {"ns": _OMT_NAMESPACE}
    for xpath, field, allowed_values, requirement in _STRICT_OMT_ENUM_SPECS:
        for value in xml_document.xpath(xpath, namespaces=namespaces):
            text = str(value)
            if text not in allowed_values:
                issues.append(
                    ValidationIssue(
                        requirement=requirement,
                        table="omtXmlSchema",
                        field=field,
                        value=text,
                        status="fail",
                        message=f"{field} must be one of {sorted(allowed_values)}",
                    )
                )
    return issues


def _validate_object_classes(module: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for spec in getattr(module, "object_classes", ()):
        leaf_name = spec.full_name.rsplit(".", 1)[-1]
        allow_standard = getattr(module, "is_mim", False) or leaf_name == "HLAobjectRoot"
        issues.extend(
            validate_hla_name(
                leaf_name,
                table="objectClassStructure",
                allow_standard=allow_standard,
            )
        )
        issues.extend(_validate_name_collection(spec.declared_attributes, table="attributeTable"))
        for attribute_name, value in getattr(spec, "attribute_value_required", {}).items():
            if str(value).lower() not in {"true", "false"}:
                issues.append(
                    ValidationIssue(
                        requirement="HLA2025-NEW-006",
                        table="attributeTable",
                        field="valueRequired",
                        value=str(value),
                        status="fail",
                        message=f"valueRequired for attribute {attribute_name!r} must be true or false",
                    )
                )
    return issues


def _validate_interaction_classes(module: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for spec in getattr(module, "interaction_classes", ()):
        leaf_name = spec.full_name.rsplit(".", 1)[-1]
        allow_standard = getattr(module, "is_mim", False) or leaf_name == "HLAinteractionRoot"
        issues.extend(
            validate_hla_name(
                leaf_name,
                table="interactionClassStructure",
                allow_standard=allow_standard,
            )
        )
        issues.extend(_validate_name_collection(spec.declared_parameters, table="parameterTable"))
    return issues


def _validate_datatypes(module: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    datatype_tables = (
        ("basicDataTypes", getattr(module, "basic_datatypes", {})),
        ("simpleDataTypes", getattr(module, "simple_datatypes", {})),
        ("referenceDataTypes", getattr(module, "reference_datatypes", {})),
        ("enumeratedDataTypes", getattr(module, "enumerated_datatypes", {})),
        ("arrayDataTypes", getattr(module, "array_datatypes", {})),
        ("fixedRecordDataTypes", getattr(module, "fixed_record_datatypes", {})),
        ("variantRecordDataTypes", getattr(module, "variant_record_datatypes", {})),
    )
    for table, mapping in datatype_tables:
        for name in mapping.keys():
            issues.extend(
                validate_hla_name(
                    name,
                    table=table,
                    allow_standard=getattr(module, "is_mim", False) or str(name).startswith("HLA"),
                )
            )
    for spec in getattr(module, "fixed_record_datatypes", {}).values():
        issues.extend(_validate_name_collection((field.name for field in spec.fields), table="fixedRecordFields"))
    for spec in getattr(module, "variant_record_datatypes", {}).values():
        issues.extend(_validate_name_collection((alt.name for alt in spec.alternatives if alt.name), table="variantRecordAlternatives"))
    return issues


def _validate_name_collection(
    names: Iterable[str],
    *,
    table: str,
    allow_standard_names: bool = False,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for name in names:
        issues.extend(validate_hla_name(name, table=table, allow_standard=allow_standard_names))
    return issues


__all__ = ["ValidationIssue", "validate_fom_module", "validate_fom_modules", "validate_hla_name", "validate_omt_xml_schema"]
