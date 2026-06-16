from __future__ import annotations

import pytest

from hla.rti1516e import mom as hla_mom
from hla.rti1516e.ambassadors import RecordingFederateAmbassador
from hla.rti1516e.backends.python_rti import InMemoryRTIEngine, PythonRTIConfig
from hla.rti1516e.enums import CallbackModel
from hla.rti1516e.exceptions import RTIexception
from hla.rti1516e.mom_negative_testing import (
    build_mom_negative_parameter_map,
    default_mom_model,
    executable_mom_negative_test_cases,
    mom_negative_case_report,
)
from hla.rti1516e.rti import create_rti_ambassador


MODEL = default_mom_model()
EXECUTABLE_CASES = executable_mom_negative_test_cases(MODEL)
REPORT = mom_negative_case_report(MODEL)


def _joined(name: str):
    engine = InMemoryRTIEngine()
    rti = create_rti_ambassador(
        "python",
        engine=engine,
        config=PythonRTIConfig(strict_mom_parameter_decoding=True),
    )
    fed = RecordingFederateAmbassador()
    rti.connect(fed, CallbackModel.HLA_EVOKED)
    rti.create_federation_execution(name, "TargetRadarFOMmodule.xml")
    rti.join_federation_execution("fed", "type", name)
    return engine, rti, fed


def _drain(rti) -> None:
    for _ in range(10):
        rti.evoke_multiple_callbacks(0.0, 0.0)


def _decoded_exception_values(fed: RecordingFederateAmbassador) -> list[str]:
    values: list[str] = []
    for rec in fed.callbacks_named("receiveInteraction"):
        for payload in rec.args[1].values():
            try:
                values.append(hla_mom.decode_text(payload))
            except Exception:
                try:
                    values.append(bytes(payload).decode("utf-8", errors="ignore"))
                except Exception:
                    pass
    return values


def test_generated_mom_negative_matrix_has_executable_parameter_cases_and_visible_semantic_backlog():
    assert REPORT["total_generated_cases"] >= 269
    assert REPORT["executable_case_count"] >= 230
    assert REPORT["planned_semantic_case_count"] >= 30
    assert REPORT["executable_case_kind_counts"]["missing_required_parameter"] >= 80
    assert REPORT["executable_case_kind_counts"]["bad_handle_encoding"] >= 70
    assert all(case.executable for case in EXECUTABLE_CASES)


@pytest.mark.parametrize("case", EXECUTABLE_CASES, ids=lambda c: c.case_id)
def test_generated_mom_negative_matrix_case_executes(case):
    _engine, rti, fed = _joined(f"mom-neg-v013-{case.case_id[-24:]}")
    rule = rti.backend._mom_exposure_model(rti.backend.state.federation).interaction_rule(case.interaction_name)
    assert rule is not None
    interaction = rti.get_interaction_class_handle(case.interaction_name)
    params = build_mom_negative_parameter_map(rti, case, rule)

    with pytest.raises(RTIexception):
        rti.send_interaction(interaction, params, case.case_id.encode("utf-8"))
    _drain(rti)

    values = _decoded_exception_values(fed)
    assert case.expected_mom_exception in values
    if case.parameter:
        assert case.parameter in values
    assert case.interaction_name in values or rule.name in values
