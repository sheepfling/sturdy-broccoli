"""Table-driven MOM/MIM exposure model derived from the active FDD catalog.

The pure Python RTI loads the standard MIM before user FOM modules, then builds
this view from the merged :class:`hla.rti1516e.fom.FOMCatalog`.  The resulting model
is the source of truth for MOM object attributes, interaction parameters,
request/report pairing, RTI-send/RTI-receive direction, and strict negative-path
validation.

Section anchors: IEEE 1516.1-2010 §11.1-§11.6 and Annex G.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from hla.rti1516e import mom as hla_mom
from hla.rti1516e.fom import FOMCatalog

MOM_PARAMETER_ALIASES: dict[str, tuple[str, ...]] = {
    "HLAMIMData": ("HLAMIMdata",),
    "HLAMIMdata": ("HLAMIMData",),
    "HLAMIMDesignator": ("HLAMIMdesignator",),
    "HLAMIMdesignator": ("HLAMIMDesignator",),
    "HLAtransportationType": ("HLAtransportation",),
    "HLAtransportation": ("HLAtransportationType",),
    "HLAorderType": ("HLAsendOrder",),
    "HLAsendOrder": ("HLAorderType",),
    "HLAattribute": ("HLAattributeList",),
    "HLAattributeList": ("HLAattribute",),
    "HLAobjectClassName": ("HLAobjectClass",),
    "HLAobjectClass": ("HLAobjectClassName",),
    "HLAinteractionClassName": ("HLAinteractionClass",),
    "HLAinteractionClass": ("HLAinteractionClassName",),
    "HLAserviceReporting": ("HLAreportingState",),
    "HLAexceptionReporting": ("HLAreportingState",),
    "HLAinitiator": ("HLAsuppliedArguments",),
    "HLAsyncPoints": ("HLAsynchronizationPoints",),
    "HLAsyncPointName": ("HLAlabel",),
    "HLAsyncPointFederates": ("HLAfederateList", "HLAfederateSynchronizationStatusList"),
}

MOM_OPTIONAL_DECLARED_PARAMETERS_BY_LEAF: dict[str, frozenset[str]] = {
    "HLAsynchronizationPointAchieved": frozenset({"HLAsuccessIndicator"}),
    "HLAfederateSaveComplete": frozenset({"HLAsuccessIndicator"}),
    "HLAfederateRestoreComplete": frozenset({"HLAsuccessIndicator"}),
    "HLAunpublishObjectClassAttributes": frozenset({"HLAattributeList"}),
    "HLAdeleteObjectInstance": frozenset({"HLAtimeStamp", "HLAtag"}),
    "HLAsubscribeObjectClassAttributes": frozenset({"HLAactive"}),
    "HLAsubscribeInteractionClass": frozenset({"HLAactive"}),
}

INTERACTION_NAME_ALIASES: dict[str, tuple[str, ...]] = {
    f"{hla_mom.MOM_FEDERATION_INTERACTION_ROOT}.HLArequest.HLArequestMIMData": (
        f"{hla_mom.MOM_FEDERATION_INTERACTION_ROOT}.HLArequest.HLArequestMIMdata",
    ),
    f"{hla_mom.MOM_FEDERATION_INTERACTION_ROOT}.HLAreport.HLAreportMIMData": (
        f"{hla_mom.MOM_FEDERATION_INTERACTION_ROOT}.HLAreport.HLAreportMIMdata",
    ),
    f"{hla_mom.MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLArequestAttributeTransportationypeChange": (
        f"{hla_mom.MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLArequestAttributeTransportationTypeChange",
    ),
    f"{hla_mom.MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLArequestInteractionTransportationypeChange": (
        f"{hla_mom.MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLArequestInteractionTransportationTypeChange",
    ),
}

MOM_BOOL_PARAMETERS = frozenset(
    {
        "HLAactive",
        "HLAautoProvide",
        "HLAconveyProducingFederate",
        "HLAconveyRegionDesignatorSets",
        "HLAexceptionReporting",
        "HLAreportingState",
        "HLAsendServiceReportsToFile",
        "HLAserviceReporting",
        "HLAsuccessIndicator",
    }
)
MOM_FLOAT_PARAMETERS = frozenset({"HLAreportPeriod", "HLAmaxUpdateRate"})
MOM_TIME_PARAMETERS = frozenset({"HLAtimeStamp", "HLAtimeGrantedTime", "HLAtimeAdvancingTime"})
MOM_INTERVAL_PARAMETERS = frozenset({"HLAlookahead"})
MOM_HANDLE_PARAMETERS = frozenset(
    {
        "HLAfederate",
        "HLAobjectClass",
        "HLAinteractionClass",
        "HLAobjectInstance",
        "HLAtransportation",
        "HLAtransportationType",
    }
)
MOM_HANDLE_SET_PARAMETERS = frozenset({"HLAattributeList", "HLAfederateList", "HLAdimensionHandleSet"})


@dataclass(frozen=True)
class MOMValidationIssue:
    kind: str
    interaction_name: str
    parameter_name: str = ""
    detail: str = ""
    severity: str = "error"
    section: str = "1516.1-2010 §11.3-§11.5"

    @property
    def code(self) -> str:
        return self.kind

    @property
    def message(self) -> str:
        return self.detail or self.kind

    def as_report_values(self, federate_handle: Any = "", service_name: str | None = None) -> dict[str, Any]:
        return {
            "HLAfederate": federate_handle or "",
            "HLAservice": service_name or self.interaction_name,
            "HLAexception": self.kind,
            "HLAparameterError": self.parameter_name or self.detail,
        }


@dataclass(frozen=True)
class MOMObjectClassRule:
    name: str
    attributes: tuple[str, ...]
    declared_attributes: tuple[str, ...]
    parent_name: str | None = None
    is_leaf: bool = False
    attribute_datatypes: Mapping[str, str] = field(default_factory=dict)

    @property
    def allowed_attributes(self) -> frozenset[str]:
        return frozenset(self.attributes)


@dataclass(frozen=True)
class MOMInteractionRule:
    name: str
    family: str
    role: str | None
    leaf_name: str
    parameters: tuple[str, ...]
    declared_parameters: tuple[str, ...]
    inherited_parameters: tuple[str, ...]
    required_parameters: tuple[str, ...]
    optional_parameters: tuple[str, ...]
    at_least_one_of: tuple[str, ...] = ()
    report_name: str | None = None
    is_leaf: bool = False
    rti_direction: str = "none"
    parameter_datatypes: Mapping[str, str] = field(default_factory=dict)

    @property
    def allowed_parameters(self) -> frozenset[str]:
        return frozenset(self.parameters)

    @property
    def is_receive_leaf(self) -> bool:
        return self.is_leaf and self.rti_direction == "rti-receives"

    @property
    def is_report_leaf(self) -> bool:
        return self.is_leaf and self.rti_direction == "rti-sends"

    @property
    def negative_case_specs(self) -> tuple[dict[str, Any], ...]:
        cases: list[dict[str, Any]] = []
        if self.is_receive_leaf:
            cases.append({"case": "unexpected_parameter", "strict_mode": "strict_mom_parameter_decoding"})
            for name in self.required_parameters:
                cases.append({"case": "missing_required_parameter", "parameter": name, "strict_mode": "strict_mom_parameter_decoding"})
            if self.at_least_one_of:
                cases.append({"case": "missing_parameter_choice", "parameters": list(self.at_least_one_of), "strict_mode": "strict_mom_parameter_decoding"})
            for name in self.parameters:
                lower = name.lower()
                if name in MOM_BOOL_PARAMETERS:
                    cases.append({"case": "bad_boolean_encoding", "parameter": name})
                elif name in MOM_FLOAT_PARAMETERS:
                    cases.append({"case": "bad_float_encoding", "parameter": name})
                elif name in MOM_TIME_PARAMETERS:
                    cases.append({"case": "bad_time_encoding", "parameter": name})
                elif name in MOM_INTERVAL_PARAMETERS:
                    cases.append({"case": "bad_interval_encoding", "parameter": name})
                elif name in MOM_HANDLE_PARAMETERS or name in MOM_HANDLE_SET_PARAMETERS or lower.endswith("handle") or lower.endswith("handlelist"):
                    cases.append({"case": "bad_handle_encoding", "parameter": name})
            if self.role == "HLAservice":
                cases.append({"case": "unsupported_or_failed_service_action", "service_leaf": self.leaf_name})
        return tuple(cases)


@dataclass(frozen=True)
class MOMExposureModel:
    object_classes: Mapping[str, MOMObjectClassRule]
    interaction_classes: Mapping[str, MOMInteractionRule]
    request_to_report: Mapping[str, str]
    aliases: Mapping[str, str] = field(default_factory=dict)

    def object_rule(self, name: str) -> MOMObjectClassRule | None:
        canonical = self.canonical_object_class_name(name) or str(name)
        return self.object_classes.get(canonical)

    def interaction_rule(self, name: str) -> MOMInteractionRule | None:
        canonical = self.canonical_interaction_name(str(name)) or str(name)
        return self.interaction_classes.get(canonical)

    def canonical_interaction_name(self, name: str) -> str | None:
        text = str(name)
        if text in self.interaction_classes:
            return text
        alias = self.aliases.get(text)
        if alias in self.interaction_classes:
            return alias
        lower = text.lower()
        for candidate in self.interaction_classes:
            if candidate.lower() == lower:
                return candidate
        return None

    def canonical_object_class_name(self, name: str) -> str | None:
        text = str(name)
        if text in self.object_classes:
            return text
        alias = self.aliases.get(text)
        if alias in self.object_classes:
            return alias
        lower = text.lower()
        for candidate in self.object_classes:
            if candidate.lower() == lower:
                return candidate
        return None

    def report_for_request(self, request_name: str) -> str | None:
        canonical = self.canonical_interaction_name(request_name) or str(request_name)
        return self.request_to_report.get(canonical)

    def parameters_for(self, interaction_name: str) -> tuple[str, ...]:
        rule = self.interaction_rule(interaction_name)
        return rule.parameters if rule else ()

    def object_attributes_for(self, object_class_name: str) -> tuple[str, ...]:
        rule = self.object_rule(object_class_name)
        return rule.attributes if rule else ()

    def validate_incoming_parameters(
        self,
        interaction_name: str,
        supplied_parameters: Mapping[str, bytes] | set[str] | tuple[str, ...] | list[str],
        *,
        strict: bool = True,
    ) -> tuple[MOMValidationIssue, ...]:
        canonical = self.canonical_interaction_name(interaction_name)
        if canonical is None:
            return (MOMValidationIssue("MOMInteractionClassNotDefined", str(interaction_name)),)
        rule = self.interaction_classes[canonical]
        if rule.rti_direction != "rti-receives":
            return (
                MOMValidationIssue(
                    "MOMInteractionNotReceivableByRTI",
                    canonical,
                    detail=f"direction={rule.rti_direction}",
                    section="1516.1-2010 §11.3",
                ),
            )
        if isinstance(supplied_parameters, Mapping):
            supplied = {canonical_parameter_name(rule, name) for name in supplied_parameters.keys()}
        else:
            supplied = {canonical_parameter_name(rule, name) for name in supplied_parameters}
        issues: list[MOMValidationIssue] = []
        unexpected = sorted(name for name in supplied if name not in rule.allowed_parameters)
        if strict:
            issues.extend(MOMValidationIssue("UnexpectedMOMParameter", canonical, name) for name in unexpected)
            missing = [name for name in rule.required_parameters if name not in supplied]
            issues.extend(MOMValidationIssue("MissingMOMParameter", canonical, name) for name in missing)
            if rule.at_least_one_of and not any(name in supplied for name in rule.at_least_one_of):
                issues.append(
                    MOMValidationIssue(
                        "MissingMOMParameterChoice",
                        canonical,
                        ",".join(rule.at_least_one_of),
                        detail="At least one switch parameter is required",
                    )
                )
        return tuple(issues)

    def interaction_matrix(self) -> dict[str, dict[str, Any]]:
        return {
            name: {
                "family": rule.family,
                "role": rule.role,
                "leaf_name": rule.leaf_name,
                "is_leaf": rule.is_leaf,
                "rti_direction": rule.rti_direction,
                "parameters": list(rule.parameters),
                "declared_parameters": list(rule.declared_parameters),
                "inherited_parameters": list(rule.inherited_parameters),
                "required_parameters": list(rule.required_parameters),
                "optional_parameters": list(rule.optional_parameters),
                "at_least_one_of": list(rule.at_least_one_of),
                "parameter_datatypes": dict(rule.parameter_datatypes),
                "report_name": rule.report_name,
                "negative_cases": list(rule.negative_case_specs),
            }
            for name, rule in sorted(self.interaction_classes.items())
        }

    def object_matrix(self) -> dict[str, dict[str, Any]]:
        return {
            name: {
                "is_leaf": rule.is_leaf,
                "parent_name": rule.parent_name,
                "attributes": list(rule.attributes),
                "declared_attributes": list(rule.declared_attributes),
                "attribute_datatypes": dict(rule.attribute_datatypes),
            }
            for name, rule in sorted(self.object_classes.items())
        }

    def as_summary(self) -> dict[str, Any]:
        return {
            "object_class_count": len(self.object_classes),
            "interaction_class_count": len(self.interaction_classes),
            "request_report_pair_count": len(self.request_to_report),
            "request_report_pairs": dict(sorted(self.request_to_report.items())),
            "mom_object_classes": sorted(self.object_classes),
            "mom_interaction_classes": sorted(self.interaction_classes),
            "object_attributes": {
                name: list(rule.attributes) for name, rule in sorted(self.object_classes.items())
            },
            "interaction_parameters": {
                name: list(rule.parameters) for name, rule in sorted(self.interaction_classes.items())
            },
            "interaction_required_parameters": {
                name: list(rule.required_parameters)
                for name, rule in sorted(self.interaction_classes.items())
                if rule.required_parameters
            },
            "interaction_at_least_one_parameters": {
                name: list(rule.at_least_one_of)
                for name, rule in sorted(self.interaction_classes.items())
                if rule.at_least_one_of
            },
            "leaf_interactions": sorted(name for name, rule in self.interaction_classes.items() if rule.is_leaf),
            "rti_received_interactions": sorted(name for name, rule in self.interaction_classes.items() if rule.rti_direction == "rti-receives"),
            "rti_sent_interactions": sorted(name for name, rule in self.interaction_classes.items() if rule.rti_direction == "rti-sends"),
            "aliases": dict(sorted(self.aliases.items())),
        }


def _mom_parts(full_name: str) -> tuple[str, str | None, str]:
    parts = full_name.split(".")
    try:
        manager_index = parts.index("HLAmanager")
    except ValueError:
        return "", None, parts[-1] if parts else ""
    family = parts[manager_index + 1] if len(parts) > manager_index + 1 else ""
    role = parts[manager_index + 2] if len(parts) > manager_index + 2 else None
    leaf = parts[-1] if parts else ""
    return family, role, leaf


def canonical_parameter_name(rule: MOMInteractionRule | None, name: str) -> str:
    if rule is None:
        return str(name)
    text = str(name)
    allowed = set(rule.parameters)
    if text in allowed:
        return text
    for candidate in MOM_PARAMETER_ALIASES.get(text, ()):  # pragma: no branch - tiny loop
        if candidate in allowed:
            return candidate
    lowered = {param.lower(): param for param in allowed}
    return lowered.get(text.lower(), text)


def canonical_attribute_name(rule: MOMObjectClassRule | None, name: str) -> str:
    if rule is None:
        return str(name)
    text = str(name)
    allowed = set(rule.attributes)
    if text in allowed:
        return text
    for candidate in MOM_PARAMETER_ALIASES.get(text, ()):
        if candidate in allowed:
            return candidate
    lowered = {attr.lower(): attr for attr in allowed}
    return lowered.get(text.lower(), text)


def _required_parameters_for(role: str | None, leaf_name: str, parameters: tuple[str, ...], declared: tuple[str, ...]) -> tuple[str, ...]:
    if role == "HLAadjust" and leaf_name == "HLAsetSwitches":
        # §11.4.1 requires at least one switch parameter; HLAfederate is optional
        # in this local RTI because omission targets the invoking federate.
        return ()
    optional = MOM_OPTIONAL_DECLARED_PARAMETERS_BY_LEAF.get(leaf_name, frozenset())
    if role in {"HLAadjust", "HLArequest", "HLAservice"}:
        return tuple(name for name in parameters if name not in optional)
    return ()


def _at_least_one_parameters_for(role: str | None, leaf_name: str, declared: tuple[str, ...]) -> tuple[str, ...]:
    if role == "HLAadjust" and leaf_name == "HLAsetSwitches":
        return tuple(name for name in declared if name != "HLAfederate")
    return ()


def _direction_for(role: str | None, is_leaf: bool) -> str:
    if not is_leaf:
        return "none"
    if role in {"HLAadjust", "HLArequest", "HLAservice"}:
        return "rti-receives"
    if role == "HLAreport":
        return "rti-sends"
    return "none"


def _build_alias_map(interaction_names: set[str], object_names: set[str]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for alias, candidates in INTERACTION_NAME_ALIASES.items():
        for candidate in candidates:
            if candidate in interaction_names:
                aliases[alias] = candidate
                break
    for name in interaction_names:
        aliases.setdefault(name.lower(), name)
    for name in object_names:
        aliases.setdefault(name.lower(), name)
    return aliases


def _canonical_request_report_pair(name: str, interaction_names: set[str], aliases: Mapping[str, str]) -> str | None:
    if ".HLArequest." not in name:
        return None
    leaf = name.rsplit(".", 1)[-1]
    if not leaf.startswith("HLArequest"):
        return None
    report_leaf = "HLAreport" + leaf[len("HLArequest") :]
    stem = name.rsplit(".HLArequest.", 1)[0]
    candidate = stem + ".HLAreport." + report_leaf
    if candidate in interaction_names:
        return candidate
    if candidate in aliases:
        return aliases[candidate]
    lower = candidate.lower()
    if lower in aliases:
        return aliases[lower]
    for interaction in interaction_names:
        if interaction.lower() == lower:
            return interaction
    return None



def _parameter_datatypes_for(parameters: tuple[str, ...]) -> dict[str, str]:
    datatypes: dict[str, str] = {}
    for name in parameters:
        if name in MOM_BOOL_PARAMETERS:
            datatypes[name] = "HLAboolean"
        elif name in MOM_FLOAT_PARAMETERS:
            datatypes[name] = "HLAfloat64BE"
        elif name in MOM_TIME_PARAMETERS:
            datatypes[name] = "HLAtime"
        elif name in MOM_INTERVAL_PARAMETERS:
            datatypes[name] = "HLAlookahead"
        elif name in MOM_HANDLE_PARAMETERS:
            datatypes[name] = "HLAhandle"
        elif name in MOM_HANDLE_SET_PARAMETERS:
            datatypes[name] = "HLAhandleList"
        elif name.lower().endswith("count") or name in {"HLAnumberOfClasses", "HLAserialNumber"}:
            datatypes[name] = "HLAinteger32BE"
        elif name.lower().endswith("data") or name in {"HLAsuppliedArguments", "HLAreturnedArguments"}:
            datatypes[name] = "HLAopaqueData"
        else:
            datatypes[name] = "HLAunicodeString"
    return datatypes


def _attribute_datatypes_for(attributes: tuple[str, ...]) -> dict[str, str]:
    # The parser does not yet preserve full OMT datatype columns for attributes;
    # provide deterministic MOM defaults for validation assets and diagnostics.
    datatypes: dict[str, str] = {}
    for name in attributes:
        if name.startswith("HLAconvey") or name in {"HLAautoProvide", "HLAtimeConstrained", "HLAtimeRegulating", "HLAasynchronousDelivery"}:
            datatypes[name] = "HLAboolean"
        elif name.endswith("Count") or name.endswith("length") or name.endswith("Sent") or name.endswith("Received"):
            datatypes[name] = "HLAinteger32BE"
        elif name in {"HLAcurrentFDD"}:
            datatypes[name] = "HLAopaqueData"
        else:
            datatypes[name] = "HLAunicodeString"
    return datatypes

def build_mom_exposure_model(catalog: FOMCatalog) -> MOMExposureModel:
    object_names = {name for name in catalog.object_classes if hla_mom.is_mom_object_class_name(name)}
    interaction_names = {name for name in catalog.interaction_classes if hla_mom.is_mom_interaction_class_name(name)}
    aliases = _build_alias_map(interaction_names, object_names)

    object_rules: dict[str, MOMObjectClassRule] = {}
    for name in sorted(object_names):
        spec = catalog.object_classes[name]
        is_leaf = not any(other != name and other.startswith(name + ".") for other in object_names)
        object_rules[name] = MOMObjectClassRule(
            name=name,
            attributes=tuple(spec.attributes),
            declared_attributes=tuple(spec.declared_attributes),
            parent_name=spec.parent_name,
            is_leaf=is_leaf,
            attribute_datatypes=_attribute_datatypes_for(tuple(spec.attributes)),
        )

    request_to_report: dict[str, str] = {}
    interaction_rules: dict[str, MOMInteractionRule] = {}
    for name in sorted(interaction_names):
        spec = catalog.interaction_classes[name]
        family, role, leaf = _mom_parts(name)
        is_leaf = not any(other != name and other.startswith(name + ".") for other in interaction_names)
        declared = tuple(spec.declared_parameters)
        inherited = tuple(param for param in spec.parameters if param not in declared)
        required = _required_parameters_for(role, leaf, tuple(spec.parameters), declared)
        at_least_one = _at_least_one_parameters_for(role, leaf, declared)
        optional = tuple(param for param in spec.parameters if param not in required)
        interaction_rules[name] = MOMInteractionRule(
            name=name,
            family=family,
            role=role,
            leaf_name=leaf,
            parameters=tuple(spec.parameters),
            declared_parameters=declared,
            inherited_parameters=inherited,
            required_parameters=required,
            optional_parameters=optional,
            at_least_one_of=at_least_one,
            is_leaf=is_leaf,
            rti_direction=_direction_for(role, is_leaf),
            parameter_datatypes=_parameter_datatypes_for(tuple(spec.parameters)),
        )

    for name, rule in list(interaction_rules.items()):
        if rule.role != "HLArequest":
            continue
        report = _canonical_request_report_pair(name, interaction_names, aliases)
        if report:
            request_to_report[name] = report

    if request_to_report:
        updated: dict[str, MOMInteractionRule] = {}
        for name, rule in interaction_rules.items():
            updated[name] = MOMInteractionRule(
                name=rule.name,
                family=rule.family,
                role=rule.role,
                leaf_name=rule.leaf_name,
                parameters=rule.parameters,
                declared_parameters=rule.declared_parameters,
                inherited_parameters=rule.inherited_parameters,
                required_parameters=rule.required_parameters,
                optional_parameters=rule.optional_parameters,
                at_least_one_of=rule.at_least_one_of,
                report_name=request_to_report.get(name),
                is_leaf=rule.is_leaf,
                rti_direction=rule.rti_direction,
                parameter_datatypes=rule.parameter_datatypes,
            )
        interaction_rules = updated

    return MOMExposureModel(
        object_classes=dict(sorted(object_rules.items())),
        interaction_classes=dict(sorted(interaction_rules.items())),
        request_to_report=dict(sorted(request_to_report.items())),
        aliases=dict(sorted(aliases.items())),
    )


def build_negative_matrix(model: MOMExposureModel) -> dict[str, Any]:
    """Return a machine-readable negative-path planning matrix."""

    entries: dict[str, Any] = {}
    for name, rule in sorted(model.interaction_classes.items()):
        if not rule.is_receive_leaf:
            continue
        entries[name] = {
            "role": rule.role,
            "leaf": rule.leaf_name,
            "rti_direction": rule.rti_direction,
            "parameters": list(rule.parameters),
            "declared_parameters": list(rule.declared_parameters),
            "inherited_parameters": list(rule.inherited_parameters),
            "required_parameters": list(rule.required_parameters),
            "optional_parameters": list(rule.optional_parameters),
            "at_least_one_of": list(rule.at_least_one_of),
            "negative_cases": list(rule.negative_case_specs),
        }
    return {
        "interaction_count": len(model.interaction_classes),
        "receive_leaf_count": len(entries),
        "entries": entries,
    }


__all__ = [
    "MOMObjectClassRule",
    "MOMInteractionRule",
    "MOMValidationIssue",
    "MOMExposureModel",
    "MOM_PARAMETER_ALIASES",
    "MOM_OPTIONAL_DECLARED_PARAMETERS_BY_LEAF",
    "MOM_BOOL_PARAMETERS",
    "MOM_FLOAT_PARAMETERS",
    "MOM_TIME_PARAMETERS",
    "MOM_INTERVAL_PARAMETERS",
    "MOM_HANDLE_PARAMETERS",
    "MOM_HANDLE_SET_PARAMETERS",
    "build_mom_exposure_model",
    "build_negative_matrix",
    "canonical_parameter_name",
    "canonical_attribute_name",
]
