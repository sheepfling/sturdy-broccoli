"""IEEE 1516.2-2025-oriented validation helpers for HLA names and FOM modules."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

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
        issues.extend(_validate_name_collection(mapping.keys(), table=table, allow_standard_names=getattr(module, "is_mim", False)))
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


__all__ = ["ValidationIssue", "validate_fom_module", "validate_fom_modules", "validate_hla_name"]
