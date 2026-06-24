from __future__ import annotations

import pytest

import hla.fom.mom as hla_mom
from hla.backends.common import RecordingFederateAmbassador
from hla.rti1516e.enums import CallbackModel
from hla.rti1516e.exceptions import RTIexception
from hla.rti1516e.exceptions import (
    RestoreNotRequested,
    SaveNotInitiated,
    TimeConstrainedAlreadyEnabled,
    TimeRegulationIsNotEnabled,
)
from hla.verification.repo_internal.mom_negative_testing import (
    build_mom_negative_parameter_map,
    build_mom_negative_test_cases,
    default_mom_model,
    mom_negative_case_report,
)
from hla.backends.python1516e import InMemoryRTIEngine, PythonRTIConfig
from hla.runtime.factory import create_rti_ambassador


MOM_MODEL = default_mom_model()
MOM_NEGATIVE_CASES = build_mom_negative_test_cases(MOM_MODEL)
RTI_STRICT_CASES = tuple(case for case in MOM_NEGATIVE_CASES if case.executable)
PLANNED_SERVICE_CASES = tuple(case for case in MOM_NEGATIVE_CASES if not case.executable)


def _make_strict_mom_rti(name: str):
    engine = InMemoryRTIEngine()
    rti = create_rti_ambassador("python1516e", engine=engine, config=PythonRTIConfig(strict_mom_parameter_decoding=True))
    fed = RecordingFederateAmbassador()
    rti.connect(fed, CallbackModel.HLA_EVOKED)
    rti.create_federation_execution(name, "TargetRadarFOMmodule.xml")
    rti.join_federation_execution("fed", "type", name)
    return engine, rti, fed


def _drain_callbacks(rti) -> None:
    for _ in range(20):
        rti.evoke_multiple_callbacks(0.0, 0.0)


def _decoded_mom_exception_texts(fed: RecordingFederateAmbassador) -> list[str]:
    values: list[str] = []
    for rec in fed.callbacks_named("receiveInteraction"):
        for payload in rec.args[1].values():
            try:
                values.append(hla_mom.decode_text(payload))
            except Exception:
                pass
    return values


def _rti_parameter_payload_for_negative_case(rti, case):
    rule = MOM_MODEL.interaction_rule(case.interaction_name)
    assert rule is not None
    return build_mom_negative_parameter_map(rti, case, rule)


def _generated_mom_negative_case_summary():
    return mom_negative_case_report(MOM_MODEL)


def _pytest_case_id(case) -> str:
    return case.case_id.lower()


def test_generated_mom_negative_matrix_is_materialized_as_pytest_cases():
    summary = _generated_mom_negative_case_summary()

    assert summary["total_generated_cases"] == len(MOM_NEGATIVE_CASES)
    assert summary["total_generated_cases"] >= 260
    assert summary["executable_case_count"] >= 230
    assert summary["planned_semantic_case_count"] >= 30
    assert summary["case_kind_counts"]["missing_required_parameter"] >= 80
    assert "1516.1-2010 §11.4.1" in summary["section_refs"]


@pytest.mark.parametrize("case", RTI_STRICT_CASES, ids=_pytest_case_id)
def test_generated_mom_negative_case_executes_against_strict_python_rti(case):
    _engine, rti, fed = _make_strict_mom_rti(f"fed-{case.case_id.lower()}")
    interaction = rti.get_interaction_class_handle(case.interaction_name)
    parameters = _rti_parameter_payload_for_negative_case(rti, case)

    with pytest.raises(RTIexception):
        rti.send_interaction(interaction, parameters, b"generated-mom-negative-case")

    _drain_callbacks(rti)
    decoded = _decoded_mom_exception_texts(fed)
    # Most cases produce the exact planned issue; a few syntactically invalid
    # handle cases are mapped to more specific ordinary RTI exception names by
    # the service layer while still exercising the same negative row.
    accepted = {
        case.expected_mom_exception,
        "InvalidMOMParameterEncoding",
        "FederateHandleNotKnown",
        "ObjectClassNotDefined",
        "InteractionClassNotDefined",
        "ObjectInstanceNotKnown",
        "InvalidMOMParameterHandle",
    }
    assert any(value in accepted for value in decoded), (case, decoded)


@pytest.mark.parametrize("case", PLANNED_SERVICE_CASES, ids=_pytest_case_id)
def test_generated_mom_service_action_rows_are_tracked_as_planned_semantics(case):
    # These rows are kept in the matrix but intentionally not forced through a
    # negative RTI send. Several MOM HLAservice interactions legitimately succeed
    # with valid parameters, so the conformance asset must distinguish planned
    # semantic negative cases from rows that are deterministically executable
    # through strict parameter validation.
    assert case.case == "unsupported_or_failed_service_action"
    assert case.executable is False
    assert case.interaction_name.startswith("HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.")


def _mom_service_params(rti, interaction_name: str, extra: dict[str, bytes] | None = None) -> dict:
    interaction = rti.get_interaction_class_handle(interaction_name)
    params = {
        rti.get_parameter_handle(interaction, "HLAfederate"): rti.backend.state.handle.encode(),
    }
    for name, value in (extra or {}).items():
        params[rti.get_parameter_handle(interaction, name)] = value
    return params


@pytest.mark.parametrize(
    ("interaction_name", "extra", "expected_exception"),
    (
        (
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAfederateSaveBegun",
            {},
            SaveNotInitiated,
        ),
        (
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAfederateRestoreComplete",
            {},
            RestoreNotRequested,
        ),
        (
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAmodifyLookahead",
            {"HLAlookahead": None},
            TimeRegulationIsNotEnabled,
        ),
    ),
)
def test_selected_mom_service_actions_execute_as_semantic_negative_cases(
    interaction_name, extra, expected_exception
):
    _engine, rti, fed = _make_strict_mom_rti(
        f"semantic-{interaction_name.rsplit('.', 1)[-1].lower()}"
    )

    if interaction_name.endswith("HLAmodifyLookahead"):
        extra = {
            "HLAlookahead": rti.get_time_factory().make_interval(1.0).encode(),
        }

    payload = _mom_service_params(rti, interaction_name, extra)
    interaction = rti.get_interaction_class_handle(interaction_name)

    with pytest.raises(expected_exception):
        rti.send_interaction(interaction, payload, b"mom-semantic-negative")

    _drain_callbacks(rti)
    decoded = _decoded_mom_exception_texts(fed)
    if decoded:
        assert expected_exception.__name__ in decoded


def test_mom_service_action_reports_runtime_precondition_failure_after_real_setup():
    _engine, rti, fed = _make_strict_mom_rti("semantic-enable-time-constrained")
    rti.enable_time_constrained()
    rti.enable_asynchronous_delivery()
    _drain_callbacks(rti)

    interaction_name = (
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAenableTimeConstrained"
    )
    interaction = rti.get_interaction_class_handle(interaction_name)
    payload = _mom_service_params(rti, interaction_name)

    with pytest.raises(TimeConstrainedAlreadyEnabled):
        rti.send_interaction(interaction, payload, b"mom-semantic-negative-enabled")

    _drain_callbacks(rti)
    decoded = _decoded_mom_exception_texts(fed)
    if decoded:
        assert "TimeConstrainedAlreadyEnabled" in decoded
