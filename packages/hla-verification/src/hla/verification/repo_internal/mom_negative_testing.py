"""Executable MOM negative-path assets generated from the active MIM/FOM catalog.

The v0.12 matrix was a planning artifact.  This module turns the parameter
validation portion of that matrix into concrete pytest-friendly cases while
keeping the semantic service-precondition rows visible as planned conformance
work.

Section anchors: IEEE 1516.1-2010 §11.3, §11.4.1, §11.5, and Annex G.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from hla.rti1516e import mom as hla_mom
from hla.rti1516e.fom import FOMCatalog, FOMResolver
from hla.rti1516e.handles import (
    AttributeHandle,
    DimensionHandle,
    InteractionClassHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    TransportationTypeHandle,
)
from hla.backends.inmemory.mom_catalog import (
    MOM_BOOL_PARAMETERS,
    MOM_FLOAT_PARAMETERS,
    MOM_INTERVAL_PARAMETERS,
    MOM_TIME_PARAMETERS,
    MOMExposureModel,
    MOMInteractionRule,
    build_mom_exposure_model,
    build_negative_matrix,
)

EXPECTED_MOM_EXCEPTION_BY_CASE: dict[str, str] = {
    "unexpected_parameter": "UnexpectedMOMParameter",
    "missing_required_parameter": "MissingMOMParameter",
    "missing_parameter_choice": "MissingMOMParameterChoice",
    "bad_boolean_encoding": "InvalidMOMParameterEncoding",
    "bad_float_encoding": "InvalidMOMParameterEncoding",
    "bad_time_encoding": "InvalidMOMParameterEncoding",
    "bad_interval_encoding": "InvalidMOMParameterEncoding",
    "bad_handle_encoding": "InvalidMOMParameterEncoding",
    "unsupported_or_failed_service_action": "MOMServiceActionFailed",
}

EXECUTABLE_PARAMETER_CASES = frozenset(
    {
        "unexpected_parameter",
        "missing_required_parameter",
        "missing_parameter_choice",
        "bad_boolean_encoding",
        "bad_float_encoding",
        "bad_time_encoding",
        "bad_interval_encoding",
        "bad_handle_encoding",
    }
)


@dataclass(frozen=True)
class MOMNegativeTestCase:
    """A single generated MOM negative-path case.

    ``executable`` is deliberately explicit so generated semantic cases can
    remain in verification assets without being hidden or misrepresented as
    already executable parameter-validation tests.
    """

    case_id: str
    interaction_name: str
    case: str
    parameter: str = ""
    parameters: tuple[str, ...] = ()
    expected_mom_exception: str = ""
    expected_python_exception: str = "RTIexception"
    executable: bool = True
    reason: str = ""
    section_refs: tuple[str, ...] = ("1516.1-2010 §11.4.1", "1516.1-2010 §11.5")
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def execution_level(self) -> str:
        return "rti-strict" if self.executable else "planned"

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "interaction_name": self.interaction_name,
            "case": self.case,
            "parameter": self.parameter,
            "parameters": list(self.parameters),
            "expected_mom_exception": self.expected_mom_exception,
            "expected_python_exception": self.expected_python_exception,
            "executable": self.executable,
            "execution_level": self.execution_level,
            "reason": self.reason,
            "section_refs": list(self.section_refs),
            "metadata": dict(self.metadata),
        }


def default_mom_model(*, fom_designators: Any = "TargetRadarFOMmodule.xml") -> MOMExposureModel:
    """Build the default Target/Radar + standard-MIM MOM exposure model."""

    catalog: FOMCatalog = FOMResolver().merge(fom_designators)
    return build_mom_exposure_model(catalog)


def _slug(text: str) -> str:
    out = []
    for ch in text:
        out.append(ch if ch.isalnum() else "-")
    return "-".join(part for part in "".join(out).split("-") if part).lower()


def build_mom_negative_test_cases(
    model: MOMExposureModel,
    *,
    include_semantic_service_cases: bool = True,
) -> tuple[MOMNegativeTestCase, ...]:
    """Return generated negative cases with executable flags.

    Parameter-shape and parameter-encoding rows are executable directly against
    the strict pure-Python RTI.  Semantic service-action rows require bespoke
    federation preconditions; they are included by default as non-executable
    matrix rows so the conformance matrix remains honest about the remaining
    work.
    """

    matrix = build_negative_matrix(model)
    cases: list[MOMNegativeTestCase] = []
    ordinal = 1
    for interaction_name, entry in sorted(matrix["entries"].items()):
        rule = model.interaction_rule(interaction_name)
        if rule is None:
            continue
        for spec in entry["negative_cases"]:
            case_kind = str(spec["case"])
            if case_kind == "unsupported_or_failed_service_action" and not include_semantic_service_cases:
                continue
            parameter = str(spec.get("parameter", ""))
            parameters = tuple(str(p) for p in spec.get("parameters", ()) if p)
            executable = case_kind in EXECUTABLE_PARAMETER_CASES
            reason = (
                "executable strict MOM parameter validation"
                if executable
                else (
                    "semantic service-action precondition case; retained in matrix, "
                    "not part of the generated parameter-validation test set"
                )
            )
            case_id = f"MOM-NEG-1516-1-2010-{ordinal:04d}-{_slug(rule.leaf_name)}-{_slug(case_kind)}"
            if parameter:
                case_id = f"{case_id}-{_slug(parameter)}"
            cases.append(
                MOMNegativeTestCase(
                    case_id=case_id,
                    interaction_name=interaction_name,
                    case=case_kind,
                    parameter=parameter,
                    parameters=parameters,
                    expected_mom_exception=EXPECTED_MOM_EXCEPTION_BY_CASE.get(case_kind, "MOMException"),
                    expected_python_exception="RTIexception",
                    executable=executable,
                    reason=reason,
                    metadata={"role": entry.get("role"), "leaf": entry.get("leaf"), "rti_direction": entry.get("rti_direction")},
                )
            )
            ordinal += 1
    return tuple(cases)


def executable_mom_negative_test_cases(model: MOMExposureModel) -> tuple[MOMNegativeTestCase, ...]:
    """Return only generated cases executable by the common strict test harness."""

    return tuple(case for case in build_mom_negative_test_cases(model) if case.executable)


def mom_negative_case_report(model: MOMExposureModel) -> dict[str, Any]:
    cases = build_mom_negative_test_cases(model)
    executable = [case for case in cases if case.executable]
    planned = [case for case in cases if not case.executable]
    by_kind: dict[str, int] = {}
    by_kind_executable: dict[str, int] = {}
    for case in cases:
        by_kind[case.case] = by_kind.get(case.case, 0) + 1
        if case.executable:
            by_kind_executable[case.case] = by_kind_executable.get(case.case, 0) + 1
    return {
        "section_refs": ["1516.1-2010 §11.3", "1516.1-2010 §11.4.1", "1516.1-2010 §11.5", "1516.1-2010 Annex G"],
        "total_generated_cases": len(cases),
        "executable_case_count": len(executable),
        "planned_semantic_case_count": len(planned),
        "case_kind_counts": dict(sorted(by_kind.items())),
        "executable_case_kind_counts": dict(sorted(by_kind_executable.items())),
        "planned_case_ids": [case.case_id for case in planned],
        "cases": [case.as_dict() for case in cases],
    }


def _encoded_known_object_class(rti: Any) -> bytes:
    for name in ("HLAobjectRoot.PhysicalEntity.Target", "HLAobjectRoot.HLAmanager.HLAfederation", "HLAobjectRoot"):
        try:
            return rti.get_object_class_handle(name).encode()
        except Exception:
            continue
    return ObjectClassHandle(1).encode()


def _encoded_known_interaction_class(rti: Any) -> bytes:
    for name in (
        "HLAinteractionRoot.TrackReport",
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetTiming",
        "HLAinteractionRoot",
    ):
        try:
            return rti.get_interaction_class_handle(name).encode()
        except Exception:
            continue
    return InteractionClassHandle(1).encode()


def valid_mom_payload_for_parameter(rti: Any, rule: MOMInteractionRule, name: str) -> bytes:
    """Return a syntactically valid payload for a MOM parameter name."""

    if name == "HLAfederate":
        return rti.backend.state.handle.encode()
    if name in MOM_BOOL_PARAMETERS:
        return hla_mom.encode_bool(True)
    if name in MOM_FLOAT_PARAMETERS:
        return hla_mom.encode_text("1.0")
    if name in MOM_TIME_PARAMETERS:
        try:
            return rti.get_time_factory().make_time(1.0).encode()
        except Exception:
            return hla_mom.encode_text("1.0")
    if name in MOM_INTERVAL_PARAMETERS:
        try:
            return rti.get_time_factory().make_interval(0.1).encode()
        except Exception:
            return hla_mom.encode_text("0.1")
    if name in {"HLAobjectClass", "HLAobjectClassName"}:
        return _encoded_known_object_class(rti)
    if name in {"HLAinteractionClass", "HLAinteractionClassName"}:
        return _encoded_known_interaction_class(rti)
    if name == "HLAobjectInstance":
        return ObjectInstanceHandle(1).encode()
    if name in {"HLAtransportation", "HLAtransportationType"}:
        try:
            return rti.get_transportation_type_handle("HLAreliable").encode()
        except Exception:
            return TransportationTypeHandle(1).encode()
    if name in {"HLAattributeList", "HLAattribute"}:
        return AttributeHandle(1).encode()
    if name == "HLAfederateList":
        return rti.backend.state.handle.encode()
    if name == "HLAdimensionHandleSet":
        return DimensionHandle(1).encode()
    if name == "HLAsendOrder":
        return hla_mom.encode_text("RECEIVE")
    if name == "HLAresignAction":
        return hla_mom.encode_text("NO_ACTION")
    if name == "HLAtag":
        return b"MOM-negative-test"
    return hla_mom.encode_text("test")


def invalid_mom_payload_for_parameter(case: MOMNegativeTestCase) -> bytes:
    if case.case == "bad_boolean_encoding":
        return b"not-a-boolean"
    if case.case == "bad_float_encoding":
        return b"not-a-float"
    if case.case == "bad_time_encoding":
        return b"x"
    if case.case == "bad_interval_encoding":
        return b"x"
    if case.case == "bad_handle_encoding":
        # Handles encode as exactly eight bytes.  A one-byte non-numeric value
        # fails both binary-handle and text-integer decode paths.
        return b"x"
    return b"bad"


def build_mom_negative_parameter_map(rti: Any, case: MOMNegativeTestCase, rule: MOMInteractionRule) -> dict[ParameterHandle, bytes]:
    """Build an HLA ParameterHandleValueMap for an executable negative case."""

    interaction = rti.get_interaction_class_handle(case.interaction_name)
    payloads: dict[str, bytes] = {}

    if case.case == "unexpected_parameter":
        encoded = {
            rti.backend.engine.get_or_create_parameter(interaction, "HLAunexpectedParameter"): b"unexpected"
        }
        for name in rule.required_parameters:
            encoded[rti.get_parameter_handle(interaction, name)] = valid_mom_payload_for_parameter(rti, rule, name)
        if rule.at_least_one_of:
            name = rule.at_least_one_of[0]
            encoded.setdefault(
                rti.get_parameter_handle(interaction, name),
                valid_mom_payload_for_parameter(rti, rule, name),
            )
        return encoded
    elif case.case == "missing_required_parameter":
        missing = case.parameter
        for name in rule.required_parameters:
            if name != missing:
                payloads[name] = valid_mom_payload_for_parameter(rti, rule, name)
    elif case.case == "missing_parameter_choice":
        if "HLAfederate" in rule.parameters:
            payloads["HLAfederate"] = valid_mom_payload_for_parameter(rti, rule, "HLAfederate")
    else:
        # Encoding errors: provide all required parameters and the bad optional
        # parameter being tested.  For HLAsetSwitches, also provide one valid
        # switch choice when the bad parameter is not itself a switch so the
        # payload validation row is the first failure observed.
        for name in rule.required_parameters:
            payloads[name] = valid_mom_payload_for_parameter(rti, rule, name)
        if rule.at_least_one_of and case.parameter not in rule.at_least_one_of:
            payloads[rule.at_least_one_of[0]] = valid_mom_payload_for_parameter(rti, rule, rule.at_least_one_of[0])
        if case.parameter:
            payloads[case.parameter] = invalid_mom_payload_for_parameter(case)

    return {rti.get_parameter_handle(interaction, name): value for name, value in payloads.items()}


__all__ = [
    "MOMNegativeTestCase",
    "EXPECTED_MOM_EXCEPTION_BY_CASE",
    "EXECUTABLE_PARAMETER_CASES",
    "build_mom_negative_test_cases",
    "build_mom_negative_parameter_map",
    "default_mom_model",
    "executable_mom_negative_test_cases",
    "invalid_mom_payload_for_parameter",
    "mom_negative_case_report",
    "valid_mom_payload_for_parameter",
]
