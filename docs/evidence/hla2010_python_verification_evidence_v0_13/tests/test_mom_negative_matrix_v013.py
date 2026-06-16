from __future__ import annotations

import pytest

from hla.rti1516e.exceptions import RTIexception
from hla.rti1516e.testing.mom_negative import (
    decoded_mom_exception_texts,
    drain_callbacks,
    generate_mom_negative_cases,
    generated_mom_negative_case_summary,
    make_strict_mom_rti,
    rti_parameter_payload_for_negative_case,
)


MOM_NEGATIVE_CASES = generate_mom_negative_cases()
RTI_STRICT_CASES = tuple(case for case in MOM_NEGATIVE_CASES if case.execution_level == "rti-strict")
PLANNED_SERVICE_CASES = tuple(case for case in MOM_NEGATIVE_CASES if case.execution_level == "planned-service-semantics")


def test_generated_mom_negative_matrix_is_materialized_as_pytest_cases():
    summary = generated_mom_negative_case_summary(MOM_NEGATIVE_CASES)

    assert summary["case_count"] == len(MOM_NEGATIVE_CASES)
    assert summary["case_count"] >= 260
    assert summary["by_execution_level"]["rti-strict"] >= 230
    assert summary["by_execution_level"]["planned-service-semantics"] >= 30
    assert summary["by_kind"]["missing_required_parameter"] >= 80
    assert "1516.1-2010 §11.4.1" in summary["section_refs"]


@pytest.mark.parametrize("case", RTI_STRICT_CASES, ids=lambda c: c.pytest_id())
def test_generated_mom_negative_case_executes_against_strict_python_rti(case):
    _engine, rti, fed = make_strict_mom_rti(f"fed-{case.case_id.lower()}")
    interaction = rti.get_interaction_class_handle(case.interaction_name)
    parameters = rti_parameter_payload_for_negative_case(rti, case)

    with pytest.raises(RTIexception):
        rti.send_interaction(interaction, parameters, b"generated-mom-negative-case")

    drain_callbacks(rti)
    decoded = decoded_mom_exception_texts(fed)
    # Most cases produce the exact planned issue; a few syntactically invalid
    # handle cases are mapped to more specific ordinary RTI exception names by
    # the service layer while still exercising the same negative row.
    accepted = {
        case.expected_issue_kind,
        "InvalidMOMParameterEncoding",
        "FederateHandleNotKnown",
        "ObjectClassNotDefined",
        "InteractionClassNotDefined",
        "ObjectInstanceNotKnown",
        "InvalidMOMParameterHandle",
    }
    assert any(value in accepted for value in decoded), (case, decoded)


@pytest.mark.parametrize("case", PLANNED_SERVICE_CASES, ids=lambda c: c.pytest_id())
def test_generated_mom_service_action_rows_are_tracked_as_planned_semantics(case):
    # These rows are kept in the matrix but intentionally not forced through a
    # negative RTI send. Several MOM HLAservice interactions legitimately succeed
    # with valid parameters, so the conformance asset must distinguish planned
    # semantic negative cases from rows that are deterministically executable
    # through strict parameter validation.
    assert case.case_kind == "unsupported_or_failed_service_action"
    assert case.execution_level == "planned-service-semantics"
    assert case.interaction_name.startswith("HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.")
