"""Executable MOM negative-test case generation from the active MIM/FOM catalog.

The generated matrix in :mod:`hla2010.mom_catalog` is useful only if it can be
turned into runnable checks.  This module provides that bridge for pytest and
for future external conformance harnesses.

Section anchors: IEEE 1516.1-2010 §11.3-§11.5 and Annex G.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable, Mapping

from .. import mom as hla_mom
from .. import mom_catalog
from ..enums import CallbackModel
from ..fom import FOMResolver
from ..handles import (
    AttributeHandle,
    FederateHandle,
    InteractionClassHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    TransportationTypeHandle,
)
from ..rti import create_rti_ambassador
from ..ambassadors import RecordingFederateAmbassador
from ..backends.python_rti import InMemoryRTIEngine, PythonRTIConfig


@dataclass(frozen=True)
class MOMNegativeCase:
    """One generated MOM negative-path case.

    ``execution_level`` is intentionally explicit.  Most rows can be exercised
    through the RTI service path.  The remaining service-action rows are useful
    conformance-planning rows but are not all deterministic negative executions
    because several of those services legitimately succeed when supplied valid
    parameters.
    """

    case_id: str
    interaction_name: str
    case_kind: str
    parameter_name: str = ""
    expected_issue_kind: str = ""
    expected_exception_name: str = "InteractionParameterNotDefined"
    execution_level: str = "rti-strict"
    section: str = "IEEE 1516.1-2010 §11.3-§11.5"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def pytest_id(self) -> str:
        suffix = f"/{self.parameter_name}" if self.parameter_name else ""
        leaf = self.interaction_name.rsplit(".", 1)[-1]
        return f"{leaf}:{self.case_kind}{suffix}"


_CASE_TO_ISSUE = {
    "unexpected_parameter": "UnexpectedMOMParameter",
    "missing_required_parameter": "MissingMOMParameter",
    "missing_parameter_choice": "MissingMOMParameterChoice",
    "bad_boolean_encoding": "InvalidMOMParameterEncoding",
    "bad_float_encoding": "InvalidMOMParameterEncoding",
    "bad_time_encoding": "InvalidMOMParameterEncoding",
    "bad_interval_encoding": "InvalidMOMParameterEncoding",
    "bad_handle_encoding": "InvalidMOMParameterEncoding",
    "unsupported_or_failed_service_action": "UnsupportedMOMServiceActionOrServiceException",
}
_CASE_TO_EXCEPTION = {
    "unexpected_parameter": "InteractionParameterNotDefined",
    "missing_required_parameter": "InteractionParameterNotDefined",
    "missing_parameter_choice": "InteractionParameterNotDefined",
    "bad_boolean_encoding": "InteractionParameterNotDefined",
    "bad_float_encoding": "InteractionParameterNotDefined",
    "bad_time_encoding": "InteractionParameterNotDefined",
    "bad_interval_encoding": "InteractionParameterNotDefined",
    "bad_handle_encoding": "InteractionParameterNotDefined",
    "unsupported_or_failed_service_action": "RTIexception",
}


def default_mom_exposure_model() -> mom_catalog.MOMExposureModel:
    """Build the same MOM exposure model used by the Python RTI startup path."""

    catalog = FOMResolver().merge("TargetRadarFOMmodule.xml")
    return mom_catalog.build_mom_exposure_model(catalog)


def generate_mom_negative_cases(model: mom_catalog.MOMExposureModel | None = None) -> tuple[MOMNegativeCase, ...]:
    """Flatten :func:`hla2010.mom_catalog.build_negative_matrix` into cases."""

    model = model or default_mom_exposure_model()
    matrix = mom_catalog.build_negative_matrix(model)
    cases: list[MOMNegativeCase] = []
    for interaction_name, entry in sorted(matrix["entries"].items()):
        for ordinal, item in enumerate(entry["negative_cases"], start=1):
            kind = str(item["case"])
            parameter = str(item.get("parameter") or ",".join(item.get("parameters") or ()) or "")
            execution_level = "planned-service-semantics" if kind == "unsupported_or_failed_service_action" else "rti-strict"
            cases.append(
                MOMNegativeCase(
                    case_id=f"MOMNEG-{len(cases) + 1:04d}",
                    interaction_name=interaction_name,
                    case_kind=kind,
                    parameter_name=parameter,
                    expected_issue_kind=_CASE_TO_ISSUE.get(kind, kind),
                    expected_exception_name=_CASE_TO_EXCEPTION.get(kind, "RTIexception"),
                    execution_level=execution_level,
                )
            )
    return tuple(cases)


def generated_mom_negative_case_summary(cases: Iterable[MOMNegativeCase] | None = None) -> dict[str, Any]:
    cases = tuple(cases or generate_mom_negative_cases())
    by_kind: dict[str, int] = {}
    by_level: dict[str, int] = {}
    for case in cases:
        by_kind[case.case_kind] = by_kind.get(case.case_kind, 0) + 1
        by_level[case.execution_level] = by_level.get(case.execution_level, 0) + 1
    return {
        "case_count": len(cases),
        "by_kind": dict(sorted(by_kind.items())),
        "by_execution_level": dict(sorted(by_level.items())),
        "section_refs": ["IEEE 1516.1-2010 §11.3", "IEEE 1516.1-2010 §11.4.1", "IEEE 1516.1-2010 §11.5", "IEEE 1516.1-2010 Annex G"],
    }


def make_strict_mom_rti(federation_name: str = "mom-negative-generated"):
    """Return ``(engine, rti, federate_ambassador)`` joined in strict MOM mode."""

    engine = InMemoryRTIEngine()
    rti = create_rti_ambassador(
        "python",
        engine=engine,
        config=PythonRTIConfig(strict_mom_parameter_decoding=True, strict_interaction_publication=False),
    )
    fed = RecordingFederateAmbassador()
    rti.connect(fed, CallbackModel.HLA_EVOKED)
    rti.create_federation_execution(federation_name, "TargetRadarFOMmodule.xml")
    rti.join_federation_execution("momNegativeFederate", "test", federation_name)
    return engine, rti, fed


def drain_callbacks(rti: Any, count: int = 20) -> None:
    for _ in range(count):
        rti.evoke_multiple_callbacks(0.0, 0.0)


def decoded_mom_exception_texts(fed: RecordingFederateAmbassador) -> list[str]:
    """Decode string-ish values in received MOM exception reports."""

    values: list[str] = []
    for rec in fed.callbacks_named("receiveInteraction"):
        for payload in rec.args[1].values():
            try:
                values.append(hla_mom.decode_text(payload))
            except Exception:
                try:
                    values.append(hla_mom.decode_opaque(payload).decode("utf-8", errors="ignore"))
                except Exception:
                    pass
    return values


def _known_object_instance_handle(rti: Any) -> ObjectInstanceHandle:
    federation = rti.backend.state.federation
    for handle, obj in federation.objects.items():
        if obj.owner is None:
            return handle
    return next(iter(federation.objects))


def _known_attribute_handle(rti: Any) -> AttributeHandle:
    class_handle = rti.get_object_class_handle("HLAobjectRoot.HLAmanager.HLAfederate")
    return rti.get_attribute_handle(class_handle, "HLAfederateName")


def valid_mom_value_for_parameter(rti: Any, parameter_name: str) -> bytes:
    """Return a syntactically valid payload for a declared MOM parameter."""

    name = str(parameter_name)
    state = rti.backend.state
    federation = state.federation
    if name == "HLAfederate":
        return state.handle.encode()
    if name in mom_catalog.MOM_BOOL_PARAMETERS:
        return hla_mom.encode_bool(True)
    if name in mom_catalog.MOM_FLOAT_PARAMETERS:
        return hla_mom.encode_text("1.0")
    if name in mom_catalog.MOM_TIME_PARAMETERS:
        return federation.time_factory.make_time(1.0).encode()
    if name in mom_catalog.MOM_INTERVAL_PARAMETERS:
        return federation.time_factory.make_interval(0.1).encode()
    if name in {"HLAobjectClass", "HLAobjectClassName"}:
        return rti.get_object_class_handle("HLAobjectRoot.HLAmanager.HLAfederate").encode()
    if name in {"HLAinteractionClass", "HLAinteractionClassName"}:
        return rti.get_interaction_class_handle("HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation").encode()
    if name == "HLAobjectInstance":
        return _known_object_instance_handle(rti).encode()
    if name in {"HLAtransportation", "HLAtransportationType"}:
        return rti.backend.engine.transportation_reliable.encode()
    if name in {"HLAattribute", "HLAattributeList"}:
        return _known_attribute_handle(rti).encode()
    if name == "HLAfederateList":
        return state.handle.encode()
    if name == "HLAdimensionHandleSet":
        return rti.get_dimension_handle("HLAdefaultRoutingSpace").encode()
    if name in {"HLAorderType", "HLAsendOrder"}:
        return hla_mom.encode_text("RECEIVE")
    if name == "HLAresignAction":
        return hla_mom.encode_text("NO_ACTION")
    if name == "HLAlabel":
        return hla_mom.encode_text("ReadyToRun")
    if name == "HLAtag":
        return b"MOM-negative-test"
    if name.endswith("Count") or name.endswith("Counts") or name in {"HLAnumberOfClasses", "HLAserialNumber", "HLAFOMmoduleIndicator"}:
        return hla_mom.encode_count(1)
    return hla_mom.encode_text(f"{name}-value")


def bad_mom_value_for_case(case: MOMNegativeCase) -> bytes:
    if case.case_kind == "bad_boolean_encoding":
        return b"not-bool"
    if case.case_kind == "bad_float_encoding":
        return hla_mom.encode_text("not-a-float")
    if case.case_kind in {"bad_time_encoding", "bad_interval_encoding"}:
        return b"bad"
    if case.case_kind == "bad_handle_encoding":
        return b"bad"
    return b"bad"


def valid_parameter_name_payloads(rti: Any, interaction_name: str) -> dict[str, bytes]:
    model = rti.backend._mom_exposure_model(rti.backend.state.federation)
    rule = model.interaction_rule(interaction_name)
    if rule is None:
        return {}
    values: dict[str, bytes] = {}
    for name in rule.required_parameters:
        values[name] = valid_mom_value_for_parameter(rti, name)
    for name in rule.at_least_one_of[:1]:
        values[name] = valid_mom_value_for_parameter(rti, name)
    return values


def parameter_name_payloads_for_negative_case(rti: Any, case: MOMNegativeCase) -> dict[str, bytes]:
    values = valid_parameter_name_payloads(rti, case.interaction_name)
    model = rti.backend._mom_exposure_model(rti.backend.state.federation)
    rule = model.interaction_rule(case.interaction_name)
    if rule is None:
        return values
    if case.case_kind == "missing_required_parameter":
        values.pop(case.parameter_name, None)
    elif case.case_kind == "missing_parameter_choice":
        for name in case.parameter_name.split(","):
            values.pop(name, None)
    elif case.case_kind.startswith("bad_") and case.parameter_name:
        for name in rule.required_parameters:
            values.setdefault(name, valid_mom_value_for_parameter(rti, name))
        for name in rule.at_least_one_of[:1]:
            values.setdefault(name, valid_mom_value_for_parameter(rti, name))
        values[case.parameter_name] = bad_mom_value_for_case(case)
    return values


def parameter_handles_for_names(rti: Any, interaction_name: str, parameters: Mapping[str, bytes]) -> dict[ParameterHandle, bytes]:
    handle = rti.get_interaction_class_handle(interaction_name)
    encoded: dict[ParameterHandle, bytes] = {}
    for name, value in parameters.items():
        encoded[rti.get_parameter_handle(handle, name)] = bytes(value)
    return encoded


def rti_parameter_payload_for_negative_case(rti: Any, case: MOMNegativeCase) -> dict[ParameterHandle, bytes]:
    interaction = rti.get_interaction_class_handle(case.interaction_name)
    if case.case_kind == "unexpected_parameter":
        values = valid_parameter_name_payloads(rti, case.interaction_name)
        result = parameter_handles_for_names(rti, case.interaction_name, values)
        result[rti.get_parameter_handle(interaction, "HLAunexpectedNegativeTestParameter")] = hla_mom.encode_text("unexpected")
        return result
    return parameter_handles_for_names(rti, case.interaction_name, parameter_name_payloads_for_negative_case(rti, case))


__all__ = [
    "MOMNegativeCase",
    "default_mom_exposure_model",
    "decoded_mom_exception_texts",
    "drain_callbacks",
    "generate_mom_negative_cases",
    "generated_mom_negative_case_summary",
    "make_strict_mom_rti",
    "parameter_name_payloads_for_negative_case",
    "rti_parameter_payload_for_negative_case",
    "valid_mom_value_for_parameter",
]
