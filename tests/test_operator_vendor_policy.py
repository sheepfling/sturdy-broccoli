from __future__ import annotations

from dataclasses import dataclass

import pytest

from tests.doc_test_helpers import (
    DocCase,
    MultiPathDocCase,
    assert_doc_case,
    assert_doc_case_across_paths,
    load_json_fixture,
    primary_text,
)


@dataclass(frozen=True)
class OperatorVendorPolicy:
    bootstrap_flow_case: MultiPathDocCase
    vendor_green_case: MultiPathDocCase
    vendor_state_case: MultiPathDocCase
    pitch_no_script_case: MultiPathDocCase
    pitch_lost_federate_case: MultiPathDocCase
    special_vendor_cases: tuple[DocCase, ...]

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> OperatorVendorPolicy:
        return cls(
            bootstrap_flow_case=MultiPathDocCase(
                case_id="bootstrap_flow_paths",
                paths=tuple(str(path) for path in payload["bootstrap_flow_paths"]),
                must_contain=(
                    "./tools/bootstrap",
                    "./tools/python",
                    "./tools/certi-easy",
                    "./tools/pitch",
                    "./tools/vendor-green",
                ),
                must_not_contain=(),
            ),
            vendor_green_case=MultiPathDocCase(
                case_id="vendor_green_paths",
                paths=tuple(str(path) for path in payload["vendor_green_paths"]),
                must_contain=("./tools/vendor-green",),
                must_not_contain=(),
            ),
            vendor_state_case=MultiPathDocCase(
                case_id="vendor_state_paths",
                paths=tuple(str(path) for path in payload["vendor_state_paths"]),
                must_contain=("./tools/vendor-state",),
                must_not_contain=(
                    "python3 scripts/classify_vendor_runtime.py",
                    "python3 scripts/ci/check_vendor_runtime_ci_state.py",
                ),
            ),
            pitch_no_script_case=MultiPathDocCase(
                case_id="pitch_no_script_paths",
                paths=tuple(str(path) for path in payload["pitch_no_script_paths"]),
                must_contain=(),
                must_not_contain=(
                    "./scripts/ci/vendor_green.sh",
                    "./scripts/pitch_docker_easy.sh",
                    "scripts/run_pitch_local.sh",
                ),
            ),
            pitch_lost_federate_case=MultiPathDocCase(
                case_id="pitch_lost_federate_paths",
                paths=tuple(str(path) for path in payload["pitch_lost_federate_paths"]),
                must_contain=(
                    "./tools/pitch lost-federate",
                    "./tools/pitch lost-federate-probe",
                ),
                must_not_contain=(
                    "./scripts/pitch_docker_easy.sh lost-federate",
                    "./scripts/pitch_docker_easy.sh lost-federate-probe",
                    "./scripts/ci/vendor_green.sh pitch",
                ),
            ),
            special_vendor_cases=tuple(
                DocCase.from_mapping(case)
                for case in payload["special_vendor_cases"]
            ),
        )


POLICY = OperatorVendorPolicy.from_mapping(load_json_fixture("operator_vendor_policy.json"))


def test_public_docs_use_tools_surface_for_vendor_operator_flows() -> None:
    assert_doc_case_across_paths(POLICY.bootstrap_flow_case, reader=primary_text)


def test_vendor_runtime_docs_use_tools_vendor_green_surface() -> None:
    assert_doc_case_across_paths(POLICY.vendor_green_case, reader=primary_text)


def test_vendor_runtime_docs_use_tools_vendor_state_surface() -> None:
    assert_doc_case_across_paths(POLICY.vendor_state_case, reader=primary_text)


def test_public_pitch_docs_do_not_promote_script_operator_surfaces() -> None:
    assert_doc_case_across_paths(POLICY.pitch_no_script_case, reader=primary_text)


def test_pitch_lost_federate_docs_keep_tools_operator_surface_explicit() -> None:
    assert_doc_case_across_paths(POLICY.pitch_lost_federate_case, reader=primary_text)


@pytest.mark.parametrize(
    "case",
    POLICY.special_vendor_cases,
    ids=lambda case: case.case_id,
)
def test_specialized_vendor_operator_surfaces(case: DocCase) -> None:
    assert_doc_case(case, reader=primary_text)
